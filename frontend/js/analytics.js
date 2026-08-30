/* analytics.js — Rendering logic for Phase 12 KPI and Performance Intelligence views */

// Global date filter states
window.analyticsPeriod = "30d";
window.analyticsStart = "";
window.analyticsEnd = "";

async function downloadCSV(path, filename) {
  const headers = {};
  const token = localStorage.getItem("wh_token");
  if (token) headers["Authorization"] = "Bearer " + token;
  try {
    const res = await fetch(path, { headers });
    if (!res.ok) throw new Error("CSV download failed");
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
    toast("CSV exported successfully", "success");
  } catch (err) {
    toast("Export failed: " + err.message, "danger");
  }
}

function renderFilterBar(el, currentView, exportEndpoint) {
  const filterHtml = `
    <div class="panel" style="margin-bottom: 20px; padding: 12px 16px;">
      <div class="panel-actions" style="display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
        <div style="display:flex;align-items:center;gap:6px;">
          <label for="analytics-period" style="font-size:12px;font-weight:600;color:var(--text-muted);">Period:</label>
          <select class="wh-select" id="analytics-period" style="width:130px;margin:0;height:32px;font-size:12.5px;padding:2px 8px;">
            <option value="today" ${window.analyticsPeriod === 'today' ? 'selected' : ''}>Today</option>
            <option value="7d" ${window.analyticsPeriod === '7d' ? 'selected' : ''}>Last 7 Days</option>
            <option value="30d" ${window.analyticsPeriod === '30d' ? 'selected' : ''}>Last 30 Days</option>
            <option value="90d" ${window.analyticsPeriod === '90d' ? 'selected' : ''}>Last 90 Days</option>
            <option value="custom" ${window.analyticsPeriod === 'custom' ? 'selected' : ''}>Custom Range</option>
          </select>
        </div>
        <div id="custom-date-inputs" style="display:${window.analyticsPeriod === 'custom' ? 'flex' : 'none'};gap:8px;align-items:center;">
          <input type="date" class="wh-select" id="analytics-start" value="${window.analyticsStart}" style="width:130px;height:32px;padding:4px 8px;margin:0;font-size:12px;">
          <span style="font-size:12px;color:var(--text-muted);">to</span>
          <input type="date" class="wh-select" id="analytics-end" value="${window.analyticsEnd}" style="width:130px;height:32px;padding:4px 8px;margin:0;font-size:12px;">
        </div>
        <button class="btn btn-secondary btn-sm" id="apply-analytics-filters" style="height:32px;margin:0;font-size:12px;padding:0 12px;">Apply Filter</button>
        
        ${exportEndpoint ? `
          <button class="btn btn-primary btn-sm" id="export-analytics-csv" style="height:32px;margin:0;margin-left:auto;font-size:12px;padding:0 12px;display:flex;align-items:center;gap:6px;">
            <i data-lucide="download" style="width:13px;height:13px;"></i> Export CSV
          </button>
        ` : ''}
      </div>
    </div>
  `;

  const div = document.createElement("div");
  div.innerHTML = filterHtml;
  el.appendChild(div.firstElementChild);

  // Setup filter triggers
  const periodSel = document.getElementById("analytics-period");
  const customDiv = document.getElementById("custom-date-inputs");
  periodSel.addEventListener("change", (e) => {
    customDiv.style.display = e.target.value === "custom" ? "flex" : "none";
  });

  document.getElementById("apply-analytics-filters").addEventListener("click", () => {
    window.analyticsPeriod = periodSel.value;
    window.analyticsStart = document.getElementById("analytics-start").value;
    window.analyticsEnd = document.getElementById("analytics-end").value;
    navigate(currentView);
  });

  if (exportEndpoint) {
    document.getElementById("export-analytics-csv").addEventListener("click", () => {
      const q = Api.buildQueryParams(currentWarehouse, window.analyticsPeriod, window.analyticsStart, window.analyticsEnd, "csv");
      downloadCSV(exportEndpoint + q, `${currentView}_export.csv`);
    });
  }
}

