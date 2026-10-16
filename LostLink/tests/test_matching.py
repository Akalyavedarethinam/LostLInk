import unittest
from services.matching import calculate_match_score

class TestMatching(unittest.TestCase):
    def test_exact_match(self):
        lost = {"item_name": "Black Wallet", "category": "Wallet", "location": "Library", "date": "2026-10-01", "description": "Black leather wallet"}
        found = {"item_name": "Black Wallet", "category": "Wallet", "location": "Library", "date": "2026-10-01", "description": "Black leather wallet"}
        result = calculate_match_score(lost, found)
        self.assertEqual(result['score'], 100.0)

    def test_partial_match(self):
        lost = {"item_name": "Black Wallet", "category": "Wallet", "location": "Library", "date": "2026-10-01", "description": "Black leather wallet with college ID"}
        found = {"item_name": "Black Leather Wallet", "category": "Wallet", "location": "College Library", "date": "2026-10-02", "description": "Black wallet containing ID"}
        result = calculate_match_score(lost, found)
        self.assertTrue(result['score'] > 75.0)

    def test_different_category(self):
        lost = {"item_name": "Keys", "category": "Keys"}
        found = {"item_name": "Keys", "category": "Accessories"}
        result = calculate_match_score(lost, found)
        self.assertEqual(result['breakdown']['category'], 0.0)

if __name__ == '__main__':
    unittest.main()
