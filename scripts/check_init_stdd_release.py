"""Verify the init-stdd release candidate and, optionally, the public download."""

import argparse
from hashlib import sha256
from http.client import HTTPException
from io import BytesIO
import json
import os
from pathlib import Path, PurePosixPath
import re
from stat import S_ISLNK
import subprocess
import sys
from tempfile import TemporaryDirectory
from time import sleep
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "zhgqwx-del/stdd-sdd"
GUIDES = ROOT / "STDD-SDD"
SKILL = GUIDES / ".agents/skills/init-stdd"
ZIP_PATH = GUIDES / "init-stdd.zip"
LATEST_URL = f"https://github.com/{REPOSITORY}/releases/latest/download/{ZIP_PATH.name}"
RELEASE_TAG = re.compile(r"v[0-9]+\.[0-9]+\.[0-9]+")
DOWNLOAD_LINK = re.compile(r"\[[^\]\n]+\]\((https?://[^)\s]+/releases/latest/download/init-stdd\.zip)\)")


def check_guides() -> str:
    quickstart = GUIDES / "QUICKSTART.md"
    usage = SKILL / "references/usage.md"
    quickstart_urls = set(DOWNLOAD_LINK.findall(quickstart.read_text(encoding="utf-8")))
    if quickstart_urls != {LATEST_URL}:
        raise ValueError(f"{quickstart.relative_to(ROOT)} must link to {LATEST_URL}")
    latest_url, = quickstart_urls
    for page in (ROOT / "README.md", usage):
        urls = set(DOWNLOAD_LINK.findall(page.read_text(encoding="utf-8")))
        if urls != {LATEST_URL}:
            raise ValueError(f"{page.relative_to(ROOT)} must link to {LATEST_URL}")

    manual = GUIDES / "STDD 与 SDD 实践手册.md"
    text = manual.read_text(encoding="utf-8")
    for target in (SKILL / "SKILL.md", ZIP_PATH):
        if f"]({target.relative_to(GUIDES).as_posix()})" not in text:
            raise ValueError(f"The practice manual must link to {target.relative_to(ROOT)}")
    for page in (manual, quickstart, SKILL / "SKILL.md", usage):
        text = page.read_text(encoding="utf-8")
        missing = [token for token in (".stdd-version", "--upgrade", "--dry-run",
                                       "--record-version", "--from-bundle") if token not in text]
        if missing:
            raise ValueError(f"{page.relative_to(ROOT)} lacks upgrade instructions for {', '.join(missing)}")

    return latest_url


def check_archive(data: bytes, tag: str, unpack_to: Path) -> None:
    expected = {}
    for path in SKILL.rglob("*"):
        relative = path.relative_to(SKILL.parent)
        if path.name == ".DS_Store" or "__pycache__" in relative.parts or path.suffix in (".pyc", ".pyo"):
            continue
        if path.is_symlink():
            raise ValueError(f"Skill source contains a symlink: {relative}")
        if path.is_file():
            expected[relative.as_posix()] = path

    with ZipFile(BytesIO(data)) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("ZIP contains duplicate paths")
        directories = {parent.as_posix() + "/" for name in expected for parent in PurePosixPath(name).parents
                       if parent.name}
        files = {entry.filename for entry in archive.infolist() if not entry.is_dir()}
        missing = expected.keys() - files
        extra = (set(names) - files - directories) | (files - expected.keys())
        if missing or extra:
            raise ValueError(f"ZIP file list differs from source. Missing: {sorted(missing)}. Extra: {sorted(extra)}.")
        for entry in archive.infolist():
            if S_ISLNK(entry.external_attr >> 16):
                raise ValueError(f"ZIP contains a symlink: {entry.filename}")
            if not entry.is_dir() and archive.read(entry) != expected[entry.filename].read_bytes():
                raise ValueError(f"ZIP content differs from source: {entry.filename}")

        if archive.read("init-stdd/VERSION").decode("ascii").strip() != tag:
            raise ValueError(f"ZIP VERSION must match the release tag {tag}")
        archive.extractall(unpack_to)
    print(f"ZIP matches all {len(expected)} files in the skill source.")


