# docs/FINAL_DEMO_CHECKLIST.md — Final Demo Checklist

Use this checklist during final presentations to verify system readiness.

---

- [x] **FastAPI Application Starts**: Health API endpoint returns 200.
- [x] **Auth & Login Flow**: Issuing JWT token works, route guards throw 401 on unauthorized access.
- [x] **Dashboard Telemetry**: KPIs load dynamically from PostgreSQL records.
- [x] **Warehouse Selection**: Map coordinates and current Open-Meteo weather fetch successfully.
- [x] **Inventory Reservation**: Available stock and reserved calculations correct (`available = on_hand - reserved`).
- [x] **SELECT FOR UPDATE locks**: Stock mutations serialize correctly under concurrency stress tests.
- [x] **Robot Grid Pathfinder**: A* routing path lists generated with zone costs constraints.
- [x] **Three.js Digital Twin**: Digital Twin visualization updates live via SSE streams events.
- [x] **Scikit-Learn Anomaly Classifier**: Isolation Forest rolling sales anomalies calculated.
- [x] **Gemini Assistant registry**: Prompt injection block filters and tools execution verify safely.
- [x] **Disaster Recovery**: Automatic database backups schedule and log successfully.
- [x] **System Health Telemetry**: Threshold check triggers logs when violations occur.
