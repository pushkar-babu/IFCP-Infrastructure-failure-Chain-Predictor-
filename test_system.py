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

    def test_security_headers(self):
        """Verify strict OWASP security response headers are enforced."""
        res = self.app.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("X-Frame-Options"), "DENY")
        self.assertIn("default-src", res.headers.get("Content-Security-Policy", ""))
        self.assertEqual(res.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")

    def test_input_validation_and_sanitization(self):
        """Verify negative / extreme values are securely clamped without exceptions."""
        # Negative rainfall should clamp to 0
        r_neg = self.app.post("/api/simulate", json={"rainfall_mm_hr": -50, "city": "mumbai"})
        self.assertEqual(r_neg.status_code, 200)
        
        # Invalid city defaults safely to mumbai without crashing or directory traversal
        r_city = self.app.post("/api/simulate", json={"city": "../../etc/passwd", "rainfall_mm_hr": 50})
        self.assertEqual(r_city.status_code, 200)
        data = json.loads(r_city.data)
        self.assertIn("timeline", data)

        # Malformed node_id in explain endpoint returns 400
        r_invalid_node = self.app.post("/api/explain/NODE@INVALID!NAME", json={})
        self.assertEqual(r_invalid_node.status_code, 400)

    def test_accessibility_compliance_elements(self):
        """Verify WCAG 2.1 AA/AAA compliance markers in rendered template."""
        res = self.app.get("/")
        html = res.data.decode("utf-8")
        self.assertIn('lang="en"', html)
        self.assertIn('class="skip-link"', html)
        self.assertIn('role="banner"', html)
        self.assertIn('<h1', html)
        self.assertIn('role="main"', html)
        self.assertIn('role="tablist"', html)
        self.assertIn('role="switch"', html)
        self.assertIn('role="log"', html)
        self.assertIn('role="img"', html)
        self.assertIn('<caption', html)

    def test_performance_latency(self):
        """Verify simulation execution latency benchmark (< 50ms)."""
        import time
        t0 = time.perf_counter()
        sim = CascadeSimulator()
        sim.run_simulation(rainfall_mm_hr=120.0)
        duration_ms = (time.perf_counter() - t0) * 1000
        self.assertLess(duration_ms, 50.0, f"Simulation latency {duration_ms:.2f}ms exceeded 50ms budget")

if __name__ == "__main__":
    unittest.main()
