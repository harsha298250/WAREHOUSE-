# PHASE 22 — FAILURE RECOVERY MATRIX
## Smart Warehouse Intelligence Platform

**Phase**: 22 — Failure, Stress, Performance & Resilience Testing  
**Date**: 2026-08-22  
**Principle**: FAILURE MUST NEVER TURN INTO FABRICATED DATA.

---

## 1. Dependency Failure Recovery Overview

| Dependency | Failure Mode | Detection | Recovery Action | Fabricated Data? | Verified By |
|---|---|---|---|---|---|
| **PostgreSQL** | Unreachable | Connection timeout / pool exhaustion | HTTP 500 returned; no silent fallback | ❌ Never | Architecture review |
| **PostgreSQL** | Slow query / deadlock | SQLAlchemy exception | Transaction rollback; 500 or 409 returned | ❌ Never | `test_concurrent_orders_locking` |
| **Redis** | Unreachable / offline | `get_redis_client()` returns `None` | Cache bypass; DB used as source of truth | ❌ Never | `test_redis_offline_resilience` |
| **Redis** | Write failure | `set_cache()` returns `False` | Log warning; operation continues without cache | ❌ Never | `test_redis_offline_resilience` |
| **RabbitMQ** | Unreachable / offline | `get_channel()` returns `None` | `publish_event()` logs locally; returns `False` | ❌ Never | `test_rabbitmq_offline_resilience` |
| **RabbitMQ** | Message loss | No confirmation | Caller receives `False`; no silent retry | ❌ Never | `backend/mq_client.py` review |
| **Celery** | Worker offline | Task not consumed | Queue persists in broker; no UI lie | ❌ Never | Architecture review |
| **Gemini AI** | HTTP error / timeout | `httpx.AsyncClient.post` exception | `offline_assistant_reply()` rule-based fallback | ❌ Never | `test_gemini_outage_resilience` |
| **Gemini AI** | Rate limit (429) | HTTP 429 response | HTTP 429 propagated to client | ❌ Never | `backend/services/ai_service.py` |
| **Backblaze B2** | Upload failure | `httpx` exception | Exception logged; backup record marked FAILED | ❌ Never | Architecture review |
| **Backblaze B2** | Auth failure | 401 response | `BackupRecord.status = "FAILED"` | ❌ Never | Architecture review |
| **Resend (email)** | Unreachable | `httpx` exception | Logged; no UI claim of sent | ❌ Never | Architecture review |
| **Sentry** | Unreachable | SDK swallows error silently | Application continues normally | N/A | Third-party SDK behaviour |
| **SSE stream** | Client disconnect | `asyncio.CancelledError` | Stream generator exits cleanly | ❌ Never | Architecture review |

---

## 2. Redis Offline — Detailed Recovery Flow

```
GET /wms/inventory (cached path)
  │
  ├─ get_redis_client() → None  (Redis offline)
  │
  ├─ get_cache("inventory:WH-BLR-01") → None  (bypass, no error raised)
  │
  └─ DB query executed → real data returned to client
```

**Test**: `test_redis_offline_resilience`  
**Result**: `get_cache()` returns `None`; `set_cache()` returns `False`. No exception, no fabricated value.

---

## 3. RabbitMQ Offline — Detailed Recovery Flow

```
publish_event("ORDER_COMPLETED", "orders", {...})
  │
  ├─ get_channel() → None  (RabbitMQ offline)
  │
  ├─ Logger.warning("MQ offline, event not published: ORDER_COMPLETED")
  │
  └─ returns False  ← caller aware of non-delivery
```

**Test**: `test_rabbitmq_offline_resilience`  
**Result**: Returns `False`. No silent claim of delivery. No fabricated queue acknowledgement.

---

## 4. Gemini AI Offline — Detailed Recovery Flow

```
POST /ai/assistant {"message": "Show me inventory"}
  │
  ├─ GeminiService.run_ai_chat()
  │     │
  │     ├─ httpx.AsyncClient.post() → Exception("Simulated Gemini Outage")
  │     │
  │     ├─ logger.error("Failed to reach Gemini API: ...")
  │     │
  │     └─ offline_assistant_reply(db, message, warehouse_id)
  │           │
  │           └─ Rule-based keyword analysis → real DB query → structured reply
  │
  └─ HTTP 200 returned with:
       {"status": "success",
        "engine": "Fallback Rule-Based (API Error)",
        "response": "...(real DB data)...\n\n*(Fallback mode triggered...)*"}
```

**Test**: `test_gemini_outage_resilience`  
**Result**: HTTP 200, fallback reply contains real DB data, engine clearly labelled as fallback. No invented inventory numbers.

---

## 5. Inventory Reservation Contention — Concurrent Locking

```
8 concurrent order requests → WH-STRESS (10 units stock, 2 per order)
  │
  ├─ Orders 1–5: SELECT FOR UPDATE → reserve 2 each → committed → RESERVED
  │
  ├─ Orders 6–8: SELECT FOR UPDATE → available=0 → shortage → INVENTORY_SHORTAGE
  │
  └─ Final state: reserved=10, available=0  ← consistent, no double-reservation
```

**Test**: `test_concurrent_orders_locking`  
**Result**: At most 5 RESERVED, at least 3 INVENTORY_SHORTAGE. Inventory arithmetic consistent.

---

## 6. Pathfinding Failure Recovery

| Failure Scenario | A* Behaviour | Return Value | Error Fabricated? |
|---|---|---|---|
| Goal cell unreachable (all neighbours blocked) | Full exhaustion of reachable graph | `path=None`, descriptive message | ❌ Never |
| Start cell non-traversable | Immediate exit | `path=None`, "non-traversable start" | ❌ Never |
| Same start and goal | Zero-hop path returned | `path=[start]`, cost=0 | ❌ Never |

**Test**: `test_astar_pathfinding_failures`
