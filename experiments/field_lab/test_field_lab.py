import copy
import json
import pathlib
import subprocess
import sys
import unittest

from experiments.field_lab.field_lab import run_field_lab


ROOT = pathlib.Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "integrations" / "ghot" / "field_lab_adapter.py"

BASE = {
    "experiment": "robotics.r001.body-morphology",
    "particular_packet": {"packet_id": "example:001"},
    "current_field": {"body": "light_rigid"},
    "perturbation": {"body": "heavy_compliant"},
    "declared_invariants": ["controller", "challenge", "dt", "steps"],
}


class FieldLab001Tests(unittest.TestCase):
    def test_controlled_perturbation_changes_trajectory_in_model(self):
        result = run_field_lab(BASE)
        self.assertTrue(result["observations"]["trajectory_changed"])
        self.assertTrue(all(result["invariant_checks"].values()))
        self.assertEqual(
            result["causal_evidence"]["status"],
            "SUPPORTS_DECLARED_BODY_CAUSAL_RELEVANCE_IN_MODEL",
        )
        self.assertFalse(result["counterfactual_candidate"]["historical_rewrite"])
        self.assertFalse(result["authority"]["mutate_external_state"])

    def test_replay_is_exact(self):
        self.assertEqual(run_field_lab(BASE), run_field_lab(BASE))

    def test_noop_perturbation_refuses(self):
        request = copy.deepcopy(BASE)
        request["perturbation"]["body"] = "light_rigid"
        with self.assertRaisesRegex(
            ValueError, "PERTURBATION_MUST_CHANGE_DECLARED_BODY"
        ):
            run_field_lab(request)

    def test_invariant_relaxation_refuses(self):
        request = copy.deepcopy(BASE)
        request["declared_invariants"] = ["controller"]
        with self.assertRaisesRegex(
            ValueError, "FIELD_LAB_001_REQUIRES_EXACT_FOUNDING_INVARIANTS"
        ):
            run_field_lab(request)

    def test_ghot_adapter_returns_content_addressed_receipt(self):
        completed = subprocess.run(
            [sys.executable, str(ADAPTER)],
            cwd=ADAPTER.parent,
            input=json.dumps(BASE),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(
            result["capability"], "analysis.tranchnose.field-lab"
        )
        self.assertEqual(
            len(result["artifact"]["receipt_sha256"]),
            64,
        )
        self.assertFalse(result["receipt"]["authority"]["admit"])
        self.assertFalse(result["receipt"]["authority"]["select"])


if __name__ == "__main__":
    unittest.main()
