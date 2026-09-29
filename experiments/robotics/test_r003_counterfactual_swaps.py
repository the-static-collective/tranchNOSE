import unittest

from r003_counterfactual_swaps import (
    CONTROLLER_A,
    HISTORY_A,
    HISTORY_B,
    STATE_A,
    STATE_B,
    TOPOLOGIES,
    counterfactual_matrix,
    run_counterfactual,
)
from r001_body_state import BODIES


class R003CounterfactualSwapTests(unittest.TestCase):
    def test_matrix_separates_causal_components_from_provenance(self):
        matrix = counterfactual_matrix()
        self.assertTrue(matrix["supports_declared_separation_in_model"])

        for key in (
            "controller_swap",
            "body_swap",
            "topology_swap",
            "latent_state_swap",
        ):
            self.assertTrue(matrix["runs"][key]["response_changed_from_baseline"])

        self.assertFalse(
            matrix["runs"]["provenance_only_swap"]["response_changed_from_baseline"]
        )

    def test_latent_swap_preserves_visible_snapshot(self):
        matrix = counterfactual_matrix()
        latent = matrix["runs"]["latent_state_swap"]
        self.assertTrue(latent["same_observable_as_baseline"])
        self.assertFalse(latent["same_latent_as_baseline"])
        self.assertTrue(latent["response_changed_from_baseline"])

    def test_provenance_only_changes_receipt_not_physics(self):
        baseline = run_counterfactual(
            controller=CONTROLLER_A,
            body=BODIES["light_rigid"],
            topology=TOPOLOGIES["direct"],
            state=STATE_A,
            history=HISTORY_A,
        )
        changed_history = run_counterfactual(
            controller=CONTROLLER_A,
            body=BODIES["light_rigid"],
            topology=TOPOLOGIES["direct"],
            state=STATE_A,
            history=HISTORY_B,
        )
        self.assertNotEqual(baseline["history_ref"], changed_history["history_ref"])
        self.assertNotEqual(baseline["receipt_digest"], changed_history["receipt_digest"])
        self.assertEqual(
            baseline["response"]["trajectory_digest"],
            changed_history["response"]["trajectory_digest"],
        )

    def test_same_visible_state_different_latent_state_changes_future(self):
        baseline = run_counterfactual(
            controller=CONTROLLER_A,
            body=BODIES["light_rigid"],
            topology=TOPOLOGIES["direct"],
            state=STATE_A,
            history=HISTORY_A,
        )
        latent = run_counterfactual(
            controller=CONTROLLER_A,
            body=BODIES["light_rigid"],
            topology=TOPOLOGIES["direct"],
            state=STATE_B,
            history=HISTORY_A,
        )
        self.assertEqual(
            baseline["observable_state_ref"],
            latent["observable_state_ref"],
        )
        self.assertNotEqual(
            baseline["latent_state_ref"],
            latent["latent_state_ref"],
        )
        self.assertNotEqual(
            baseline["response"]["trajectory_digest"],
            latent["response"]["trajectory_digest"],
        )

    def test_exact_replay(self):
        kwargs = dict(
            controller=CONTROLLER_A,
            body=BODIES["heavy_compliant"],
            topology=TOPOLOGIES["soft_coupled"],
            state=STATE_B,
            history=HISTORY_B,
        )
        self.assertEqual(run_counterfactual(**kwargs), run_counterfactual(**kwargs))


if __name__ == "__main__":
    unittest.main()
