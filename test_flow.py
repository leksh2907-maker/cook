"""Core API regression tests. Run with: python test_flow.py"""
import os
os.environ["MONGO_URL"] = "mock"
os.environ["ADMIN_USER"] = "admin"
os.environ["ADMIN_PASSWORD"] = "adminpw"
os.environ["JWT_SECRET"] = "test-secret-not-for-production"

from fastapi.testclient import TestClient
from main import app, db

client = TestClient(app)
H = lambda token: {"Authorization": f"Bearer {token}"}
admin = client.post("/api/admin/login", json={"id": "admin", "password": "adminpw"}).json()["token"]
assert len(client.get("/api/admin/teams", headers=H(admin)).json()) == 25
team = client.post("/api/login", json={"id": "CFC001", "password": "chef001"}).json()["token"]
assert client.post("/api/login", json={"id": "CFC001", "password": "wrong"}).status_code == 401
assert client.get("/api/admin/teams", headers=H(team)).status_code == 403
assert client.post("/api/level/1/start", headers=H(team)).status_code == 403
client.post("/api/admin/event/start", headers=H(admin))
started = client.post("/api/level/1/start", headers=H(team))
assert started.status_code == 200 and len(started.json()["questions"]) == 10
assert "answer" not in started.text
correct = {str(q["idx"]): q["answer"] for q in db.questions.find({"level": 1})}
assert client.post("/api/level/1/submit", headers=H(team), json={"answers": correct}).json()["score"] == 100
assert client.post("/api/level/1/submit", headers=H(team), json={"answers": correct}).status_code == 409
assert client.post("/api/level/3/start", headers=H(team)).status_code == 403
client.post("/api/security/event", headers=H(team), json={"kind": "tab_switch"})
assert client.post("/api/security/verify", headers=H(team), json={"password": "bad"}).status_code == 403
assert client.post("/api/security/verify", headers=H(team), json={"password": "adminpw"}).status_code == 200
assert len(client.get("/api/admin/security-logs", headers=H(admin)).json()) == 3
assert client.get("/api/admin/overview", headers=H(admin)).json()["teams"] == 25
assert client.get("/api/admin/submissions", headers=H(admin)).status_code == 200
assert "CFC001" in client.get("/api/admin/export.csv", headers=H(admin)).text
assert client.get("/").status_code == 200
assert client.get("/admin").status_code == 200
assert client.delete("/api/admin/sample-data", headers=H(admin)).json()["removed"] == 25
print("CORE API TESTS PASSED")
