"""
Automated Test & Validation Suite for IFCP Resilience Platform
"""

import unittest
import json
from app import app
from engine.topology import get_urban_topology
from engine.cascade_model import CascadeSimulator
from engine.intervention import evaluate_interventions
from engine.xai_engine import XAIEngine
from engine.report_generator import generate_pdf_report

class TestIFCPPlatform(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_topology_graph_integrity(self):
        topo = get_urban_topology()
        self.assertIn("nodes", topo)
        self.assertIn("edges", topo)
        self.assertGreaterEqual(len(topo["nodes"]), 20)
        self.assertGreaterEqual(len(topo["edges"]), 20)
        
        # Verify all 4 layers are present
        layers = set(n["layer"] for n in topo["nodes"])
        self.assertEqual(layers, {"drainage", "power", "transport", "emergency"})

    def test_simulation_engine_cascade(self):
        sim = CascadeSimulator()
        
        # Run baseline low rain
        low_res = sim.run_simulation(rainfall_mm_hr=20.0)
        self.assertGreater(low_res["final_summary"]["final_resilience"], 75.0)
        
        # Run severe deluge
        deluge_res = sim.run_simulation(rainfall_mm_hr=160.0)
        self.assertLess(deluge_res["final_summary"]["final_resilience"], 60.0)
        self.assertGreater(deluge_res["final_summary"]["total_failures"], 0)
        affected_names = [sim.nodes[nid]["name"] for nid in deluge_res["final_summary"]["critical_hospitals_affected"]]
        self.assertTrue(any("Asian Heart" in name for name in affected_names))

    def test_multi_city_basins(self):
        from engine.topology import get_available_cities
        cities = get_available_cities()
        self.assertGreaterEqual(len(cities), 3)

        for c in cities:
            topo = get_urban_topology(c["id"])
            self.assertGreater(len(topo["nodes"]), 10)
            self.assertGreater(len(topo["edges"]), 5)
            
            # Run simulation on each city
            sim = CascadeSimulator(city_id=c["id"])
            res = sim.run_simulation(rainfall_mm_hr=90.0)
            self.assertIn("timeline", res)
            self.assertIn("final_summary", res)

    def test_intervention_mitigation_delta(self):
        eval_data = evaluate_interventions(
            rainfall_mm_hr=90.0,
            selected_actions=["ACTION_MOBILE_PUMPS", "ACTION_GREEN_CORRIDOR"]
        )
        self.assertIn("comparison_matrix", eval_data)
        self.assertGreater(len(eval_data["comparison_matrix"]), 0)
        self.assertGreater(eval_data["selected_portfolio"]["resilience_improvement"], 0)

    def test_xai_causal_path(self):
        sim = CascadeSimulator()
        sim_state = sim.run_simulation(rainfall_mm_hr=140.0)
        
        xai = XAIEngine()
        explanation = xai.explain_node_failure("H_ASIAN_HEART", sim_state)
        
        self.assertIn("causal_chain", explanation)
        self.assertIn("feature_contributions", explanation)
        self.assertGreater(len(explanation["feature_contributions"]), 0)

    def test_pdf_sitrep_generation(self):
        sim = CascadeSimulator()
        sim_state = sim.run_simulation(rainfall_mm_hr=100.0)
        pdf_bytes = generate_pdf_report(sim_state)
        
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_api_endpoints(self):
        # 1. Topology
        r1 = self.app.get("/api/topology")
        self.assertEqual(r1.status_code, 200)

        # 2. Simulate
        r2 = self.app.post("/api/simulate", json={"rainfall_mm_hr": 95})
        self.assertEqual(r2.status_code, 200)
        data2 = json.loads(r2.data)
        self.assertIn("timeline", data2)

        # 3. Interventions compare
        r3 = self.app.post("/api/interventions/compare", json={"rainfall_mm_hr": 95})
        self.assertEqual(r3.status_code, 200)

        # 4. Explain
        r4 = self.app.post("/api/explain/H_ASIAN_HEART", json=data2)
        self.assertEqual(r4.status_code, 200)

        # 5. PDF Sitrep
        r5 = self.app.post("/api/report/pdf", json={"simulation": data2})
        self.assertEqual(r5.status_code, 200)
        self.assertEqual(r5.content_type, "application/pdf")

if __name__ == "__main__":
    unittest.main()
