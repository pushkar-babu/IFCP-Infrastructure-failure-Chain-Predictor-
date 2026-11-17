"""
Infrastructure Failure Chain Predictor (IFCP) - Main Application Server
Flask REST API & Web Command Center for Urban Resilience Digital Twin.
Supports Multi-City Simulation: Mumbai, Bengaluru, Delhi.
"""

import os
import json
from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_cors import CORS

from engine.topology import get_urban_topology, get_available_cities
from engine.cascade_model import CascadeSimulator
from engine.intervention import evaluate_interventions, AVAILABLE_INTERVENTIONS
from engine.xai_engine import XAIEngine
from engine.report_generator import generate_pdf_report

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

@app.route("/")
def index():
    """Renders the primary Digital Twin Command Center dashboard."""
    cities = get_available_cities()
    initial_city = cities[0]["id"]
    topology = get_urban_topology(initial_city)
    return render_template(
        "index.html",
        cities=cities,
        current_city=initial_city,
        total_nodes=topology["metadata"]["total_nodes"],
        total_edges=topology["metadata"]["total_edges"],
        city_name=topology["metadata"]["city"]
    )

@app.route("/api/cities", methods=["GET"])
def api_cities():
    """Returns list of all available city resilience basins."""
    return jsonify(get_available_cities())

@app.route("/api/topology", methods=["GET"])
def api_topology():
    """Returns the multi-layer infrastructure graph for the requested city."""
    city_id = request.args.get("city", "mumbai")
    return jsonify(get_urban_topology(city_id))

@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    """Runs a 60-minute spatio-temporal cascade simulation for the given city."""
    data = request.get_json() or {}
    
    city_id = data.get("city", "mumbai")
    rainfall = float(data.get("rainfall_mm_hr", 85.0))
    grid_load = float(data.get("grid_load_pct", 100.0))
    siltation = float(data.get("drainage_siltation_pct", 35.0))
    high_tide = float(data.get("high_tide_m", 3.4))
    interventions = data.get("interventions", [])

    sim = CascadeSimulator(city_id=city_id)
    results = sim.run_simulation(
        rainfall_mm_hr=rainfall,
        grid_load_pct=grid_load,
        drainage_siltation_pct=siltation,
        high_tide_m=high_tide,
        interventions=interventions
    )
    return jsonify(results)

@app.route("/api/interventions/compare", methods=["POST"])
def api_compare_interventions():
    """Compares baseline vs individual interventions and active portfolio."""
    data = request.get_json() or {}
    
    city_id = data.get("city", "mumbai")
    rainfall = float(data.get("rainfall_mm_hr", 85.0))
    grid_load = float(data.get("grid_load_pct", 100.0))
    siltation = float(data.get("drainage_siltation_pct", 35.0))
    high_tide = float(data.get("high_tide_m", 3.4))
    selected_actions = data.get("selected_actions", [])

    comparison = evaluate_interventions(
        rainfall_mm_hr=rainfall,
        grid_load_pct=grid_load,
        drainage_siltation_pct=siltation,
        high_tide_m=high_tide,
        selected_actions=selected_actions,
        city_id=city_id
    )
    return jsonify(comparison)

@app.route("/api/explain/<node_id>", methods=["POST"])
def api_explain_node(node_id):
    """Provides XAI causal attribution and feature breakdown for a specific node."""
    sim_state = request.get_json()
    city_id = "mumbai"
    if sim_state and "parameters" in sim_state:
        city_id = sim_state["parameters"].get("city", "mumbai")
        
    xai = XAIEngine(city_id=city_id)
    if not sim_state or "timeline" not in sim_state:
        sim = CascadeSimulator(city_id=city_id)
        sim_state = sim.run_simulation()
        
    explanation = xai.explain_node_failure(node_id, sim_state)
    return jsonify(explanation)

@app.route("/api/report/pdf", methods=["POST"])
def api_generate_pdf():
    """Generates and streams an official Situation Report (SITREP) in PDF format."""
    data = request.get_json() or {}
    sim_data = data.get("simulation")
    city_id = data.get("city", "mumbai")
    
    if not sim_data:
        sim = CascadeSimulator(city_id=city_id)
        sim_data = sim.run_simulation()
        
    interventions = evaluate_interventions(
        rainfall_mm_hr=sim_data["parameters"]["rainfall_mm_hr"],
        selected_actions=sim_data["parameters"].get("interventions", []),
        city_id=city_id
    )
    
    pdf_bytes = generate_pdf_report(sim_data, interventions)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment;filename=IFCP_{city_id.upper()}_SITREP.pdf"}
    )

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "IFCP Resilience Engine",
        "supported_cities": [c["id"] for c in get_available_cities()],
        "version": "2.4.0"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 IFCP Resilience Digital Twin starting at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
