#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("exp001a_harness", ROOT / "harness.py")
assert SPEC and SPEC.loader
harness = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(harness)


class HarnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = json.loads(
            (ROOT / "synthetic_manifest.json").read_text(encoding="utf-8")
        )

    def test_receipt_validates_and_replays_exactly(self) -> None:
        first = harness.build_receipt(self.manifest)
        second = harness.build_receipt(self.manifest)
        harness.validate_receipt(first)
        harness.replay(self.manifest, first)
        self.assertEqual(
            harness.canonical_bytes(first), harness.canonical_bytes(second)
        )
        self.assertTrue(first["coordination_audit"]["ceiling_compliant"])

    def test_real_field_dynamics_complete_target_after_node_loss(self) -> None:
        receipt = harness.build_receipt(self.manifest)
        self.assertEqual(receipt["condition"]["label"], "B")
        self.assertEqual(receipt["interventions"][0]["type"], "node_remove")
        self.assertEqual(receipt["observations"]["winning_basin"], "F_A")
        self.assertTrue(receipt["observations"]["converged"])
        self.assertGreaterEqual(receipt["observations"]["final_overlap"]["F_A"], 0.75)
        self.assertLess(receipt["observations"]["final_overlap"]["F_A"], 1.0)
        self.assertIsNone(receipt["failure"])

    def test_all_four_candidate_attractors_are_writable_and_measurable(self) -> None:
        for target in harness.dynamics.BASIN_NAMES:
            manifest = copy.deepcopy(self.manifest)
            manifest["inputs"]["target"] = target
            manifest["inputs"].update(
                harness.dynamics.expected_input_addresses(
                    target, harness.canonical_bytes
                )
            )
            manifest["intervention_count"] = 0
            receipt = harness.build_receipt(manifest)
            self.assertEqual(receipt["observations"]["winning_basin"], target)
            self.assertEqual(receipt["observations"]["final_overlap"][target], 1.0)

    def test_condition_a_loses_target_after_temporary_seed(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["condition"]["label"] = "A"
        manifest["condition"]["field_recurrence"] = False
        manifest["condition"]["electronic_reconstruction"] = False
        manifest["intervention_count"] = 0
        receipt = harness.build_receipt(manifest)
        self.assertFalse(receipt["observations"]["converged"])
        self.assertIsNone(receipt["observations"]["winning_basin"])
        self.assertEqual(receipt["failure"]["class"], "insufficient_recurrence")

    def test_condition_flags_are_mechanical_not_labels_only(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["condition"]["label"] = "A"
        with self.assertRaisesRegex(ValueError, "mechanically"):
            harness.build_receipt(manifest)

    def test_coordination_seed_does_not_change_field_outcome(self) -> None:
        first = harness.build_receipt(self.manifest)
        changed = copy.deepcopy(self.manifest)
        changed["randomness"]["streams"][1]["seed"] += "-changed"
        second = harness.build_receipt(changed)
        self.assertNotEqual(
            first["coordination_audit"]["transcript_digest"],
            second["coordination_audit"]["transcript_digest"],
        )
        self.assertNotEqual(first["identity"]["run_id"], second["identity"]["run_id"])
        self.assertEqual(first["observations"], second["observations"])

    def test_named_seed_change_changes_identity_and_digest(self) -> None:
        first = harness.build_receipt(self.manifest)
        changed = copy.deepcopy(self.manifest)
        changed["randomness"]["streams"][0]["seed"] += "-changed"
        second = harness.build_receipt(changed)
        self.assertNotEqual(
            first["identity"]["run_id"], second["identity"]["run_id"]
        )
        self.assertNotEqual(
            first["identity"]["receipt_digest"],
            second["identity"]["receipt_digest"],
        )

    def test_receipt_digest_recomputes_exactly(self) -> None:
        receipt = harness.build_receipt(self.manifest)
        digest_input = copy.deepcopy(receipt)
        digest_input["identity"].pop("receipt_digest")
        expected = harness.digest(harness.RECEIPT_DOMAIN, digest_input)
        self.assertEqual(expected, receipt["identity"]["receipt_digest"])

    def test_run_identity_excludes_ambient_metadata(self) -> None:
        interventions = harness.build_receipt(self.manifest)["interventions"]
        identity = harness.run_identity_input(self.manifest, interventions)
        encoded = harness.canonical_bytes(identity)
        for forbidden in (
            b"timestamp",
            b"hostname",
            b"process",
            b"filesystem",
            b"Date.now",
        ):
            self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
