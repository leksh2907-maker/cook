# Corrected project changes

- Fixed `/` to serve the actual root `index.html` and added `/admin` for the new admin dashboard.
- Added admin overview and submissions endpoints and a functional dashboard for team management, event controls, logs and CSV export.
- Added pause/resume timer preservation on the server and periodic participant timer synchronization.
- Added stricter validation for level IDs, submissions, team records and admin actions.
- Preserved compatibility with password hashes from the first project version while using stronger hashes for new credentials.
- Changed code execution to fail closed when Docker is unavailable; removed the unsafe local-process fallback.
- Added a Docker runner image definition with no network, read-only root, dropped capabilities, unprivileged UID, memory/CPU/PID limits and a per-run timeout.
- Fixed a test that previously allowed level skipping because of `or True`.
- Expanded setup documentation and added `.env.example` and `.gitignore`.

## Validation performed in this workspace

- Python files passed `compileall` syntax compilation.
- Participant and admin inline JavaScript passed `node --check`.
- Challenge content scoring helpers were checked with deterministic sample inputs.
- Full FastAPI/MongoDB integration tests could not be executed here because this workspace has no network access to install `pymongo` and `mongomock`, and no MongoDB/Docker services. Run the included test scripts after installing `requirements.txt` and before event day.
