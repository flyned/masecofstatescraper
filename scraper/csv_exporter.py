"""
CSV Exporter for exporting resolved LLC details, officers, filing histories, officer change timelines, and financial insights.
"""

import csv
import io
from typing import List, Dict, Any

def export_entities_to_csv(entities: List[Dict[str, Any]], filepath: str = None) -> str:
    """
    Exports a list of resolved LLC entities and their complete metadata into CSV format.
    If filepath is provided, writes to file. Returns CSV string.
    """
    output = io.StringIO()
    fieldnames = [
        "Entity ID",
        "Entity Name",
        "Entity Type",
        "Status",
        "Date of Organization / Registration",
        "Principal Office Address",
        "Resident Agent Name",
        "Resident Agent Address",
        "Managers / Officers",
        "Annual Reports Summary",
        "Recent Officer Changes",
        "Latest Financial Metrics",
        "Filing Count"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for item in entities:
        # Format officers list
        officers = item.get("officers", [])
        officers_str = " | ".join([f"{o.get('title', 'Officer')}: {o.get('name', '')} ({o.get('address', '')})" for o in officers])

        # Format annual reports summary
        annual_reports = item.get("annual_reports", [])
        ar_str = " | ".join([f"Year {ar.get('year')}: Filing Date {ar.get('filing_date', 'N/A')}, Assets: {ar.get('total_assets', 'N/A')}" for ar in annual_reports])

        # Format officer changes
        officer_changes = item.get("officer_changes", [])
        changes_str = " | ".join([f"[{c.get('date', 'N/A')}] {c.get('type', 'CHANGE')}: {c.get('officer_name', '')} ({c.get('role', '')})" for c in officer_changes])

        # Format financial insights
        financial_insights = item.get("financial_insights", {})
        fin_str = f"Assets: {financial_insights.get('total_assets', 'N/A')}, Capital: {financial_insights.get('capital_stock', 'N/A')}, Revenue/Gross: {financial_insights.get('gross_revenue', 'N/A')}"

        filings = item.get("filings", [])

        writer.writerow({
            "Entity ID": item.get("entity_id", ""),
            "Entity Name": item.get("entity_name", ""),
            "Entity Type": item.get("entity_type", "Limited Liability Company"),
            "Status": item.get("status", "Active"),
            "Date of Organization / Registration": item.get("organization_date", ""),
            "Principal Office Address": item.get("principal_address", ""),
            "Resident Agent Name": item.get("resident_agent_name", ""),
            "Resident Agent Address": item.get("resident_agent_address", ""),
            "Managers / Officers": officers_str,
            "Annual Reports Summary": ar_str,
            "Recent Officer Changes": changes_str,
            "Latest Financial Metrics": fin_str,
            "Filing Count": len(filings)
        })

    csv_text = output.getvalue()
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(csv_text)

    return csv_text


def export_detailed_officer_changes_csv(entities: List[Dict[str, Any]], filepath: str = None) -> str:
    """
    Exports detailed officer additions, removals, and title changes per entity to CSV.
    """
    output = io.StringIO()
    fieldnames = [
        "Entity ID",
        "Entity Name",
        "Change Date",
        "Change Type",
        "Officer Name",
        "Role / Title",
        "Source Filing Document"
    ]

    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for item in entities:
        entity_id = item.get("entity_id", "")
        entity_name = item.get("entity_name", "")
        officer_changes = item.get("officer_changes", [])

        for change in officer_changes:
            writer.writerow({
                "Entity ID": entity_id,
                "Entity Name": entity_name,
                "Change Date": change.get("date", "N/A"),
                "Change Type": change.get("type", "MODIFIED"),
                "Officer Name": change.get("officer_name", ""),
                "Role / Title": change.get("role", ""),
                "Source Filing Document": change.get("document_name", "Annual Report / Amendment")
            })

    csv_text = output.getvalue()
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(csv_text)

    return csv_text
