import unittest
from app import app

class TestAppRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_index_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"MA Secretary of State LLC Owner Resolver", response.data)

    def test_search_page(self):
        response = self.client.get("/?query=Bay+State&search_by=entity_name&search_type=begins_with")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"BAY STATE VENTURES LLC", response.data)

    def test_entity_detail_page(self):
        response = self.client.get("/entity/001234567")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"BAY STATE VENTURES LLC", response.data)
        self.assertIn(b"JOHN SMITH", response.data)
        self.assertIn(b"SARAH JENKINS", response.data)

    def test_csv_export(self):
        response = self.client.get("/export/csv?query=Bay+State&search_by=entity_name&search_type=begins_with")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/csv")
        self.assertIn(b"BAY STATE VENTURES LLC", response.data)

    def test_officer_changes_csv_export(self):
        response = self.client.get("/export/officer_changes/csv?query=Bay+State&search_by=entity_name&search_type=begins_with")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/csv")
        self.assertIn(b"JOHN SMITH", response.data)

if __name__ == "__main__":
    unittest.main()
