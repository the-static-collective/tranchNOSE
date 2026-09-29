import unittest

from experiments.robotics.r001_body_state import (
    BODIES,
    Controller,
    compare_bodies,
    simulate,
)


class R001BodyStateTests(unittest.TestCase):
    def test_same_controller_different_body_changes_trajectory(self):
        result = compare_bodies()
        self.assertTrue(result["same_controller"])
        self.assertTrue(result["different_body"])
        self.assertTrue(result["different_trajectory"])
        self.assertTrue(result["supports_body_causal_relevance_in_model"])

    def test_replay_is_exact(self):
        first = simulate(BODIES["light_rigid"])
        second = simulate(BODIES["light_rigid"])
        self.assertEqual(first, second)

    def test_controller_change_changes_controller_ref(self):
        base = simulate(BODIES["light_rigid"], Controller())
        changed = simulate(
            BODIES["light_rigid"],
            Controller(target_velocity=0.8, kp=2.0, command_limit=2.5),
        )
        self.assertNotEqual(
            base["receipt"]["controller_ref"],
            changed["receipt"]["controller_ref"],
        )

    def test_receipt_preserves_non_claims(self):
        receipt = simulate(BODIES["heavy_compliant"])["receipt"]
        self.assertIn(
            "software dynamics are not physical proof",
            receipt["non_claims"],
        )


if __name__ == "__main__":
    unittest.main()
