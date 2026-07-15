import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.validate import MANAGED_PROFILES, validate_repository


class AgentProfileTests(unittest.TestCase):
    def test_exact_profile_set_and_settings(self):
        agent_dir = ROOT / "plugins" / "senior-sol" / "agents"
        self.assertEqual({p.stem for p in agent_dir.glob("*.toml")}, set(MANAGED_PROFILES))
        for name, (model, effort, read_only) in MANAGED_PROFILES.items():
            data = tomllib.loads((agent_dir / f"{name}.toml").read_text(encoding="utf-8"))
            self.assertEqual(data["name"], name)
            self.assertEqual(data["model"], model)
            self.assertEqual(data["model_reasoning_effort"], effort)
            self.assertTrue(data["description"])
            self.assertTrue(data["developer_instructions"])
            self.assertEqual(data.get("sandbox_mode") == "read-only", read_only)

    def test_repository_validator_accepts_profiles(self):
        self.assertEqual(validate_repository(ROOT), [])
