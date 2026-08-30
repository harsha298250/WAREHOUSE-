# Phase 14 Optional AI Security Hardening

This document registers the security specifications, sandbox protections, and injection attack defenses implemented for Phase 14 optional AI features.

## 1. Sandbox Code Execution Security
The python calculation tool (`execute_python_calculation`) enforces absolute security:
- **Keyword Blacklisting**: Instantly rejects calculations containing unsafe keywords like `import`, `open`, `eval`, `exec`, `getattr`, `globals`, `locals`, `os`, `sys`, `subprocess`, `builtins`, and `__`.
- **Global Context Sanitization**: Evaluates equations in a sandbox with `__builtins__` disabled (`{"__builtins__": None}`) and limits scope to safe arithmetic libraries (`math`, `abs`, `round`, `sum`, `len`, `min`, `max`, `pow`).

## 2. RAG File Isolation
- Document reading (`read_warehouse_document`) prevents traversal attacks (e.g. `filename=../database.py`) by checking for directory traversal structures and throwing `HTTPException(400)`.
- RAG document matching operates strictly on flat files stored inside the `docs/` folder, completely isolated from WMS database credentials.

## 3. Prompt Injection Defense
- System instructions force the model to treat retrieved documents and user-provided inputs strictly as data values, preventing injection overrides.
- Loops are strictly bounded to 3 iterations and a maximum of 8 tool calls per prompt execution to prevent recursive loop attacks.
