"""
Urban Infrastructure Topology & Knowledge Graph
Multi-city interdependent infrastructure network supporting:
1. Mumbai Metropolitan Region (BKC & Mithi Coastal River Basin)
2. Bengaluru Urban District (Koramangala & Bellandur Lake Basin)
3. Delhi NCR Region (Yamuna Riverfront & ITO Basin)
"""

import json
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any, Optional

@dataclass
class InfraNode:
    id: str
    name: str
    layer: str  # 'drainage', 'power', 'transport', 'emergency'
    lat: float
    lng: float
    elevation_m: float
    base_capacity: float  # Normalized 100 max
    criticality: float    # 0.0 to 1.0 (importance to city functioning)
    population_impact: int # Citizens dependent
    backup_systems: str   # e.g., 'Dual Diesel Generator (4h)', 'UPS 30min', 'None'
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class InfraEdge:
    source: str
    target: str
    relation: str  # 'supplies_power', 'drains_surface_water', 'emergency_access', 'physical_road', 'flow_downstream'
    weight: float  # 0.1 to 1.0 (dependency strength)
    latency_min: int # Time lag before dependency failure kicks in
    description: str

def get_available_cities() -> List[Dict[str, str]]:
    """Returns list of supported multi-city resilience basins."""
    return [
        {"id": "mumbai", "name": "Mumbai (BKC & Mithi River Coastal Basin)", "type": "Coastal Estuary"},
        {"id": "bengaluru", "name": "Bengaluru (Koramangala & Bellandur Lake Basin)", "type": "Inland Valley Lake System"},
        {"id": "delhi", "name": "Delhi (Yamuna Riverfront & ITO Corridor)", "type": "Riverine Floodplain"}
    ]

