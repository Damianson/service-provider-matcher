import unittest
import json
import os
import sys

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, get_all_providers, get_providers_by_category, DB_PATH
from seed import seed, PROVIDERS
from matcher import apply_hard_filters, match_and_rank_providers
from app import app

class TestServiceProviderMatcher(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure clean seeded database
        seed()

    def test_01_seed_count_and_categories(self):
        providers = get_all_providers()
        self.assertGreaterEqual(len(providers), 15, "Expected at least 15 seeded providers")
        self.assertEqual(len(providers), 20, "Expected exactly 20 seeded providers")

        categories = {p["category"] for p in providers}
        expected_categories = {"plumber", "electrician", "cleaner", "tutor"}
        self.assertTrue(expected_categories.issubset(categories), f"Missing categories: {expected_categories - categories}")

        for cat in expected_categories:
            cat_providers = get_providers_by_category(cat)
            self.assertGreaterEqual(len(cat_providers), 4, f"Category {cat} should have at least 4 providers")

    def test_02_hard_filter_category(self):
        all_p = get_all_providers()
        passed, rejected = apply_hard_filters(all_p, category="plumber")
        self.assertEqual(len(passed), 5)
        for p in passed:
            self.assertEqual(p["category"], "plumber")
        self.assertEqual(len(rejected), 15)

    def test_03_hard_filter_budget(self):
        all_p = get_all_providers()
        # Plumbers: 45, 55, 65, 80, 95
        # Max budget 60 should allow 45 and 55 (2 providers)
        passed, rejected = apply_hard_filters(all_p, category="plumber", max_budget=60.0)
        self.assertEqual(len(passed), 2)
        for p in passed:
            self.assertLessEqual(p["hourly_rate"], 60.0)

    def test_04_hard_filter_availability(self):
        all_p = get_all_providers()
        # Filter cleaners by emergency/urgent
        passed, rejected = apply_hard_filters(all_p, category="cleaner", availability_needed="emergency")
        # Viktor Hansen has 'emergency,weekends'
        self.assertGreaterEqual(len(passed), 1)
        for p in passed:
            self.assertTrue("emergency" in p["availability"].lower())

    def test_05_match_and_rank_pipeline(self):
        all_p = get_all_providers()
        client_req = {
            "category": "plumber",
            "max_budget": 100,
            "availability": "emergency",
            "description": "Pipe leaking heavily under the kitchen sink, need immediate help."
        }
        result = match_and_rank_providers(all_p, client_req)
        self.assertEqual(result["status"], "success")
        self.assertIn("pipeline", result)
        self.assertIn("ranked_matches", result)
        self.assertGreater(len(result["ranked_matches"]), 0)

        # Check top match has ranking and reasoning
        top_match = result["ranked_matches"][0]
        self.assertEqual(top_match["rank"], 1)
        self.assertIn("reasoning", top_match)
        self.assertTrue(len(top_match["reasoning"]) > 10, "Reasoning should be a descriptive sentence")
        self.assertIn("match_score", top_match)
        self.assertIn("provider", top_match)

    def test_06_flask_health_and_config(self):
        client = app.test_client()
        res_health = client.get("/api/health")
        self.assertEqual(res_health.status_code, 200)
        data = res_health.get_json()
        self.assertEqual(data["status"], "healthy")

        res_config = client.get("/api/config")
        self.assertEqual(res_config.status_code, 200)
        cfg = res_config.get_json()
        self.assertIn("categories", cfg)
        self.assertIn("has_gemini", cfg)
        self.assertIn("engine_name", cfg)

    def test_07_flask_match_endpoint(self):
        client = app.test_client()
        payload = {
            "category": "electrician",
            "max_budget": 95,
            "availability": "weekends",
            "description": "Level 2 Tesla EV charger installation in garage."
        }
        res = client.post("/api/match", data=json.dumps(payload), content_type="application/json")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertGreater(len(data["ranked_matches"]), 0)

        # Leo Zhang is $90/hr and EV specialist -> should be high rank
        top = data["ranked_matches"][0]
        self.assertIn("reasoning", top)
        print(f"\n[Test Output] Top Matched Electrician: {top['provider']['name']} - Reasoning: {top['reasoning']}")

if __name__ == "__main__":
    unittest.main()

