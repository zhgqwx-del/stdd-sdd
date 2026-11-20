import shutil
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile


SOURCE = Path(__file__).resolve().parents[1] / "STDD-SDD/.agents/skills/init-stdd"
STARTER = Path("assets/starter")
TEMPLATES = Path("docs/stdd/templates")
SKILLS = Path(".agents/skills")


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

    def test_custom_skill_layout_and_symlink(self):
        root = Path(".custom/skills")
        self.run_cli("--skills-dir", root.as_posix())
        stock_skill = SKILLS / "stdd-wrap/SKILL.md"
        target = self.project / root / stock_skill.relative_to(SKILLS)
        self.set_new_asset(stock_skill, b"New upstream version\n")
        self.assertNotIn(target.relative_to(self.project).as_posix(), self.upgrade("--dry-run"))
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


if __name__ == "__main__":
    unittest.main()
