# docs/FINAL_SYSTEM_ARCHITECTURE.md — System Architecture Description

This document describes the final production architecture topology and dataflow layers.

---

## 1. System Topology

```mermaid
graph TD
    User([Users / Operators]) -->|HTTPS / WSS| Frontend[Vite Static HTML/JS Frontend]
    Frontend -->|REST API Request / SSE Connection| Backend[FastAPI Backend Web Service]
    Backend -->|SELECT FOR UPDATE Lock| DB[(PostgreSQL Database)]
    Backend -->|Get/Set Cache & Rate Limits| Redis[(Upstash Redis Cache)]
    Backend -->|Publish Event| Broker[(RabbitMQ Message Broker)]
    Broker -->|Fetch task| Worker[Celery Background Tasks Worker]
    Worker -->|Read/Write state| DB
    
    subgraph Core Services
        Backend -->|Run A* search| Pathfinder[A* Pathfinder]
        Backend -->|Optimize schedules| Solver[OR-Tools CP-SAT Solver]
        Backend -->|Query AI context| Gemini[Gemini LLM Registry Service]
        Backend -->|Isolation Forest| ML[Scikit-Learn ML Engines]
    end
    
    subgraph External Connections
        Backend -->|Fetch weather| Weather[Open-Meteo API]
        Backend -->|Logical backup| B2[Backblaze B2 Storage]
        Backend -->|Alert logs| Sentry[Sentry SDK]
    end
```

---

## 2. Component Descriptions

### Source of Truth
- **PostgreSQL**: Stores relational models (Users, Warehouses, Items, Inventory, Orders, Tasks, Robots, AccessLogs). Uses row-locking transactions to maintain ACID safety.

### Messaging & Scheduling
- **RabbitMQ / Celery**: Decouples async workflows (order status logs, backups, analytics triggers).
- **Redis**: Rate limiter, transient caches, session tokens.

### Visualization & Sync
- **Server-Sent Events (SSE)**: Streams increment coordinates updates from the robot queue simulator directly to the Three.js dashboard canvas.