// 1. EXECUTIVE KPI DASHBOARD
async function renderAnalyticsExecutive(el) {
  el.innerHTML = "";
  renderFilterBar(el, "analytics-executive", null);

  const container = document.createElement("div");
  container.innerHTML = '<div class="loading-spinner"><div class="spin"></div> Executing aggregate queries for Executive KPIs...</div>';
  el.appendChild(container);

  try {
    const data = await Api.analyticsOverview(currentWarehouse, window.analyticsPeriod, window.analyticsStart, window.analyticsEnd);
    const k = data.kpis;

    container.innerHTML = `
      <div class="stat-row" style="margin-bottom: 20px;">
        <div class="stat-box">
          <div class="n" style="color:var(--success)">${k.orders_completed.value || 0}</div>
          <div class="l">Orders Throughput</div>
        </div>
        <div class="stat-box">
          <div class="n">${k.order_cycle_time.value !== null ? k.order_cycle_time.value + 'h' : 'N/A'}</div>
          <div class="l">Avg Cycle Time (Target: 48h)</div>
        </div>
        <div class="stat-box">
          <div class="n">${k.task_completion_rate.value || 0}%</div>
          <div class="l">Task Completion Rate</div>
        </div>
      </div>

      <div class="stat-row" style="margin-bottom: 20px;">
        <div class="stat-box">
          <div class="n" style="color:var(--primary)">${k.inventory_availability.value || 0}</div>
          <div class="l">Available Inventory (Units)</div>
        </div>
        <div class="stat-box">
          <div class="n" style="color:${k.stockout_risk.value > 10 ? 'var(--danger)' : 'var(--success)'}">${k.stockout_risk.value || 0}%</div>
          <div class="l">Stockout Risk Rate</div>
        </div>
        <div class="stat-box">
          <div class="n">${k.robot_utilization.value !== null ? k.robot_utilization.value + '%' : 'N/A'}</div>
          <div class="l">Avg Fleet Utilization</div>
        </div>
      </div>

      <div class="grid-container" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:20px;">
        <div class="panel">
          <div class="panel-title">AI & Forecasting KPI Status</div>
          <div class="panel-desc">Validation bounds computed from current state models.</div>
          <div style="margin-top:12px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>Forecast Median Error (WAPE):</span>
              <strong>${k.forecast_reliability.value !== null ? k.forecast_reliability.value + '%' : 'N/A'}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>AI Recommender Approval Rate:</span>
              <strong>${k.ai_approval_rate.value || 0}%</strong>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:12.5px;">
              <span>Active Discrepancies Count:</span>
              <strong style="color:var(--danger);">${k.potential_anomalies.value || 0}</strong>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-title">Reliability & Engineering Checks</div>
          <div class="panel-desc">SLA counts and pipeline statistics.</div>
          <div style="margin-top:12px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>Notification Dispatch Success:</span>
              <strong>${k.notification_success.value || 0}%</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>Path Routing Collision Avoided:</span>
              <strong>${k.congestion_events.value || 0} events</strong>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:12.5px;">
              <span>Data Sourcing Mode:</span>
              <span class="badge badge-success">DATABASE_SYNCHRONIZED</span>
            </div>
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="ask-answer" style="background:var(--danger-light); border:1px solid var(--danger); color:var(--danger);">${esc(err.message)}</div>`;
  }
}

