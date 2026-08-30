# Phase 20 Warning Audit

## Initial Warning Count

8 (Discovered in Phase 20 test suite run) + 1 (Discovered in wider regression suite run)

## Discovery Results

| ID | Type | File | Line | Cause | Severity | Action | Status |
|----|------|------|------|-------|----------|--------|--------|
| 1 | `StarletteDeprecationWarning` | `fastapi/testclient.py` | 1 | Starlette internal test client import deprecation | LOW | None (Third-party) | Harmless Third-Party |
| 2 | `SADeprecationWarning` | `backend/models.py` | 685 | Late dynamic override of `OTPRecord.user` relationship | MEDIUM | Define relationship in class scope and delete dynamic override | **FIXED** |
| 3 | `SADeprecationWarning` | `backend/models.py` | 686 | Late dynamic override of `UserSession.user` relationship | MEDIUM | Define relationship in class scope and delete dynamic override | **FIXED** |
| 4 | `PendingDeprecationWarning` | `sentry_sdk/integrations/starlette.py` | 60 | Sentry Starlette integration import deprecation | LOW | None (Third-party) | Harmless Third-Party |
| 5 | `PydanticDeprecatedSince20` | `backend/routers/robots.py` | 53 | Deprecated `example` Field parameter | MEDIUM | Use `json_schema_extra={"example": ...}` | **FIXED** |
| 6 | `PydanticDeprecatedSince20` | `backend/routers/robots.py` | 54 | Deprecated `example` Field parameter | MEDIUM | Use `json_schema_extra={"example": ...}` | **FIXED** |
| 7 | `PydanticDeprecatedSince20` | `backend/routers/robots.py` | 55 | Deprecated `example` Field parameter | MEDIUM | Use `json_schema_extra={"example": ...}` | **FIXED** |
| 8 | `FastAPIDeprecationWarning` | `backend/routers/scenarios.py` | 463 | Deprecated `regex` parameter in FastAPI Query | MEDIUM | Use `pattern` instead | **FIXED** |
| 9 | `DeprecationWarning` | `tests/test_input_validation.py` | 73 | Deprecated HTTPX `data` param for raw string POST | LOW | Use `content` instead | **FIXED** |

---

## Warnings Fixed

1. **SQLAlchemy ORM Mapping overrides**: Declared direct `back_populates` relationship mappings within class declarations for `OTPRecord` and `UserSession` in [`backend/models.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/models.py) and removed late dynamic overriding assignments at the bottom of the file.
2. **Pydantic schema warnings**: Replaced deprecated `example` parameter with `json_schema_extra` configuration block for `robot_code`, `name`, and `warehouse_id` inside `RobotCreateSchema` inside [`backend/routers/robots.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/routers/robots.py).
3. **FastAPI Query warning**: Replaced deprecated `regex` argument with `pattern` argument inside the export endpoint Query param of [`backend/routers/scenarios.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/backend/routers/scenarios.py).
4. **HTTPX deprecation in tests**: Updated the raw string payload key from `data=` to `content=` inside `test_malformed_json_returns_422` of [`tests/test_input_validation.py`](file:///c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/tests/test_input_validation.py).

---

## Warnings Remaining

0 application warnings remaining.

Only **2 third-party warnings** remain, both originating internally within vendor packages and outside of application control:
* `StarletteDeprecationWarning` (FastAPI TestClient Starlette import setup)
* `PendingDeprecationWarning` (Sentry SDK Starlette integration setup)

---

## Validation

* **Phase 20 Warnings-As-Errors Run**:
  `5 passed, 0 warnings treated as errors`
* **Full Regression Suite**:
  `350 passed, 21 skipped, 1 xfailed, 2 warnings (third-party)`
* **Failures**:
  `0 failures`
