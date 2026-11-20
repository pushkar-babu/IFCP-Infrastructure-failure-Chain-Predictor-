"""
Intervention & Countermeasure Optimizer
Evaluates, compares and prioritizes preventive actions to mitigate cascading infrastructure failures.
"""

from typing import Dict, List, Any
from engine.cascade_model import CascadeSimulator

AVAILABLE_INTERVENTIONS = [
    {
        "id": "ACTION_MOBILE_PUMPS",
        "title": "Deploy 4x High-Capacity Mobile Dewatering Pumps",
        "target_layer": "drainage",
        "target_nodes": ["D_BKC_PUMP", "D_KALINA_DRAIN"],
        "lead_time_min": 15,
        "resource_cost": "Medium ($12,000)",
        "description": "Mobilizes truck-mounted municipal suction pumps to relieve flooded low-lying sumps and outfalls.",
        "effectiveness_score": 0.88
    },
    {
        "id": "ACTION_GRID_REROUTE",
        "title": "Substation Load Shedding & Bus-Tie Reroute",
        "target_layer": "power",
        "target_nodes": ["E_BKC_SUBSTATION", "E_KALINA_GRID"],
        "lead_time_min": 5,
        "resource_cost": "Low ($2,500)",
        "description": "Remotely commands supervisory SCADA to shed 35% non-essential commercial load and reroute power via auxiliary ring.",
        "effectiveness_score": 0.82
    },
    {
        "id": "ACTION_GREEN_CORRIDOR",
        "title": "Police Emergency Green Corridor & Highway Bypass",
        "target_layer": "transport",
        "target_nodes": ["R_CST_ROAD", "R_WEH_JUNCTION", "H_ASIAN_HEART"],
        "lead_time_min": 10,
        "resource_cost": "Low ($4,000)",
        "description": "Deploys traffic police to commandeer dry elevated flyovers and enforce a barricaded VIP corridor exclusively for ambulances.",
        "effectiveness_score": 0.94
    },
    {
        "id": "ACTION_FLOOD_BARRIERS",
        "title": "Deploy Inflatable Modular Flood Walls & Sandbags",
        "target_layer": "power",
        "target_nodes": ["E_KALINA_GRID", "R_MITHI_BRIDGE"],
        "lead_time_min": 25,
        "resource_cost": "Medium ($18,000)",
        "description": "Rapidly erects 1.2-meter high polyurethane water barriers around transformer yards and highway causeway ramps.",
        "effectiveness_score": 0.85
    }
]

ALLOWED_ACTION_IDS = {action["id"] for action in AVAILABLE_INTERVENTIONS}

def evaluate_interventions(
    rainfall_mm_hr: float = 110.0,
    grid_load_pct: float = 105.0,
    drainage_siltation_pct: float = 40.0,
    high_tide_m: float = 3.6,
    selected_actions: List[str] = None,
    city_id: str = "mumbai"
) -> Dict[str, Any]:
    """
    Compares baseline scenario (zero actions) against individual actions and combined portfolio.
    """
    sim = CascadeSimulator(city_id=city_id)
    # Sanitize and filter actions against allowed set
    selected_actions = [a for a in (selected_actions or []) if a in ALLOWED_ACTION_IDS]

    # 1. Baseline Run (No Interventions)
    baseline_run = sim.run_simulation(
        rainfall_mm_hr=rainfall_mm_hr,
        grid_load_pct=grid_load_pct,
        drainage_siltation_pct=drainage_siltation_pct,
        high_tide_m=high_tide_m,
        interventions=[]
    )
    base_resilience = baseline_run["final_summary"]["final_resilience"]
    base_failures = baseline_run["final_summary"]["total_failures"]
    base_pop_affected = baseline_run["final_summary"]["total_population_affected"]
    base_hospitals_hit = len(baseline_run["final_summary"]["critical_hospitals_affected"])

    # 2. Evaluate Individual Available Interventions
    comparison_table = []
    for action in AVAILABLE_INTERVENTIONS:
        run = sim.run_simulation(
            rainfall_mm_hr=rainfall_mm_hr,
            grid_load_pct=grid_load_pct,
            drainage_siltation_pct=drainage_siltation_pct,
            high_tide_m=high_tide_m,
            interventions=[action["id"]]
        )
        res = run["final_summary"]["final_resilience"]
        fail = run["final_summary"]["total_failures"]
        pop = run["final_summary"]["total_population_affected"]
        hosp_hit = len(run["final_summary"]["critical_hospitals_affected"])

        delta_res = round(res - base_resilience, 1)
        failures_prevented = max(0, base_failures - fail)
        pop_protected = max(0, base_pop_affected - pop)

        comparison_table.append({
            "action_id": action["id"],
            "title": action["title"],
            "target_layer": action["target_layer"],
            "lead_time_min": action["lead_time_min"],
            "resource_cost": action["resource_cost"],
            "resulting_resilience": res,
            "resilience_delta_pct": delta_res,
            "failures_prevented": failures_prevented,
            "population_protected": pop_protected,
            "hospitals_saved": max(0, base_hospitals_hit - hosp_hit),
            "recommendation_rank": 0 # to be sorted
        })

    # Sort by resilience improvement
    comparison_table.sort(key=lambda x: x["resilience_delta_pct"], reverse=True)
    for idx, item in enumerate(comparison_table):
        item["recommendation_rank"] = idx + 1

    # 3. Evaluate User's Currently Selected Custom Portfolio
    portfolio_run = sim.run_simulation(
        rainfall_mm_hr=rainfall_mm_hr,
        grid_load_pct=grid_load_pct,
        drainage_siltation_pct=drainage_siltation_pct,
        high_tide_m=high_tide_m,
        interventions=selected_actions
    )
    port_res = portfolio_run["final_summary"]["final_resilience"]
    port_fail = portfolio_run["final_summary"]["total_failures"]
    port_pop = portfolio_run["final_summary"]["total_population_affected"]
    port_hosp_hit = len(portfolio_run["final_summary"]["critical_hospitals_affected"])

    portfolio_delta_res = round(port_res - base_resilience, 1)
    portfolio_failures_prevented = max(0, base_failures - port_fail)
    portfolio_pop_protected = max(0, base_pop_affected - port_pop)
    portfolio_hospitals_saved = max(0, base_hospitals_hit - port_hosp_hit)

    return {
        "baseline": {
            "resilience_index": base_resilience,
            "total_failures": base_failures,
            "population_affected": base_pop_affected,
            "hospitals_disrupted": base_hospitals_hit
        },
        "selected_portfolio": {
            "active_interventions": selected_actions,
            "resulting_resilience": port_res,
            "resilience_improvement": portfolio_delta_res,
            "failures_prevented": portfolio_failures_prevented,
            "population_protected": portfolio_pop_protected,
            "hospitals_saved": portfolio_hospitals_saved
        },
        "available_actions": AVAILABLE_INTERVENTIONS,
        "comparison_matrix": comparison_table,
        "ai_top_recommendation": comparison_table[0] if comparison_table else None
    }
