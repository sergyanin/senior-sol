import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "senior-sol"
INSTALL_SCRIPT = PLUGIN / "scripts" / "install-agents.ps1"
UNINSTALL_SCRIPT = PLUGIN / "scripts" / "uninstall-agents.ps1"
MANAGED_FILES = {
    "senior-sol-luna-low.toml",
    "senior-sol-luna-medium.toml",
    "senior-sol-terra-high.toml",
    "senior-sol-terra-low.toml",
    "senior-sol-terra-medium.toml",
}


def powershell_executable():
    return shutil.which("pwsh") or shutil.which("powershell")


def run_script(executable, script, codex_home, *args):
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    return subprocess.run(
        [executable, "-NoProfile", "-File", str(script), *args],
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


class PowerShellInstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.executable = powershell_executable()
        if cls.executable is None:
            raise unittest.SkipTest("PowerShell is not available")

    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.codex_home = Path(self.temporary_directory.name)
        self.target = self.codex_home / "agents"

    def install(self, *args):
        return run_script(self.executable, INSTALL_SCRIPT, self.codex_home, *args)

    def uninstall(self):
        return run_script(self.executable, UNINSTALL_SCRIPT, self.codex_home)

    def test_clean_install_creates_exactly_the_managed_files(self):
        result = self.install()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({path.name for path in self.target.iterdir()}, MANAGED_FILES)
        for name in MANAGED_FILES:
            self.assertEqual(
                (self.target / name).read_bytes(),
                (PLUGIN / "agents" / name).read_bytes(),
            )

    def test_second_install_reports_all_files_unchanged(self):
        self.assertEqual(self.install().returncode, 0)

        result = self.install()

        self.assertEqual(result.returncode, 0, result.stderr)
        for name in MANAGED_FILES:
            self.assertIn(f"unchanged: {name}", result.stdout)

    def test_conflict_fails_and_force_restores_template(self):
        self.assertEqual(self.install().returncode, 0)
        name = "senior-sol-luna-low.toml"
        destination = self.target / name
        destination.write_text("locally modified\n", encoding="utf-8")

        conflict = self.install()

        self.assertEqual(conflict.returncode, 1)
        self.assertIn(f"conflict: {name}", conflict.stdout)
        self.assertEqual(destination.read_text(encoding="utf-8"), "locally modified\n")

        forced = self.install("-Force")

        self.assertEqual(forced.returncode, 0, forced.stderr)
        self.assertIn(f"replaced: {name}", forced.stdout)
        self.assertEqual(destination.read_bytes(), (PLUGIN / "agents" / name).read_bytes())

    def test_uninstall_removes_managed_files_and_preserves_unrelated_file(self):
        self.assertEqual(self.install().returncode, 0)
        unrelated = self.target / "unrelated.toml"
        unrelated.write_text("unrelated\n", encoding="utf-8")

        result = self.uninstall()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.target.is_dir())
        self.assertEqual({path.name for path in self.target.iterdir()}, {"unrelated.toml"})
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "unrelated\n")
        for name in MANAGED_FILES:
            self.assertIn(f"removed: {name}", result.stdout)

    def test_uninstall_preserves_directory_with_managed_filename(self):
        self.target.mkdir()
        name = "senior-sol-luna-low.toml"
        same_named_directory = self.target / name
        same_named_directory.mkdir()

        result = self.uninstall()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(same_named_directory.is_dir())
        self.assertIn(f"missing: {name}", result.stdout)


if __name__ == "__main__":
    unittest.main()
