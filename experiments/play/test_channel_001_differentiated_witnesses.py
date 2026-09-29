import unittest

from channel_001_differentiated_witnesses import (
    World,
    differentiated_signature,
    redundant_signature,
    run,
    signature_classes,
    worlds,
    worlds_matching_channel,
)


class Channel001Tests(unittest.TestCase):
    def test_same_channel_count_different_distinguishability(self):
        receipt = run()
        self.assertEqual(receipt["channel_count"]["redundant"], 4)
        self.assertEqual(receipt["channel_count"]["differentiated"], 4)
        self.assertLess(
            receipt["redundant_bank"]["unique_signature_count"],
            receipt["registered_world_count"],
        )
        self.assertEqual(
            receipt["differentiated_bank"]["unique_signature_count"],
            receipt["registered_world_count"],
        )
        self.assertTrue(
            receipt[
                "supports_specialization_distinguishability_in_registered_world"
            ]
        )

    def test_target_is_ambiguous_under_every_single_differentiated_channel(self):
        target = World("red", 1)
        signature = differentiated_signature(target)
        counts = [
            len(
                worlds_matching_channel(
                    differentiated_signature, index, signature[index]
                )
            )
            for index in range(4)
        ]
        self.assertTrue(all(count > 1 for count in counts))

    def test_full_differentiated_signature_is_unique_for_every_world(self):
        classes = signature_classes(differentiated_signature)
        self.assertEqual(len(classes), len(worlds()))
        self.assertTrue(all(len(group) == 1 for group in classes.values()))

    def test_redundant_bank_cannot_distinguish_spectrum_at_fixed_intensity(self):
        self.assertEqual(
            redundant_signature(World("blue", 2)),
            redundant_signature(World("green", 2)),
        )
        self.assertEqual(
            redundant_signature(World("green", 2)),
            redundant_signature(World("red", 2)),
        )

    def test_exact_replay(self):
        self.assertEqual(run(), run())


if __name__ == "__main__":
    unittest.main()
