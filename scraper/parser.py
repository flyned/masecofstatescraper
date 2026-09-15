"""
HTML Parser module for MA Secretary of State web scraping.
Extracts search results, entity profile summary, officers/managers, filing history, annual reports, and financial insights.
"""

import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup

def parse_search_results(html_content: str) -> List[Dict[str, str]]:
    """
    Parses search results table from MA Secretary of State HTML page.
    Returns list of dicts with entity_id, entity_name, entity_type, address, status, detail_url.
    """
    results = []
    if not html_content:
        return results

    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", id=re.compile(r".*MainContent.*Search.*", re.I)) or soup.find("table", class_=re.compile(r".*grid.*|.*table.*", re.I))

    if not table:
        tables = soup.find_all("table")
        for tbl in tables:
            if tbl.find("a", href=re.compile(r"CorpSearchSummary|CorpSummary", re.I)):
                table = tbl
                break

    if not table:
        return results

    rows = table.find_all("tr")
    header_found = False

    for row in rows:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue

        cell_texts = [c.get_text(strip=True) for c in cells]
        if any("entity" in txt.lower() or "id" in txt.lower() or "name" in txt.lower() for txt in cell_texts):
            if not header_found and row.find("th"):
                header_found = True
                continue

        link = row.find("a", href=True)
        if link:
            href = link["href"]
            entity_name = link.get_text(strip=True)

            id_match = re.search(r"sys_id=(\d+)", href, re.I) or re.search(r"id=(\d+)", href, re.I) or re.search(r"IDNum=(\d+)", href, re.I)
            entity_id = id_match.group(1) if id_match else (cell_texts[0] if len(cell_texts) > 1 and cell_texts[0].isdigit() else "")

            address = cell_texts[2] if len(cell_texts) > 2 else ""
            entity_type = cell_texts[3] if len(cell_texts) > 3 else "LLC"
            status = cell_texts[-1] if len(cell_texts) > 1 else "Active"

            results.append({
                "entity_id": entity_id,
                "entity_name": entity_name,
                "entity_type": entity_type,
                "address": address,
                "status": status,
                "detail_url": href
            })

    return results


