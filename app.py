"""
Flask Web Application for Secretary of State LLC Owner Resolver & Analyzer.
"""

from flask import Flask, render_template, request, Response, jsonify
from scraper.ma_sos_scraper import MASOSScraper
from scraper.csv_exporter import export_entities_to_csv, export_detailed_officer_changes_csv

app = Flask(__name__)
scraper = MASOSScraper()

@app.route("/")
def index():
    query = request.args.get("query", "").strip()
    search_by = request.args.get("search_by", "entity_name")
    search_type = request.args.get("search_type", "begins_with")

    results = []
    if query:
        results = scraper.search(query, search_by=search_by, search_type=search_type)

    return render_template(
        "index.html",
        query=query,
        search_by=search_by,
        search_type=search_type,
        results=results
    )

@app.route("/entity/<entity_id>")
def entity_detail(entity_id):
    entity = scraper.get_entity_details(entity_id)
    return render_template("entity.html", entity=entity)

@app.route("/export/csv")
def export_csv():
    query = request.args.get("query", "").strip()
    search_by = request.args.get("search_by", "entity_name")
    search_type = request.args.get("search_type", "begins_with")

    results = scraper.search(query, search_by=search_by, search_type=search_type)
    detailed_entities = [scraper.get_entity_details(r["entity_id"]) for r in results]

    csv_data = export_entities_to_csv(detailed_entities)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=llc_search_export.csv"}
    )

@app.route("/export/officer_changes/csv")
def export_officer_changes_csv():
    query = request.args.get("query", "").strip()
    search_by = request.args.get("search_by", "entity_name")
    search_type = request.args.get("search_type", "begins_with")

    results = scraper.search(query, search_by=search_by, search_type=search_type)
    detailed_entities = [scraper.get_entity_details(r["entity_id"]) for r in results]

    csv_data = export_detailed_officer_changes_csv(detailed_entities)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=officer_changes_export.csv"}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
