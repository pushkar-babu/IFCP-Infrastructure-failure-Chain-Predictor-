"""
Infrastructure Failure Chain Predictor (IFCP) - Main Application Server
Flask REST API & Web Command Center for Urban Resilience Digital Twin.
Enhanced with Enterprise Security Headers, Robust Input Sanitization, and Response Caching.
"""

import os
import re
import math
import logging
from typing import Dict, Any, List, Optional
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS

from engine.topology import get_urban_topology, get_available_cities, VALID_CITIES
from engine.cascade_model import CascadeSimulator
from engine.intervention import evaluate_interventions, AVAILABLE_INTERVENTIONS
from engine.xai_engine import XAIEngine
from engine.report_generator import generate_pdf_report

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("IFCP-App")

app = Flask(__name__, template_folder="templates", static_folder="static")

# Security: Limit maximum request payload size to 2MB to prevent DOS
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

# CORS: Configured securely for API endpoints
CORS(app, resources={r"/api/*": {"origins": "*"}}, methods=["GET", "POST", "OPTIONS"])

# Performance Optimization: Pre-warm and cache simulator and XAI engines per city
_SIMULATORS: Dict[str, CascadeSimulator] = {}
_XAI_ENGINES: Dict[str, XAIEngine] = {}

def get_cached_simulator(city_id: str) -> CascadeSimulator:
    city = sanitize_city(city_id)
    if city not in _SIMULATORS:
        _SIMULATORS[city] = CascadeSimulator(city_id=city)
    return _SIMULATORS[city]

def get_cached_xai(city_id: str) -> XAIEngine:
    city = sanitize_city(city_id)
    if city not in _XAI_ENGINES:
        _XAI_ENGINES[city] = XAIEngine(city_id=city)
    return _XAI_ENGINES[city]

# Security Sanitization Utilities
ALLOWED_CITIES = {"mumbai", "bengaluru", "bangalore", "delhi"}
ALLOWED_ACTIONS = {action["id"] for action in AVAILABLE_INTERVENTIONS}
NODE_ID_REGEX = re.compile(r"^[A-Za-z0-9_]{1,64}$")

def sanitize_city(raw_city: Any) -> str:
    """Sanitizes city ID against directory traversal and unknown values."""
    if not isinstance(raw_city, str):
        return "mumbai"
    clean = raw_city.lower().strip()
    if clean in ("bengaluru", "bangalore"):
        return "bengaluru"
    elif clean == "delhi":
        return "delhi"
    return "mumbai"

def sanitize_float(val: Any, default: float, min_val: float, max_val: float) -> float:
    """Validates and bounds numeric float inputs against NaN, Inf, and overflow."""
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return max(min_val, min(max_val, f))
    except (ValueError, TypeError):
        return default

def sanitize_interventions(raw_actions: Any) -> List[str]:
    """Ensures intervention actions match strict allowed identifiers."""
    if not isinstance(raw_actions, list):
        return []
    return [str(a) for a in raw_actions if isinstance(a, str) and a in ALLOWED_ACTIONS]

def sanitize_node_id(raw_node: Any) -> Optional[str]:
    """Validates asset node identifier against injection patterns."""
    if not isinstance(raw_node, str):
        return None
    clean = raw_node.strip()
    if NODE_ID_REGEX.match(clean):
        return clean
    return None

# Security Middleware: Inject Security Headers into every response
@app.after_request
def apply_security_headers(response: Response) -> Response:
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://unpkg.com; "
        "img-src 'self' data: https://*.basemaps.cartocdn.com https://unpkg.com; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "frame-ancestors 'none';"
    )
    if request.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=86400"
    else:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# Standardized Error Handlers (Prevents stack trace leakage)
@app.errorhandler(400)
def bad_request_handler(e):
    return jsonify({"error": "Bad Request", "message": "Invalid parameter input", "status_code": 400}), 400

@app.errorhandler(404)
def not_found_handler(e):
    return jsonify({"error": "Not Found", "message": "Requested resource not found", "status_code": 404}), 404

@app.errorhandler(405)
def method_not_allowed_handler(e):
    return jsonify({"error": "Method Not Allowed", "status_code": 405}), 405