# ==========================================
# 1. MUMBAI TOPOLOGY
# ==========================================
def _get_mumbai_topology() -> Dict[str, Any]:
    nodes = [
        InfraNode("D_MITHI_OUTFALL", "Mithi Estuary Tidal Outfall & Gates", "drainage", 19.0535, 72.8420, 2.1, 100.0, 0.95, 450000, "Hydraulic Winch", "Primary sea outfall with floodgates; vulnerable to high-tide backflow.", {"max_discharge_cumec": 320, "silt_level_pct": 28}),
        InfraNode("D_BKC_PUMP", "BKC Stormwater Heavy Pumping Station", "drainage", 19.0630, 72.8640, 3.2, 100.0, 0.92, 320000, "Diesel Genset (2h)", "5x high-capacity submersible pumps lifting stormwater from commercial district.", {"pump_count": 5, "rated_power_mw": 3.8}),
        InfraNode("D_KALINA_DRAIN", "Kalina Box Drain & Retention Basin", "drainage", 19.0740, 72.8570, 4.0, 100.0, 0.78, 180000, "None", "Concrete stormwater channel carrying runoff from airport slopes into Mithi river.", {"basin_volume_m3": 85000, "silt_level_pct": 42}),
        InfraNode("D_DHARAVI_CHANNEL", "Dharavi Trunk Stormwater Canal", "drainage", 19.0450, 72.8520, 2.5, 100.0, 0.85, 390000, "Emergency Sump", "Canal draining informal settlements and peripheral industrial clusters.", {"channel_width_m": 14, "silt_level_pct": 55}),
        InfraNode("D_CHAMBUR_BASIN", "Chunabhatti Low-Lying Sump & Canal", "drainage", 19.0560, 72.8750, 2.2, 100.0, 0.75, 160000, "None", "Depression basin collecting runoff before funneling towards Mahim Bay.", {"silt_level_pct": 35}),
        InfraNode("D_VAKOLA_NULLAH", "Vakola Tributary Confluence", "drainage", 19.0780, 72.8480, 4.8, 100.0, 0.79, 195000, "None", "Feeder nullah entering main Mithi basin; prone to debris blockages.", {"debris_clog_pct": 38}),

        InfraNode("E_BKC_SUBSTATION", "220kV BKC Transmission Substation", "power", 19.0610, 72.8680, 3.5, 100.0, 0.98, 520000, "Dual Ring Feeders", "Central substation feeding financial hub, pumping stations, and hospitals.", {"voltage_kv": 220, "transformer_units": 4}),
        InfraNode("E_DHARAVI_FEEDER", "110kV Dharavi Switching Substation", "power", 19.0430, 72.8560, 2.8, 100.0, 0.88, 310000, "Auxiliary DC Bank", "Powers south-central residential grids, sewage lifts, and street lighting.", {"voltage_kv": 110, "transformer_units": 3}),
        InfraNode("E_KALINA_GRID", "33kV Kalina Distribution Substation", "power", 19.0710, 72.8610, 3.1, 100.0, 0.84, 175000, "Bus-Tie Switch", "Medium-voltage station supplying university campus and arterial traffic signals.", {"voltage_kv": 33, "transformer_units": 2}),
        InfraNode("E_BANDRA_STEPDOWN", "33kV Bandra East Step-Down Yard", "power", 19.0580, 72.8450, 4.2, 100.0, 0.86, 230000, "Auto-reclose Breaker", "Powers railway traction lines, Kalanagar intersection traffic systems.", {"voltage_kv": 33, "transformer_units": 3}),
        InfraNode("E_KURLA_FEEDER", "33kV Kurla West Industrial Feeder", "power", 19.0670, 72.8790, 2.9, 100.0, 0.76, 140000, "None", "Supplies eastern manufacturing sheds and local water sumps.", {"voltage_kv": 33, "transformer_units": 2}),

        InfraNode("R_WEH_JUNCTION", "Western Express Highway (Kalanagar Junction)", "transport", 19.0595, 72.8445, 3.8, 100.0, 0.96, 680000, "Variable Signs", "Lifeline 8-lane arterial junction connecting South Mumbai to Suburbs.", {"daily_vehicles": 185000, "lanes": 8}),
        InfraNode("R_BKC_CONNECTOR", "BKC Connector Flyover & Boulevard", "transport", 19.0570, 72.8620, 4.5, 100.0, 0.90, 290000, "Toll Bypass", "Direct link funneling traffic from Eastern Express Highway directly into BKC.", {"daily_vehicles": 95000, "lanes": 4}),
        InfraNode("R_SCLR_INTERCHANGE", "Santa Cruz-Chembur Link Road Interchange", "transport", 19.0720, 72.8690, 4.8, 100.0, 0.88, 340000, "CCTV Tracking", "Double-decker flyover crossing Central Railway tracks; key transit artery.", {"daily_vehicles": 120000, "lanes": 6}),
        InfraNode("R_LBS_MARG", "LBS Marg Critical Underpass", "transport", 19.0650, 72.8810, 2.3, 100.0, 0.85, 260000, "Submersible Pump", "Sunken underpass linking Kurla to Ghatkopar; prone to rapid flooding.", {"daily_vehicles": 80000, "lanes": 4}),
        InfraNode("R_MITHI_BRIDGE", "Mithi Causeway Bridge", "transport", 19.0560, 72.8500, 3.0, 100.0, 0.91, 410000, "Stress Sensors", "Primary surface bridge crossing the Mithi estuary connecting Bandra to Dharavi.", {"daily_vehicles": 110000, "lanes": 6}),
        InfraNode("R_CST_ROAD", "CST Road Hospital Corridor", "transport", 19.0690, 72.8620, 4.1, 100.0, 0.93, 210000, "Bus Lane", "Access road connecting major multi-speciality tertiary hospitals.", {"daily_vehicles": 65000, "lanes": 4}),
        InfraNode("R_KALINA_MILITARY_RD", "Kalina University Link Arterial", "transport", 19.0760, 72.8530, 5.0, 100.0, 0.73, 110000, "None", "Alternative bypass road running north of Mithi basin.", {"daily_vehicles": 45000, "lanes": 2}),

        InfraNode("H_ASIAN_HEART", "Asian Heart Institute (Super-Speciality Trauma)", "emergency", 19.0645, 72.8670, 4.2, 100.0, 0.99, 85000, "Diesel Genset (12h)", "Premier 250-bed cardiac and trauma center; requires uninterrupted power.", {"bed_capacity": 250, "icu_beds": 65}),
        InfraNode("H_LILAVATI", "Lilavati Hospital & Research Centre", "emergency", 19.0510, 72.8310, 6.5, 100.0, 0.97, 120000, "Triple Gensets", "Major 320-bed tertiary hospital serving western coastline.", {"bed_capacity": 320, "icu_beds": 80}),
        InfraNode("H_VN_DESAI", "VN Desai Municipal Hospital", "emergency", 19.0805, 72.8440, 5.5, 100.0, 0.91, 290000, "Civic Genset (6h)", "Civic hospital catering to large underserved populations in Santa Cruz.", {"bed_capacity": 280, "icu_beds": 35}),
        InfraNode("EM_BKC_FIRE", "BKC Central Disaster Response & Fire Brigade", "emergency", 19.0620, 72.8600, 4.0, 100.0, 0.94, 450000, "Satellite Comms", "Emergency HQ housing water-rescue Zodiac boats and heavy pumps.", {"fire_tenders": 8, "rescue_boats": 4}),
        InfraNode("EM_AMBULANCE_HUB", "Suburban 108 Emergency Ambulance Hub", "emergency", 19.0600, 72.8530, 3.6, 100.0, 0.96, 500000, "TETRA Radio", "Dispatch hub for 24 Advanced Life Support ambulances.", {"active_ambulances": 24})
    ]

    edges = [
        InfraEdge("D_VAKOLA_NULLAH", "D_KALINA_DRAIN", "flow_downstream", 0.85, 10, "Runoff enters Kalina basin"),
        InfraEdge("D_KALINA_DRAIN", "D_BKC_PUMP", "flow_downstream", 0.90, 15, "Basin spillover channels towards BKC pump sump"),
        InfraEdge("D_BKC_PUMP", "D_MITHI_OUTFALL", "flow_downstream", 0.95, 5, "Pumped discharge pumped out into tidal estuary"),
        InfraEdge("D_DHARAVI_CHANNEL", "D_MITHI_OUTFALL", "flow_downstream", 0.88, 12, "Trunk canal discharges into lower Mithi reach"),
        InfraEdge("D_CHAMBUR_BASIN", "D_BKC_PUMP", "flow_downstream", 0.70, 20, "Overflow canal diverted toward BKC lift"),

        InfraEdge("E_BKC_SUBSTATION", "E_KALINA_GRID", "supplies_power", 0.85, 2, "220kV to 33kV distribution feeder line"),
        InfraEdge("E_BKC_SUBSTATION", "E_BANDRA_STEPDOWN", "supplies_power", 0.90, 2, "High-voltage intertie supply line"),
        InfraEdge("E_BKC_SUBSTATION", "E_KURLA_FEEDER", "supplies_power", 0.75, 5, "Radial sub-feeder to Kurla industrial rim"),
        InfraEdge("E_DHARAVI_FEEDER", "E_BANDRA_STEPDOWN", "supplies_power", 0.65, 8, "Secondary grid loop tie-breaker line"),

        InfraEdge("R_WEH_JUNCTION", "R_MITHI_BRIDGE", "physical_road", 0.90, 1, "Arterial connection from Kalanagar onto causeway"),
        InfraEdge("R_MITHI_BRIDGE", "R_BKC_CONNECTOR", "physical_road", 0.88, 2, "Causeway transitions onto BKC connector road"),
        InfraEdge("R_BKC_CONNECTOR", "R_CST_ROAD", "physical_road", 0.92, 2, "Express traffic merges into hospital corridor"),
        InfraEdge("R_CST_ROAD", "R_SCLR_INTERCHANGE", "physical_road", 0.85, 3, "Feeds SCLR double-decker flyover approach"),
        InfraEdge("R_SCLR_INTERCHANGE", "R_LBS_MARG", "physical_road", 0.82, 3, "Eastbound ramp drops directly onto LBS underpass"),
        InfraEdge("R_WEH_JUNCTION", "R_KALINA_MILITARY_RD", "physical_road", 0.75, 4, "Northbound bypass toward airport boundary"),

        InfraEdge("E_BKC_SUBSTATION", "D_BKC_PUMP", "supplies_power", 0.96, 5, "Heavy pumps rely on 3.8MW feeder from BKC 220kV substation."),
        InfraEdge("E_BANDRA_STEPDOWN", "D_MITHI_OUTFALL", "supplies_power", 0.70, 8, "Powers automated tidal sluice gate winches."),
        InfraEdge("D_MITHI_OUTFALL", "R_MITHI_BRIDGE", "drains_surface_water", 0.94, 10, "Mithi backflow inundates causeway road under 0.8m water."),
        InfraEdge("D_BKC_PUMP", "R_BKC_CONNECTOR", "drains_surface_water", 0.92, 12, "Pump slowdown causes pooling at ramp basin of BKC Connector."),
        InfraEdge("D_KALINA_DRAIN", "R_CST_ROAD", "drains_surface_water", 0.89, 15, "Kalina canal breach cascades directly across CST Road hospital access corridor."),
        InfraEdge("D_CHAMBUR_BASIN", "R_LBS_MARG", "drains_surface_water", 0.95, 8, "Chunabhatti sump silt overflow immediately paralyzes LBS Underpass."),
        InfraEdge("D_VAKOLA_NULLAH", "R_WEH_JUNCTION", "drains_surface_water", 0.87, 15, "Vakola trash clog forces overflow across highway bottleneck."),

        InfraEdge("D_KALINA_DRAIN", "E_KALINA_GRID", "drains_surface_water", 0.86, 18, "Kalina basin spillover inundates basement circuit breakers of 33kV Substation."),
        InfraEdge("D_MITHI_OUTFALL", "E_BKC_SUBSTATION", "drains_surface_water", 0.82, 25, "Mithi tidal surge threatens switchyard of 220kV BKC station."),

        InfraEdge("E_BANDRA_STEPDOWN", "R_WEH_JUNCTION", "supplies_power", 0.80, 2, "Powers traffic signals & CCTV at Kalanagar 8-way intersection."),
        InfraEdge("E_KALINA_GRID", "R_SCLR_INTERCHANGE", "supplies_power", 0.72, 3, "Powers ramp illumination and flyover sump pumps."),

        InfraEdge("E_BKC_SUBSTATION", "H_ASIAN_HEART", "supplies_power", 0.98, 1, "Primary 11kV grid feeder to Asian Heart Institute ICU."),
        InfraEdge("E_BANDRA_STEPDOWN", "EM_AMBULANCE_HUB", "supplies_power", 0.88, 2, "Supplies 108 Emergency Radio Dispatch and vehicle bays."),
        InfraEdge("E_KALINA_GRID", "H_VN_DESAI", "supplies_power", 0.92, 2, "Primary power feed to VN Desai Municipal Hospital."),

        InfraEdge("R_CST_ROAD", "H_ASIAN_HEART", "emergency_access", 0.97, 3, "Dedicated dual-carriageway access route for ambulances to Asian Heart."),
        InfraEdge("R_WEH_JUNCTION", "EM_AMBULANCE_HUB", "emergency_access", 0.95, 2, "Ambulance fleet cannot exit base if Kalanagar junction is choked."),
        InfraEdge("R_MITHI_BRIDGE", "EM_BKC_FIRE", "emergency_access", 0.91, 5, "Fire tenders blocked from reaching Dharavi during causeway flood."),
        InfraEdge("R_BKC_CONNECTOR", "H_ASIAN_HEART", "emergency_access", 0.85, 4, "Express patient transfer route from Eastern suburbs."),
        InfraEdge("R_KALINA_MILITARY_RD", "H_VN_DESAI", "emergency_access", 0.84, 5, "Primary ambulance route reaching VN Desai trauma center.")
    ]

    return {
        "city_id": "mumbai",
        "nodes": [asdict(n) for n in nodes],
        "edges": [asdict(e) for e in edges],
        "metadata": {
            "city": "Mumbai Metropolitan Region (BKC Basin)",
            "geo_center": {"lat": 19.0620, "lng": 72.8580},
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "layers": ["drainage", "power", "transport", "emergency"],
            "version": "2.4.0-resilience-twin"
        }
    }

