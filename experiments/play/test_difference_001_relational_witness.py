import unittest

from difference_001_relational_witness import (
    TARGET,
    World,
    observe,
    run,
    worlds_matching_left,
    worlds_matching_pair,
    worlds_matching_right,
)


class Difference001Tests(unittest.TestCase):
    def test_registered_target_requires_relation_for_unique_depth(self):
        receipt = run()
        self.assertTrue(receipt["left_witness"]["ambiguous_depth"])
        self.assertTrue(receipt["right_witness"]["ambiguous_depth"])
        self.assertTrue(receipt["pair"]["unique_registered_world"])
        self.assertTrue(receipt["relation"]["matches_target_depth"])
        self.assertTrue(
            receipt["supports_relational_recovery_in_registered_geometry"]
        )

    def test_single_witnesses_really_have_multiple_depth_candidates(self):
        left, right = observe(TARGET)
        self.assertGreater(
            len({w.z for w in worlds_matching_left(left)}), 1
        )
        self.assertGreater(
            len({w.z for w in worlds_matching_right(right)}), 1
        )

    def test_pair_identifies_registered_world(self):
        left, right = observe(TARGET)
        self.assertEqual(worlds_matching_pair(left, right), (TARGET,))

    def test_exact_replay(self):
        self.assertEqual(run(), run())

    def test_nonregistered_easy_case_does_not_fake_acceptance(self):
        # This world is valid geometry, but the acceptance predicate is allowed
        # to fail when a single witness is already sufficient in the candidate set.
        receipt = run(World(x=9, z=6))
        if not (
            receipt["left_witness"]["ambiguous_depth"]
            and receipt["right_witness"]["ambiguous_depth"]
        ):
            self.assertFalse(
                receipt["supports_relational_recovery_in_registered_geometry"]
            )


if __name__ == "__main__":
    unittest.main()