@app.errorhandler(500)
def server_error_handler(e):
    logger.error("Internal Server Error: %s", str(e))
    return jsonify({"error": "Internal Server Error", "message": "Resilience engine encountered an internal condition", "status_code": 500}), 500

# Web Dashboard Route
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

# REST API Endpoints
@app.route("/api/cities", methods=["GET"])
def api_cities():
    """Returns list of all available city resilience basins."""
    return jsonify(get_available_cities())

@app.route("/api/topology", methods=["GET"])
def api_topology():
    """Returns the multi-layer infrastructure graph for the requested city."""
    city_id = sanitize_city(request.args.get("city", "mumbai"))
    return jsonify(get_urban_topology(city_id))

@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    """Runs a 60-minute spatio-temporal cascade simulation for the given city."""
    data = request.get_json(silent=True) or {}
    
    city_id = sanitize_city(data.get("city", "mumbai"))
    rainfall = sanitize_float(data.get("rainfall_mm_hr"), default=85.0, min_val=0.0, max_val=500.0)
    grid_load = sanitize_float(data.get("grid_load_pct"), default=100.0, min_val=10.0, max_val=300.0)
    siltation = sanitize_float(data.get("drainage_siltation_pct"), default=35.0, min_val=0.0, max_val=100.0)
    high_tide = sanitize_float(data.get("high_tide_m"), default=3.4, min_val=0.0, max_val=15.0)
    interventions = sanitize_interventions(data.get("interventions"))

    sim = get_cached_simulator(city_id)
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
    data = request.get_json(silent=True) or {}
    
    city_id = sanitize_city(data.get("city", "mumbai"))
    rainfall = sanitize_float(data.get("rainfall_mm_hr"), default=85.0, min_val=0.0, max_val=500.0)
    grid_load = sanitize_float(data.get("grid_load_pct"), default=100.0, min_val=10.0, max_val=300.0)
    siltation = sanitize_float(data.get("drainage_siltation_pct"), default=35.0, min_val=0.0, max_val=100.0)
    high_tide = sanitize_float(data.get("high_tide_m"), default=3.4, min_val=0.0, max_val=15.0)
    selected_actions = sanitize_interventions(data.get("selected_actions"))

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
def api_explain_node(node_id: str):
    """Provides XAI causal attribution and feature breakdown for a specific node."""
    clean_node = sanitize_node_id(node_id)
    if not clean_node:
        return jsonify({"error": "Invalid node identifier", "status_code": 400}), 400

    sim_state = request.get_json(silent=True) or {}
    city_id = "mumbai"
    if "parameters" in sim_state and isinstance(sim_state["parameters"], dict):
        city_id = sanitize_city(sim_state["parameters"].get("city", "mumbai"))

    xai = get_cached_xai(city_id)
    if "timeline" not in sim_state or not isinstance(sim_state["timeline"], list):
        sim = get_cached_simulator(city_id)
        sim_state = sim.run_simulation()

    explanation = xai.explain_node_failure(clean_node, sim_state)
    if "error" in explanation:
        return jsonify(explanation), 404
    return jsonify(explanation)

@app.route("/api/report/pdf", methods=["POST"])
def api_generate_pdf():
    """Generates and streams an official Situation Report (SITREP) in PDF format."""
    data = request.get_json(silent=True) or {}
    sim_data = data.get("simulation")
    city_id = sanitize_city(data.get("city", "mumbai"))

    if not sim_data or not isinstance(sim_data, dict) or "parameters" not in sim_data:
        sim = get_cached_simulator(city_id)
        sim_data = sim.run_simulation()

    rain_val = sanitize_float(sim_data.get("parameters", {}).get("rainfall_mm_hr"), default=85.0, min_val=0.0, max_val=500.0)
    active_actions = sanitize_interventions(sim_data.get("parameters", {}).get("interventions"))

    interventions = evaluate_interventions(
        rainfall_mm_hr=rain_val,
        selected_actions=active_actions,
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
        "security_policy": "Strict-Enforced",
        "version": "2.5.0"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 IFCP Resilience Digital Twin starting at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