# ==========================================
# 2. BENGALURU TOPOLOGY (Lake-Valley Cascade)
# ==========================================
def _get_bengaluru_topology() -> Dict[str, Any]:
    nodes = [
        # Drainage (Interconnected Lake Cascade)
        InfraNode("D_BELLANDUR_OUTLET", "Bellandur Lake Primary Weir & Sluice", "drainage", 12.9350, 77.6650, 890.0, 100.0, 0.96, 420000, "Manual Gate Sluice", "Largest urban water body outlet; vulnerable to froth overflow and breach.", {"surface_area_sqkm": 3.6, "silt_level_pct": 52}),
        InfraNode("D_AGARA_REGULATOR", "Agara Lake Inflow Waste Weir", "drainage", 12.9230, 77.6350, 895.0, 100.0, 0.88, 280000, "None", "Upstream retention basin controlling runoff from Madivala into Bellandur.", {"silt_level_pct": 38}),
        InfraNode("D_KORAMANGALA_VALLEY", "Koramangala Valley Box Storm Drain (SWD)", "drainage", 12.9360, 77.6200, 902.0, 100.0, 0.92, 360000, "Desilting Traps", "Major concrete storm channel running through dense residential/tech corridors.", {"channel_width_m": 12, "silt_level_pct": 45}),
        InfraNode("D_IBLUR_SUMP", "Iblur Junction Stormwater Retention Sump", "drainage", 12.9220, 77.6620, 892.0, 100.0, 0.78, 150000, "1x Submersible Pump", "Sunken culvert prone to flash flood stagnation during heavy spells.", {"silt_level_pct": 40}),

        # Power Grid (BESCOM)
        InfraNode("E_HAL_RECEIVING", "66/11kV HAL Receiving Substation", "power", 12.9550, 77.6520, 898.0, 100.0, 0.95, 480000, "Dual Ring Feeders", "Central eastern grid station powering aerospace zone and tech corridors.", {"voltage_kv": 66, "transformer_units": 3}),
        InfraNode("E_KORAMANGALA_SUB", "66kV Koramangala BESCOM Substation", "power", 12.9310, 77.6280, 905.0, 100.0, 0.91, 310000, "Auto Bus Coupler", "Feeds tertiary hospitals, traffic controllers, and residential blocks.", {"voltage_kv": 66, "transformer_units": 3}),
        InfraNode("E_BELLANDUR_FEEDER", "33kV Bellandur Tech Park Feeder", "power", 12.9280, 77.6710, 891.0, 100.0, 0.85, 220000, "Auxiliary Transformer", "Supplies outer IT campuses and municipal water lift stations.", {"voltage_kv": 33, "transformer_units": 2}),

        # Transport & Roads
        InfraNode("R_ORR_ECOSPACE", "Outer Ring Road (Eco-Space Flyover & Underpass)", "transport", 12.9260, 77.6760, 892.0, 100.0, 0.97, 650000, "CCTV & Variable Signs", "Lifeline 6-lane IT corridor; chronically submerged in cloudbursts.", {"daily_vehicles": 195000, "lanes": 6}),
        InfraNode("R_SONY_WORLD_JCT", "Sony World Signal Intersection (100ft Rd)", "transport", 12.9345, 77.6270, 904.0, 100.0, 0.92, 380000, "Traffic Surveillance", "Bottleneck commercial crossroads linking Koramangala to Indiranagar.", {"daily_vehicles": 110000, "lanes": 4}),
        InfraNode("R_SARJAPUR_ORR", "Sarjapur Road - Iblur Junction Interchange", "transport", 12.9235, 77.6600, 893.0, 100.0, 0.94, 490000, "Elevated Ramp Bypass", "Massive junction linking southeast Bengaluru to Electronic City.", {"daily_vehicles": 140000, "lanes": 6}),
        InfraNode("R_HOSUR_RD_FLYOVER", "Hosur Road - Silk Board Flyover Approach", "transport", 12.9175, 77.6225, 908.0, 100.0, 0.96, 720000, "Express Lane Barricades", "Critical artery funneling highway traffic into city core.", {"daily_vehicles": 220000, "lanes": 8}),

        # Emergency & Hospitals
        InfraNode("H_ST_JOHNS", "St. John's Medical College Hospital (Level 1 Trauma)", "emergency", 12.9285, 77.6200, 908.0, 100.0, 0.99, 140000, "Dual 500kVA Gensets (24h)", "Premier 1,200-bed university hospital and multi-speciality trauma hub.", {"bed_capacity": 1200, "icu_beds": 120}),
        InfraNode("H_MANIPAL_HAL", "Manipal Hospital Old Airport Road", "emergency", 12.9580, 77.6480, 900.0, 100.0, 0.96, 95000, "Automatic Genset", "600-bed tertiary care and cardiac emergency hospital.", {"bed_capacity": 600, "icu_beds": 75}),
        InfraNode("EM_KORAMANGALA_FIRE", "South-East Fire & Disaster Rescue Base", "emergency", 12.9320, 77.6150, 906.0, 100.0, 0.93, 400000, "High-Power Sump Trailers", "Fire department HQ for boat and pump deployment.", {"fire_tenders": 6, "rescue_boats": 3}),
        InfraNode("EM_BLR_AMBULANCE", "108 GVK-EMRI South Ambulance Depot", "emergency", 12.9260, 77.6250, 905.0, 100.0, 0.95, 450000, "GPS Radio Dispatch", "Stationing 20 ALS emergency ambulances.", {"active_ambulances": 20})
    ]

    edges = [
        # Drainage Cascade
        InfraEdge("D_AGARA_REGULATOR", "D_BELLANDUR_OUTLET", "flow_downstream", 0.92, 10, "Agara lake overflow discharges into Bellandur lake basin"),
        InfraEdge("D_KORAMANGALA_VALLEY", "D_BELLANDUR_OUTLET", "flow_downstream", 0.95, 12, "Storm trunk drain funnels runoff towards Bellandur inlet"),
        InfraEdge("D_IBLUR_SUMP", "D_BELLANDUR_OUTLET", "flow_downstream", 0.85, 8, "Culvert runoff discharges into southern lake fringe"),

        # Power
        InfraEdge("E_HAL_RECEIVING", "E_BELLANDUR_FEEDER", "supplies_power", 0.88, 3, "High-voltage tie line to tech park substations"),
        InfraEdge("E_KORAMANGALA_SUB", "E_HAL_RECEIVING", "supplies_power", 0.75, 4, "Ring main feeder backup intertie"),

        # Roads
        InfraEdge("R_SARJAPUR_ORR", "R_ORR_ECOSPACE", "physical_road", 0.94, 2, "Major traffic flow from Iblur junction to Eco-Space"),
        InfraEdge("R_HOSUR_RD_FLYOVER", "R_SONY_WORLD_JCT", "physical_road", 0.88, 3, "Feeds traffic into central Koramangala 100ft road"),
        InfraEdge("R_SONY_WORLD_JCT", "R_SARJAPUR_ORR", "physical_road", 0.86, 4, "Connecting corridor to southeast suburbs"),

        # Cross-Layer Dependencies (CASCADES)
        InfraEdge("D_BELLANDUR_OUTLET", "R_ORR_ECOSPACE", "drains_surface_water", 0.96, 12, "Bellandur lake foam and water breach inundates Outer Ring Road underpass under 1m water."),
        InfraEdge("D_IBLUR_SUMP", "R_SARJAPUR_ORR", "drains_surface_water", 0.92, 8, "Iblur sump backflow chokes Sarjapur interchange completely."),
        InfraEdge("D_KORAMANGALA_VALLEY", "R_SONY_WORLD_JCT", "drains_surface_water", 0.88, 15, "Storm drain overflow floods 100ft road Sony World junction."),

        InfraEdge("D_BELLANDUR_OUTLET", "E_BELLANDUR_FEEDER", "drains_surface_water", 0.89, 20, "Floodwaters breach basement transformer of Bellandur distribution station."),
        InfraEdge("E_KORAMANGALA_SUB", "H_ST_JOHNS", "supplies_power", 0.98, 1, "Primary power feeder to St. John's Hospital ICU and emergency blocks."),
        InfraEdge("E_HAL_RECEIVING", "H_MANIPAL_HAL", "supplies_power", 0.95, 2, "Powers Manipal Hospital critical care units."),
        InfraEdge("E_KORAMANGALA_SUB", "EM_BLR_AMBULANCE", "supplies_power", 0.86, 2, "Supplies central 108 ambulance dispatch radio."),

        InfraEdge("R_SONY_WORLD_JCT", "H_ST_JOHNS", "emergency_access", 0.96, 3, "LIFELINE: Direct ambulance route to St. John's Trauma Center."),
        InfraEdge("R_HOSUR_RD_FLYOVER", "EM_BLR_AMBULANCE", "emergency_access", 0.94, 2, "Ambulance fleet trapped if Silk Board junction is choked."),
        InfraEdge("R_ORR_ECOSPACE", "H_MANIPAL_HAL", "emergency_access", 0.91, 5, "Ambulance patient transfers from IT corridor to Manipal Hospital.")
    ]

    return {
        "city_id": "bengaluru",
        "nodes": [asdict(n) for n in nodes],
        "edges": [asdict(e) for e in edges],
        "metadata": {
            "city": "Bengaluru Urban District (Koramangala & Bellandur Lake Basin)",
            "geo_center": {"lat": 12.9352, "lng": 77.6450},
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "layers": ["drainage", "power", "transport", "emergency"],
            "version": "2.4.0-resilience-twin"
        }
    }

