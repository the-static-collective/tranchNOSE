import unittest

from r001_body_state import BODIES, Body, Controller
from r002_address_answer import address_answer, compare_answerability


class R002AddressAnswerTests(unittest.TestCase):
    def test_registered_bodies_are_response_discriminable(self):
        result = compare_answerability()
        self.assertTrue(result["same_controller"])
        self.assertTrue(result["same_initial_observable"])
        self.assertTrue(result["different_body_particular"])
        self.assertTrue(result["different_answer_set"])
        self.assertTrue(result["supports_response_discriminability_in_model"])

    def test_exact_replay(self):
        first = address_answer(BODIES["light_rigid"])
        second = address_answer(BODIES["light_rigid"])
        self.assertEqual(first, second)

    def test_name_is_not_particular(self):
        original = BODIES["light_rigid"]
        alias = Body(
            name="renamed_only",
            mass=original.mass,
            drag=original.drag,
            traction=original.traction,
            compliance=original.compliance,
        )
        first = address_answer(original)
        second = address_answer(alias)
        self.assertEqual(first["body_particular_ref"], second["body_particular_ref"])
        self.assertEqual(first["answer_set_digest"], second["answer_set_digest"])
        self.assertNotEqual(first["body_label"], second["body_label"])

    def test_body_change_changes_answer_without_controller_change(self):
        controller = Controller()
        first = address_answer(BODIES["light_rigid"], controller)
        second = address_answer(BODIES["heavy_compliant"], controller)
        self.assertEqual(first["controller_ref"], second["controller_ref"])
        self.assertNotEqual(first["body_particular_ref"], second["body_particular_ref"])
        self.assertNotEqual(first["answer_set_digest"], second["answer_set_digest"])

    def test_non_claims_remain_explicit(self):
        receipt = address_answer(BODIES["heavy_compliant"])
        self.assertIn(
            "answer signature is not consciousness or personhood evidence",
            receipt["non_claims"],
        )


if __name__ == "__main__":
    unittest.main()
