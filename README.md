# COOK FOR THE CODE

A cooking-and-programming event application using **FastAPI + MongoDB**. The project contains five participant levels, server-side scoring/timers, participant authentication, a separate admin dashboard, security-event logging and an isolated Docker runner for C/Python submissions.

## Project files

- `main.py` — FastAPI API, authentication, database access, timers, scoring and admin endpoints.
- `index.html` — participant game interface.
- `admin.html` — admin dashboard at `/admin`.
- `content.py` — level 2–5 challenge content and scoring helpers.
- `runner.py` — fail-closed Docker code runner (no local execution fallback).
- `Dockerfile.runner` — image definition for the isolated compiler/runtime.
- `test_flow.py`, `test_levels.py` — API and gameplay regression tests.

## Requirements

- Python 3.10+
- MongoDB 6+ (local or hosted)
- Docker Engine/Desktop for Level 4 code execution

## Setup (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:MONGO_URL = "mongodb://localhost:27017"
$env:ADMIN_USER = "admin"
$env:ADMIN_PASSWORD = "Set-A-Strong-Unique-Password"
$env:JWT_SECRET = "replace-with-a-long-random-secret-at-least-32-characters"
$env:SEED_DATA = "1"
```

Start MongoDB before starting the app. Then build the isolated runner image:

```powershell
docker build -f Dockerfile.runner -t cftc-runner:latest .
$env:RUNNER_IMAGE = "cftc-runner:latest"
```

Start the website:

```powershell
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open participant site: http://127.0.0.1:8000  
Open admin dashboard: http://127.0.0.1:8000/admin

## Sample accounts

With `SEED_DATA=1`, first startup creates 25 sample teams:

- Team IDs: `CFC001` through `CFC025`
- Passwords: `chef001` through `chef025`
- Admin username/password: values configured in `ADMIN_USER` and `ADMIN_PASSWORD`

These are development credentials only. Change or remove sample teams before a real event. Do not use the sample passwords for a public deployment. Admin login is not exposed on the participant page.

The admin password is also used as the participant fullscreen-verification password in this build. Keep it private and use a strong unique value. For a production event, use a separate invigilator verification credential and rotate it after the event.

## Tests

Install dependencies, then run:

```powershell
python test_flow.py
python test_levels.py
```

The tests use `mongomock` and a deterministic fake runner for test isolation. They verify API behavior and game logic; **they do not prove real MongoDB deployment, Docker isolation or browser compatibility**. Run a separate staging test with real MongoDB and Docker before the event.

## Five levels

1. **Taste Test** — 10 programming/cooking MCQs.
2. **Mystery Ingredients** — logic, clues and sequence MCQs.
3. **Recipe Decoder** — arrange C/Python code blocks.
4. **Code Kitchen** — write, run and submit C/Python code against hidden tests.
5. **Master Chef** — arrange a virtual recipe and corresponding code.

## Code runner security

Level 4 intentionally **fails closed** if Docker is unavailable; participant code is never executed as a child process on the FastAPI host. Build `Dockerfile.runner` and set `RUNNER_IMAGE=cftc-runner:latest`. The runner disables networking, drops Linux capabilities, uses a read-only root filesystem, applies memory/CPU/PID limits, and executes as an unprivileged user. Docker isolation is not a substitute for a dedicated hardened execution service. Keep Docker patched and do not expose its daemon socket to participants.

## Important limitations / event checklist

- Fullscreen and tab-switch detection are browser deterrents, not tamper-proof kiosk controls. Participants can still use OS-level shortcuts or another device.
- Admin pause/resume freezes the server-side round timer and preserves remaining time.
- The admin dashboard supports team creation/deletion, unlock, pause/resume, reset, event start/end, security logs, submissions and CSV export. Question/timer editing is not yet exposed in the dashboard; edit `QUESTIONS`, `content.py` and `LEVELS` before the event if needed.
- Leaderboard refreshes by polling every 5 seconds rather than WebSockets.
- The participant editor is a functional plain text editor, not a full IDE with syntax highlighting.
- Test the complete workflow in the actual target browsers and network. Confirm Docker runner availability and run a C and Python sample before admitting participants.
- Use HTTPS, a strong persistent `JWT_SECRET`, private MongoDB credentials, backups and a firewall for any hosted deployment.
