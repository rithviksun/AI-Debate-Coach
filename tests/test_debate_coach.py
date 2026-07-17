import unittest

from debate_coach import generate_debate_content, rate_opening_statement


class DebateCoachTests(unittest.TestCase):
    def test_generate_debate_content_uses_fallback_without_api_key(self):
        result = generate_debate_content("Should AI be regulated?", "For", "Logical", api_key=None)

        self.assertEqual(result["source"], "fallback")
        self.assertIn("I support", result["opening_statement"])
        self.assertGreaterEqual(len(result["possible_rebuttals"]), 3)
        self.assertIn("feedback", result)
        self.assertGreaterEqual(result["score"], 0)

    def test_rate_opening_statement_returns_structured_feedback(self):
        result = rate_opening_statement("AI should be regulated because it reduces harm.", "Should AI be regulated?", "For")

        self.assertEqual(result["source"], "user")
        self.assertGreaterEqual(result["score"], 0)
        self.assertIsInstance(result["feedback"], dict)
        self.assertIn("feedback", result["feedback"])
        self.assertGreaterEqual(result["feedback"]["score"], 0)


if __name__ == "__main__":
    unittest.main()
