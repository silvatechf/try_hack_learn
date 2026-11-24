# Python Lab frontend integration

## Scope

The Python Lab frontend uses a configurable API base URL and a small API client module to keep transport handling separate from the React view.

The frontend:

- Loads the exercise catalog and reports loading or service errors.
- Preserves the existing exercise selection and guided/assisted/free-code flow.
- Enforces the backend's 10,000-character student-code limit in the editor and API client.
- Handles unsuccessful HTTP responses and malformed response payloads without rendering an empty result panel.
- Displays the technical execution status separately from the pedagogical outcome, including output-limit and timeout outcomes.
- Keeps user-facing messages localized in English and Spanish.

## API configuration

Set `VITE_PYTHON_LAB_API_URL` to the browser-reachable Python Lab API base URL. The local Compose configuration uses:

```text
http://localhost:8002/api/v1/python-lab
```

The value is a Vite client-side setting. It is not a secret and must point to an address reachable from the learner's browser, not an internal Compose-only hostname.

## Local checks

From the repository root:

```powershell
cd frontend
npm ci
npm test
npm run build
cd ..
docker compose build frontend
docker compose up -d frontend python_lab python_lab_executor
```

Then verify in the browser at `http://localhost:3001`:

1. The Python Lab catalog loads and `PY-001` is selectable.
2. A correct `PY-001` solution displays technical status `EXECUTED`, all test results, and pedagogical outcome `MASTERED`.
3. An output-overflow submission displays `OUTPUT_LIMIT_EXCEEDED` and the corresponding localized technical explanation.
4. Stopping the Python Lab API produces a visible service error; restarting it and retrying restores catalog/execution behavior.
5. Switch between English and Spanish and confirm the new messages are translated.

## Verification status

**IMPLEMENTED; LOCAL FRONTEND BUILD AND BROWSER FLOW NOT YET VERIFIED.**

The API client tests are designed for Node.js 20's built-in test runner. They do not replace a browser-level end-to-end check.

## Remaining boundaries

- The frontend API URL is configuration, not authentication.
- CORS and backend authentication/network boundaries remain tracked separately.
- Client-side character limits improve UX but do not replace server-side request/body limits.
