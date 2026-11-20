from contextlib import redirect_stderr, redirect_stdout
from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO, StringIO
import shutil
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile


SOURCE = Path(__file__).resolve().parents[1] / "STDD-SDD/.agents/skills/init-stdd"
STARTER = Path("assets/starter")
TEMPLATES = Path("docs/stdd/templates")
SKILLS = Path(".agents/skills")
PREVIOUS_RELEASE = "v1.4.0"


class UpgradeTest(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.bundle = self.root / "init-stdd"
        shutil.copytree(SOURCE, self.bundle)
        self.baseline = self.root / "old.zip"
        with ZipFile(self.baseline, "w") as archive:
            for path in sorted((self.bundle / "assets").rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(self.root).as_posix())
        self.project = self.root / "project"
        self.version_file = self.project / ".stdd-version"
        self.tag = (self.bundle / "VERSION").read_text(encoding="ascii").strip()

    def run_cli(self, *args, check=True):
        return subprocess.run(
            [sys.executable, "-B", str(self.bundle / "scripts/init_stdd.py"), str(self.project), *args],
            check=check, capture_output=True, text=True, encoding="utf-8",
        )

    def upgrade(self, *args):
        return self.run_cli("--upgrade", "--from-bundle", str(self.baseline), *args).stdout

    def set_new_asset(self, path, data):
        asset = self.bundle / STARTER / path
        asset.write_bytes(data)

    def test_preview_and_apply_with_local_changes_and_deleted_files(self):
        self.run_cli("--agent", "codex")
        self.run_cli("--record-version", PREVIOUS_RELEASE)
        stock_skill = SKILLS / "stdd-wrap/SKILL.md"
        custom_skill = SKILLS / "stdd-start/SKILL.md"
        modified_template = TEMPLATES / "verification.md"
        customized_only = TEMPLATES / "test-plan.md"
        deleted = TEMPLATES / "tasks.md"
        retired = TEMPLATES / "release.md"
        added = TEMPLATES / "new-template.md"
        workflow = Path("docs/stdd/workflows.md")
        owned = Path("changes/001-first-slice/change.md")
        (self.project / owned).write_bytes(b"Project-owned change\n")
        (self.project / custom_skill).write_bytes(b"Local policy\n")
        (self.project / customized_only).write_bytes(b"Local test commands\n")
        (self.project / deleted).unlink()
        (self.project / stock_skill).chmod(0o640)
        for path in (stock_skill, custom_skill, modified_template, deleted, added):
            self.set_new_asset(path, b"New upstream version\n")
        (self.bundle / STARTER / retired).unlink()
        with (self.bundle / "assets/team" / workflow).open("ab") as asset:
            asset.write(b"\nNew workflow instructions\n")
        snapshot = {p: p.read_bytes() for p in self.project.rglob("*") if p.is_file()}

        preview = self.upgrade("--dry-run")
        self.assertIn(f"UPDATE    {stock_skill.as_posix()}", preview)
        self.assertIn(f"UPDATE    {modified_template.as_posix()}", preview)
        self.assertIn(f"UPDATE    {workflow.as_posix()}", preview)
        self.assertIn(f"MERGE     {custom_skill.as_posix()}", preview)
        self.assertIn(f"KEEP      {customized_only.as_posix()}", preview)
        self.assertIn(f"CREATE    {added.as_posix()}", preview)
        self.assertIn(f"MISSING   {deleted.as_posix()}", preview)
        self.assertIn(f"RETIRED   {retired.as_posix()}", preview)
        self.assertIn(f"--- baseline/{custom_skill.as_posix()}", preview)
        self.assertNotIn("Local policy", preview)
        self.assertEqual({p: p.read_bytes() for p in self.project.rglob("*") if p.is_file()}, snapshot)

        result = self.upgrade()
        self.assertIn(f"UPDATED   {stock_skill.as_posix()}", result)
        self.assertIn(f"CREATED   {added.as_posix()}", result)
        self.assertEqual((self.project / stock_skill).read_bytes(), b"New upstream version\n")
        self.assertEqual((self.project / stock_skill).stat().st_mode & 0o777, 0o640)
        self.assertEqual((self.project / custom_skill).read_bytes(), b"Local policy\n")
        self.assertEqual((self.project / owned).read_bytes(), b"Project-owned change\n")
        self.assertFalse((self.project / deleted).exists())
        self.assertEqual((self.project / retired).read_bytes(), snapshot[self.project / retired])
        self.assertFalse((self.project / ".claude").exists())
        self.assertFalse((self.project / ".qoder").exists())
        self.assertNotIn("UPDATED", self.upgrade())
        self.assertEqual(self.version_file.read_text(encoding="ascii").strip(), PREVIOUS_RELEASE)
        (self.project / custom_skill).write_bytes(b"New upstream version\n")
        self.assertIn("RECORDED", self.upgrade())
        self.assertEqual(self.version_file.read_text(encoding="ascii").strip(), self.tag)

    def test_custom_skill_layout_and_symlink(self):
        root = Path(".custom/skills")
        self.run_cli("--skills-dir", root.as_posix())
        stock_skill = SKILLS / "stdd-wrap/SKILL.md"
        target = self.project / root / stock_skill.relative_to(SKILLS)
        self.set_new_asset(stock_skill, b"New upstream version\n")
        self.assertIn(f"UPDATE    {target.relative_to(self.project).as_posix()}", self.upgrade("--dry-run"))
        self.assertIn(f"UPDATE    {target.relative_to(self.project).as_posix()}",
                      self.upgrade("--skills-dir", root.as_posix(), "--dry-run"))

        external = self.root / "external.md"
        target.rename(external)
        target.symlink_to(external)
        original = external.read_bytes()
        result = self.upgrade("--skills-dir", root.as_posix())
        self.assertIn(f"BLOCKED   {target.relative_to(self.project).as_posix()}", result)
        self.assertTrue(target.is_symlink())
        self.assertEqual(external.read_bytes(), original)

    def test_invalid_baseline_and_spec_profile(self):
        self.run_cli("--profile", "spec")
        template = TEMPLATES / "verification.md"
        self.set_new_asset(template, b"New upstream version\n")
        original = (self.project / template).read_bytes()
        invalid = self.root / "invalid.zip"
        with ZipFile(invalid, "w") as archive:
            archive.writestr("init-stdd/assets/starter/docs/stdd/templates/../spec.md", b"unsafe")
        result = self.run_cli("--upgrade", "--from-bundle", str(invalid), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid asset path", result.stderr)
        self.assertEqual((self.project / template).read_bytes(), original)
        self.assertIn(f"UPDATED   {template.as_posix()}", self.upgrade("--profile", "spec"))
        self.assertFalse((self.project / SKILLS).exists())

    def test_fresh_initialization_and_manual_recording_for_legacy_project(self):
        self.assertIn("RECORD    .stdd-version", self.run_cli("--dry-run").stdout)
        self.assertFalse(self.project.exists())
        self.run_cli()
        self.assertEqual(self.version_file.read_text(encoding="ascii").strip(), self.tag)

        self.version_file.unlink()
        self.run_cli()
        self.run_cli("--skills-only")
        self.assertFalse(self.version_file.exists())
        missing = self.run_cli("--upgrade", "--dry-run", check=False)
        self.assertIn("--record-version TAG", missing.stderr)
        invalid = self.run_cli("--record-version", "../v1.4.0", check=False)
        self.assertNotEqual(invalid.returncode, 0)
        self.run_cli("--record-version", PREVIOUS_RELEASE, "--dry-run")
        self.assertFalse(self.version_file.exists())
        self.run_cli("--record-version", PREVIOUS_RELEASE)
        self.run_cli()
        self.assertEqual(self.version_file.read_text(encoding="ascii").strip(), PREVIOUS_RELEASE)

    def test_upgrade_downloads_the_recorded_release_and_advances_after_apply(self):
        self.run_cli("--agent", "codex")
        self.run_cli("--record-version", PREVIOUS_RELEASE)
        template = TEMPLATES / "verification.md"
        self.set_new_asset(template, b"New upstream version\n")
        script = self.bundle / "scripts/init_stdd.py"
        spec = spec_from_file_location("isolated_init_stdd", script)
        initializer = module_from_spec(spec)
        spec.loader.exec_module(initializer)

        url = f"https://github.com/zhgqwx-del/stdd-sdd/releases/download/{PREVIOUS_RELEASE}/init-stdd.zip"
        argv = [str(script), str(self.project), "--upgrade"]
        mismatched_bundle = BytesIO(self.baseline.read_bytes())
        with ZipFile(mismatched_bundle, "a") as archive:
            archive.writestr("init-stdd/VERSION", self.tag + "\n")
        mismatched_bundle.seek(0)
        error = StringIO()
        with patch.object(initializer, "urlopen", return_value=mismatched_bundle):
            with patch.object(sys, "argv", argv), redirect_stdout(StringIO()), redirect_stderr(error):
                with self.assertRaises(SystemExit) as exit_status:
                    initializer.main()
        self.assertEqual(exit_status.exception.code, 1)
        self.assertIn(f"expected {PREVIOUS_RELEASE}", error.getvalue())
        self.assertEqual(self.version_file.read_text(encoding="ascii").strip(), PREVIOUS_RELEASE)
        self.assertNotEqual((self.project / template).read_bytes(), b"New upstream version\n")

        for args in (["--dry-run"], []):
            output = StringIO()
            with patch.object(initializer, "urlopen", return_value=BytesIO(self.baseline.read_bytes())) as download:
                with patch.object(sys, "argv", [*argv, *args]), redirect_stdout(output):
                    initializer.main()
            download.assert_called_once_with(url, timeout=30)
            state = "UPDATE    " if args else "UPDATED   "
            self.assertIn(state + template.as_posix(), output.getvalue())
            self.assertEqual(self.version_file.read_text(encoding="ascii").strip(),
                             PREVIOUS_RELEASE if args else self.tag)

        with patch.object(initializer, "urlopen") as download:
            with patch.object(sys, "argv", argv), redirect_stdout(StringIO()):
                initializer.main()
        download.assert_not_called()

    def test_subset_upgrade_keeps_previous_release(self):
        self.run_cli()
        self.run_cli("--record-version", PREVIOUS_RELEASE)
        self.set_new_asset(SKILLS / "stdd-start/SKILL.md", b"New upstream version\n")
        result = self.upgrade("--agent", "codex")
        self.assertIn("only part of the installed scaffold", result)
        self.assertEqual(self.version_file.read_text(encoding="ascii").strip(), PREVIOUS_RELEASE)
        self.assertIn("UPDATED   .claude/skills/stdd-start/SKILL.md", self.upgrade())
        self.assertEqual(self.version_file.read_text(encoding="ascii").strip(), self.tag)


if __name__ == "__main__":
    unittest.main()
