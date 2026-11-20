/**
 * IFCP Application Master Controller
 * Wires together GIS Map, Graph Explorer, Simulation Engine, XAI, Intervention Planner,
 * and the Cinematic Auto-Play Demo Walkthrough Engine.
 */

let appState = {
  city: "mumbai",
  topology: null,
  currentSimulation: null,
  selectedNodeId: "H_ASIAN_HEART",
  activeInterventions: [],
  mapManager: null,
  graphExplorer: null,
  simController: null
};

document.addEventListener("DOMContentLoaded", async () => {
  initUI();
  await loadTopology();
  await runSimulation();
  await loadInterventionComparison();
});

function initUI() {
  // City Selector Listener
  document.getElementById("city-selector")?.addEventListener("change", async (e) => {
    appState.city = e.target.value;
    if (appState.city === "bengaluru") appState.selectedNodeId = "H_ST_JOHNS";
    else if (appState.city === "delhi") appState.selectedNodeId = "H_LNJP";
    else appState.selectedNodeId = "H_ASIAN_HEART";

    await loadTopology();
    await runSimulation();
    await loadInterventionComparison();
  });

  // 1. Simulator setup
  appState.simController = new SimulationController((stepIdx, snapshot, fullSim) => {
    updateTimelineUI(stepIdx, snapshot, fullSim);
    if (appState.mapManager) {
      appState.mapManager.updateNodeStates(snapshot.nodes, snapshot.events_at_step);
    }
    if (appState.graphExplorer) {
      appState.graphExplorer.updateNodeStates(snapshot.nodes);
    }
  });

  // 2. Playback buttons
  document.getElementById("btn-play")?.addEventListener("click", () => {
    const btn = document.getElementById("btn-play");
    if (appState.simController.isPlaying) {
      appState.simController.pause();
      btn.innerText = "▶ Play Cascade";
    } else {
      appState.simController.play();
      btn.innerText = "⏸ Pause";
    }
  });

  document.getElementById("btn-step")?.addEventListener("click", () => {
    appState.simController.stepForward();
  });

  document.getElementById("btn-reset")?.addEventListener("click", () => {
    appState.simController.reset();
    const btn = document.getElementById("btn-play");
    if (btn) btn.innerText = "▶ Play Cascade";
  });

  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  const debouncedRunSimulation = debounce(() => {
    runSimulation();
    loadInterventionComparison();
  }, 180);

  const timelineSlider = document.getElementById("timeline-slider");
  timelineSlider?.addEventListener("input", (e) => {
    const val = parseInt(e.target.value);
    timelineSlider.setAttribute("aria-valuenow", val);
    timelineSlider.setAttribute("aria-valuetext", `Simulation step ${val}`);
    appState.simController.seek(val);
  });

  // 3. Environmental Sliders
  ["rainfall", "grid", "silt", "tide"].forEach(param => {
    const slider = document.getElementById(`slider-${param}`);
    const display = document.getElementById(`val-${param}`);
    if (slider && display) {
      slider.addEventListener("input", (e) => {
        let suffix = param === "rainfall" ? " mm/h" : (param === "tide" ? " m" : "%");
        display.innerText = e.target.value + suffix;
        slider.setAttribute("aria-valuenow", e.target.value);
        slider.setAttribute("aria-valuetext", `${e.target.value}${suffix}`);
        debouncedRunSimulation();
      });
      slider.addEventListener("change", () => {
        runSimulation();
        loadInterventionComparison();
      });
    }
  });

  // 4. Scenario Presets
  document.querySelectorAll(".scenario-preset-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const rain = e.target.dataset.rain;
      const silt = e.target.dataset.silt;
      const tide = e.target.dataset.tide;

      if (rain) {
        const sl = document.getElementById("slider-rainfall");
        if (sl) {
          sl.value = rain;
          sl.setAttribute("aria-valuenow", rain);
          sl.setAttribute("aria-valuetext", `${rain} mm/h`);
        }
        const valRain = document.getElementById("val-rainfall");
        if (valRain) valRain.innerText = rain + " mm/h";
      }
      if (silt) {
        const sl = document.getElementById("slider-silt");
        if (sl) {
          sl.value = silt;
          sl.setAttribute("aria-valuenow", silt);
          sl.setAttribute("aria-valuetext", `${silt}%`);
        }
        const valSilt = document.getElementById("val-silt");
        if (valSilt) valSilt.innerText = silt + "%";
      }
      if (tide) {
        const sl = document.getElementById("slider-tide");
        if (sl) {
          sl.value = tide;
          sl.setAttribute("aria-valuenow", tide);
          sl.setAttribute("aria-valuetext", `${tide} m`);
        }
        const valTide = document.getElementById("val-tide");
        if (valTide) valTide.innerText = tide + " m";
      }
      runSimulation();
      loadInterventionComparison();
    });
  });

  // 5. Active Intervention Checkboxes
  document.querySelectorAll(".intervention-checkbox").forEach(cb => {
    cb.addEventListener("change", () => {
      const active = [];
      document.querySelectorAll(".intervention-checkbox:checked").forEach(c => {
        active.push(c.value);
      });
      appState.activeInterventions = active;
      runSimulation();
      loadInterventionComparison();
    });
  });

  // 6. Tab Navigation
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      document.querySelectorAll(".tab-btn").forEach(b => {
        b.classList.remove("active");
        b.setAttribute("aria-selected", "false");
      });
      document.querySelectorAll(".tab-pane").forEach(p => p.style.display = "none");
      
      btn.classList.add("active");
      btn.setAttribute("aria-selected", "true");
      const tabId = btn.dataset.tab;
      const pane = document.getElementById(`pane-${tabId}`);
      if (pane) pane.style.display = "block";

      if (tabId === "graph") {
        if (appState.graphExplorer) {
          appState.graphExplorer.startAnimationLoop();
          setTimeout(() => appState.graphExplorer.resize(), 50);
        }
      } else {
        if (appState.graphExplorer) {
          appState.graphExplorer.stopAnimationLoop();
        }
      }

      if (tabId === "map" && appState.mapManager && appState.mapManager.map) {
        setTimeout(() => appState.mapManager.map.invalidateSize(), 50);
      }
    });
  });

  // 7. Layer Filter Toggles
  document.querySelectorAll(".layer-toggle-btn").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const layer = btn.dataset.layer || e.target.dataset.layer;
      const isActive = appState.mapManager.toggleLayer(layer);
      btn.style.opacity = isActive ? "1" : "0.4";
      btn.setAttribute("aria-checked", isActive ? "true" : "false");
    });
  });

  // 8. Download PDF Report Button
  document.getElementById("btn-download-pdf")?.addEventListener("click", downloadPdfReport);
}