// 2. OPERATIONAL DASHBOARD
async function renderAnalyticsOperations(el) {
  el.innerHTML = "";
  renderFilterBar(el, "analytics-operations", null);

  const container = document.createElement("div");
  container.innerHTML = '<div class="loading-spinner"><div class="spin"></div> Fetching real-time operational buffers...</div>';
  el.appendChild(container);

  try {
    const tasksData = await Api.analyticsTasks(currentWarehouse, window.analyticsPeriod, window.analyticsStart, window.analyticsEnd);
    const routingData = await Api.analyticsRouting(currentWarehouse, window.analyticsPeriod, window.analyticsStart, window.analyticsEnd);

    container.innerHTML = `
      <div class="grid-container" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:20px; margin-bottom: 20px;">
        <div class="panel">
          <div class="panel-title">Active Workload Queues</div>
          <div class="panel-desc">Pending work units categorized in current queue.</div>
          <div style="margin-top:12px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>Pending Tasks:</span>
              <strong>${tasksData.tasks_pending.value || 0}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>Overdue High-Priority Tasks:</span>
              <strong style="color:var(--danger);">${tasksData.overdue_high_priority.value || 0}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:12.5px;">
              <span>Average Queue Delay:</span>
              <strong>${tasksData.avg_queue_time_minutes.value !== null ? tasksData.avg_queue_time_minutes.value + ' mins' : 'N/A'}</strong>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-title">Spatial Traffic & Congestion</div>
          <div class="panel-desc">Dynamic route calculation flags.</div>
          <div style="margin-top:12px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>Dynamic Replanning Loops:</span>
              <strong>${routingData.replanning_count.value || 0}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>Robot Wait Bottlenecks:</span>
              <strong>${routingData.robot_waiting_events.value || 0}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:12.5px;">
              <span>Active Cell Obstacles:</span>
              <strong>${routingData.obstacles_logged.value || 0}</strong>
            </div>
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="ask-answer" style="background:var(--danger-light); border:1px solid var(--danger); color:var(--danger);">${esc(err.message)}</div>`;
  }
}

