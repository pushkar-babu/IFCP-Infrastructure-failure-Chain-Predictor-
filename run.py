"""
Infrastructure Failure Chain Predictor (IFCP) - Unified Launcher
Run with: python run.py
"""

import sys
import os
import webbrowser
from threading import Timer

def open_browser(port):
    try:
        webbrowser.open_new(f"http://127.0.0.1:{port}")
    except Exception:
        pass

def main():
    print("=" * 72)
    print("   🌐 INFRASTRUCTURE FAILURE CHAIN PREDICTOR (IFCP)")
    print("   AI-Powered Urban Cascading Disruption & Resilience Digital Twin")
    print("=" * 72)
    print(" • Target Urban Basin : Mumbai Coastal Zone (BKC & Mithi River Basin)")
    print(" • Model Architecture : Heterogeneous Graph Convolutional Percolation (HGCP-v2)")
    print(" • Interdependent Layers : Drainage, Power Grid, Transport, Emergency Hospitals")
    print(" • Features Included  : Live GIS Twin, XAI Causal Paths, Mitigation Optimizer, PDF SITREP")
    print("=" * 72)

    port = int(os.environ.get("PORT", 5000))
    print(f"\n[+] Starting Server at http://127.0.0.1:{port} ...")
    print("[+] Press Ctrl+C to stop.\n")

    # Open browser automatically after 1.5 seconds
    Timer(1.5, lambda: open_browser(port)).start()

    from app import app
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    main()
