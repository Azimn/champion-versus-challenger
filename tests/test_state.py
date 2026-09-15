import json
import tempfile
import unittest
from pathlib import Path

from cvc_research.state import PERMANENT_ARTIFACTS, validate_research_state


class ResearchStateTests(unittest.TestCase):
    def make_repo(self, state):
        tempdir = tempfile.TemporaryDirectory()
        root = Path(tempdir.name)
        for relative in PERMANENT_ARTIFACTS:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("placeholder\n", encoding="utf-8")
        state_path = root / "research" / "state.json"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        return tempdir, root

    def base_state(self):
        return {
            "protocol_version": "1.0",
            "champion": None,
            "last_experiment": "EXP-000",
            "candidates": {
                "PC-001": {
                    "name": "Candidate",
                    "classification": "RUNNABLE BASELINE",
                    "qualification_state": ["SOURCE VERIFIED", "EXECUTION PENDING"],
                    "source": "https://example.test/repo",
                }
            },
        }

    def test_initial_state_is_valid(self):
        tempdir, root = self.make_repo(self.base_state())
        try:
            self.assertEqual(validate_research_state(root), [])
        finally:
            tempdir.cleanup()

    def test_champion_without_battery_evidence_is_rejected(self):
        state = self.base_state()
        state["champion"] = {
            "candidate_id": "PC-001",
            "frozen_ref": "abc123",
            "promotion_experiment": "EXP-001",
        }
        tempdir, root = self.make_repo(state)
        try:
            errors = validate_research_state(root)
            self.assertTrue(any("BATTERY COMPLETE" in error for error in errors))
        finally:
            tempdir.cleanup()

    def test_champion_with_matching_evidence_is_valid(self):
        state = self.base_state()
        state["last_experiment"] = "EXP-001"
        state["candidates"]["PC-001"]["qualification_state"] = [
            "SOURCE VERIFIED",
            "EXECUTED",
            "ADAPTED",
            "BATTERY COMPLETE",
        ]
        state["candidates"]["PC-001"]["evidence_experiment"] = "EXP-001"
        state["champion"] = {
            "candidate_id": "PC-001",
            "frozen_ref": "abc123",
            "promotion_experiment": "EXP-001",
        }
        tempdir, root = self.make_repo(state)
        try:
            self.assertEqual(validate_research_state(root), [])
        finally:
            tempdir.cleanup()

    def test_exp_zero_cannot_promote_champion(self):
        state = self.base_state()
        state["candidates"]["PC-001"]["qualification_state"] = ["BATTERY COMPLETE"]
        state["candidates"]["PC-001"]["evidence_experiment"] = "EXP-000"
        state["champion"] = {
            "candidate_id": "PC-001",
            "frozen_ref": "abc123",
            "promotion_experiment": "EXP-000",
        }
        tempdir, root = self.make_repo(state)
        try:
            errors = validate_research_state(root)
            self.assertIn("EXP-000 cannot promote a champion", errors)
        finally:
            tempdir.cleanup()


if __name__ == "__main__":
    unittest.main()
