import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent.gtm_agent import send_prospect_email


class SendProspectEmailTest(unittest.TestCase):
    runtime = SimpleNamespace(config={"metadata": {"user_id": "rep_amills"}})

    def call(self, prospect_id, **kwargs):
        return send_prospect_email.func(
            {
                "prospect_id": prospect_id,
                "email": "caller@example.com",
                "name": "Caller Name",
                "disqualified": False,
            },
            "Subject",
            "Body",
            self.runtime,
            **kwargs,
        )

    def test_disqualified_target_without_acknowledgement_is_blocked(self):
        result = self.call("LEAD-50002")

        self.assertEqual(
            result,
            {"status": "blocked", "reason": "prospect_disqualified", "prospect_id": "LEAD-50002"},
        )
        self.assertNotIn("message_id", result)

    def test_disqualified_target_with_acknowledgement_is_sent(self):
        result = self.call("LEAD-50002", disqualified_override_ack=True)

        self.assertEqual(result["status"], "sent")
        self.assertIn("message_id", result)
        self.assertTrue(result["disqualified"])

    def test_non_disqualified_target_is_sent(self):
        result = self.call("LEAD-12853")

        self.assertEqual(result["status"], "sent")
        self.assertIn("message_id", result)
        self.assertNotIn("disqualified", result)


if __name__ == "__main__":
    unittest.main()