async function loadTopology() {
  try {
    const res = await fetch(`/api/topology?city=${appState.city}`);
    appState.topology = await res.json();

    // Update subtitle
    const sub = document.getElementById("city-subtitle");
    if (sub && appState.topology.metadata) {
      sub.innerHTML = `Target: <b style="color:#e2e8f0;">${appState.topology.metadata.city}</b> (${appState.topology.metadata.total_nodes} Assets, ${appState.topology.metadata.total_edges} Conduits)`;
    }

    // Init or update Map
    if (!appState.mapManager) {
      appState.mapManager = new GISMapManager("map", (nodeId) => {
        selectNode(nodeId);
      });
      appState.mapManager.init(appState.topology);
    } else {
      appState.mapManager.setCity(appState.topology);
    }

    // Init or update Graph Explorer
    if (!appState.graphExplorer) {
      appState.graphExplorer = new DependencyGraphExplorer("graph-canvas", (nodeId) => {
        selectNode(nodeId);
      });
      appState.graphExplorer.init(appState.topology);
    } else {
      appState.graphExplorer.init(appState.topology);
    }

  } catch (err) {
    console.error("Failed to load topology:", err);
  }
}

async function runSimulation() {
  const rain = parseFloat(document.getElementById("slider-rainfall")?.value || 85);
  const grid = parseFloat(document.getElementById("slider-grid")?.value || 100);
  const silt = parseFloat(document.getElementById("slider-silt")?.value || 35);
  const tide = parseFloat(document.getElementById("slider-tide")?.value || 3.4);

  try {
    const res = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: jsonBody({
        city: appState.city,
        rainfall_mm_hr: rain,
        grid_load_pct: grid,
        drainage_siltation_pct: silt,
        high_tide_m: tide,
        interventions: appState.activeInterventions
      })
    });

    appState.currentSimulation = await res.json();
    appState.simController.setSimulationData(appState.currentSimulation);

    // Update Evaluation Metrics Tab
    renderModelMetrics(appState.currentSimulation.metrics);

    // Update XAI for currently selected node
    explainCurrentNode();

  } catch (err) {
    console.error("Simulation failed:", err);
  }
}