// 3. INVENTORY ANALYTICS PAGE
async function renderAnalyticsInventory(el) {
  el.innerHTML = "";
  renderFilterBar(el, "analytics-inventory", "/analytics/inventory");

  const container = document.createElement("div");
  container.innerHTML = `
    <div class="loading-spinner"><div class="spin"></div> Fetching stock allocations and calculating ABC tiers...</div>
  `;
  el.appendChild(container);

  try {
    const data = await Api.analyticsInventory(currentWarehouse, window.analyticsPeriod, window.analyticsStart, window.analyticsEnd);
    const abc = data.abc_distribution;

    container.innerHTML = `
      <div class="stat-row" style="margin-bottom: 20px;">
        <div class="stat-box">
          <div class="n">${data.on_hand.value || 0}</div>
          <div class="l">On Hand Units</div>
        </div>
        <div class="stat-box">
          <div class="n">${data.reserved.value || 0}</div>
          <div class="l">Reserved Units</div>
        </div>
        <div class="stat-box">
          <div class="n">${data.damaged.value || 0}</div>
          <div class="l">Damaged Stock</div>
        </div>
      </div>

      <div class="grid-container" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:20px; margin-bottom:20px;">
        <div class="panel">
          <div class="panel-title">Valuation Metrics</div>
          <div class="panel-desc">Calculated based on WMS SKU unit costs.</div>
          <div style="margin-top:12px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>Total Value:</span>
              <strong>${data.inventory_value.value !== null ? 'INR ' + data.inventory_value.value.toLocaleString() : 'Cost data unavailable'}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>Damaged Stock Value:</span>
              <strong>${data.damaged_value.value !== null ? 'INR ' + data.damaged_value.value.toLocaleString() : 'Cost data unavailable'}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:12.5px;">
              <span>Estimated Overstock Value:</span>
              <strong>${data.overstock_value.value !== null ? 'INR ' + data.overstock_value.value.toLocaleString() : 'Cost data unavailable'}</strong>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-title">WMS ABC Analysis Summary</div>
          <div class="panel-desc">Based on WMS historical stock_out movements.</div>
          <div style="margin-top:12px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>Class A (High-value SKUs):</span>
              <strong>${abc.A.count} items / INR ${abc.A.value.toLocaleString()}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>Class B (Medium-value SKUs):</span>
              <strong>${abc.B.count} items / INR ${abc.B.value.toLocaleString()}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:12.5px;">
              <span>Class C (Low-value SKUs):</span>
              <strong>${abc.C.count} items / INR ${abc.C.value.toLocaleString()}</strong>
            </div>
          </div>
        </div>
      </div>

      <!-- Configurable ABC Engine Control Panel -->
      <div class="panel" style="margin-bottom: 20px;">
        <div class="panel-header">
          <div>
            <div class="panel-title">Configurable ABC Classification Engine</div>
            <div class="panel-desc">Run cumulative Pareto analysis with custom parameters on any dataset.</div>
          </div>
        </div>
        
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom:20px; align-items: end;">
          <div>
            <label style="font-size:11.5px; font-weight:600; color:var(--text-muted); display:block; margin-bottom:5px;">Source Dataset</label>
            <select class="wh-select" id="abc-source-select" style="width:100%; height:36px; padding:6px;">
              <option value="wms">WMS Live Inventory</option>
              <option value="store_sales">Kaggle Store Sales (NeuroCipher)</option>
              <option value="online_retail">UCI Online Retail II</option>
              <option value="mlzc">MLZC Retail Demand Forecast</option>
            </select>
          </div>
          <div>
            <label style="font-size:11.5px; font-weight:600; color:var(--text-muted); display:block; margin-bottom:5px;">Threshold A (Class A %)</label>
            <input type="number" class="wh-select" id="abc-thresh-a" value="80" min="10" max="95" style="width:100%; height:36px; padding:6px;">
          </div>
          <div>
            <label style="font-size:11.5px; font-weight:600; color:var(--text-muted); display:block; margin-bottom:5px;">Threshold B (Class B %)</label>
            <input type="number" class="wh-select" id="abc-thresh-b" value="95" min="15" max="99" style="width:100%; height:36px; padding:6px;">
          </div>
          <div>
            <button class="btn btn-primary" id="btn-run-abc" style="width:100%; height:36px; padding:0;">Calculate & Classify</button>
          </div>
        </div>

        <div id="abc-engine-body"></div>
      </div>
    `;

    const sourceSel = document.getElementById("abc-source-select");
    const threshA = document.getElementById("abc-thresh-a");
    const threshB = document.getElementById("abc-thresh-b");
    const runBtn = document.getElementById("btn-run-abc");
    const engineBody = document.getElementById("abc-engine-body");

    const loadAbcEngineData = async () => {
      engineBody.innerHTML = '<div class="loading-spinner"><div class="spin"></div> Fetching source classification...</div>';
      try {
        const source = sourceSel.value;
        const res = await Api.getABC(source);
        
        if (res.results.length === 0) {
          engineBody.innerHTML = `
            <div class="empty-state" style="padding:20px 0;">
              No classification run exists in DB for source '${esc(source)}'. Click Calculate above.
            </div>
          `;
          return;
        }

        const counts = res.summary;
        engineBody.innerHTML = `
          <div class="responsive-grid-1-15" style="margin-top:10px;">
            <div>
              <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
                <span>Class A:</span>
                <strong>${counts.A.count} items / INR ${counts.A.total_value.toLocaleString()}</strong>
              </div>
              <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
                <span>Class B:</span>
                <strong>${counts.B.count} items / INR ${counts.B.total_value.toLocaleString()}</strong>
              </div>
              <div style="display:flex; justify-content:space-between; margin-bottom:15px; font-size:12.5px;">
                <span>Class C:</span>
                <strong>${counts.C.count} items / INR ${counts.C.total_value.toLocaleString()}</strong>
              </div>
              
              <div class="chart-wrapper" style="height:120px;"><canvas id="abc-engine-chart"></canvas></div>
            </div>
            <div>
              <div style="max-height:210px; overflow-y:auto; border:1px solid var(--border); border-radius:6px;">
                <table class="data-table" style="font-size:11.5px; margin-bottom:0;">
                  <thead>
                    <tr><th>Item ID</th><th>Name / Dept</th><th>Total Qty</th><th>Cum. %</th><th>Class</th></tr>
                  </thead>
                  <tbody>
                    ${res.results.slice(0, 50).map(r => `
                      <tr>
                        <td class="mono">${esc(r.item_id)}</td>
                        <td style="max-width:140px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${esc(r.item_name || 'N/A')}</td>
                        <td class="mono">${r.total_qty.toLocaleString()}</td>
                        <td class="mono">${r.cumulative_pct.toFixed(2)}%</td>
                        <td><span class="badge ${r.abc_class === 'A' ? 'badge-danger' : (r.abc_class === 'B' ? 'badge-warn' : 'badge-success')}">${r.abc_class}</span></td>
                      </tr>
                    `).join('')}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        `;

        getOrCreateChart("abc-engine-chart", {
          type: "doughnut",
          data: {
            labels: ["A", "B", "C"],
            datasets: [{
              data: [counts.A.count, counts.B.count, counts.C.count],
              backgroundColor: ["#ef4444", "#f59e0b", "#10b981"]
            }]
          },
          options: getThemeChartOptions({ plugins: { legend: { position: 'right' } } })
        });
      } catch (err) {
        engineBody.innerHTML = `<div class="empty-state">Error loading ABC classification: ${esc(err.message)}</div>`;
      }
    };

    runBtn.addEventListener("click", async () => {
      engineBody.innerHTML = '<div class="loading-spinner"><div class="spin"></div> Executing Pareto contribution calculations...</div>';
      runBtn.disabled = true;
      try {
        await Api.runABC(sourceSel.value, parseFloat(threshA.value), parseFloat(threshB.value));
        await loadAbcEngineData();
        // Also reload main inventory stats if source is WMS
        if (sourceSel.value === "wms") {
          await renderAnalyticsInventory(el);
        }
      } catch (err) {
        engineBody.innerHTML = `<div class="empty-state" style="color:var(--danger)">Calculation failed: ${esc(err.message)}</div>`;
      } finally {
        runBtn.disabled = false;
      }
    });

    sourceSel.addEventListener("change", loadAbcEngineData);
    await loadAbcEngineData();

  } catch (err) {
    container.innerHTML = `<div class="ask-answer" style="background:var(--danger-light); border:1px solid var(--danger); color:var(--danger);">${esc(err.message)}</div>`;
  }

}

