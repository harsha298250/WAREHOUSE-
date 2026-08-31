/* scenario_lab.js — Scenario Lab & Algorithm Experiments Workspace */

(function () {
  let activeTab = "scenarios"; // scenarios | experiments
  let selectedExperimentId = null;
  let chartInstance = null;
  let pollInterval = null;

  async function renderScenarioLabWorkspace(el, defaultTab = "scenarios") {
    activeTab = defaultTab;
    clearInterval(pollInterval);

    el.innerHTML = `
      <div class="analytics-tabs" style="margin-bottom:20px;display:flex;gap:10px;flex-wrap:wrap;">
        <button class="btn ${activeTab === 'scenarios' ? 'btn-primary' : 'btn-secondary'}" id="tab-scenarios">📋 Manage Scenarios</button>
        <button class="btn ${activeTab === 'whatif' ? 'btn-primary' : 'btn-secondary'}" id="tab-whatif">⚡ What-If Simulator & Impact Analysis</button>
        <button class="btn ${activeTab === 'experiments' ? 'btn-primary' : 'btn-secondary'}" id="tab-experiments">🔬 Run Experiments & History</button>
        <button class="btn ${activeTab === 'packing' ? 'btn-primary' : 'btn-secondary'}" id="tab-packing">📦 Packing Station Simulator</button>
        <button class="btn ${activeTab === 'simpy' ? 'btn-primary' : 'btn-secondary'}" id="tab-simpy">🤖 SimPy Simulation Lab</button>
      </div>
      <div id="scenario-lab-body"></div>
    `;

    document.getElementById("tab-scenarios").addEventListener("click", () => {
      activeTab = "scenarios";
      renderScenarioLabWorkspace(el, "scenarios");
    });
    document.getElementById("tab-whatif").addEventListener("click", () => {
      activeTab = "whatif";
      renderScenarioLabWorkspace(el, "whatif");
    });
    document.getElementById("tab-experiments").addEventListener("click", () => {
      activeTab = "experiments";
      renderScenarioLabWorkspace(el, "experiments");
    });
    document.getElementById("tab-packing").addEventListener("click", () => {
      activeTab = "packing";
      renderScenarioLabWorkspace(el, "packing");
    });
    document.getElementById("tab-simpy").addEventListener("click", () => {
      activeTab = "simpy";
      renderScenarioLabWorkspace(el, "simpy");
    });

    const bodyEl = document.getElementById("scenario-lab-body");
    if (activeTab === "scenarios") {
      await renderScenariosTab(bodyEl);
    } else if (activeTab === "whatif") {
      await renderWhatIfTab(bodyEl);
    } else if (activeTab === "experiments") {
      await renderExperimentsTab(bodyEl);
    } else if (activeTab === "packing") {
      await renderPackingSimulatorTab(bodyEl);
    } else if (activeTab === "simpy") {
      await renderSimpySimulationLabTab(bodyEl);
    }
  }

  // ---------------------------------------------------------------------------
  // TAB 1: SCENARIOS MANAGEMENT
  // ---------------------------------------------------------------------------
  async function renderScenariosTab(el) {
    el.innerHTML = `
      <div class="grid-2" style="gap:20px;align-items:start;">
        <div>
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">Active Scenarios</div>
            </div>
            <div id="scenarios-list-container">Loading scenarios...</div>
          </div>
        </div>

        <div>
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">Create Simulation Scenario</div>
            </div>
            <form id="create-scenario-form" style="display:flex;flex-direction:column;gap:12px;">
              <div class="field">
                <label>Scenario Name *</label>
                <input type="text" id="scen-name" placeholder="e.g. Peak Surge Test" required />
              </div>
              <div class="field">
                <label>Description</label>
                <textarea id="scen-desc" placeholder="Describe the purpose of this stress test..." rows="2"></textarea>
              </div>
              <div class="field">
                <label>Scenario Type</label>
                <select id="scen-type">
                  <option value="BASELINE">BASELINE</option>
                  <option value="HIGH_DEMAND">HIGH_DEMAND</option>
                  <option value="LOW_DEMAND">LOW_DEMAND</option>
                  <option value="ROBOT_FAILURE">ROBOT_FAILURE</option>
                  <option value="CONGESTION">CONGESTION</option>
                  <option value="INVENTORY_PRESSURE">INVENTORY_PRESSURE</option>
                  <option value="CUSTOM" selected>CUSTOM</option>
                </select>
              </div>
              <div class="field">
                <label>Demand settings</label>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                  <div>
                    <label style="font-size:11px;">Order Volume (count)</label>
                    <input type="number" id="scen-vol" value="6" min="1" max="50" required />
                  </div>
                  <div>
                    <label style="font-size:11px;">Arrival Frequency (ticks)</label>
                    <input type="number" id="scen-freq" value="40" min="10" max="200" required />
                  </div>
                </div>
              </div>
              <div class="field">
                <label>Robot settings</label>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                  <div>
                    <label style="font-size:11px;">Robot Fleet Count</label>
                    <input type="number" id="scen-rob" value="4" min="1" max="10" required />
                  </div>
                  <div>
                    <label style="font-size:11px;">Robot Speed multiplier</label>
                    <input type="number" id="scen-speed" value="1.0" step="0.1" min="0.5" max="3.0" required />
                  </div>
                </div>
              </div>
              <div class="field">
                <label>Robot Failure settings</label>
                <div style="display:flex;gap:10px;align-items:center;">
                  <input type="checkbox" id="scen-fail-enabled" />
                  <label for="scen-fail-enabled" style="font-size:12px;margin:0;">Inject simulated failure at tick</label>
                  <input type="number" id="scen-fail-tick" value="120" min="10" style="width:70px;" />
                </div>
              </div>
              <div class="field">
                <label>Base Random Seed</label>
                <input type="number" id="scen-seed" value="42" required />
              </div>
              <button type="submit" class="btn btn-primary btn-block">💾 Create Scenario</button>
            </form>
          </div>
        </div>
      </div>
    `;

    // Load scenarios list
    const container = document.getElementById("scenarios-list-container");
    const loadList = async () => {
      try {
        const wh = window.currentWarehouse || "WH-BLR-01";
        const list = await Api.getScenarios(wh);
        if (!list || list.length === 0) {
          container.innerHTML = `<div class="empty-state">No scenarios created yet.</div>`;
          return;
        }

        container.innerHTML = `
          <div style="display:flex;flex-direction:column;gap:10px;">
            ${list.map(s => `
              <div class="panel" style="margin:0;padding:12px;">
                <div style="display:flex;justify-content:space-between;align-items:start;">
                  <div>
                    <strong>${esc(s.name)}</strong>
                    <span class="badge badge-neutral">${s.scenario_type}</span>
                  </div>
                  <div style="display:flex;gap:6px;">
                    <button class="btn btn-secondary btn-xs btn-duplicate" data-id="${s.id}">Copy</button>
                    <button class="btn btn-danger btn-xs btn-delete" data-id="${s.id}">Delete</button>
                  </div>
                </div>
                <p style="font-size:12px;color:var(--text-muted);margin:8px 0 0 0;">${esc(s.description || "No description provided.")}</p>
                <div style="font-size:11px;color:var(--text-faint);margin-top:6px;">
                  Orders: ${s.configuration.demand.order_volume} | Robots: ${s.configuration.robots.robot_count} | Seed: ${s.random_seed}
                </div>
              </div>
            `).join('')}
          </div>
        `;

        // Add actions
        container.querySelectorAll(".btn-duplicate").forEach(btn => {
          btn.addEventListener("click", async () => {
            if (btn.disabled) return;
            btn.disabled = true;
            const originalText = btn.innerHTML;
            btn.innerHTML = "...";
            try {
              const id = btn.getAttribute("data-id");
              await Api.duplicateScenario(id);
              loadList();
            } catch (err) {
              alert("Error copying scenario: " + err.message);
            } finally {
              btn.disabled = false;
              btn.innerHTML = originalText;
            }
          });
        });

        container.querySelectorAll(".btn-delete").forEach(btn => {
          btn.addEventListener("click", async () => {
            if (btn.disabled) return;
            const id = btn.getAttribute("data-id");
            if (confirm("Are you sure you want to archive this scenario?")) {
              btn.disabled = true;
              const originalText = btn.innerHTML;
              btn.innerHTML = "...";
              try {
                await Api.deleteScenario(id);
                loadList();
              } catch (err) {
                alert("Error archiving scenario: " + err.message);
              } finally {
                btn.disabled = false;
                btn.innerHTML = originalText;
              }
            }
          });
        });

      } catch (err) {
        container.innerHTML = `<div class="login-error">${esc(err.message)}</div>`;
      }
    };
    loadList();

    // Form submit
    document.getElementById("create-scenario-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = e.target.querySelector("button[type='submit']");
      if (btn.disabled) return;
      
      const name = document.getElementById("scen-name").value;
      const desc = document.getElementById("scen-desc").value;
      const type = document.getElementById("scen-type").value;
      const seed = parseInt(document.getElementById("scen-seed").value);
      const vol = parseInt(document.getElementById("scen-vol").value);
      const freq = parseInt(document.getElementById("scen-freq").value);
      const rob = parseInt(document.getElementById("scen-rob").value);
      const speed = parseFloat(document.getElementById("scen-speed").value);
      const failEnabled = document.getElementById("scen-fail-enabled").checked;
      const failTick = parseInt(document.getElementById("scen-fail-tick").value);

      const configuration = {
        demand: { order_volume: vol, order_arrival_rate: freq },
        robots: { robot_count: rob, initial_battery_pct: 100.0, robot_speed: speed },
        failures: { enabled: failEnabled, failure_tick: failTick },
        simulation: { duration_ticks: 500 },
        inventory: { initial_stock_units: 100, reorder_threshold_units: 20 },
        warehouse: { blocked_cells: [] }
      };

      const originalText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = "💾 Saving Scenario...";

      try {
        await Api.createScenario({
          name,
          description: desc,
          warehouse_id: window.currentWarehouse || "WH-BLR-01",
          scenario_type: type,
          random_seed: seed,
          configuration
        });
        document.getElementById("create-scenario-form").reset();
        loadList();
      } catch (err) {
        alert("Error creating scenario: " + err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    });
  }

  // ---------------------------------------------------------------------------
  // TAB 2: EXPERIMENT RUNNER & HISTORY
  // ---------------------------------------------------------------------------
  async function renderExperimentsTab(el) {
    el.innerHTML = `
      <div class="grid-2" style="gap:20px;align-items:start;">
        <div>
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">Run Simulation Experiment</div>
            </div>
            <form id="run-experiment-form" style="display:flex;flex-direction:column;gap:12px;">
              <div class="field">
                <label>Target Scenario *</label>
                <select id="exp-scen-select" required><option>Loading scenarios...</option></select>
              </div>
              <div class="field">
                <label>Experiment Title *</label>
                <input type="text" id="exp-title" placeholder="e.g. OR-Tools Comparison Run" required />
              </div>
              <div class="field">
                <label>Strategy / Algorithm *</label>
                <select id="exp-strategy">
                  <option value="CURRENT_HEURISTIC">Greedy Manhattan Heuristic Assignment</option>
                  <option value="OR_TOOLS_ASSIGNMENT">Google OR-Tools Balanced Assignment</option>
                  <option value="A_STAR_BASELINE">A* Baseline Routing (Unaware)</option>
                  <option value="A_STAR_CONGESTION_AWARE">A* Congestion-Aware Routing (Default)</option>
                </select>
              </div>
              <div class="field">
                <label>Repetitions * (1 to 10)</label>
                <input type="number" id="exp-rep" value="3" min="1" max="10" required />
              </div>
              <button type="submit" class="btn btn-primary btn-block">🚀 Queue & Execute Experiment</button>
            </form>
          </div>

          <div class="panel" style="margin-top:20px;">
            <div class="panel-header">
              <div class="panel-title">Execution History</div>
            </div>
            <div id="experiments-list-container">Loading runs...</div>
          </div>
        </div>

        <div>
          <div class="panel" id="experiment-details-panel">
            <div class="empty-state">Select an experiment run from history to view aggregate KPI statistics and comparisons.</div>
          </div>
        </div>
      </div>
    `;

    // Populate scenario selector
    const select = document.getElementById("exp-scen-select");
    try {
      const wh = window.currentWarehouse || "WH-BLR-01";
      const scens = await Api.getScenarios(wh);
      select.innerHTML = scens.map(s => `<option value="${s.id}">${esc(s.name)} [${s.scenario_type}]</option>`).join('');
    } catch (e) {
      select.innerHTML = `<option>Error loading scenarios</option>`;
    }

    // Load experiments history
    const expContainer = document.getElementById("experiments-list-container");
    const loadExpList = async () => {
      try {
        const list = await Api.getExperiments();
        if (!list || list.length === 0) {
          expContainer.innerHTML = `<div class="empty-state">No experiments executed yet.</div>`;
          return;
        }

        expContainer.innerHTML = `
          <div style="display:flex;flex-direction:column;gap:10px;max-height:400px;overflow-y:auto;">
            ${list.map(e => `
              <div class="panel btn-select-exp" data-id="${e.id}" style="margin:0;padding:12px;cursor:pointer;border-left:4px solid ${
                e.status === 'COMPLETED' ? 'var(--success)' : e.status === 'FAILED' ? 'var(--danger)' : 'var(--warning)'
              };">
                <div style="display:flex;justify-content:space-between;">
                  <strong>${esc(e.experiment_name)}</strong>
                  <span class="badge ${
                    e.status === 'COMPLETED' ? 'badge-success' : e.status === 'FAILED' ? 'badge-danger' : 'badge-neutral'
                  }">${e.status}</span>
                </div>
                <div style="font-size:11px;color:var(--text-muted);margin-top:6px;">
                  Strategy: ${e.algorithm_name} | Reps: ${e.repetitions} | Seed: ${e.random_seed}
                </div>
              </div>
            `).join('')}
          </div>
        `;

        // Click handler to select
        expContainer.querySelectorAll(".btn-select-exp").forEach(panel => {
          panel.addEventListener("click", () => {
            const id = panel.getAttribute("data-id");
            selectedExperimentId = id;
            loadExperimentDetails(id);
          });
        });
      } catch (err) {
        expContainer.innerHTML = `<div class="login-error">${esc(err.message)}</div>`;
      }
    };
    loadExpList();

    // Poll running status
    pollInterval = setInterval(() => {
      loadExpList();
      if (selectedExperimentId) {
        loadExperimentDetails(selectedExperimentId);
      }
    }, 5000);

    // Form submit
    document.getElementById("run-experiment-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const btn = e.target.querySelector("button[type='submit']");
      if (btn.disabled) return;

      const scenId = parseInt(document.getElementById("exp-scen-select").value);
      const title = document.getElementById("exp-title").value;
      const strategy = document.getElementById("exp-strategy").value;
      const repetitions = parseInt(document.getElementById("exp-rep").value);

      const originalText = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = "🚀 Queueing Experiment...";

      try {
        const exp = await Api.createExperiment({
          scenario_id: scenId,
          experiment_name: title,
          algorithm_name: strategy,
          repetitions
        });
        selectedExperimentId = exp.id;
        loadExpList();
        loadExperimentDetails(exp.id);
      } catch (err) {
        alert("Error launching experiment: " + err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
      }
    });
  }

  // ---------------------------------------------------------------------------
  // DETAILS PAGE & CHARTING RENDERS
  // ---------------------------------------------------------------------------
  async function loadExperimentDetails(id) {
    const panel = document.getElementById("experiment-details-panel");
    if (!panel) return;

    try {
      const data = await Api.getExperiment(id);
      const exp = data.experiment;
      const runs = data.runs;

      let html = `
        <div class="panel-header" style="justify-content:space-between;align-items:start;">
          <div>
            <div class="panel-title">${esc(exp.experiment_name)}</div>
            <div class="panel-desc">Algorithm: ${exp.algorithm_name} | Seed: ${exp.random_seed}</div>
          </div>
          <div style="display:flex;gap:6px;">
            <button class="btn btn-secondary btn-xs" id="btn-rerun">Re-run</button>
            <button class="btn btn-secondary btn-xs" id="btn-export-csv">Export CSV</button>
            <button class="btn btn-secondary btn-xs" id="btn-export-json">Export JSON</button>
          </div>
        </div>

        <div class="kpi-grid cols-3" style="margin-top:14px;margin-bottom:16px;">
          <div class="kpi-card">
            <div class="kpi-label">Status</div>
            <div class="kpi-value ${exp.status === 'COMPLETED' ? 'good' : exp.status === 'FAILED' ? 'danger' : 'warn'}">${exp.status}</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Repetitions</div>
            <div class="kpi-value">${exp.repetitions} runs</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-label">Runtime</div>
            <div class="kpi-value">${exp.duration_seconds ? exp.duration_seconds.toFixed(1) + 's' : '—'}</div>
          </div>
        </div>
      `;

      if (exp.status === "FAILED") {
        html += `<div class="login-error" style="margin-bottom:12px;"><strong>Error:</strong> ${esc(exp.error_message)}</div>`;
      }

      if (exp.status === "COMPLETED" && exp.metrics_summary) {
        const s = exp.metrics_summary;
        html += `
          <div style="font-size:12px;font-weight:800;color:var(--text-muted);margin-bottom:8px;text-transform:uppercase;">Repetition Aggregated KPIs</div>
          <table class="data-table" style="margin-bottom:20px;">
            <thead>
              <tr>
                <th>Operational Metric</th>
                <th class="text-right">Mean</th>
                <th class="text-right">Median</th>
                <th class="text-right">Min</th>
                <th class="text-right">Max</th>
                <th class="text-right">StdDev</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>📦 Completed Orders</td>
                <td class="text-right mono">${s.orders_completed.mean}</td>
                <td class="text-right mono">${s.orders_completed.median}</td>
                <td class="text-right mono">${s.orders_completed.min}</td>
                <td class="text-right mono">${s.orders_completed.max}</td>
                <td class="text-right mono">${s.orders_completed.stddev}</td>
              </tr>
              <tr>
                <td>📈 Completion Rate (%)</td>
                <td class="text-right mono">${s.order_completion_rate.mean}%</td>
                <td class="text-right mono">${s.order_completion_rate.median}%</td>
                <td class="text-right mono">${s.order_completion_rate.min}%</td>
                <td class="text-right mono">${s.order_completion_rate.max}%</td>
                <td class="text-right mono">${s.order_completion_rate.stddev}%</td>
              </tr>
              <tr>
                <td>⏱ avg Cycle Time (h)</td>
                <td class="text-right mono">${s.avg_cycle_time_hours.mean}</td>
                <td class="text-right mono">${s.avg_cycle_time_hours.median}</td>
                <td class="text-right mono">${s.avg_cycle_time_hours.min}</td>
                <td class="text-right mono">${s.avg_cycle_time_hours.max}</td>
                <td class="text-right mono">${s.avg_cycle_time_hours.stddev}</td>
              </tr>
              <tr>
                <td>⚡ avg Robot Utilization (%)</td>
                <td class="text-right mono">${s.avg_robot_utilization.mean}%</td>
                <td class="text-right mono">${s.avg_robot_utilization.median}%</td>
                <td class="text-right mono">${s.avg_robot_utilization.min}%</td>
                <td class="text-right mono">${s.avg_robot_utilization.max}%</td>
                <td class="text-right mono">${s.avg_robot_utilization.stddev}%</td>
              </tr>
            </tbody>
          </table>

          <div class="chart-wrapper" style="height:220px;margin-bottom:20px;">
            <canvas id="experiment-runs-chart"></canvas>
          </div>

          <div class="callout callout-warning" style="margin-top:14px;padding:12px;border-left:4px solid var(--warning);background:var(--surface-2);font-size:11.5px;color:var(--text-muted);border-radius:4px;">
            <strong>⚠️ Simulated Outcome limits:</strong> These results are simulation-based and depend on the configured scenario, assumptions, algorithms, random seed, and model behavior. They should not be interpreted as proof of real-world operational performance.
          </div>
        `;
      } else if (exp.status === "RUNNING" || exp.status === "QUEUED") {
        html += `
          <div style="text-align:center;padding:40px;">
            <div class="spinner"></div><br/>
            <strong>Running isolated simulation repetitions...</strong>
            <div style="font-size:12px;color:var(--text-faint);margin-top:6px;">Seed configurations: ${exp.random_seed}</div>
          </div>
        `;
      }

      panel.innerHTML = html;

      // Event handlers
      document.getElementById("btn-rerun")?.addEventListener("click", async () => {
        const btn = document.getElementById("btn-rerun");
        if (btn.disabled) return;
        btn.disabled = true;
        const originalText = btn.innerHTML;
        btn.innerHTML = "...";
        try {
          const re = await Api.rerunExperiment(id);
          selectedExperimentId = re.id;
          loadExperimentDetails(re.id);
        } catch (err) {
          alert("Error rerunning experiment: " + err.message);
        } finally {
          btn.disabled = false;
          btn.innerHTML = originalText;
        }
      });

      document.getElementById("btn-export-csv")?.addEventListener("click", () => {
        window.open(`/scenarios/experiments/${id}/export?format=csv&token=${localStorage.getItem("token") || ""}`, "_blank");
      });

      document.getElementById("btn-export-json")?.addEventListener("click", () => {
        window.open(`/scenarios/experiments/${id}/export?format=json&token=${localStorage.getItem("token") || ""}`, "_blank");
      });

      // Chart.js render
      if (exp.status === "COMPLETED" && exp.metrics_summary && runs.length > 0) {
        const isDark = document.body.classList.contains("dark-mode");
        const textColor = isDark ? "#cbd5e1" : "#6b7290";
        const gridColor = isDark ? "#374151" : "#f0f1f6";

        if (chartInstance) {
          chartInstance.destroy();
        }

        const ctx = document.getElementById("experiment-runs-chart");
        if (ctx) {
          chartInstance = new Chart(ctx, {
            type: "line",
            data: {
              labels: runs.map(r => `Run ${r.repetition_number}`),
              datasets: [
                {
                  label: "Completion Rate (%)",
                  data: runs.map(r => r.metrics ? r.metrics.order_completion_rate : null),
                  borderColor: "#10b981",
                  tension: 0.2,
                  fill: false
                },
                {
                  label: "Robot Fleet Utilization (%)",
                  data: runs.map(r => r.metrics ? r.metrics.avg_robot_utilization : null),
                  borderColor: "#8b5cf6",
                  tension: 0.2,
                  fill: false
                }
              ]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: { labels: { color: textColor } }
              },
              scales: {
                x: { ticks: { color: textColor }, grid: { display: false } },
                y: { ticks: { color: textColor }, grid: { color: gridColor } }
              }
            }
          });
        }
      }

    } catch (err) {
      panel.innerHTML = `<div class="login-error">${esc(err.message)}</div>`;
    }
  }

  // ---------------------------------------------------------------------------
  // TAB 3: PACKING STATION SIMULATOR (SimPy Discrete-Event)
  // ---------------------------------------------------------------------------
  async function renderPackingSimulatorTab(el) {
    el.innerHTML = `
      <div class="grid-2" style="gap:20px;align-items:start;">
        <div>
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">🏭 SimPy Packing Station Configuration</div>
            </div>
            <p style="font-size:12px;color:var(--text-muted);margin-bottom:14px;">
              Discrete-event queueing simulation modeling operator resource contention at packing stations.
              Orders arrive at random intervals and wait in a queue for an available operator.
            </p>
            <form id="packing-sim-form" style="display:flex;flex-direction:column;gap:12px;">
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                <div class="field">
                  <label>Number of Operators</label>
                  <input type="number" id="ps-operators" value="3" min="1" max="20" required />
                </div>
                <div class="field">
                  <label>Mean Packing Time (min)</label>
                  <input type="number" id="ps-pack-time" value="12.0" step="0.5" min="0.5" required />
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                <div class="field">
                  <label>Shift Duration (min)</label>
                  <input type="number" id="ps-duration" value="480" min="10" max="10000" required />
                </div>
                <div class="field">
                  <label>Mean Arrival Interval (min)</label>
                  <input type="number" id="ps-arrival" value="5.0" step="0.5" min="0.5" required />
                </div>
              </div>
              <div class="field">
                <label>Random Seed (optional, for reproducibility)</label>
                <input type="number" id="ps-seed" placeholder="e.g. 42" />
              </div>
              <button type="submit" class="btn btn-primary btn-block">🚀 Run Packing Simulation</button>
            </form>
          </div>
        </div>

        <div>
          <div class="panel" id="packing-results-panel">
            <div class="empty-state">Configure simulation parameters and click "Run" to see queueing metrics and operator utilization results.</div>
          </div>
        </div>
      </div>
    `;

    document.getElementById("packing-sim-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const resultsPanel = document.getElementById("packing-results-panel");
      resultsPanel.innerHTML = `<div style="text-align:center;padding:40px;"><div class="spinner"></div><br/><strong>Running SimPy simulation...</strong></div>`;

      const seedVal = document.getElementById("ps-seed").value;

      try {
        const result = await Api.runPackingSimulation({
          num_operators: parseInt(document.getElementById("ps-operators").value),
          mean_packing_time: parseFloat(document.getElementById("ps-pack-time").value),
          duration: parseFloat(document.getElementById("ps-duration").value),
          mean_arrival_interval: parseFloat(document.getElementById("ps-arrival").value),
          random_seed: seedVal ? parseInt(seedVal) : null
        });

        const isMock = result.status === "mock";
        resultsPanel.innerHTML = `
          <div class="panel-header">
            <div class="panel-title">Simulation Results</div>
            ${isMock ? '<span class="badge badge-neutral">MOCK MODE</span>' : '<span class="badge badge-success">SimPy Engine</span>'}
          </div>

          <div class="kpi-grid cols-3" style="margin-top:14px;margin-bottom:16px;">
            <div class="kpi-card">
              <div class="kpi-label">📦 Orders Processed</div>
              <div class="kpi-value good">${result.orders_processed}</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">⏱ Avg Queue Wait</div>
              <div class="kpi-value ${result.average_queue_wait_minutes > 15 ? 'danger' : 'good'}">${result.average_queue_wait_minutes} min</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">📋 Avg Packing Time</div>
              <div class="kpi-value">${result.average_packing_time_minutes} min</div>
            </div>
          </div>

          <div class="kpi-grid cols-3" style="margin-bottom:16px;">
            <div class="kpi-card">
              <div class="kpi-label">⚡ Operator Utilization</div>
              <div class="kpi-value ${result.operator_utilization_pct > 90 ? 'danger' : result.operator_utilization_pct > 70 ? 'warn' : 'good'}">${result.operator_utilization_pct}%</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">🚧 Max Queue Depth</div>
              <div class="kpi-value ${result.max_queue_bottleneck > 5 ? 'danger' : 'good'}">${result.max_queue_bottleneck}</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">👷 Operators</div>
              <div class="kpi-value">${result.operators_count}</div>
            </div>
          </div>

          <div style="font-size:12px;color:var(--text-muted);margin-top:10px;">
            Duration: ${result.experiment_duration_minutes} min
            ${result.random_seed != null ? '| Seed: ' + result.random_seed : '| Seed: random'}
          </div>

          <div class="callout callout-warning" style="margin-top:14px;padding:12px;border-left:4px solid var(--warning);background:var(--surface-2);font-size:11.5px;color:var(--text-muted);border-radius:4px;">
            <strong>⚠️ Queueing Theory Model:</strong> Orders arrive as a Poisson process, packing times follow an exponential distribution (M/M/c queueing model). Results reflect steady-state behavior over the configured shift duration.
          </div>
        `;
      } catch (err) {
        resultsPanel.innerHTML = `<div class="login-error">${esc(err.message)}</div>`;
      }
    });
  }

  // ---------------------------------------------------------------------------
  // TAB 4: SIMPY SIMULATION LAB (Discrete-Event Robot Operations)
  // ---------------------------------------------------------------------------
  async function renderSimpySimulationLabTab(el) {
    el.innerHTML = `
      <div class="grid-2" style="gap:20px;align-items:start;">
        <div>
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">🤖 SimPy Robot & WMS Operations Simulation</div>
            </div>
            <p style="font-size:12px;color:var(--text-muted);margin-bottom:14px;">
              Discrete-event robot pathing, scheduling, collision avoidance, and battery/charging simulation.
              Runs entirely in-memory using database snapshots without modifying operational state.
            </p>
            <form id="simpy-lab-form" style="display:flex;flex-direction:column;gap:12px;">
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                <div class="field">
                  <label>Warehouse ID</label>
                  <select id="simpy-wh" required>
                    <option value="WH-BLR-01">WH-BLR-01 (Bengaluru)</option>
                    <option value="WH-DEL-01">WH-DEL-01 (Delhi)</option>
                    <option value="WH-CCU-01">WH-CCU-01 (Kolkata)</option>
                  </select>
                </div>
                <div class="field">
                  <label>Simulation Mode</label>
                  <select id="simpy-mode" required>
                    <option value="OFFLINE_SNAPSHOT" selected>OFFLINE_SNAPSHOT (Live Snapshot)</option>
                    <option value="HISTORICAL_REPLAY">HISTORICAL_REPLAY (Real Orders Replay)</option>
                    <option value="EXPERIMENT">EXPERIMENT (Parametric Config)</option>
                  </select>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                <div class="field">
                  <label>Simulation Duration (min)</label>
                  <input type="number" id="simpy-duration" value="480" min="10" max="2880" required />
                </div>
                <div class="field">
                  <label>Robot Fleet Size</label>
                  <input type="number" id="simpy-robots" value="3" min="1" max="10" required />
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                <div class="field">
                  <label>Random Seed</label>
                  <input type="number" id="simpy-seed" value="42" required />
                </div>
                <div class="field">
                  <label>Robot Speed Factor</label>
                  <input type="number" id="simpy-speed" value="1.0" step="0.1" min="0.5" max="3.0" required />
                </div>
              </div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                <div class="field">
                  <label>Mean Arrival Interval (min)</label>
                  <input type="number" id="simpy-arrival" value="15.0" step="0.5" min="1.0" required />
                </div>
                <div class="field">
                  <label>Picking Duration (min)</label>
                  <input type="number" id="simpy-picking" value="3.0" step="0.5" min="0.5" required />
                </div>
              </div>
              <button type="submit" class="btn btn-primary btn-block">⚡ Execute SimPy Simulation Run</button>
            </form>
          </div>

          <!-- COMPARISON PANEL -->
          <div class="panel" style="margin-top:20px;" id="simpy-comparison-panel">
            <div class="panel-header"><div class="panel-title">📊 Compare Simulation Runs</div></div>
            <div style="display:flex;gap:10px;margin-bottom:12px;">
              <select id="compare-run-a" style="flex:1;"><option value="">Select Run A</option></select>
              <select id="compare-run-b" style="flex:1;"><option value="">Select Run B</option></select>
            </div>
            <button id="btn-compare-runs" class="btn btn-secondary btn-block">Compare Selected Runs</button>
            <div id="comparison-results" style="margin-top:12px;"></div>
          </div>
        </div>

        <div>
          <div class="panel" id="simpy-results-panel">
            <div class="empty-state">Trigger a simulation run or select a run from WMS logs history below to review performance KPIs.</div>
          </div>

          <div class="panel" style="margin-top:20px;">
            <div class="panel-header">
              <div class="panel-title">📋 Simulation Execution History Logs</div>
            </div>
            <div style="overflow-x:auto;">
              <table class="table" style="width:100%;font-size:12px;">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Mode</th>
                    <th>Duration</th>
                    <th>Seed</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody id="simpy-history-tbody">
                  <tr><td colspan="7" style="text-align:center;">Loading history logs...</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    `;

    // Load History list initially
    await loadSimpyHistory();

    // Bind Form submit
    document.getElementById("simpy-lab-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const runBtn = e.target.querySelector("button[type='submit']");
      runBtn.disabled = true;
      runBtn.innerText = "Queuing Simulation Run...";

      try {
        const payload = {
          warehouse_id: document.getElementById("simpy-wh").value,
          mode: document.getElementById("simpy-mode").value,
          duration: parseFloat(document.getElementById("simpy-duration").value),
          random_seed: parseInt(document.getElementById("simpy-seed").value),
          name: `SimPy Run (${document.getElementById("simpy-mode").value})`,
          configuration: {
            robots: {
              robot_count: parseInt(document.getElementById("simpy-robots").value),
              robot_speed: parseFloat(document.getElementById("simpy-speed").value),
              initial_battery_pct: 100.0
            },
            demand: {
              order_arrival_rate: parseFloat(document.getElementById("simpy-arrival").value)
            },
            simulation: {
              picking_duration: parseFloat(document.getElementById("simpy-picking").value)
            }
          }
        };

        const run = await Api.createSimulationRun(payload);
        Notifications.success(`Simulation ${run.id} queued successfully.`);
        
        // Start polling for results
        pollSimulationStatus(run.id);

      } catch (err) {
        Notifications.error(`Failed to launch simulation: ${err.message}`);
      } finally {
        runBtn.disabled = false;
        runBtn.innerText = "⚡ Execute SimPy Simulation Run";
        await loadSimpyHistory();
      }
    });

    // Bind comparison trigger
    document.getElementById("btn-compare-runs").addEventListener("click", async () => {
      const runAId = document.getElementById("compare-run-a").value;
      const runBId = document.getElementById("compare-run-b").value;
      if (!runAId || !runBId) {
        Notifications.error("Please select two simulation runs to compare.");
        return;
      }
      
      const compDiv = document.getElementById("comparison-results");
      compDiv.innerHTML = '<div style="text-align:center;padding:10px;"><div class="spinner"></div></div>';

      try {
        const comp = await Api.compareSimulationRuns(runAId, { compare_with_id: parseInt(runBId) });
        let html = `
          <div style="font-size:11.5px;border-top:1px solid var(--border);padding-top:10px;">
            <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;font-weight:bold;margin-bottom:6px;color:var(--text-muted);">
              <div>Metric</div>
              <div>Run A (#${comp.run_a.id})</div>
              <div>Run B (#${comp.run_b.id})</div>
              <div>Diff %</div>
            </div>
        `;
        
        for (const [metric, data] of Object.entries(comp.comparison)) {
          const valA = data.run_a_value !== null ? data.run_a_value : "-";
          const valB = data.run_b_value !== null ? data.run_b_value : "-";
          const pct = data.percent_difference !== null ? `${data.percent_difference > 0 ? '+' : ''}${data.percent_difference}%` : "-";
          const diffClass = data.percent_difference > 0 ? "warn" : "good";

          html += `
            <div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;padding:4px 0;border-bottom:1px dashed var(--surface-3);">
              <div style="color:var(--text-normal);">${metric}</div>
              <div>${valA}</div>
              <div>${valB}</div>
              <div class="${diffClass}">${pct}</div>
            </div>
          `;
        }
        html += "</div>";
        compDiv.innerHTML = html;
      } catch (err) {
        compDiv.innerHTML = `<div class="login-error">${esc(err.message)}</div>`;
      }
    });

    async function loadSimpyHistory() {
      try {
        const wh = document.getElementById("simpy-wh").value;
        const runs = await Api.getSimulationRuns(wh);
        const tbody = document.getElementById("simpy-history-tbody");
        
        // Populate Comparison selects
        const compA = document.getElementById("compare-run-a");
        const compB = document.getElementById("compare-run-b");
        const valA = compA.value;
        const valB = compB.value;

        let compOptions = '<option value="">Select Run</option>';
        
        if (!runs.length) {
          tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-muted);">No simulation run logs recorded yet.</td></tr>`;
          return;
        }

        let html = "";
        runs.forEach(r => {
          compOptions += `<option value="${r.id}">Run #${r.id} - ${r.mode} (${r.status})</option>`;
          const badgeClass = r.status === "COMPLETED" ? "badge-success" : (r.status === "FAILED" ? "badge-danger" : "badge-neutral");
          html += `
            <tr>
              <td>#${r.id}</td>
              <td>${esc(r.name)}</td>
              <td><span class="badge badge-neutral">${r.mode}</span></td>
              <td>${r.simulation_duration} min</td>
              <td>${r.random_seed}</td>
              <td><span class="badge ${badgeClass}">${r.status}</span></td>
              <td>
                <button class="btn btn-secondary btn-xs btn-view-run" data-id="${r.id}">View</button>
                ${r.created_by === "admin" || true ? `<button class="btn btn-secondary btn-xs btn-del-run danger" data-id="${r.id}" style="margin-left:4px;">Del</button>` : ""}
              </td>
            </tr>
          `;
        });
        
        tbody.innerHTML = html;
        compA.innerHTML = compOptions;
        compB.innerHTML = compOptions;
        compA.value = valA;
        compB.value = valB;

        // Bind View buttons
        tbody.querySelectorAll(".btn-view-run").forEach(btn => {
          btn.addEventListener("click", () => renderSimulationResults(btn.dataset.id));
        });

        // Bind Delete buttons
        tbody.querySelectorAll(".btn-del-run").forEach(btn => {
          btn.addEventListener("click", async () => {
            if (confirm("Are you sure you want to delete this simulation run history log?")) {
              try {
                await Api.deleteSimulationRun(btn.dataset.id);
                Notifications.success("Run deleted successfully.");
                await loadSimpyHistory();
              } catch (err) {
                Notifications.error(`Failed to delete: ${err.message}`);
              }
            }
          });
        });

      } catch (err) {
        logger.error("Failed to load SimPy runs history list: %s", err.message);
      }
    }

    function pollSimulationStatus(runId) {
      const resultsPanel = document.getElementById("simpy-results-panel");
      resultsPanel.innerHTML = `
        <div style="text-align:center;padding:40px;">
          <div class="spinner"></div><br/>
          <strong>SimPy Environment processing WMS WAREHOUSE Snapshot...</strong><br/>
          <span style="font-size:11px;color:var(--text-muted);">Running path planning & conflict schedules in background.</span>
        </div>
      `;

      let counter = 0;
      const interval = setInterval(async () => {
        counter++;
        try {
          const run = await Api.getSimulationRun(runId);
          if (run.status === "COMPLETED") {
            clearInterval(interval);
            Notifications.success("SimPy warehouse simulation completed.");
            await renderSimulationResults(runId);
            await loadSimpyHistory();
          } else if (run.status === "FAILED") {
            clearInterval(interval);
            resultsPanel.innerHTML = `
              <div class="panel-header"><div class="panel-title danger">Simulation Execution Failed</div></div>
              <p style="color:var(--danger);font-size:13px;margin-top:10px;">${esc(run.error_message || "Unknown error occurred during simulation engine ticks.")}</p>
            `;
            await loadSimpyHistory();
          } else if (counter > 30) {
            // timeout after 60 seconds
            clearInterval(interval);
            resultsPanel.innerHTML = `<div class="empty-state">Simulation execution timed out. Check server background worker task logs.</div>`;
          }
        } catch (err) {
          clearInterval(interval);
          resultsPanel.innerHTML = `<div class="login-error">${esc(err.message)}</div>`;
        }
      }, 2000);
    }

    async function renderSimulationResults(runId) {
      const panel = document.getElementById("simpy-results-panel");
      panel.innerHTML = `<div style="text-align:center;padding:30px;"><div class="spinner"></div></div>`;

      try {
        const resultsData = await Api.getSimulationResults(runId);
        const runData = await Api.getSimulationRun(runId);
        
        let kpis = {};
        resultsData.results.forEach(r => {
          kpis[r.metric] = r.value;
        });

        panel.innerHTML = `
          <div class="panel-header" style="justify-content:space-between;display:flex;align-items:center;">
            <div class="panel-title">📊 SimPy Execution Results (Run #${runId})</div>
            <span class="badge badge-success">Time-Driven SimPy</span>
          </div>

          <div class="kpi-grid cols-3" style="margin-top:14px;margin-bottom:16px;">
            <div class="kpi-card">
              <div class="kpi-label">📦 Throughput / Hour</div>
              <div class="kpi-value good">${kpis["throughput_orders_per_hour"] || 0} ord</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">⏱ Fulfillment Rate</div>
              <div class="kpi-value good">${kpis["fulfillment_rate_pct"] || 0}%</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">⚡ Fleet Utilization</div>
              <div class="kpi-value">${kpis["average_robot_utilization_pct"] || 0}%</div>
            </div>
          </div>

          <div class="kpi-grid cols-3" style="margin-bottom:16px;">
            <div class="kpi-card">
              <div class="kpi-label">🚧 Collision Conflicts</div>
              <div class="kpi-value ${kpis["collision_conflicts"] > 5 ? 'danger' : 'good'}">${kpis["collision_conflicts"] || 0}</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">🚦 Replan events</div>
              <div class="kpi-value warn">${kpis["replanning_events"] || 0}</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">⚓ Corridor Deadlocks</div>
              <div class="kpi-value ${kpis["deadlocks_detected"] > 0 ? 'danger' : 'good'}">${kpis["deadlocks_detected"] || 0}</div>
            </div>
          </div>

          <div class="kpi-grid cols-3" style="margin-bottom:16px;">
            <div class="kpi-card">
              <div class="kpi-label">🔌 Charging Sessions</div>
              <div class="kpi-value">${kpis["charging_sessions_count"] || 0}</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">⏱ Avg Charger Queue Wait</div>
              <div class="kpi-value">${kpis["average_charging_queue_wait_minutes"] || 0} min</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-label">🏁 Total Distance</div>
              <div class="kpi-value">${kpis["total_distance_traveled"] || 0} units</div>
            </div>
          </div>

          <div style="font-size:11.5px;color:var(--text-muted);border-top:1px solid var(--border);padding-top:10px;">
            <strong>Simulation Metadata:</strong><br/>
            - Mode: ${runData.mode} | Seed: ${runData.random_seed} | Duration: ${runData.simulation_duration} min<br/>
            - Provenance: Map: WMS layout cells (REAL), Scheduler: CP-SAT optimization (REAL)<br/>
            - Execution Time: ${kpis["wall_clock_execution_seconds"] || 0} sec (Zero delays model)
          </div>
        `;
      } catch (err) {
        panel.innerHTML = `<div class="login-error">${esc(err.message)}</div>`;
      }
    }
  }

  // ---------------------------------------------------------------------------
  // TAB: WHAT-IF SIMULATION & IMPACT ANALYSIS
  // ---------------------------------------------------------------------------
  async function renderWhatIfTab(el) {
    el.innerHTML = `
      <div class="grid-2" style="gap:20px;align-items:start;">
        <div>
          <div class="panel">
            <div class="panel-header">
              <div class="panel-title">⚡ What-If Scenario Configuration</div>
              <div class="panel-desc">Simulate hypothetical warehouse conditions safely in-memory without mutating production data.</div>
            </div>
            <form id="whatif-form" style="display:flex;flex-direction:column;gap:12px;">
              <div class="field">
                <label>Scenario Type *</label>
                <select id="whatif-scenario-type">
                  <option value="ROBOT_UNAVAILABLE" selected>🤖 Robot Unavailability ("What if N robots fail?")</option>
                  <option value="DEMAND_INCREASE">📈 Order Demand Surge ("What if demand increases by X%?")</option>
                  <option value="AISLE_BLOCKAGE">🚧 Aisle / Route Blockage ("What if an aisle is blocked?")</option>
                  <option value="REPLENISHMENT_DELAY">🚚 Replenishment Delay ("What if supplier is delayed?")</option>
                  <option value="TASK_LOAD_INCREASE">📋 Increased Task Load ("What if task volume spikes?")</option>
                </select>
              </div>

              <!-- Scenario Parameter Inputs -->
              <div id="whatif-params-container" class="panel" style="padding:12px;margin:0;background:var(--bg-subtle);">
                <!-- Dynamic Controls inserted by JS -->
              </div>

              <button type="submit" class="btn btn-primary btn-block">🚀 Run What-If Impact Simulation</button>
            </form>
          </div>
        </div>

        <div>
          <div class="panel" id="whatif-results-panel">
            <div class="panel-header">
              <div class="panel-title">📊 Scenario Impact & Baseline Comparison</div>
            </div>
            <div class="empty-state">Select a scenario type and run simulation to view impact analysis results.</div>
          </div>
        </div>
      </div>
    `;

    const typeSelect = document.getElementById("whatif-scenario-type");
    const paramsContainer = document.getElementById("whatif-params-container");

    const updateParamsForm = () => {
      const type = typeSelect.value;
      if (type === "ROBOT_UNAVAILABLE") {
        paramsContainer.innerHTML = `
          <div class="field">
            <label>Unavailable Robot Count (0 to 10)</label>
            <input type="number" id="param-disabled-robots" value="2" min="0" max="10" required />
          </div>
        `;
      } else if (type === "DEMAND_INCREASE") {
        paramsContainer.innerHTML = `
          <div class="field">
            <label>Demand Surge Percentage (%)</label>
            <input type="number" id="param-demand-surge" value="20" min="0" max="100" required />
          </div>
        `;
      } else if (type === "AISLE_BLOCKAGE") {
        paramsContainer.innerHTML = `
          <div class="field">
            <label>Blocked Zone Identifier</label>
            <input type="text" id="param-blocked-zone" value="Zone A" required />
          </div>
          <div class="field" style="margin-top:8px;">
            <label>Blocked Locations Count</label>
            <input type="number" id="param-blocked-count" value="3" min="1" max="20" required />
          </div>
        `;
      } else if (type === "REPLENISHMENT_DELAY") {
        paramsContainer.innerHTML = `
          <div class="field">
            <label>Supplier Lead Time Delay (Days)</label>
            <input type="number" id="param-delay-days" value="5" min="0" max="30" required />
          </div>
        `;
      } else if (type === "TASK_LOAD_INCREASE") {
        paramsContainer.innerHTML = `
          <div class="field">
            <label>Task Load Multiplier (1.0x to 2.0x)</label>
            <input type="number" id="param-task-multiplier" value="1.25" step="0.05" min="1.0" max="2.0" required />
          </div>
        `;
      }
    };

    typeSelect.addEventListener("change", updateParamsForm);
    updateParamsForm();

    document.getElementById("whatif-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const resultsPanel = document.getElementById("whatif-results-panel");
      resultsPanel.innerHTML = '<div class="empty-state">Running scenario impact analysis...</div>';

      const type = typeSelect.value;
      const params = { warehouse_id: window.currentWarehouse || "WH-BLR-01" };

      if (type === "ROBOT_UNAVAILABLE") {
        params.disabled_robots_count = parseInt(document.getElementById("param-disabled-robots").value || 2);
      } else if (type === "DEMAND_INCREASE") {
        params.demand_surge_percent = parseFloat(document.getElementById("param-demand-surge").value || 20);
      } else if (type === "AISLE_BLOCKAGE") {
        params.blocked_zone = document.getElementById("param-blocked-zone").value || "Zone A";
        params.blocked_locations_count = parseInt(document.getElementById("param-blocked-count").value || 3);
      } else if (type === "REPLENISHMENT_DELAY") {
        params.lead_time_delay_days = parseFloat(document.getElementById("param-delay-days").value || 5);
      } else if (type === "TASK_LOAD_INCREASE") {
        params.task_load_multiplier = parseFloat(document.getElementById("param-task-multiplier").value || 1.25);
      }

      try {
        const res = await Api.runWhatIfScenario({
          scenario_type: type,
          warehouse_id: params.warehouse_id,
          parameters: params
        });

        const badgeClass = res.impact_severity === 'CRITICAL' ? 'badge-danger' :
                           (res.impact_severity === 'HIGH' ? 'badge-danger' :
                           (res.impact_severity === 'MEDIUM' ? 'badge-warning' : 'badge-success'));

        resultsPanel.innerHTML = `
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
            <div>
              <strong style="font-size:16px;">${res.scenario} Impact Analysis</strong>
              <div style="font-size:11px;color:var(--text-faint);">Warehouse: ${res.warehouse_id} | Mode: ${res.data_mode}</div>
            </div>
            <span class="badge ${badgeClass}" style="font-size:13px;padding:4px 10px;">${res.impact_severity} IMPACT</span>
          </div>

          <div class="panel" style="margin-bottom:16px;background:var(--bg-subtle);">
            <strong>💡 Explanation:</strong>
            <p style="font-size:12.5px;margin:6px 0 0 0;color:var(--text-muted);">${esc(res.explanation)}</p>
          </div>

          <div class="table-scroll" style="margin-bottom:16px;">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Metric Name</th>
                  <th>Baseline</th>
                  <th>Simulated Scenario</th>
                  <th>Delta Difference</th>
                </tr>
              </thead>
              <tbody>
                ${Object.keys(res.baseline).map(m => {
                  const b = res.baseline[m];
                  const s = res.scenario_result[m];
                  const d = res.deltas[m];
                  const deltaColor = d > 0 ? 'var(--danger)' : (d < 0 ? 'var(--success)' : 'var(--text-faint)');
                  const deltaSign = d > 0 ? `+${d}` : `${d}`;
                  return `
                    <tr>
                      <td><strong>${m.replace(/_/g, ' ')}</strong></td>
                      <td>${b}</td>
                      <td class="mono" style="font-weight:700;">${s}</td>
                      <td class="mono" style="color:${deltaColor};font-weight:700;">${deltaSign}</td>
                    </tr>
                  `;
                }).join('')}
              </tbody>
            </table>
          </div>

          <div class="panel" style="border-left:4px solid var(--primary);margin:0;">
            <strong>🎯 Advisory Decision-Support Recommendation:</strong>
            <p style="font-size:12.5px;margin:6px 0 0 0;color:var(--text-muted);">${esc(res.recommendation)}</p>
          </div>
        `;
      } catch (err) {
        resultsPanel.innerHTML = `<div class="login-error">What-If Simulation Failed: ${esc(err.message)}</div>`;
      }
    });
  }

  // Export globally
  window.renderScenarioLabWorkspace = renderScenarioLabWorkspace;
})();