def parse_entity_summary(html_content: str) -> Dict[str, Any]:
    """
    Parses an entity summary page to extract main details, officers, and filing links.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    data = {
        "entity_id": "",
        "entity_name": "",
        "entity_type": "Limited Liability Company (LLC)",
        "status": "Active",
        "organization_date": "",
        "principal_address": "",
        "resident_agent_name": "",
        "resident_agent_address": "",
        "officers": [],
        "filings": [],
        "annual_reports": [],
        "financial_insights": {
            "total_assets": "N/A",
            "capital_stock": "N/A",
            "gross_revenue": "N/A",
            "asset_growth_rate": "N/A",
            "financial_health_status": "Active Filings Recorded"
        },
        "officer_changes": []
    }

    for span_id, key in [
        ("MainContent_lblEntityName", "entity_name"),
        ("MainContent_lblIDNum", "entity_id"),
        ("MainContent_lblOrgDate", "organization_date"),
        ("MainContent_lblStatus", "status"),
        ("MainContent_lblEntityType", "entity_type")
    ]:
        element = soup.find(id=re.compile(f".*{span_id}.*", re.I))
        if element:
            data[key] = element.get_text(strip=True)

    text_content = soup.get_text()
    if not data["entity_name"]:
        m = re.search(r"Summary for:\s*([^\n\r]+)", text_content, re.I) or re.search(r"Entity Name:\s*([^\n\r]+)", text_content, re.I)
        if m: data["entity_name"] = m.group(1).strip()

    if not data["entity_id"]:
        m = re.search(r"ID Number:\s*(\d+)", text_content, re.I) or re.search(r"Identification Number:\s*(\d+)", text_content, re.I)
        if m: data["entity_id"] = m.group(1).strip()

    if not data["organization_date"]:
        m = re.search(r"Date of Organization[^:]*:\s*([\d\-\/]+)", text_content, re.I)
        if m: data["organization_date"] = m.group(1).strip()

    # Parse Officers / Managers Table
    officers = []
    tables = soup.find_all("table")
    for tbl in tables:
        tbl_text = tbl.get_text().lower()
        if "title" in tbl_text and ("individual name" in tbl_text or "name" in tbl_text or "address" in tbl_text):
            rows = tbl.find_all("tr")
            for r in rows[1:]:
                cols = [c.get_text(strip=True) for c in r.find_all(["td", "th"])]
                if len(cols) >= 2:
                    title = cols[0]
                    name = cols[1]
                    addr = cols[2] if len(cols) > 2 else ""
                    if name and title.lower() != "title":
                        officers.append({
                            "title": title,
                            "name": name,
                            "address": addr
                        })

    data["officers"] = officers

    # Parse Filings using parse_filing_history
    filings = parse_filing_history(html_content)
    data["filings"] = filings

    # Financial insights extraction from HTML tables if present
    assets_m = re.search(r"Total Assets:?\s*\$?([\d,]+)", text_content, re.I)
    if assets_m:
        data["financial_insights"]["total_assets"] = f"${assets_m.group(1)}"

    capital_m = re.search(r"Capital Stock:?\s*\$?([\d,]+)", text_content, re.I)
    if capital_m:
        data["financial_insights"]["capital_stock"] = f"${capital_m.group(1)}"

    revenue_m = re.search(r"Gross Revenue:?\s*\$?([\d,]+)", text_content, re.I)
    if revenue_m:
        data["financial_insights"]["gross_revenue"] = f"${revenue_m.group(1)}"

    return data


def parse_filing_history(html_content: str) -> List[Dict[str, Any]]:
    """
    Parses filing history page or table to extract document filings and annual reports.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    filings = []

    for tbl in soup.find_all("table"):
        tbl_text = tbl.get_text().lower()
        if "filing" in tbl_text or "document" in tbl_text or "annual report" in tbl_text or "view filings" in tbl_text:
            rows = tbl.find_all("tr")
            for r in rows:
                cols = [c.get_text(strip=True) for c in r.find_all(["td", "th"])]
                if len(cols) >= 2:
                    doc_name = cols[0]
                    filing_date = cols[1] if len(cols) > 1 else ""
                    doc_id = cols[2] if len(cols) > 2 else ""
                    link = r.find("a", href=True)
                    url = link["href"] if link else ""

                    if doc_name and doc_name.lower() != "document type":
                        filings.append({
                            "document_name": doc_name,
                            "filing_date": filing_date,
                            "document_id": doc_id,
                            "url": url
                        })

    # Also parse option tags inside filing selects if available
    select_tag = soup.find("select", id=re.compile(r".*filing.*|.*document.*", re.I)) or soup.find("select")
    if select_tag:
        for opt in select_tag.find_all("option"):
            opt_text = opt.get_text(strip=True)
            if opt_text and opt_text.lower() != "select":
                filings.append({
                    "document_name": opt_text,
                    "filing_date": "N/A",
                    "document_id": opt.get("value", "DOC-OPT"),
                    "url": ""
                })

    return filings


def extract_officer_changes(annual_reports_or_filings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyzes historical filings and annual reports to track changes in LLC managers and officers over time.
    """
    changes = []
    sorted_filings = sorted(
        annual_reports_or_filings,
        key=lambda x: x.get("filing_date", ""),
        reverse=False
    )

    seen_officers = set()
    for filing in sorted_filings:
        filing_date = filing.get("filing_date", "N/A")
        doc_name = filing.get("document_name", "Annual Report")
        officers_in_filing = filing.get("officers", [])

        for off in officers_in_filing:
            name = off.get("name")
            role = off.get("title", "Manager")
            if not name:
                continue

            if name not in seen_officers:
                changes.append({
                    "date": filing_date,
                    "type": "ADDED",
                    "officer_name": name,
                    "role": role,
                    "document_name": doc_name
                })
                seen_officers.add(name)

    return changes