// 4. TASK PERFORMANCE PAGE
async function renderAnalyticsTasks(el) {
  el.innerHTML = "";
  renderFilterBar(el, "analytics-tasks", "/analytics/tasks");

  const container = document.createElement("div");
  container.innerHTML = '<div class="loading-spinner"><div class="spin"></div> Fetching task logs and queue timing distributions...</div>';
  el.appendChild(container);

  try {
    const data = await Api.analyticsTasks(currentWarehouse, window.analyticsPeriod, window.analyticsStart, window.analyticsEnd);
    
    // Parse priorities
    const priorities = data.by_priority || {};
    const labels = Object.keys(priorities).map(k => k.toUpperCase());
    const counts = Object.values(priorities);

    container.innerHTML = `
      <div class="stat-row" style="margin-bottom: 20px;">
        <div class="stat-box">
          <div class="n">${data.tasks_created.value || 0}</div>
          <div class="l">Tasks Created</div>
        </div>
        <div class="stat-box">
          <div class="n" style="color:var(--success)">${data.tasks_completed.value || 0}</div>
          <div class="l">Tasks Completed</div>
        </div>
        <div class="stat-box">
          <div class="n" style="color:var(--danger)">${data.tasks_failed.value || 0}</div>
          <div class="l">Tasks Failed</div>
        </div>
      </div>

      <div class="grid-container" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:20px; margin-bottom:20px;">
        <div class="panel">
          <div class="panel-title">Task Timing Performance</div>
          <div class="panel-desc">Average durations for picking, replenishing and cycle checks.</div>
          <div style="margin-top:12px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>Average Queue Delay:</span>
              <strong>${data.avg_queue_time_minutes.value !== null ? data.avg_queue_time_minutes.value + ' mins' : 'N/A'}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:8px; font-size:12.5px;">
              <span>Average Task Execution:</span>
              <strong>${data.avg_duration_minutes.value !== null ? data.avg_duration_minutes.value + ' mins' : 'N/A'}</strong>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:12.5px;">
              <span>Completion Rate:</span>
              <strong>${data.completion_rate.value || 0}%</strong>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-title">Task Priority Distribution</div>
          <div style="height:150px; position:relative; margin-top:10px;">
            <canvas id="task-priority-donut"></canvas>
          </div>
        </div>
      </div>
    `;

    // Render Donut Chart
    getOrCreateChart("task-priority-donut", {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{
          data: counts,
          backgroundColor: ["#10b981", "#3b82f6", "#f59e0b", "#ef4444"]
        }]
      },
      options: getThemeChartOptions()
    });

  } catch (err) {
    container.innerHTML = `<div class="ask-answer" style="background:var(--danger-light); border:1px solid var(--danger); color:var(--danger);">${esc(err.message)}</div>`;
  }
}

