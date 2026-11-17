"""
Explainable AI (XAI) & Causal Attribution Engine
Explains cascading failure predictions, backtracks causal pathways, and breaks down feature contributions.
"""

from typing import Dict, List, Any
from engine.topology import get_urban_topology

class XAIEngine:
    def __init__(self, city_id: str = "mumbai"):
        self.city_id = city_id or "mumbai"
        self.topology = get_urban_topology(self.city_id)
        self.nodes = {n["id"]: n for n in self.topology["nodes"]}
        self.edges = self.topology["edges"]
        
        # Build reverse adjacency map (target -> sources)
        self.incoming = {nid: [] for nid in self.nodes}
        for e in self.edges:
            self.incoming[e["target"]].append(e)

    def explain_node_failure(self, node_id: str, simulation_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates full XAI report for a specific infrastructure asset.
        """
        if node_id not in self.nodes:
            return {"error": f"Node {node_id} not found."}

        target_node = self.nodes[node_id]
        final_timeline_snapshot = simulation_state["timeline"][-1]
        node_status_info = final_timeline_snapshot["nodes"].get(node_id, {})

        status = node_status_info.get("status", "HEALTHY")
        stress = node_status_info.get("stress", 0.2)
        prob = node_status_info.get("failure_prob", 0.05)
        ci = node_status_info.get("confidence_interval", [0.03, 0.07])

        # 1. Backtrack Causal Propagation Chain (BFS backwards up to 3 hops)
        causal_chain = self._trace_causal_path(node_id, final_timeline_snapshot)

        # 2. Compute Feature Contribution Breakdown (Simulated Shapley attribution)
        feature_importance = self._compute_feature_importance(node_id, simulation_state)

        # 3. Plain English Explanation
        narrative = self._generate_narrative(target_node, status, causal_chain, feature_importance)

        return {
            "node_id": node_id,
            "node_name": target_node["name"],
            "layer": target_node["layer"],
            "elevation_m": target_node["elevation_m"],
            "status": status,
            "failure_probability": prob,
            "confidence_interval_95": ci,
            "uncertainty_rating": "Moderate" if (ci[1] - ci[0]) > 0.08 else "Low (High Confidence)",
            "causal_chain": causal_chain,
            "feature_contributions": feature_importance,
            "executive_narrative": narrative
        }

    def _trace_causal_path(self, target_id: str, snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Backtracks causal path to find root upstream triggers."""
        path = []
        curr = target_id
        visited = set()

        while curr and curr not in visited:
            visited.add(curr)
            curr_node = self.nodes[curr]
            curr_state = snapshot["nodes"].get(curr, {})
            
            path.append({
                "node_id": curr,
                "name": curr_node["name"],
                "layer": curr_node["layer"],
                "status": curr_state.get("status", "HEALTHY"),
                "stress": curr_state.get("stress", 0.2)
            })

            # Find worst incoming degraded/failed parent
            incoming_edges = self.incoming.get(curr, [])
            worst_parent = None
            max_stress = 0.55

            for edge in incoming_edges:
                src = edge["source"]
                src_stress = snapshot["nodes"].get(src, {}).get("stress", 0.0)
                if src_stress > max_stress and src not in visited:
                    max_stress = src_stress
                    worst_parent = src

            curr = worst_parent

        path.reverse() # Root trigger at start, target asset at end
        return path

    def _compute_feature_importance(self, node_id: str, simulation_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculates percentage attribution of exogenous factors vs network propagation."""
        params = simulation_state.get("parameters", {})
        rain = params.get("rainfall_mm_hr", 85.0)
        silt = params.get("drainage_siltation_pct", 35.0)
        tide = params.get("high_tide_m", 3.5)
        
        node = self.nodes[node_id]
        layer = node["layer"]

        if layer == "drainage":
            weights = [
                {"factor": "Rainfall Precipitation Intensity", "contribution_pct": round(min(65.0, (rain / 140.0) * 55.0), 1)},
                {"factor": "Drainage Siltation / Debris Clog", "contribution_pct": round(min(35.0, (silt / 60.0) * 30.0), 1)},
                {"factor": "Tidal Backpressure & Low Elevation", "contribution_pct": round(15.0 if tide > 3.2 else 5.0, 1)},
                {"factor": "Upstream Runoff Tributaries", "contribution_pct": 10.0}
            ]
        elif layer == "power":
            weights = [
                {"factor": "Surface Flood Inundation (Drainage breach)", "contribution_pct": 46.0},
                {"factor": "Grid Overload / Transmission Imbalance", "contribution_pct": 28.0},
                {"factor": "Basement Transformer Sump Vulnerability", "contribution_pct": 16.0},
                {"factor": "Auxiliary Circuit Aging", "contribution_pct": 10.0}
            ]
        elif layer == "transport":
            weights = [
                {"factor": "Adjacent Drainage Canal Sump Overflow", "contribution_pct": 52.0},
                {"factor": "Rainfall Visibility & Surface Slick", "contribution_pct": 22.0},
                {"factor": "Downstream Bottleneck Congestion Spillover", "contribution_pct": 16.0},
                {"factor": "Intersection Signal Power Disruption", "contribution_pct": 10.0}
            ]
        else: # emergency
            weights = [
                {"factor": "Ingress Road Inundation & Blocked Corridors", "contribution_pct": 58.0},
                {"factor": "Primary Grid Electrical Tripping", "contribution_pct": 24.0},
                {"factor": "Surge in Patient Emergency Admissions", "contribution_pct": 12.0},
                {"factor": "Ambulance Base Mobilization Delay", "contribution_pct": 6.0}
            ]

        # Normalize to 100%
        total = sum(w["contribution_pct"] for w in weights)
        for w in weights:
            w["contribution_pct"] = round((w["contribution_pct"] / total) * 100.0, 1)

        return weights

    def _generate_narrative(self, node: Dict[str, Any], status: str, path: List[Dict[str, Any]], features: List[Dict[str, Any]]) -> str:
        name = node["name"]
        if status in ["DEGRADED", "FAILED"]:
            root = path[0]["name"] if path else "Unfavorable Environmental Conditions"
            top_factor = features[0]["factor"]
            top_pct = features[0]["contribution_pct"]
            return (
                f"Asset [{name}] reached '{status}' state primarily driven by {top_factor} "
                f"(accounting for {top_pct}% of vulnerability score). The failure cascaded from {root} "
                f"across interconnected multi-system conduits. Immediate preventive intervention is required "
                f"to halt further downstream service deprivation."
            )
        else:
            return f"Asset [{name}] remains in stable '{status}' status under current stress loads."
