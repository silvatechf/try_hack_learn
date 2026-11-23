# SentinelForge

Interactive Security Engineering Laboratory & Continuous Security Validation Platform.

## 1. Prerequisites

* Docker Desktop with Docker Compose

## 2. Startup

```powershell
docker compose up -d --build

```

## 3. Verification

```powershell
docker compose ps

```

Expected active services:

* `frontend`
* `orchestrator`
* `target_api`
* `python_lab`
* `python_lab_executor`

## 4. Local URLs

* **Frontend:** `http://localhost:3001`
* **Orchestrator API:** `http://localhost:8000`
* **Target API Sandbox:** `http://localhost:8001`
* **Python Lab API:** `http://localhost:8002`

## 5. Minimum Validation Workflow

1. **Home / Learning Map:** Open `http://localhost:3001` to view the curriculum domains and missions.
2. **Mission Execution:** Select a mission, place defensive controls into the architecture stack, and execute sandbox validation.
3. **Python Lab:** Switch to the Python Lab via the navigation bar.
4. **Code Execution:** Select exercise `PY-001`, edit or complete the code implementation, and run code.
5. **Result:** Inspect test evaluation outcomes and execution results.

## 6. Executor Architecture Note

* `python_lab_executor` is an internal backend service operating on port `8003`.
* It does not need to be published to the host machine for normal application flow.

## 7. Troubleshooting

* **If the Python Lab execution fails or hangs:** Verify that the `python_lab_executor` container is running via `docker compose ps`.
* **If the Home / Learning Map fails to load missions:** Verify that the `orchestrator` service is running and accessible at port `8000`.

