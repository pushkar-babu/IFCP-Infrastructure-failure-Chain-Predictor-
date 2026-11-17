# 🏆 Hackathon Online Submission Package
## Project Name: Infrastructure Failure Chain Predictor (IFCP)
### Tagline: AI-Powered Urban Resilience Digital Twin for Cascading Disaster Mitigation

---

### 1. Elevator Pitch (Problem & Solution in 100 Words)
When extreme weather strikes modern cities, failures in one infrastructure layer trigger devastating chain reactions: heavy rainfall breaches stormwater drains, which submerges major arterial highways, gridlocks traffic, trips low-lying electrical substations, and cuts off ambulance access to trauma hospitals. Because municipal departments operate in isolated data silos, predicting these cross-system cascading failures before disruption occurs is virtually impossible. 

**IFCP** solves this by unifying city networks into an interdependent **Heterogeneous Graph Digital Twin**. Using **Graph Convolutional Percolation (HGCP-v2)** and **Explainable AI (XAI)**, IFCP forecasts multi-hop failure chains, explains root causes, and empowers emergency commanders to simulate, compare, and deploy preventive countermeasures in real-time.

---

### 2. Submission Categories / Tracks
* **Primary Track:** Smart Cities & Urban Resilience / AI for Social Good / Disaster Management
* **Secondary Track:** Open Innovation / Deep Learning & Graph Intelligence

---

### 3. Key Differentiators & Innovation
1. **Beyond Single-System Detection:** Unlike conventional flood-monitoring or smart-grid apps that only look at one utility, IFCP explicitly models **inter-layer dependencies** (Power $\to$ Pumps, Drainage $\to$ Roads, Roads $\to$ Hospitals).
2. **Actionable "What-If" Countermeasures:** Evaluates active interventions (Mobile Dewatering Pumps, SCADA Grid Shedding, Ambulance Green Corridors, Modular Water Barriers) and immediately re-simulates the **Resilience Delta ($\Delta \text{SRI}$)**.
3. **Transparent & Auditable (XAI):** Backtracks multi-hop causal chains to tell the incident commander exactly *why* an asset is at risk and how confident the prediction is (95% Credible Intervals).
4. **Automated Municipal SITREP (PDF):** Generates formal, NDMA-grade Situation Reports ready for immediate operational deployment.

---

### 4. Technical Architecture & Tech Stack
* **Frontend:** Interactive Command Center (HTML5, Vanilla ES6, Leaflet.js GIS, Canvas 2D Graph Explorer, CSS Glassmorphism).
* **Backend:** Python 3 + Flask REST API with async cross-origin resource sharing (`flask-cors`).
* **Analytical Engine:** Heterogeneous Graph Convolutional Percolation (HGCP-v2), Causal BFS Backtracking, Non-linear Threshold Dynamics.
* **Reporting:** ReportLab PDF Generation Engine for automated Situation Reports.
* **Datasets & Geography:** OpenStreetMap (OSM) calibrated topology for the Mumbai BKC Coastal River Basin (22 multi-layer assets, 26 dependency conduits).

---

### 5. Quick Demo & Verification Instructions for Evaluators

```bash
# 1. Clone repository
git clone https://github.com/<your-username>/promptwars2.git
cd promptwars2

# 2. Install dependencies (100% pure lightweight Python)
pip install -r requirements.txt

# 3. Launch application
python run.py
```
* **URL:** Navigate to `http://127.0.0.1:5000` in any browser.
* **Run Tests:** Run `python test_system.py` (6/6 tests passing, 0.16s).

#### Recommended 60-Second Evaluator Walkthrough:
1. **Inspect Baseline State:** Note the green nodes on the GIS Digital Twin map.
2. **Inject Environmental Stress:** Click the **Cloudburst (130mm)** scenario preset or drag the Rainfall slider to **130 mm/h**.
3. **Play Cascade:** Click **"▶ Play Cascade"** and watch the time scrubber advance from $T+00\text{m}$ to $T+60\text{m}$.
   * Watch the Mithi Outfall overflow $\to$ Kalanagar Highway submerge $\to$ Kalina Substation trip $\to$ Asian Heart Institute corridor severed!
4. **Deploy Countermeasures:** In the left sidebar, activate **Mobile Dewatering Pumps** and **Ambulance Green Corridor**. Watch the System Resilience Index immediately recover and hospital access turn safe (Green)!
5. **Inspect Causal Chain (XAI):** Click on **Asian Heart Institute** on the map or graph. Review the causal propagation pathway and feature importance breakdown in the right sidebar.
6. **Download SITREP:** Click **"📄 Download Official PDF SITREP"** in the top navigation to view the generated municipal incident report.
