import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "senior-sol"
POWERSHELL_INSTALL_SCRIPT = PLUGIN / "scripts" / "install-agents.ps1"
POWERSHELL_UNINSTALL_SCRIPT = PLUGIN / "scripts" / "uninstall-agents.ps1"
POSIX_INSTALL_SCRIPT = PLUGIN / "scripts" / "install-agents.sh"
POSIX_UNINSTALL_SCRIPT = PLUGIN / "scripts" / "uninstall-agents.sh"
MANAGED_FILES = {
    "senior-sol-luna-low.toml",
    "senior-sol-luna-medium.toml",
    "senior-sol-terra-high.toml",
    "senior-sol-terra-low.toml",
    "senior-sol-terra-medium.toml",
}


def powershell_executable():
    return shutil.which("pwsh") or shutil.which("powershell")


def bash_executable():
    if os.name == "nt":
        git = shutil.which("git")
        if git:
            git_bash = Path(git).resolve().parent.parent / "bin" / "bash.exe"
            if git_bash.is_file():
                return str(git_bash)
    return shutil.which("bash")


def run_script(command, codex_home):
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    return subprocess.run(
        command,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


class InstallerContract:
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.workspace = Path(self.temporary_directory.name).resolve()
        system_temp = Path(tempfile.gettempdir()).resolve()
        self.assertEqual(
            os.path.commonpath((str(self.workspace), str(system_temp))),
            str(system_temp),
            "recursive TemporaryDirectory cleanup must stay under the system temp directory",
        )
        self.codex_home = self.workspace / "codex-home"
        self.codex_home.mkdir()
        self.target = self.codex_home / "agents"

    def install(self, *args):
        return run_script(self.install_command(*args), self.codex_home)

    def uninstall(self):
        return run_script(self.uninstall_command(), self.codex_home)

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

        forced = self.install(self.force_argument)

        self.assertEqual(forced.returncode, 0, forced.stderr)
        self.assertIn(f"replaced: {name}", forced.stdout)
        self.assertEqual(destination.read_bytes(), (PLUGIN / "agents" / name).read_bytes())

    def test_managed_destination_directory_is_rejected_even_with_force(self):
        self.target.mkdir()
        name = "senior-sol-luna-low.toml"
        destination = self.target / name
        destination.mkdir()

        for argument in ((), (self.force_argument,)):
            with self.subTest(argument=argument):
                result = self.install(*argument)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(destination.is_dir())
                self.assertFalse(any(destination.iterdir()))

    def test_managed_destination_symlink_is_rejected_even_with_force(self):
        self.target.mkdir()
        name = "senior-sol-luna-low.toml"
        outside = self.workspace / "outside-managed.toml"
        outside.write_text("outside\n", encoding="utf-8")
        destination = self.target / name
        try:
            destination.symlink_to(outside)
        except OSError as exc:
            self.skipTest(f"symlink creation unavailable on this platform: {exc}")

        for argument in ((), (self.force_argument,)):
            with self.subTest(argument=argument):
                result = self.install(*argument)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(destination.is_symlink())
                self.assertEqual(outside.read_text(encoding="utf-8"), "outside\n")

    def test_agents_directory_symlink_is_rejected_without_writing_through_it(self):
        outside = self.workspace / "outside-agents"
        outside.mkdir()
        try:
            self.target.symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlink creation unavailable on this platform: {exc}")

        result = self.install(self.force_argument)

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(list(outside.iterdir()), [])

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


class PowerShellInstallerTests(InstallerContract, unittest.TestCase):
    force_argument = "-Force"

    @classmethod
    def setUpClass(cls):
        cls.executable = powershell_executable()
        if cls.executable is None:
            raise unittest.SkipTest("PowerShell is not available")

    def install_command(self, *args):
        return [
            self.executable,
            "-NoProfile",
            "-File",
            str(POWERSHELL_INSTALL_SCRIPT),
            *args,
        ]

    def uninstall_command(self):
        return [
            self.executable,
            "-NoProfile",
            "-File",
            str(POWERSHELL_UNINSTALL_SCRIPT),
        ]


class PosixInstallerTests(InstallerContract, unittest.TestCase):
    force_argument = "--force"

    @classmethod
    def setUpClass(cls):
        cls.executable = bash_executable()
        if cls.executable is None:
            raise unittest.SkipTest("bash is not available")

    def install_command(self, *args):
        return [self.executable, str(POSIX_INSTALL_SCRIPT), *args]

    def uninstall_command(self):
        return [self.executable, str(POSIX_UNINSTALL_SCRIPT)]


if __name__ == "__main__":
    unittest.main()