// 5. ROBOT PERFORMANCE PAGE
async function renderAnalyticsRobots(el) {
  el.innerHTML = "";
  renderFilterBar(el, "analytics-robots", "/analytics/robots");

  const container = document.createElement("div");
  container.innerHTML = '<div class="loading-spinner"><div class="spin"></div> Fetching robot fleet logs and telemetry summaries...</div>';
  el.appendChild(container);

  try {
    const data = await Api.analyticsRobots(currentWarehouse, window.analyticsPeriod, window.analyticsStart, window.analyticsEnd);
    
    let rows = `<tr><td colspan="7" style="text-align:center;color:#6b7280;padding:20px;">No robot logs found in database.</td></tr>`;
    if (data.comparison && data.comparison.length > 0) {
      rows = data.comparison.map(r => `
        <tr>
          <td><strong style="font-family:monospace;">${esc(r.robot_code)}</strong></td>
          <td>${esc(r.name)}</td>
          <td><span class="badge badge-neutral">${esc(r.status)}</span></td>
          <td><strong>${r.utilization_percent}%</strong></td>
          <td>${r.tasks_completed}</td>
          <td>${r.distance_travelled} cells</td>
          <td><span style="color:${r.failures > 0 ? 'var(--danger)' : 'inherit'};">${r.failures}</span></td>
        </tr>
      `).join("");
    }

    container.innerHTML = `
      <div class="stat-row" style="margin-bottom: 20px;">
        <div class="stat-box">
          <div class="n">${data.fleet_size.value || 0}</div>
          <div class="l">Active Fleet Size</div>
        </div>
        <div class="stat-box">
          <div class="n" style="color:var(--success)">${data.avg_utilization.value !== null ? data.avg_utilization.value + '%' : 'N/A'}</div>
          <div class="l">Average Fleet Utilization</div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-title">Robot Performance Overview</div>
        <div class="panel-desc">Detailed comparison metrics per AGV fleet unit.</div>
        
        <div class="table-container" style="margin-top:15px;">
          <table class="wh-table">
            <thead>
              <tr>
                <th>Robot Code</th>
                <th>Name</th>
                <th>Status</th>
                <th>Utilization %</th>
                <th>Tasks Completed</th>
                <th>Distance Travelled</th>
                <th>Failures</th>
              </tr>
            </thead>
            <tbody>
              ${rows}
            </tbody>
          </table>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = `<div class="ask-answer" style="background:var(--danger-light); border:1px solid var(--danger); color:var(--danger);">${esc(err.message)}</div>`;
  }
}

// 6. AI & FORECAST ANALYTICS PAGE
async function renderAnalyticsAI(el) {
  el.innerHTML = "";
  renderFilterBar(el, "analytics-ai", null);

  const container = document.createElement("div");
  container.innerHTML = '<div class="loading-spinner"><div class="spin"></div> Fetching replenishment forecasts and shrinkage anomalies...</div>';
  el.appendChild(container);

  try {
    const fcData = await Api.analyticsForecasting(currentWarehouse);
    const anomaliesData = await Api.analyticsAnomalies(currentWarehouse, window.analyticsPeriod, window.analyticsStart, window.analyticsEnd);

    let fcRows = `<tr><td colspan="4" style="text-align:center;color:#6b7280;padding:20px;">Insufficient demand holdout data for accuracy validation.</td></tr>`;
    if (fcData.items_evaluated && fcData.items_evaluated.length > 0) {
      fcRows = fcData.items_evaluated.map(item => `
        <tr>
          <td><strong style="font-family:monospace;">${esc(item.item_id)}</strong></td>
          <td>${esc(item.item_name)}</td>
          <td><strong>${item.wape}%</strong></td>
          <td><span class="badge ${item.reliability === 'HIGH' ? 'badge-success' : (item.reliability === 'MODERATE' ? 'badge-warn' : 'badge-danger')}">${item.reliability}</span></td>
        </tr>
      `).join("");
    }

    let anomRows = `<tr><td colspan="5" style="text-align:center;color:#6b7280;padding:20px;">No inventory discrepancies requiring investigation detected.</td></tr>`;
    if (anomaliesData.raw_anomalies && anomaliesData.raw_anomalies.length > 0) {
      anomRows = anomaliesData.raw_anomalies.map(a => `
        <tr>
          <td><span style="font-size:11.5px;">${new Date(a.date).toLocaleDateString('en-IN')}</span></td>
          <td>${esc(a.item_name)}</td>
          <td><span style="color:var(--danger);">${a.discrepancy} units</span></td>
          <td>INR ${a.exposure ? a.exposure.toLocaleString() : '0'}</td>
          <td><span class="badge ${a.severity === 'CRITICAL' ? 'badge-danger' : 'badge-warn'}">${a.severity}</span></td>
        </tr>
      `).join("");
    }

    container.innerHTML = `
      <div class="stat-row" style="margin-bottom: 20px;">
        <div class="stat-box">
          <div class="n">${fcData.median_wape.value !== null ? fcData.median_wape.value + '%' : 'N/A'}</div>
          <div class="l">Median Forecast Error (WAPE)</div>
        </div>
        <div class="stat-box">
          <div class="n" style="color:var(--danger)">INR ${anomaliesData.estimated_exposure.value ? anomaliesData.estimated_exposure.value.toLocaleString() : '0'}</div>
          <div class="l">Shrinkage Valuation Exposure</div>
        </div>
      </div>

      <div class="grid-container" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap:20px;">
        <div class="panel">
          <div class="panel-title">SKU Forecast Accuracy backtest</div>
          <div class="panel-desc">14-day holdout validation check.</div>
          <div class="table-container" style="margin-top:12px;">
            <table class="wh-table">
              <thead>
                <tr>
                  <th>SKU</th>
                  <th>Name</th>
                  <th>WAPE</th>
                  <th>Reliability</th>
                </tr>
              </thead>
              <tbody>
                ${fcRows}
              </tbody>
            </table>
          </div>
        </div>

        <div class="panel">
          <div class="panel-title">Potential Inventory Anomalies</div>
          <div class="panel-desc">Shrinkage discrepancy review log.</div>
          <div class="table-container" style="margin-top:12px;">
            <table class="wh-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>SKU Name</th>
                  <th>Discrepancy</th>
                  <th>Exposure</th>
                  <th>Severity</th>
                </tr>
              </thead>
              <tbody>
                ${anomRows}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    `;

  } catch (err) {
    container.innerHTML = `<div class="ask-answer" style="background:var(--danger-light); border:1px solid var(--danger); color:var(--danger);">${esc(err.message)}</div>`;
  }
}
