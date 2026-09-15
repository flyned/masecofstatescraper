#!/usr/bin/env python3
"""
Command Line Interface (CLI) for Secretary of State LLC Owner Resolver & Analyzer.
"""

import argparse
import sys
import json
from scraper.ma_sos_scraper import MASOSScraper
from scraper.csv_exporter import export_entities_to_csv, export_detailed_officer_changes_csv

def main():
    parser = argparse.ArgumentParser(
        description="Automated LLC Owner Resolver & Secretary of State Scraper"
    )
    parser.add_argument(
        "-q", "--query",
        type=str,
        required=True,
        help="Search term (entity name or individual name)"
    )
    parser.add_argument(
        "--by",
        choices=["entity_name", "individual_name"],
        default="entity_name",
        help="Search category: entity_name or individual_name (default: entity_name)"
    )
    parser.add_argument(
        "--type",
        choices=["begins_with", "exact_match", "full_text", "soundex"],
        default="begins_with",
        help="Search match mode: begins_with, exact_match, full_text, soundex (default: begins_with)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output CSV file path to save entity details"
    )
    parser.add_argument(
        "--changes-csv",
        type=str,
        help="Output CSV file path to save detailed officer change logs"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON formatted string to stdout"
    )

    args = parser.parse_args()

    scraper = MASOSScraper()
    print(f"[*] Searching for '{args.query}' (By: {args.by}, Type: {args.type})...")
    results = scraper.search(args.query, search_by=args.by, search_type=args.type)

    if not results:
        print("[!] No matching LLC entities found.")
        sys.exit(0)

    print(f"[+] Found {len(results)} matching entity/entities:\n")

    detailed_entities = []
    for item in results:
        entity_id = item["entity_id"]
        details = scraper.get_entity_details(entity_id)
        detailed_entities.append(details)

        print(f"==================================================")
        print(f"Entity ID        : {details.get('entity_id')}")
        print(f"Entity Name      : {details.get('entity_name')}")
        print(f"Status           : {details.get('status')}")
        print(f"Organization Date: {details.get('organization_date')}")
        print(f"Principal Address: {details.get('principal_address')}")
        print(f"Resident Agent   : {details.get('resident_agent_name')}")

        print("\nManagers / Officers / Owners:")
        for off in details.get("officers", []):
            print(f"  - [{off.get('title')}] {off.get('name')} ({off.get('address')})")

        print("\nFinancial Insights (Annual Reports):")
        fin = details.get("financial_insights", {})
        print(f"  - Assets: {fin.get('total_assets', 'N/A')}")
        print(f"  - Capital Stock: {fin.get('capital_stock', 'N/A')}")
        print(f"  - Gross Revenue: {fin.get('gross_revenue', 'N/A')}")
        print(f"  - Financial Health: {fin.get('financial_health_status', 'N/A')}")

        print("\nOfficer / Manager Changes Log:")
        for chg in details.get("officer_changes", []):
            print(f"  - [{chg.get('date')}] {chg.get('type')}: {chg.get('officer_name')} ({chg.get('role')})")

        print("==================================================\n")

    if args.json:
        print(json.dumps(detailed_entities, indent=2))

    if args.output:
        export_entities_to_csv(detailed_entities, args.output)
        print(f"[+] Exported entity search summary to CSV file: {args.output}")

    if args.changes_csv:
        export_detailed_officer_changes_csv(detailed_entities, args.changes_csv)
        print(f"[+] Exported officer change history to CSV file: {args.changes_csv}")

if __name__ == "__main__":
    main()
