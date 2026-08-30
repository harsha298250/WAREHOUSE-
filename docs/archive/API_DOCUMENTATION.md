# API_DOCUMENTATION.md — Smart Warehouse Intelligence Platform

All endpoints require JWT bearer tokens passed in the `Authorization` header unless labeled otherwise.

---

## 1. Authentication Endpoints

### POST `/auth/login`
* **Purpose**: Authenticate using username and password. Returns JWT token.
* **Authentication**: None (Public)
* **Request Example**:
  ```json
  {
    "username": "admin",
    "password": "Admin@123"
  }
  ```
* **Response Example (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "token_type": "bearer",
    "role": "admin",
    "username": "admin"
  }
  ```
* **Error Cases**:
  - `401 Unauthorized`: Invalid credentials
  - `429 Too Many Requests`: Login rate limit reached

### POST `/auth/google-signin`
* **Purpose**: Authenticate using Google OAuth 2.0 credential token.
* **Authentication**: None (Public)
* **Request Example**:
  ```json
  {
    "id_token": "ya29.a0AfB_..."
  }
  ```
* **Response Example (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1Ni...",
    "token_type": "bearer",
    "role": "viewer",
    "username": "google_user_123"
  }
  ```

### GET `/auth/me`
* **Purpose**: Retrieve current logged-in user profile.
* **Authentication**: Required (JWT Bearer)
* **Response Example (200 OK)**:
  ```json
  {
    "username": "admin",
    "role": "admin",
    "full_name": "Warehouse Admin"
  }
  ```

---

## 2. Inventory & Warehouse Endpoints

### GET `/warehouses`
* **Purpose**: List all warehouses.
* **Authentication**: Required
* **Response Example (200 OK)**:
  ```json
  [
    {
      "id": "WH-BLR-01",
      "name": "Bangalore Central",
      "location": "Karnataka, IN",
      "latitude": 12.9716,
      "longitude": 77.5946
    }
  ]
  ```

### POST `/warehouses`
* **Purpose**: Register a new warehouse.
* **Required Role**: `admin` or `manager`
* **Request Example**:
  ```json
  {
    "id": "WH-CHN-01",
    "name": "Chennai North",
    "location": "Tamil Nadu, IN",
    "latitude": 13.0827,
    "longitude": 80.2707
  }
  ```

### GET `/inventory/{warehouse_id}`
* **Purpose**: Retrieve current stock levels for a specific warehouse.
* **Authentication**: Required
* **Response Example (200 OK)**:
  ```json
  [
    {
      "item_id": "ITM001",
      "item_name": "Industrial Sensor Model B",
      "category": "Electronics",
      "current_stock": 234,
      "safety_stock": 50,
      "unit_cost": 120.0
    }
  ]
  ```

---

## 3. Machine Learning & Forecasting Endpoints

### GET `/forecast/{warehouse_id}/{item_id}`
* **Purpose**: Fetch 14-day demand forecast for an item, complete with backtest WAPE validation.
* **Authentication**: Required
* **Response Example (200 OK)**:
  ```json
  {
    "status": "success",
    "warehouse_id": "WH-BLR-01",
    "item_id": "ITM001",
    "item_name": "Sensor B",
    "current_stock": 234,
    "forecast_values": [215, 210, 204, 199, 195, 192],
    "lead_time_days": 3,
    "lead_time_demand": 38.5,
    "safety_stock": 50,
    "needs_reorder": false,
    "backtest_validation": {
      "wape_pct": 14.8,
      "mae": 4.2,
      "rmse": 5.8
    }
  }
  ```

### GET `/shrinkage/anomalies`
* **Purpose**: List active stock discrepancy anomalies flagged by IsolationForest.
* **Authentication**: Required
* **Response Example (200 OK)**:
  ```json
  [
    {
      "date": "2026-08-12",
      "warehouse_id": "WH-BLR-01",
      "item_id": "ITM001",
      "item_name": "Sensor B",
      "discrepancy": -12,
      "severity": "HIGH",
      "estimated_exposure": 1440.0,
      "explanation": "Stock dropped by 12 units without a corresponding recorded stock movement."
    }
  ]
  ```

---

## 4. AI Decision Center Endpoints

### GET `/ai/decision-center`
* **Purpose**: List all pending, approved, and rejected AI recommendations.
* **Authentication**: Required
* **Response Example (200 OK)**:
  ```json
  [
    {
      "id": 14,
      "timestamp": "2026-08-14T08:00:00Z",
      "warehouse_id": "WH-BLR-01",
      "item_id": "ITM001",
      "title": "Low Stock Warning (Lead-Time Demand)",
      "risk_level": "HIGH",
      "action_recommended": "Generate Reorder Purchase Request for 150 units",
      "confidence_score": 88,
      "input_factors": "{\"current_stock\": 12, \"lead_time_demand\": 45}",
      "status": "PENDING",
      "decision_by": "",
      "decision_time": null,
      "notes": ""
    }
  ]
  ```

### POST `/ai/recommendations/{id}/action`
* **Purpose**: Record human manager decision (Approve, Reject, Modify) for a recommendation.
* **Required Role**: `admin` or `manager`
* **Request Example**:
  ```json
  {
    "action": "APPROVED",
    "notes": "Purchase request authorized and sent to vendor."
  }
  ```
* **Response Example (200 OK)**:
  ```json
  {
    "status": "success",
    "message": "Recommendation #14 APPROVED by admin. Stock movement synchronized."
  }
  ```

---

## 5. Trust Ledger Endpoints

### GET `/audit/verify`
* **Purpose**: Recalculate linear SHA-256 hash chains to check for offline modifications.
* **Authentication**: Required
* **Response Example (200 OK - Verified)**:
  ```json
  {
    "valid": true,
    "records_checked": 154,
    "message": "Audit ledger integrity verified across 154 records."
  }
  ```

---

## 6. Reports & Health Check Endpoints

### GET `/reports/export`
* **Purpose**: Export CSV, XLSX, or PDF inventory summaries.
* **Authentication**: Required (Accepts `?token=...` or `Authorization: Bearer <token>`)
* **Response**: Binary stream of the requested file format.

### GET `/health`
* **Purpose**: Liveliness indicator for container health checks.
* **Authentication**: None (Public)
* **Response Example (200 OK)**:
  ```json
  {
    "status": "healthy",
    "database": "connected",
    "version": "3.0",
    "timestamp": "2026-08-14T10:24:26Z"
  }
  ```
