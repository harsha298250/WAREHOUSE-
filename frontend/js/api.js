const API_BASE = typeof window !== "undefined" && window.__API_BASE_URL__ ? window.__API_BASE_URL__ : ""; // same-origin, backend serves the frontend
const API_BASE_URL = API_BASE;
if (typeof window !== "undefined") {
  window.API_BASE_URL = API_BASE;
}

const Api = {
  token: localStorage.getItem("wh_token") || null,

  setToken(t) {
    this.token = t;
    if (t) localStorage.setItem("wh_token", t);
    else localStorage.removeItem("wh_token");
  },

  async request(method, path, body, timeoutMs = 20000) {
    const headers = { "Content-Type": "application/json" };
    if (this.token) headers["Authorization"] = "Bearer " + this.token;
    
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    let res;
    try {
      res = await fetch(API_BASE + path, {
        method, headers, body: body ? JSON.stringify(body) : undefined,
        signal: controller.signal
      });
    } catch (err) {
      if (err.name === "AbortError") {
        throw new Error("Warehouse service timed out. The server took too long to respond.");
      }
      throw new Error("Cannot reach the warehouse server. Please check your network connection.");
    } finally {
      clearTimeout(timer);
    }
    if (res.status === 401) {
      if (path !== "/auth/login") {
        this.setToken(null);
        if (typeof showLogin === "function") showLogin();
        throw new Error("Session expired — please log in again.");
      }
    }
    let data;
    try { data = await res.json(); } catch (e) { data = null; }
    if (!res.ok) {
      let errMsg = `Request failed (${res.status})`;
      if (data) {
        if (data.detail) {
          if (typeof data.detail === "string") {
            errMsg = data.detail;
          } else if (Array.isArray(data.detail)) {
            errMsg = data.detail.map(err => {
              const loc = err.loc ? err.loc.slice(1).join(".") : "";
              return `${loc ? loc + ": " : ""}${err.msg}`;
            }).join("; ");
          } else if (typeof data.detail === "object") {
            errMsg = JSON.stringify(data.detail);
          }
        } else if (data.message) {
          errMsg = data.message;
        } else if (data.error) {
          errMsg = typeof data.error === "string" ? data.error : JSON.stringify(data.error);
        }
      }
      throw new Error(errMsg);
    }
    return data;
  },

  get(path) { return this.request("GET", path); },
  post(path, body) { return this.request("POST", path, body); },
  put(path, body) { return this.request("PUT", path, body); },
  patch(path, body) { return this.request("PATCH", path, body); },
  delete(path) { return this.request("DELETE", path); },


  login(username, password) { return this.post("/auth/login", { username, password }); },
  logout() { return this.post("/auth/logout", {}); },
  googleConfig() { return this.get("/auth/google-config"); },
  googleSignInToken(id_token) { return this.post("/auth/google-signin", { id_token }); },
  me() { return this.get("/auth/me"); },

  // ---- Phase 9: User Management ----
  listUsers() { return this.get("/users"); },
  listOperators() { return this.get("/users/operators"); },
  getUser(id) { return this.get(`/users/${id}`); },
  updateUserRole(id, role, reason = "", confirmPassword = "") { return this.request("PUT", `/users/${id}/role`, { role, reason, confirm_password: confirmPassword }); },
  activateUser(id) { return this.request("PUT", `/users/${id}/activate`, {}); },
  deactivateUser(id) { return this.request("PUT", `/users/${id}/deactivate`, {}); },
  unlockUser(id) { return this.request("PUT", `/users/${id}/unlock`, {}); },

  // ---- Phase 9: Security Center ----
  securityDashboard() { return this.get("/security/dashboard"); },
  securityEvents(limit = 50, actionFilter = "", usernameFilter = "") {
    let q = `?limit=${limit}`;
    if (actionFilter) q += `&action_filter=${encodeURIComponent(actionFilter)}`;
    if (usernameFilter) q += `&username_filter=${encodeURIComponent(usernameFilter)}`;
    return this.get(`/security/events${q}`);
  },
  securityPermissions() { return this.get("/security/permissions"); },

  // ---- Phase 9: Audit Ledger ----
  auditLedger(limit = 100, offset = 0, eventTypeFilter = "") {
    let q = `?limit=${limit}&offset=${offset}`;
    if (eventTypeFilter) q += `&event_type_filter=${encodeURIComponent(eventTypeFilter)}`;
    return this.get(`/audit/ledger${q}`);
  },
  auditVerify() { return this.get("/audit/verify"); },

  // ---- Phase 9: Step-Up OTP ----
  requestStepUpOTP() { return this.post("/auth/request-stepup-otp", {}); },
  verifyStepUpOTP(passkey) { return this.post("/auth/verify-stepup-otp", { passkey }); },

  requestChangePassword(current_password, new_password) {
    return this.post("/auth/request-change-password", { current_password, new_password });
  },
  confirmChangePassword(passkey) {
    return this.post("/auth/confirm-change-password", { passkey });
  },
  requestAddAdmin(payload) { return this.post("/admin/request-add-admin", payload); },
  confirmAddAdmin(passkey) { return this.post("/admin/confirm-add-admin", { passkey }); },
  verifyPassword(password) { return this.post("/auth/verify-password", { password }); },


  warehouses() { return this.get("/warehouses"); },
  getWarehouse(id) { return this.get(`/warehouses/${encodeURIComponent(id)}`); },
  createWarehouse(payload) { return this.post("/warehouses", payload); },
  updateWarehouse(id, payload) { return this.put(`/warehouses/${encodeURIComponent(id)}`, payload); },
  patchWarehouseLocation(id, lat, lng) { return this.patch(`/warehouses/${encodeURIComponent(id)}/location`, { latitude: lat, longitude: lng }); },
  warehouseWeather(id) { return this.get(`/warehouses/${encodeURIComponent(id)}/weather`); },
  deleteWarehouse(id, password) { return this.request("DELETE", `/warehouses/${encodeURIComponent(id)}`, { password: password }); },
  items() { return this.get("/items"); },
  getItem(id) { return this.get(`/items/${encodeURIComponent(id)}`); },
  createItem(payload) { return this.post("/items", payload); },
  updateItem(id, payload) { return this.patch(`/items/${encodeURIComponent(id)}`, payload); },
  deleteItem(id) { return this.delete(`/items/${encodeURIComponent(id)}`); },
  recordStock(payload) { return this.post("/stock-movements", payload); },
  stockHistory(wh) { return this.get(`/stock-movements/${wh}`); },

  aiDecisionCenter(wh) { return this.get(`/ai/decision-center${wh ? '?warehouse_id=' + encodeURIComponent(wh) : ''}`); },
  actOnRecommendation(id, action, notes) { return this.post(`/ai/recommendations/${id}/action`, { action, notes }); },
  approveRecommendation(id, notes) { return this.post(`/ai/recommendations/${id}/approve`, { action: "APPROVED", notes }); },
  rejectRecommendation(id, notes) { return this.post(`/ai/recommendations/${id}/reject`, { action: "REJECTED", notes }); },
  dismissRecommendation(id) { return this.post(`/ai/recommendations/${id}/dismiss`, {}); },
  aiDecisionHistory(limit = 50) { return this.get(`/ai/decision-history?limit=${limit}`); },
  digitalTwin(wh) { return this.get(`/apps/digital-twin/${wh}`); },
  simulateScenario(payload) { return this.post("/ai/simulate-scenario", payload); },
  runWhatIfScenario(payload) { return this.post("/decision-support/what-if", payload); },
  getDecisions(wh, category) {
    let q = [];
    if (wh) q.push(`warehouse_id=${encodeURIComponent(wh)}`);
    if (category) q.push(`category=${encodeURIComponent(category)}`);
    return this.get(`/decision-support/decisions` + (q.length ? '?' + q.join('&') : ''));
  },
  getTopActions(wh, limit = 5) {
    return this.get(`/decision-support/top-actions?limit=${limit}` + (wh ? `&warehouse_id=${encodeURIComponent(wh)}` : ''));
  },
  acknowledgeDecision(id) { return this.post(`/decision-support/decisions/${encodeURIComponent(id)}/acknowledge`, {}); },
  dismissDecision(id) { return this.post(`/decision-support/decisions/${encodeURIComponent(id)}/dismiss`, {}); },
  resolveDecision(id) { return this.post(`/decision-support/decisions/${encodeURIComponent(id)}/resolve`, {}); },
  health() { return this.get("/health"); },
  healthDB() { return this.get("/health/db"); },
  healthML() { return this.get("/health/ml"); },
  healthIntegrations() { return this.get("/health/integrations"); },
  aiAssistant(message, warehouseId) { return this.post("/ai/assistant", { message, warehouse_id: warehouseId }); },
  optimizeScheduler(warehouseId) { return this.get(`/ai/optimize-scheduler?warehouse_id=${warehouseId}`); },

  analyticsDashboard(wh) { return this.get(`/analytics/dashboard${wh ? '?warehouse_id=' + encodeURIComponent(wh) : ''}`); },
  inventory(wh) { return this.get(`/inventory/${wh}`); },
  trend(wh) { return this.get(`/trend/${wh}`); },
  
  buildQueryParams(wh, period, start, end, format) {
    let params = [];
    if (wh) params.push(`warehouse_id=${encodeURIComponent(wh)}`);
    if (period) params.push(`period=${encodeURIComponent(period)}`);
    if (start) params.push(`start_date=${encodeURIComponent(start)}`);
    if (end) params.push(`end_date=${encodeURIComponent(end)}`);
    if (format) params.push(`format=${encodeURIComponent(format)}`);
    return params.length ? '?' + params.join('&') : '';
  },
  analyticsOverview(wh, period, start, end) { return this.get(`/analytics/overview` + this.buildQueryParams(wh, period, start, end)); },
  getExplainableAnalytics(wh, period, start, end) { return this.get(`/analytics/explainable-overview` + this.buildQueryParams(wh, period, start, end)); },
  getAnalyticsTrends(wh, period) { return this.get(`/analytics/trends` + this.buildQueryParams(wh, period)); },
  getAnalyticsBottlenecks(wh) { return this.get(`/analytics/bottlenecks` + (wh ? `?warehouse_id=${encodeURIComponent(wh)}` : '')); },
  getPathfindingComparison(wh, period) { return this.get(`/analytics/pathfinding-comparison` + this.buildQueryParams(wh, period)); },
  explainDecisionMetrics(decisionId) { return this.get(`/analytics/decision-explanation/${encodeURIComponent(decisionId)}`); },
  analyticsOrders(wh, period, start, end, format) { return this.get(`/analytics/orders` + this.buildQueryParams(wh, period, start, end, format)); },
  analyticsInventory(wh, period, start, end, format) { return this.get(`/analytics/inventory` + this.buildQueryParams(wh, period, start, end, format)); },
  analyticsTasks(wh, period, start, end, format) { return this.get(`/analytics/tasks` + this.buildQueryParams(wh, period, start, end, format)); },
  analyticsRobots(wh, period, start, end, format) { return this.get(`/analytics/robots` + this.buildQueryParams(wh, period, start, end, format)); },
  analyticsRouting(wh, period, start, end, format) { return this.get(`/analytics/routing` + this.buildQueryParams(wh, period, start, end, format)); },
  analyticsForecasting(wh) { return this.get(`/analytics/forecasting${wh ? '?warehouse_id=' + encodeURIComponent(wh) : ''}`); },
  analyticsAnomalies(wh, period, start, end, format) { return this.get(`/analytics/anomalies` + this.buildQueryParams(wh, period, start, end, format)); },
  analyticsAI(wh, period, start, end) { return this.get(`/analytics/ai` + this.buildQueryParams(wh, period, start, end)); },
  analyticsSimulation(wh, period, start, end) { return this.get(`/analytics/simulation` + this.buildQueryParams(wh, period, start, end)); },
  analyticsSystem(period, start, end) { return this.get(`/analytics/system` + this.buildQueryParams(null, period, start, end)); },
  runForecastPipeline(family, horizon, trainPct) {
    let q = [];
    if (family) q.push(`family=${encodeURIComponent(family)}`);
    if (horizon) q.push(`horizon=${horizon}`);
    if (trainPct) q.push(`train_pct=${trainPct}`);
    return this.post(`/analytics/forecasting/run` + (q.length ? '?' + q.join('&') : ''));
  },
  getForecastRuns(limit, offset) {
    return this.get(`/analytics/forecasting/runs` + (limit ? `?limit=${limit}` : '') + (offset ? `${limit ? '&' : '?'}offset=${offset}` : ''));
  },
  getForecastResults(family, runId, limit, offset) {
    let q = [];
    if (family) q.push(`family=${encodeURIComponent(family)}`);
    if (runId) q.push(`run_id=${encodeURIComponent(runId)}`);
    if (limit) q.push(`limit=${limit}`);
    if (offset) q.push(`offset=${offset}`);
    return this.get(`/analytics/forecasting/results` + (q.length ? '?' + q.join('&') : ''));
  },
  runABC(source, thresholdA, thresholdB, warehouseId = null) {
    let q = [];
    if (source) q.push(`source=${source}`);
    if (thresholdA) q.push(`threshold_a=${thresholdA}`);
    if (thresholdB) q.push(`threshold_b=${thresholdB}`);
    const wh = warehouseId || (typeof currentWarehouse !== 'undefined' ? currentWarehouse : null);
    if (wh) q.push(`warehouse_id=${encodeURIComponent(wh)}`);
    return this.post(`/analytics/abc/run` + (q.length ? '?' + q.join('&') : ''));
  },
  getABC(source, abcClass, limit, offset, warehouseId = null) {
    let q = [];
    if (source) q.push(`source=${source}`);
    if (abcClass) q.push(`abc_class=${abcClass}`);
    const wh = warehouseId || (typeof currentWarehouse !== 'undefined' ? currentWarehouse : null);
    if (wh) q.push(`warehouse_id=${encodeURIComponent(wh)}`);
    if (limit) q.push(`limit=${limit}`);
    if (offset) q.push(`offset=${offset}`);
    return this.get(`/analytics/abc` + (q.length ? '?' + q.join('&') : ''));
  },
  runDemandAnomalies(contamination) {
    return this.post(`/analytics/anomalies/run` + (contamination ? `?contamination=${contamination}` : ''));
  },
  getDemandAnomalies(severity, limit, offset) {
    let q = [];
    if (severity) q.push(`severity=${severity}`);
    if (limit) q.push(`limit=${limit}`);
    if (offset) q.push(`offset=${offset}`);
    return this.get(`/analytics/anomalies/demand` + (q.length ? '?' + q.join('&') : ''));
  },
  runReplenishment(wh) {
    return this.post(`/analytics/replenishment/run` + (wh ? `?warehouse_id=${encodeURIComponent(wh)}` : ''));
  },
  getReplenishment(wh, urgency, abcClass, limit, offset) {
    let q = [];
    if (wh) q.push(`warehouse_id=${encodeURIComponent(wh)}`);
    if (urgency) q.push(`urgency=${urgency}`);
    if (abcClass) q.push(`abc_class=${abcClass}`);
    if (limit) q.push(`limit=${limit}`);
    if (offset) q.push(`offset=${offset}`);
    return this.get(`/analytics/replenishment` + (q.length ? '?' + q.join('&') : ''));
  },
  forecast(wh, item) { return this.get(`/forecast/${wh}/${item}`); },
  reorderAlerts(wh) { return this.get(`/alerts/reorder/${wh}`); },

  shrinkageAlerts(wh) { return this.get(`/alerts/shrinkage/${wh}`); },
  runShrinkageDetection() { return this.post("/run-shrinkage-detection"); },

  transferOpportunities() { return this.get("/apps/transfer-optimizer"); },
  getCloudBackupStatus() { return this.get("/apps/cloud-backup/status"); },
  runCloudBackup() { return this.post("/apps/cloud-backup/run", {}); },
  eventCalendar() { return this.get("/apps/event-calendar"); },
  shrinkageInsights() { return this.get("/apps/shrinkage-insights"); },
  securityMonitor() { return this.get("/apps/security-monitor"); },
  trustLedger() { return this.get("/apps/trust-ledger"); },
  storageTiering() { return this.get("/apps/cloud-cost/storage"); },
  autoscaling() { return this.get("/apps/cloud-cost/autoscaling"); },
  ask(q) { return this.get("/apps/ask?q=" + encodeURIComponent(q)); },
  getDatasets() { return this.get("/analytics/datasets"); },
  alertDigest(wh) { return this.get(`/apps/alert-digest/${wh}`); },
  recentActivity() { return this.get("/apps/recent-activity"); },
  tasks(wh) { return this.get(`/tasks${wh ? '?warehouse_id=' + encodeURIComponent(wh) : ''}`); },
  taskDetail(id) { return this.get(`/tasks/${id}`); },
  taskHistory(id) { return this.get(`/tasks/${id}/history`); },
  prioritizeTask(id) { return this.post(`/tasks/${id}/prioritize`); },
  claimTask(id) { return this.post(`/tasks/${id}/claim`); },
  assignTask(id, userId, notes) { return this.post(`/tasks/${id}/assign`, { assigned_user_id: userId, notes }); },
  reassignTask(id, userId, reason, notes) { return this.post(`/tasks/${id}/reassign`, { assigned_user_id: userId, reason, notes }); },
  startTask(id) { return this.post(`/tasks/${id}/start`); },
  pauseTask(id) { return this.post(`/tasks/${id}/pause`); },
  resumeTask(id) { return this.post(`/tasks/${id}/resume`); },
  completeTask(id, qty, notes) { return this.post(`/tasks/${id}/complete`, { completed_quantity: qty, notes }); },
  failTask(id, reason, notes) { return this.post(`/tasks/${id}/fail`, { failure_reason: reason, notes }); },
  cancelTask(id) { return this.post(`/tasks/${id}/cancel`); },
  generateReplenishment() { return this.post("/tasks/generate-replenishment"); },
  robots(wh, status) {
    let q = "";
    if (wh) q += `?warehouse_id=${encodeURIComponent(wh)}`;
    if (status) q += `${q ? '&' : '?'}status=${encodeURIComponent(status)}`;
    return this.get(`/robots${q}`);
  },
  robotDetail(id) { return this.get(`/robots/${id}`); },
  createRobot(data) { return this.post("/robots", data); },
  updateRobot(id, data) { return this.patch(`/robots/${id}`, data); },
  assignRobot(id, taskId) { return this.post(`/robots/${id}/assign`, { task_id: taskId }); },
  releaseRobot(id) { return this.post(`/robots/${id}/release`); },
  simulateFailure(id) { return this.post(`/robots/${id}/simulate-failure`); },
  recoverRobot(id) { return this.post(`/robots/${id}/recover`); },
  chargeRobot(id) { return this.post(`/robots/${id}/charge`); },
  recommendRobotForTask(taskId) { return this.post(`/tasks/${taskId}/recommend-robot`, {}); },
  assignRobotToTask(taskId, robotCode, method = "INTELLIGENT") { return this.post(`/tasks/${taskId}/assign-robot`, { robot_code: robotCode, assignment_method: method }); },
  updateTask(id, data) { return this.patch(`/tasks/${id}`, data); },
  removeRobot(id) { return this.delete(`/robots/${id}`); },
  orders(wh = "", status = "", page = 1, pageSize = 50) {
    let q = `?page=${page}&page_size=${pageSize}`;
    if (wh) q += `&warehouse_id=${encodeURIComponent(wh)}`;
    if (status) q += `&status=${encodeURIComponent(status)}`;
    return this.get(`/wms/orders${q}`);
  },
  createOrder(payload) { return this.post("/wms/orders", payload); },
  getOrderDetail(id) { return this.get(`/wms/orders/${id}`); },
  updateOrder(id, data) { return this.patch(`/wms/orders/${id}`, data); },
  cancelOrder(id) { return this.post(`/wms/orders/${id}/cancel`); },
  retryTask(id) { return this.post(`/tasks/${id}/retry`); },
  autoAssignRobot(wh) { return this.post(`/robots/auto-assign?warehouse_id=${encodeURIComponent(wh)}`); },

  simulationStart() { return this.post("/robots/simulation/start"); },
  simulationPause() { return this.post("/robots/simulation/pause"); },
  simulationResume() { return this.post("/robots/simulation/resume"); },
  simulationStep() { return this.post("/robots/simulation/step"); },
  simulationReset() { return this.post("/robots/simulation/reset"); },
  robotTelemetry(id) { return this.get(`/robots/${id}/telemetry`); },
  robotHistory(id) { return this.get(`/robots/${id}/history`); },
  planPath(wh, sx, sy, gx, gy, robotId = null, algorithm = "A_STAR") {
    return this.post("/pathfinding/plan", { warehouse_id: wh, start_x: sx, start_y: sy, goal_x: gx, goal_y: gy, robot_id: robotId, algorithm: algorithm });
  },
  planTaskRoute(taskId, robotCode = null, algorithm = "A_STAR") {
    return this.post("/pathfinding/task-route", { task_id: taskId, robot_code: robotCode, algorithm: algorithm });
  },
  rerouteRobotPath(robotCode, algorithm = "A_STAR") {
    return this.post("/pathfinding/reroute", { robot_code: robotCode, algorithm: algorithm });
  },
  runReplenishmentEngine(wh = null) {
    const q = wh ? `?warehouse_id=${encodeURIComponent(wh)}` : "";
    return this.post(`/analytics/replenishment/run${q}`);
  },
  getReplenishmentRecommendations(wh = null, urgency = null, abc = null) {
    let q = [];
    if (wh) q.push(`warehouse_id=${encodeURIComponent(wh)}`);
    if (urgency) q.push(`urgency=${encodeURIComponent(urgency)}`);
    if (abc) q.push(`abc_class=${encodeURIComponent(abc)}`);
    const qStr = q.length ? `?${q.join("&")}` : "";
    return this.get(`/analytics/replenishment${qStr}`);
  },
  approveReplenishment(id) {
    return this.post(`/analytics/replenishment/${id}/approve`);
  },
  rejectReplenishment(id, reason = null) {
    return this.post(`/analytics/replenishment/${id}/reject`, { reason });
  },
  updateGridCell(wh, x, y, cell_type, traversable, cost) {


    return this.put(`/pathfinding/warehouse/${encodeURIComponent(wh)}/grid/cell`, { x, y, cell_type, traversable, cost });
  },
  getGrid(wh) {
    return this.get(`/pathfinding/warehouse/${encodeURIComponent(wh)}/grid`);
  },
  createObstacle(wh, type, x, y, width, height, severity) {
    return this.post("/pathfinding/obstacles", { warehouse_id: wh, obstacle_type: type, x, y, width, height, severity });
  },
  deleteObstacle(id) {
    return this.delete(`/pathfinding/obstacles/${id}`);
  },
  getRobotRoute(id) {
    return this.get(`/pathfinding/robots/${id}/route`);
  },
  getRobotRouteHistory(id) {
    return this.get(`/pathfinding/robots/${id}/route/history`);
  },
  getDTState(wh) { return this.get(`/digital-twin/${wh}/state`); },
  getDTEvents(wh, severity, type, limit = 50, offset = 0) {
    let q = `?limit=${limit}&offset=${offset}`;
    if (severity) q += `&severity=${encodeURIComponent(severity)}`;
    if (type) q += `&event_type=${encodeURIComponent(type)}`;
    return this.get(`/digital-twin/${wh}/events${q}`);
  },
  getDTHeatmap(wh, metric) { return this.get(`/digital-twin/${wh}/heatmap?metric=${encodeURIComponent(metric)}`); },
  dtSimulationStart(wh, scenario = "NORMAL_OPERATIONS", seed = 42, speed = 1.0) {
    return this.post("/digital-twin/simulation/start", { warehouse_id: wh, scenario_type: scenario, seed, speed_multiplier: speed });
  },
  dtSimulationPause(simId) { return this.post(`/digital-twin/simulation/${simId}/pause`); },
  dtSimulationResume(simId) { return this.post(`/digital-twin/simulation/${simId}/resume`); },
  dtSimulationStep(simId) { return this.post(`/digital-twin/simulation/${simId}/step`); },
  dtSimulationStop(simId) { return this.post(`/digital-twin/simulation/${simId}/stop`); },
  dtSimulationReset(simId) { return this.post(`/digital-twin/simulation/${simId}/reset`); },
  dtSimulationGet(simId) { return this.get(`/digital-twin/simulation/${simId}`); },
  dtSimulationEvents(simId, severity, type, limit = 100, offset = 0) {
    let q = `?limit=${limit}&offset=${offset}`;
    if (severity) q += `&severity=${encodeURIComponent(severity)}`;
    if (type) q += `&event_type=${encodeURIComponent(type)}`;
    return this.get(`/digital-twin/simulation/${simId}/events${q}`);
  },
  dtSimulationMetrics(simId) { return this.get(`/digital-twin/simulation/${simId}/metrics`); },
  dtSimulationSnapshot(simId) { return this.post(`/digital-twin/simulation/${simId}/snapshot`); },
  dtSimulationSnapshots(simId) { return this.get(`/digital-twin/simulation/${simId}/snapshots`); },
  dtSimulationSpeed(simId, speed) { return this.patch(`/digital-twin/simulation/${simId}/speed`, { speed_multiplier: speed }); },

  // ---- Phase 10: Notifications & Preferences ----
  listNotifications(readFilter = null, category = "", severity = "", warehouseId = "", limit = 50, offset = 0) {
    let q = `?limit=${limit}&offset=${offset}`;
    if (readFilter !== null) q += `&read_filter=${readFilter}`;
    if (category) q += `&category=${encodeURIComponent(category)}`;
    if (severity) q += `&severity=${encodeURIComponent(severity)}`;
    if (warehouseId) q += `&warehouse_id=${encodeURIComponent(warehouseId)}`;
    return this.get(`/notifications${q}`);
  },
  getUnreadNotificationsCount() { return this.get("/notifications/unread-count"); },
  getNotification(id) { return this.get(`/notifications/${id}`); },
  markNotificationRead(id) { return this.post(`/notifications/${id}/read`, {}); },
  markNotificationUnread(id) { return this.post(`/notifications/${id}/unread`, {}); },
  dismissNotification(id) { return this.post(`/notifications/${id}/dismiss`, {}); },
  markAllNotificationsRead() { return this.post("/notifications/mark-all-read", {}); },
  getNotificationPreferences() { return this.get("/notification-preferences"); },
  updateNotificationPreferences(preferencesList) { return this.put("/notification-preferences", { preferences: preferencesList }); },
  getNotificationHistory(limit = 100, offset = 0, category = "", severity = "", channel = "", status = "") {
    let q = `?limit=${limit}&offset=${offset}`;
    if (category) q += `&category=${encodeURIComponent(category)}`;
    if (severity) q += `&severity=${encodeURIComponent(severity)}`;
    if (channel) q += `&channel=${encodeURIComponent(channel)}`;
    if (status) q += `&status=${encodeURIComponent(status)}`;
    return this.get(`/notification-history${q}`);
  },
  grantWarehouseAccess(userId, warehouseId) { return this.post("/admin/user-warehouse-access", { user_id: userId, warehouse_id: warehouseId }); },
  testEmailConfiguration() { return this.post("/notifications/test-email", {}); },
  getSettings() { return this.get("/api/settings"); },
  updateSettings(payload) { return this.post("/api/settings", payload); },
  getSystemHealth() { return this.get("/api/system/health"); },
  getHealthHistory(service, limit) { return this.get(`/api/system/health/history?service=${encodeURIComponent(service)}&limit=${limit}`); },
  getSystemIncidents() { return this.get("/api/system/incidents"); },
  resolveIncident(id) { return this.post(`/api/system/incidents/${id}/resolve`, {}); },
  getSystemThresholds() { return this.get("/api/system/thresholds"); },
  updateSystemThresholds(payload) { return this.put("/api/system/thresholds", payload); },
  runOrToolsBenchmark(wh) { return this.get(`/ai/optimize-scheduler?warehouse_id=${encodeURIComponent(wh)}`); },


  // ---- Phase 13: Scenario Lab & Experiments ----
  getScenarios(wh) { return this.get(`/scenarios${wh ? `?warehouse_id=${encodeURIComponent(wh)}` : ''}`); },
  createScenario(data) { return this.post('/scenarios', data); },
  getScenario(id) { return this.get(`/scenarios/${id}`); },
  updateScenario(id, data) { return this.put(`/scenarios/${id}`, data); },
  deleteScenario(id) { return this.delete(`/scenarios/${id}`); },
  duplicateScenario(id) { return this.post(`/scenarios/${id}/duplicate`); },
  getExperiments(scenId) { return this.get(`/scenarios/experiments/list${scenId ? `?scenario_id=${scenId}` : ''}`); },
  createExperiment(data) { return this.post('/scenarios/experiments', data); },
  getExperiment(id) { return this.get(`/scenarios/experiments/${id}`); },
  cancelExperiment(id) { return this.post(`/scenarios/experiments/${id}/cancel`); },
  rerunExperiment(id) { return this.post(`/scenarios/experiments/${id}/rerun`); },
  runPackingSimulation(data) { return this.post('/scenarios/packing-simulation', data); },

  // ---- Phase 11: SimPy Simulation Lab ----
  createSimulationRun(data) { return this.post('/simulation/runs', data); },
  getSimulationRuns(wh) { return this.get(`/simulation/runs${wh ? `?warehouse_id=${encodeURIComponent(wh)}` : ''}`); },
  getSimulationRun(id) { return this.get(`/simulation/runs/${id}`); },
  getSimulationResults(id) { return this.get(`/simulation/runs/${id}/results`); },
  getSimulationMetrics(id) { return this.get(`/simulation/runs/${id}/metrics`); },
  deleteSimulationRun(id) { return this.delete(`/simulation/runs/${id}`); },
  compareSimulationRuns(id, data) { return this.post(`/simulation/runs/${id}/compare`, data); },

  // ---- Phase 14: Real-Time, Observability & System Health ----
  getSystemHealth() { return this.get("/api/system/health"); },
  getSystemIncidents() { return this.get("/api/system/incidents"); },
  acknowledgeIncident(id) { return this.post(`/api/system/incidents/${id}/acknowledge`, {}); },
  resolveIncident(id) { return this.post(`/api/system/incidents/${id}/resolve`, {}); },
  getSystemThresholds() { return this.get("/api/system/thresholds"); },
  updateSystemThresholds(payload) { return this.put("/api/system/thresholds", payload); },
  getHealthHistory(service, limit = 30) { return this.get(`/api/system/health/history?service=${encodeURIComponent(service)}&limit=${limit}`); },

  // ---- Phase 3: Receiving & Shipping Operations ----
  receivingList(wh = "", status = "") {
    let q = "";
    if (wh) q += (q ? '&' : '?') + "warehouse_id=" + encodeURIComponent(wh);
    if (status) q += (q ? '&' : '?') + "status=" + encodeURIComponent(status);
    return this.get("/wms/receiving/shipments" + q);
  },
  receivingCreate(data) { return this.post("/wms/receiving/shipments", data); },
  receivingReceive(id, receivedQty) { return this.post(`/wms/receiving/shipments/${id}/receive`, { received_qty: receivedQty }); },
  receivingVerify(id) { return this.post(`/wms/receiving/shipments/${id}/verify`, {}); },
  receivingQC(id, qcResult) { return this.post(`/wms/receiving/shipments/${id}/qc`, { qc_result: qcResult }); },
  receivingPutaway(id, locationId) { return this.post(`/wms/receiving/shipments/${id}/putaway`, { location_id: locationId }); },

  shippingList(status = "") { return this.get(`/wms/shipments${status ? '?status=' + encodeURIComponent(status) : ''}`); },
  shippingCreate(orderId, carrier = "Standard Carrier", tracking = "") { return this.post("/wms/shipments", { order_id: orderId, carrier, tracking_reference: tracking }); },
  shippingShip(shipmentId) { return this.post(`/wms/shipments/${shipmentId}/ship`, {}); },
  shippingDeliver(shipmentId) { return this.post(`/wms/shipments/${shipmentId}/deliver`, {}); },

  // ---- Phase 4: Operational Ledger & Reconciliation ----
  getInventoryMovements(itemId = "", wh = "", type = "", page = 1, pageSize = 50) {
    let q = `?page=${page}&page_size=${pageSize}`;
    if (itemId) q += `&item_id=${encodeURIComponent(itemId)}`;
    if (wh) q += `&warehouse_id=${encodeURIComponent(wh)}`;
    if (type) q += `&movement_type=${encodeURIComponent(type)}`;
    return this.get(`/wms/inventory/movements${q}`);
  },
  getInventoryTrace(sku, wh = "") {
    let q = wh ? `?warehouse_id=${encodeURIComponent(wh)}` : "";
    return this.get(`/wms/inventory/trace/${encodeURIComponent(sku)}${q}`);
  },
  runReconciliationCheck() {
    return this.get("/wms/reconciliation/check");
  },

  // ---- Phase 5: Financial & Revenue System ----
  getFinancialRevenue(wh = "") {
    let q = wh ? `?warehouse_id=${encodeURIComponent(wh)}` : "";
    return this.get(`/wms/financial/revenue${q}`);
  },
  getFinancialRevenueHistory(wh = "", period = "daily") {
    let q = `?period=${period}`;
    if (wh) q += `&warehouse_id=${encodeURIComponent(wh)}`;
    return this.get(`/wms/financial/revenue/history${q}`);
  },
  getFinancialRevenueWarehouses() {
    return this.get("/wms/financial/revenue/warehouses");
  },
  getFinancialTransactions(wh = "", type = "", orderId = "", page = 1, limit = 50) {
    let q = `?page=${page}&limit=${limit}`;
    if (wh) q += `&warehouse_id=${encodeURIComponent(wh)}`;
    if (type) q += `&transaction_type=${encodeURIComponent(type)}`;
    if (orderId) q += `&order_id=${encodeURIComponent(orderId)}`;
    return this.get(`/wms/financial/transactions${q}`);
  },
  createRefund(orderId, amount, reason, refId = "") {
    return this.post("/wms/financial/refunds", { order_id: orderId, amount: parseFloat(amount), reason, reference_id: refId });
  },
};


