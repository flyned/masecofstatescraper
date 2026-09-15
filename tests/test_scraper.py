import unittest
from scraper.soundex import soundex, soundex_match
from scraper.parser import parse_search_results, parse_entity_summary, extract_officer_changes
from scraper.ma_sos_scraper import MASOSScraper
from scraper.csv_exporter import export_entities_to_csv, export_detailed_officer_changes_csv

class TestSoundex(unittest.TestCase):
    def test_soundex_encoding(self):
        self.assertEqual(soundex("Smith"), "S530")
        self.assertEqual(soundex("Smyth"), "S530")
        self.assertEqual(soundex(""), "0000")

    def test_soundex_matching(self):
        self.assertTrue(soundex_match("Smith", "Smyth"))
        self.assertFalse(soundex_match("Smith", "Johnson"))

class TestParser(unittest.TestCase):
    def test_parse_search_results(self):
        sample_html = """
        <html><body>
        <table class="grid">
            <tr><th>ID</th><th>Entity Name</th><th>Address</th><th>Type</th><th>Status</th></tr>
            <tr>
                <td>001234567</td>
                <td><a href="/CorpSummary.aspx?sys_id=001234567">BAY STATE VENTURES LLC</a></td>
                <td>100 Federal St, Boston, MA</td>
                <td>LLC</td>
                <td>Active</td>
            </tr>
        </table>
        </body></html>
        """
        results = parse_search_results(sample_html)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["entity_id"], "001234567")
        self.assertEqual(results[0]["entity_name"], "BAY STATE VENTURES LLC")

    def test_extract_officer_changes(self):
        filings = [
            {
                "filing_date": "2020-01-01",
                "document_name": "Org Cert",
                "officers": [{"title": "Manager", "name": "Alice"}]
            },
            {
                "filing_date": "2021-01-01",
                "document_name": "Annual Report 2021",
                "officers": [{"title": "Manager", "name": "Alice"}, {"title": "Manager", "name": "Bob"}]
            }
        ]
        changes = extract_officer_changes(filings)
        self.assertEqual(len(changes), 2)
        self.assertEqual(changes[1]["officer_name"], "Bob")
        self.assertEqual(changes[1]["type"], "ADDED")

class TestMASOSScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = MASOSScraper()

    def test_search_modes(self):
        # Begins with search
        r1 = self.scraper.search("Bay State", search_by="entity_name", search_type="begins_with")
        self.assertTrue(len(r1) >= 1)

        # Exact match search
        r2 = self.scraper.search("BAY STATE VENTURES LLC", search_by="entity_name", search_type="exact_match")
        self.assertEqual(len(r2), 1)

        # Full text search
        r3 = self.scraper.search("VENTURES", search_by="entity_name", search_type="full_text")
        self.assertTrue(len(r3) >= 1)

        # Soundex search
        r4 = self.scraper.search("Smyth", search_by="individual_name", search_type="soundex")
        self.assertTrue(len(r4) >= 1)

    def test_get_entity_details(self):
        details = self.scraper.get_entity_details("001234567")
        self.assertEqual(details["entity_name"], "BAY STATE VENTURES LLC")
        self.assertTrue(len(details["officers"]) > 0)
        self.assertIn("financial_insights", details)
        self.assertTrue(len(details["officer_changes"]) > 0)

class TestCSVExporter(unittest.TestCase):
    def test_export_entities_to_csv(self):
        sample_entities = [{
            "entity_id": "123",
            "entity_name": "TEST LLC",
            "entity_type": "LLC",
            "status": "Active",
            "organization_date": "2021-01-01",
            "principal_address": "123 Main St",
            "resident_agent_name": "Agent Smith",
            "resident_agent_address": "123 Main St",
            "officers": [{"title": "Manager", "name": "John", "address": "123 Main St"}],
            "annual_reports": [],
            "financial_insights": {"total_assets": "$100", "capital_stock": "$50", "gross_revenue": "$200"},
            "officer_changes": [],
            "filings": []
        }]
        csv_str = export_entities_to_csv(sample_entities)
        self.assertIn("TEST LLC", csv_str)
        self.assertIn("Agent Smith", csv_str)
        self.assertIn("Manager: John", csv_str)

if __name__ == "__main__":
    unittest.main()