def check_initializer(unpacked: Path, tag: str) -> None:
    script = unpacked / "init-stdd/scripts/init_stdd.py"
    for profile in ("spec", "team", "demo"):
        project = unpacked / profile
        command = [sys.executable, "-B", str(script), str(project), "--profile", profile]
        subprocess.run([*command, "--dry-run"], check=True, capture_output=True, text=True)
        if project.exists():
            raise ValueError(f"{profile} preview wrote to the target project")
        subprocess.run(command, check=True, capture_output=True, text=True)
        if (project / ".stdd-version").read_text(encoding="ascii").strip() != tag:
            raise ValueError(f"{profile} recorded the wrong bundle version")
        rules = project / "AGENTS.md"
        rules.write_bytes(b"# Project-specific rules\n")
        subprocess.run(command, check=True, capture_output=True, text=True)
        if rules.read_bytes() != b"# Project-specific rules\n":
            raise ValueError(f"{profile} changed the project's existing AGENTS.md")
        if profile == "demo":
            subprocess.run(["make", "-C", str(project), "check"], check=True)
        print(f"{profile}: preview, initialization and existing file preservation passed.")

    blocked = unpacked / "blocked"
    (blocked / "AGENTS.md").mkdir(parents=True)
    result = subprocess.run([sys.executable, "-B", str(script), str(blocked)],
                            check=True, capture_output=True, text=True)
    if "BLOCKED   AGENTS.md" not in result.stdout or not (blocked / "AGENTS.md").is_dir():
        raise ValueError("The initializer did not report and preserve a blocked path")
    print("Blocked path preservation passed.")


def read_url(url: str, headers: dict[str, str]) -> bytes:
    with urlopen(Request(url, headers=headers), timeout=20) as response:
        return response.read()


def check_latest(tag: str, url: str, digest: str, commit: str) -> None:
    metadata_url = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "stdd-sdd-release-check"}
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    ref = f"refs/tags/{tag}"

    # Latest metadata and the asset CDN may update at different times.
    for delay in (0, 5, 10, 20, 30):
        try:
            sleep(delay)
            release = json.loads(read_url(metadata_url, headers))
            if release["tag_name"] != tag:
                raise ValueError(f"GitHub Latest is {release['tag_name']}, expected {tag}")
            assets = [asset for asset in release["assets"] if asset["name"] == ZIP_PATH.name]
            if len(assets) != 1 or assets[0]["state"] != "uploaded":
                raise ValueError(f"GitHub Latest has no uploaded {ZIP_PATH.name} asset")
            downloaded = sha256(read_url(url, {})).hexdigest()
            if downloaded != digest:
                raise ValueError(f"Latest download SHA-256 is {downloaded}, expected {digest}")
            asset_digest = assets[0].get("digest")
            if asset_digest and asset_digest != f"sha256:{digest}":
                raise ValueError(f"GitHub asset digest is {asset_digest}, expected sha256:{digest}")

            output = subprocess.check_output(
                ["git", "ls-remote", f"https://github.com/{REPOSITORY}.git", ref, ref + "^{}"],
                timeout=20, text=True,
            )
            refs = {name: sha for sha, name in (line.split() for line in output.splitlines())}
            tagged_commit = refs.get(ref + "^{}", refs.get(ref))
            if not tagged_commit or (commit and tagged_commit != commit):
                raise ValueError(f"{tag} points to {tagged_commit}, expected {commit or 'a Git commit'}")
            raw_url = f"https://raw.githubusercontent.com/{REPOSITORY}/{tagged_commit}/{ZIP_PATH.relative_to(ROOT).as_posix()}"
            if sha256(read_url(raw_url, {})).hexdigest() != digest:
                raise ValueError(f"The ZIP committed at {tag} differs from the published file")
        except (OSError, HTTPException, ValueError, subprocess.SubprocessError) as error:
            last_error = error
            print(f"Latest check pending: {error}", file=sys.stderr, flush=True)
        else:
            print(f"Latest download verified: {tag}, commit {tagged_commit}, SHA-256 `{digest}`.")
            return
    raise ValueError(f"Latest download check failed: {last_error}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="Expected release tag, in the form vX.Y.Z")
    parser.add_argument("--check-latest", action="store_true", help="Also verify the public Latest attachment")
    parser.add_argument("--commit", default="", help="Expected Git commit for the published tag")
    args = parser.parse_args()
    try:
        if not RELEASE_TAG.fullmatch(args.tag):
            raise ValueError("--tag must use the form vX.Y.Z")
        source_tag = (SKILL / "VERSION").read_text(encoding="ascii").strip()
        if source_tag != args.tag:
            raise ValueError(f"Skill VERSION is {source_tag}, expected {args.tag}")
        url = check_guides()
        data = ZIP_PATH.read_bytes()
        with TemporaryDirectory(prefix="init-stdd-release-") as temporary:
            directory = Path(temporary)
            check_archive(data, args.tag, directory)
            if not args.check_latest:
                check_initializer(directory, args.tag)
        digest = sha256(data).hexdigest()
        print(f"Release candidate: {args.tag}, SHA-256 `{digest}`.")
        if args.check_latest:
            check_latest(args.tag, url, digest, args.commit)
    except subprocess.CalledProcessError as error:
        parser.exit(1, f"Release check failed: {error}\n{error.stdout or ''}{error.stderr or ''}")
    except (OSError, ValueError, BadZipFile) as error:
        parser.exit(1, f"Release check failed: {error}\n")


if __name__ == "__main__":
    main()
