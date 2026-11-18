"""Five-level gameplay and admin pause/resume regression tests."""
import os
os.environ["MONGO_URL"] = "mock"
os.environ["ADMIN_USER"] = "admin"
os.environ["ADMIN_PASSWORD"] = "adminpw"
os.environ["JWT_SECRET"] = "test-secret-not-for-production"

from fastapi.testclient import TestClient
import content
import main

# Deterministic stand-in for the isolated runner in automated unit tests only.
def fake_run(lang, code, stdin=""):
    if "while True" in code:
        return {"ok": False, "stdout": "", "stderr": "Time limit exceeded", "stage": "timeout"}
    if "bad syntax" in code:
        return {"ok": False, "stdout": "", "stderr": "SyntaxError", "stage": "compile"}
    try:
        a, b = map(int, stdin.split())
        return {"ok": True, "stdout": str(a + b), "stderr": "", "stage": "run"}
    except Exception:
        return {"ok": False, "stdout": "", "stderr": "Invalid input", "stage": "run"}

main.runner.run = fake_run
c = TestClient(main.app)
H = lambda t: {"Authorization": f"Bearer {t}"}
a = c.post("/api/admin/login", json={"id": "admin", "password": "adminpw"}).json()["token"]
c.post("/api/admin/event/start", headers=H(a))
t = c.post("/api/login", json={"id": "CFC002", "password": "chef002"}).json()["token"]

def start(n):
    r = c.post(f"/api/level/{n}/start", headers=H(t))
    assert r.status_code == 200, (n, r.text)
    return r.json()

def submit(n, answers):
    r = c.post(f"/api/level/{n}/submit", headers=H(t), json={"answers": answers})
    assert r.status_code == 200, (n, r.text)
    return r.json()["score"]

start(1)
assert submit(1, {str(q["idx"]): q["answer"] for q in main.db.questions.find({"level": 1})}) == 100
assert c.post("/api/level/3/start", headers=H(t)).status_code == 403
start(2)
assert submit(2, {str(q["idx"]): q["answer"] for q in main.db.questions.find({"level": 2})}) == 120
r3 = start(3)
assert len(r3["challenges"]) == 3 and "correct" not in str(r3)
assert submit(3, {x["id"]: next(ch["correct"] for ch in content.L3 if ch["id"] == x["id"]) for x in r3["challenges"]}) == 100
r4 = start(4)
assert r4["problem"]["sample"]["out"] == "5"
assert c.post("/api/level/4/run", headers=H(t), json={"lang": "python", "code": "print(1)", "stdin": "2 3"}).json()["stdout"] == "5"
assert c.post("/api/level/4/run", headers=H(t), json={"lang": "python", "code": "while True: pass"}).json()["stage"] == "timeout"
c_code = '#include <stdio.h>\nint main(){int a,b;scanf("%d %d",&a,&b);printf("%d",a+b);return 0;}'
assert submit(4, {"lang": "c", "code": c_code}) == 100
r5 = start(5)
assert {p["kind"] for p in r5["parts"]} == {"recipe", "code"}
assert submit(5, {"a": content.L5A["correct"], "b": content.L5B["correct"]}) == 100
assert c.get("/api/leaderboard").json()[0]["score"] == 520

# A paused team cannot run/submit; pause stores remaining time and resume shifts start time.
t2 = c.post("/api/login", json={"id": "CFC003", "password": "chef003"}).json()["token"]
assert c.post("/api/level/3/start", headers=H(t2)).status_code == 403
assert c.post("/api/admin/teams/CFC003/unlock", headers=H(a)).json()["unlocked"] == 2
c.post("/api/level/1/start", headers=H(t2))
assert c.post("/api/admin/teams/CFC003/pause/1", headers=H(a)).json()["paused"] is True
assert c.post("/api/level/1/submit", headers=H(t2), json={"answers": {}}).status_code == 403
assert c.post("/api/admin/teams/CFC003/pause/0", headers=H(a)).json()["paused"] is False
print("ALL FIVE LEVEL TESTS PASSED")