# ==========================================
# 3. DELHI TOPOLOGY (Yamuna Riverine Basin)
# ==========================================
def _get_delhi_topology() -> Dict[str, Any]:
    nodes = [
        # Drainage
        InfraNode("D_ITO_DRAIN", "ITO Stormwater Trunk Drain & Gates", "drainage", 28.6290, 77.2480, 208.0, 100.0, 0.96, 490000, "Motorized Sluice", "Primary outfall draining Central Delhi into Yamuna; prone to river backflow.", {"silt_level_pct": 45}),
        InfraNode("D_BARAPULLAH_NULLAH", "Barapullah Major Drainage Basin", "drainage", 28.5860, 77.2520, 209.0, 100.0, 0.91, 380000, "None", "Vast stormwater basin carrying south Delhi drainage into river Yamuna.", {"silt_level_pct": 50}),
        InfraNode("D_KASHMERE_GATE_DRAIN", "ISBT Ring Road Sump & Canal", "drainage", 28.6650, 77.2320, 207.0, 100.0, 0.88, 310000, "Heavy Sump", "Low-lying collector canal near northern Yamuna embankment.", {"silt_level_pct": 36}),

        # Power Grid (DTL & BSES)
        InfraNode("E_IP_SUBSTATION", "220kV IP Estate DTL Substation", "power", 28.6240, 77.2470, 211.0, 100.0, 0.98, 550000, "Dual Ring Feeders", "Critical grid station powering Delhi Secretariat, Police HQ, and major hospitals.", {"voltage_kv": 220, "transformer_units": 4}),
        InfraNode("E_PRAGATI_FEEDER", "66kV Pragati Power Feeder", "power", 28.6180, 77.2430, 214.0, 100.0, 0.86, 210000, "Auxiliary Transformer", "Feeds exhibition transit complex and tunnel pumping systems.", {"voltage_kv": 66, "transformer_units": 2}),
        InfraNode("E_KASHMERE_GRID", "33kV Kashmere Gate Distribution Substation", "power", 28.6630, 77.2280, 212.0, 100.0, 0.84, 190000, "Bus-Tie Switch", "Supplies North Delhi transit hubs and metro feeders.", {"voltage_kv": 33, "transformer_units": 2}),

        # Transport
        InfraNode("R_RING_ROAD_ITO", "Ring Road (ITO Vikas Minar Chokepoint)", "transport", 28.6285, 77.2460, 209.0, 100.0, 0.98, 780000, "Variable Signs", "The most congested arterial in Delhi; completely submerged when Yamuna breaches 207.5m.", {"daily_vehicles": 240000, "lanes": 8}),
        InfraNode("R_PRAGATI_TUNNEL", "Pragati Maidan Integrated Transit Tunnel", "transport", 28.6170, 77.2420, 204.0, 100.0, 0.93, 310000, "Automated Drainage Pumps", "Sub-surface tunnel vulnerable to water pooling during intense rain spells.", {"daily_vehicles": 90000, "lanes": 6}),
        InfraNode("R_BHAIRO_MARG", "Bhairo Marg Arterial Link", "transport", 28.6120, 77.2490, 208.0, 100.0, 0.89, 290000, "Traffic Surveillance", "Connector road between Ring Road and Mathura Road.", {"daily_vehicles": 85000, "lanes": 4}),
        InfraNode("R_ISBT_KASHMERE", "ISBT Ring Road Flyover & Boulevard", "transport", 28.6660, 77.2310, 209.0, 100.0, 0.94, 450000, "Barricade Bypass", "Major transit gateway connecting Delhi to Haryana and Punjab.", {"daily_vehicles": 160000, "lanes": 6}),

        # Emergency
        InfraNode("H_LNJP", "Lok Nayak Hospital (LNJP Level 1 Trauma)", "emergency", 28.6360, 77.2410, 216.0, 100.0, 0.99, 320000, "Triple Genset (24h)", "Delhi's largest 2,000-bed government emergency trauma hospital.", {"bed_capacity": 2000, "icu_beds": 150}),
        InfraNode("H_GB_PANT", "GB Pant Institute of Post Graduate Medical Care", "emergency", 28.6380, 77.2420, 217.0, 100.0, 0.97, 180000, "Dedicated Diesel Genset", "Super-speciality cardiac and neurology tertiary hospital.", {"bed_capacity": 700, "icu_beds": 90}),
        InfraNode("EM_DELHI_DISASTER", "Delhi Disaster Management Authority (DDMA HQ)", "emergency", 28.6220, 77.2350, 215.0, 100.0, 0.95, 600000, "Satellite TETRA Comms", "State emergency operations center coordinating NDRF and Fire brigades.", {"rescue_boats": 12, "personnel": 120}),
        InfraNode("EM_CENTRAL_AMBULANCE", "Central CATS 102/108 Ambulance Base", "emergency", 28.6310, 77.2370, 214.0, 100.0, 0.96, 520000, "Radio Fleet Dispatch", "Central base dispatching 28 emergency life-support ambulances.", {"active_ambulances": 28})
    ]

    edges = [
        # Drainage
        InfraEdge("D_ITO_DRAIN", "R_RING_ROAD_ITO", "drains_surface_water", 0.96, 10, "ITO drain regulator breach causes Yamuna river water to submerge Ring Road."),
        InfraEdge("D_BARAPULLAH_NULLAH", "R_BHAIRO_MARG", "drains_surface_water", 0.90, 12, "Barapullah overflow spills onto low-lying Bhairo Marg link road."),
        InfraEdge("D_KASHMERE_GATE_DRAIN", "R_ISBT_KASHMERE", "drains_surface_water", 0.92, 10, "ISBT sump overflow floods north Ring Road carriageway."),

        # Cross-layer Power & Drainage
        InfraEdge("D_ITO_DRAIN", "E_IP_SUBSTATION", "drains_surface_water", 0.88, 20, "Yamuna floodwaters threaten perimeter transformer switchyard of IP Substation."),
        InfraEdge("E_IP_SUBSTATION", "H_LNJP", "supplies_power", 0.98, 1, "Direct 11kV grid feeder to LNJP Trauma and ICU blocks."),
        InfraEdge("E_IP_SUBSTATION", "H_GB_PANT", "supplies_power", 0.97, 1, "Powers GB Pant neurology and cardiac emergency units."),
        InfraEdge("E_PRAGATI_FEEDER", "R_PRAGATI_TUNNEL", "supplies_power", 0.92, 2, "Powers continuous drainage pumps inside Pragati tunnel."),
        InfraEdge("E_IP_SUBSTATION", "EM_CENTRAL_AMBULANCE", "supplies_power", 0.85, 2, "Powers central CATS ambulance command and GPS radios."),

        # Roads & Emergency
        InfraEdge("R_RING_ROAD_ITO", "H_LNJP", "emergency_access", 0.97, 2, "CRITICAL: Primary ambulance route reaching LNJP Trauma center from East Delhi."),
        InfraEdge("R_BHAIRO_MARG", "R_PRAGATI_TUNNEL", "physical_road", 0.88, 3, "Traffic feeder into Pragati Maidan transit tunnel."),
        InfraEdge("R_RING_ROAD_ITO", "EM_CENTRAL_AMBULANCE", "emergency_access", 0.95, 2, "CATS ambulance fleet blocked from deploying if Ring Road is waterlogged."),
        InfraEdge("R_ISBT_KASHMERE", "H_GB_PANT", "emergency_access", 0.91, 4, "Key corridor bringing northern emergency transfers to GB Pant Hospital.")
    ]

    return {
        "city_id": "delhi",
        "nodes": [asdict(n) for n in nodes],
        "edges": [asdict(e) for e in edges],
        "metadata": {
            "city": "Delhi NCR (Yamuna Riverfront & ITO Corridor)",
            "geo_center": {"lat": 28.6280, "lng": 77.2420},
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "layers": ["drainage", "power", "transport", "emergency"],
            "version": "2.4.0-resilience-twin"
        }
    }

def get_urban_topology(city_id: str = "mumbai") -> Dict[str, Any]:
    """Returns the multi-layer infrastructure graph for the specified city."""
    city_id = (city_id or "mumbai").lower().strip()
    if city_id == "bengaluru" or city_id == "bangalore":
        return _get_bengaluru_topology()
    elif city_id == "delhi":
        return _get_delhi_topology()
    else:
        return _get_mumbai_topology()

if __name__ == "__main__":
    cities = get_available_cities()
    for c in cities:
        topo = get_urban_topology(c["id"])
        print(f"Loaded {c['name']}: {topo['metadata']['total_nodes']} nodes, {topo['metadata']['total_edges']} edges.")