function updateTimelineUI(stepIdx, snapshot, fullSim) {
  const slider = document.getElementById("timeline-slider");
  if (slider) {
    slider.value = stepIdx;
    slider.setAttribute("aria-valuenow", stepIdx);
    slider.setAttribute("aria-valuetext", `Step ${stepIdx}, T + ${String(snapshot.time_min).padStart(2, '0')} minutes`);
  }

  const timeLabel = document.getElementById("current-time-label");
  if (timeLabel) timeLabel.innerText = `T + ${String(snapshot.time_min).padStart(2, '0')} min`;

  const sriEl = document.getElementById("metric-sri");
  if (sriEl) {
    sriEl.innerText = snapshot.resilience_index + "%";
    sriEl.style.color = snapshot.resilience_index > 70 ? "#34d399" : (snapshot.resilience_index > 40 ? "#fbbf24" : "#f87171");
  }

  const failEl = document.getElementById("metric-failures");
  if (failEl) failEl.innerText = snapshot.counts.failed;

  const degEl = document.getElementById("metric-degraded");
  if (degEl) degEl.innerText = snapshot.counts.degraded;

  const popEl = document.getElementById("metric-population");
  if (popEl) popEl.innerText = (snapshot.population_affected / 1000).toFixed(0) + "k";

  // Stream events into event log container
  const eventsContainer = document.getElementById("events-feed");
  if (eventsContainer) {
    const allEventsUpToNow = fullSim.all_events.filter(e => e.time_min <= snapshot.time_min);
    if (allEventsUpToNow.length === 0) {
      eventsContainer.innerHTML = `<div style="color:#64748b; font-size:12px; padding:8px;">No systemic failures recorded at this step.</div>`;
    } else {
      eventsContainer.innerHTML = allEventsUpToNow.slice().reverse().map(ev => `
        <div class="event-item">
          <div style="font-weight:700; color:#fca5a5; display:flex; justify-content:space-between;">
            <span>[T+${ev.time_min}m] ${ev.type.replace(/_/g, ' ')}</span>
          </div>
          <div style="color:#e2e8f0; margin-top:2px;">${ev.message}</div>
        </div>
      `).join('');
    }
  }
}

async function selectNode(nodeId) {
  appState.selectedNodeId = nodeId;
  if (appState.graphExplorer) appState.graphExplorer.selectedNodeId = nodeId;
  explainCurrentNode();
}

async function explainCurrentNode() {
  const nodeId = appState.selectedNodeId;
  if (!nodeId || !appState.currentSimulation) return;

  try {
    const res = await fetch(`/api/explain/${nodeId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(appState.currentSimulation)
    });
    const xaiData = await res.json();
    renderXAIReport(xaiData);
  } catch (err) {
    console.error("XAI explanation failed:", err);
  }
}

function renderXAIReport(xai) {
  const container = document.getElementById("xai-container");
  if (!container) return;

  const statusBadge = `<span class="badge badge-${xai.status.toLowerCase()}">${xai.status}</span>`;
  
  const causalChainHtml = xai.causal_chain.map((step, idx) => `
    <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">
      <span style="font-size:11px; color:#94a3b8; width:22px;">#${idx + 1}</span>
      <div style="flex:1; background:rgba(30,41,59,0.7); padding:6px 10px; border-radius:6px; border:1px solid #334155;">
        <div style="font-weight:600; font-size:12px; color:#f8fafc;">${step.name}</div>
        <div style="font-size:10px; color:#94a3b8; display:flex; justify-content:space-between;">
          <span style="text-transform:capitalize">${step.layer}</span>
          <span class="badge badge-${step.status.toLowerCase()}">${step.status}</span>
        </div>
      </div>
    </div>
  `).join('');

  const featuresHtml = xai.feature_contributions.map(f => `
    <div style="margin-bottom:8px;">
      <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:2px;">
        <span style="color:#cbd5e1;">${f.factor}</span>
        <span style="font-weight:700; color:#38bdf8;">${f.contribution_pct}%</span>
      </div>
      <div style="background:#1e293b; height:6px; border-radius:3px; overflow:hidden;">
        <div style="background:#0284c7; width:${f.contribution_pct}%; height:100%;"></div>
      </div>
    </div>
  `).join('');

  container.innerHTML = `
    <div style="border-bottom:1px solid var(--border-color); padding-bottom:10px; margin-bottom:12px;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <h4 style="font-size:14px; font-weight:700; color:#f8fafc;">${xai.node_name}</h4>
        ${statusBadge}
      </div>
      <div style="font-size:11px; color:#94a3b8; margin-top:4px;">
        Layer: <b style="text-transform:capitalize; color:#cbd5e1;">${xai.layer}</b> | Elev: <b>${xai.elevation_m}m</b>
      </div>
    </div>

    <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:14px;">
      <div class="metric-card" style="padding:8px;">
        <div class="metric-label">Failure Probability</div>
        <div class="metric-val" style="font-size:18px; color:${xai.failure_probability > 0.6 ? '#f87171' : '#34d399'};">
          ${(xai.failure_probability * 100).toFixed(1)}%
        </div>
      </div>
      <div class="metric-card" style="padding:8px;">
        <div class="metric-label">95% Confidence Band</div>
        <div class="metric-val" style="font-size:14px; color:#38bdf8; margin-top:6px;">
          [${(xai.confidence_interval_95[0]*100).toFixed(0)}% - ${(xai.confidence_interval_95[1]*100).toFixed(0)}%]
        </div>
      </div>
    </div>

    <div style="margin-bottom:14px;">
      <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:#94a3b8; margin-bottom:6px;">
        Causal Propagation Pathway
      </div>
      ${causalChainHtml}
    </div>

    <div style="margin-bottom:14px;">
      <div style="font-size:11px; font-weight:700; text-transform:uppercase; color:#94a3b8; margin-bottom:8px;">
        Attribution Drivers (SHAP/Feature Importance)
      </div>
      ${featuresHtml}
    </div>

    <div style="background:rgba(15,23,42,0.8); border:1px solid #334155; padding:10px; border-radius:6px; font-size:11px; color:#cbd5e1; line-height:1.4;">
      <b style="color:#38bdf8;">AI Executive Assessment:</b><br/>
      ${xai.executive_narrative}
    </div>
  `;
}

async function loadInterventionComparison() {
  const rain = parseFloat(document.getElementById("slider-rainfall")?.value || 85);
  const grid = parseFloat(document.getElementById("slider-grid")?.value || 100);
  const silt = parseFloat(document.getElementById("slider-silt")?.value || 35);
  const tide = parseFloat(document.getElementById("slider-tide")?.value || 3.4);

  try {
    const res = await fetch("/api/interventions/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        city: appState.city,
        rainfall_mm_hr: rain,
        grid_load_pct: grid,
        drainage_siltation_pct: silt,
        high_tide_m: tide,
        selected_actions: appState.activeInterventions
      })
    });
    const data = await res.json();
    renderInterventionPlanner(data);
  } catch (err) {
    console.error("Failed to load interventions:", err);
  }
}

function renderInterventionPlanner(data) {
  const tableBody = document.getElementById("intervention-matrix-body");
  if (!tableBody) return;

  tableBody.innerHTML = data.comparison_matrix.map(row => `
    <tr style="border-bottom:1px solid #334155; font-size:12px;">
      <td style="padding:10px 8px; font-weight:600; color:#f8fafc;">
        #${row.recommendation_rank} ${row.title}
        <div style="font-size:10px; color:#94a3b8;">${row.resource_cost} | Lead: ${row.lead_time_min}m</div>
      </td>
      <td style="padding:10px 8px; text-transform:capitalize; color:#38bdf8;">${row.target_layer}</td>
      <td style="padding:10px 8px; font-weight:700; color:#34d399;">+${row.resilience_delta_pct}%</td>
      <td style="padding:10px 8px; color:#e2e8f0;">${row.failures_prevented} assets</td>
      <td style="padding:10px 8px; color:#e2e8f0;">${(row.population_protected/1000).toFixed(0)}k citizens</td>
      <td style="padding:10px 8px; font-weight:700; color:${row.hospitals_saved > 0 ? '#34d399' : '#94a3b8'};">
        ${row.hospitals_saved > 0 ? `🛡️ ${row.hospitals_saved} Saved` : '0'}
      </td>
    </tr>
  `).join('');

  const recBanner = document.getElementById("ai-rec-banner");
  if (recBanner && data.ai_top_recommendation) {
    const top = data.ai_top_recommendation;
    recBanner.innerHTML = `
      <div style="background:rgba(2,132,199,0.15); border:1px solid #0284c7; padding:12px; border-radius:8px;">
        <div style="font-weight:700; color:#38bdf8; font-size:13px;">
          ⭐ Priority Recommended Mitigation: ${top.title}
        </div>
        <div style="font-size:12px; color:#cbd5e1; margin-top:4px;">
          Deploying this single intervention yields a <b>+${top.resilience_delta_pct}%</b> resilience recovery, 
          averts <b>${top.failures_prevented}</b> downstream infrastructure failures, and protects <b>${(top.population_protected/1000).toFixed(0)}k citizens</b>.
        </div>
      </div>
    `;
  }
}

function renderModelMetrics(metrics) {
  const container = document.getElementById("metrics-container");
  if (!container || !metrics) return;

  container.innerHTML = `
    <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin-bottom:16px;">
      <div class="metric-card">
        <div class="metric-label">Precision</div>
        <div class="metric-val" style="color:#38bdf8;">${(metrics.precision * 100).toFixed(1)}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">Recall</div>
        <div class="metric-val" style="color:#38bdf8;">${(metrics.recall * 100).toFixed(1)}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">F1-Score</div>
        <div class="metric-val" style="color:#34d399;">${(metrics.f1_score * 100).toFixed(1)}%</div>
      </div>
      <div class="metric-card">
        <div class="metric-label">PR-AUC</div>
        <div class="metric-val" style="color:#a855f7;">${(metrics.pr_auc * 100).toFixed(1)}%</div>
      </div>
    </div>

    <div style="background:rgba(15,23,42,0.8); border:1px solid #334155; padding:14px; border-radius:8px; margin-bottom:16px;">
      <h4 style="font-size:13px; font-weight:700; color:#f8fafc; margin-bottom:10px;">
        Empirical Benchmark vs Baseline Architectures (F1-Score)
      </h4>
      <div style="display:flex; flex-direction:column; gap:8px;">
        ${renderBenchmarkBar("Baseline: Logistic Regression", metrics.baseline_comparison.logistic_regression_f1, "#64748b")}
        ${renderBenchmarkBar("Baseline: Random Forest", metrics.baseline_comparison.random_forest_f1, "#0284c7")}
        ${renderBenchmarkBar("Baseline: Pure Graph BFS Percolation", metrics.baseline_comparison.pure_bfs_cascade_f1, "#f59e0b")}
        ${renderBenchmarkBar("IFCP: Heterogeneous GNN (Ours)", metrics.baseline_comparison.ifcp_gnn_f1, "#10b981", true)}
      </div>
    </div>

    <div class="metric-card">
      <div class="metric-label">Brier Calibration Score (Lower is Better)</div>
      <div class="metric-val" style="font-size:16px; color:#38bdf8; margin-top:4px;">
        ${metrics.brier_calibration_score} <span style="font-size:11px; color:#94a3b8;">(Well-calibrated probabilistic predictions)</span>
      </div>
    </div>
  `;
}

function renderBenchmarkBar(label, score, color, isHighlight = false) {
  const pct = (score * 100).toFixed(1);
  return `
    <div>
      <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:2px;">
        <span style="color:${isHighlight ? '#34d399' : '#cbd5e1'}; font-weight:${isHighlight ? '700' : '500'};">${label}</span>
        <span style="font-weight:700; color:${color};">${pct}%</span>
      </div>
      <div style="background:#1e293b; height:7px; border-radius:4px; overflow:hidden;">
        <div style="background:${color}; width:${pct}%; height:100%;"></div>
      </div>
    </div>
  `;
}

async function downloadPdfReport() {
  const btn = document.getElementById("btn-download-pdf");
  if (btn) btn.innerText = "⏳ Compiling Report...";
  
  try {
    const res = await fetch("/api/report/pdf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        simulation: appState.currentSimulation,
        city: appState.city
      })
    });
    
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `IFCP_${appState.city.toUpperCase()}_SITREP_${Date.now()}.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } catch (err) {
    alert("Failed to download PDF SITREP: " + err.message);
  } finally {
    if (btn) btn.innerText = "📄 Download Official PDF SITREP";
  }
}

function jsonBody(obj) {
  return JSON.stringify(obj);
}
