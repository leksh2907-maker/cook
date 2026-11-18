"""Fail-closed Docker runner for participant code. No unsafe local execution fallback."""
import os
import shutil
import subprocess
import tempfile

IMAGE = os.getenv("RUNNER_IMAGE", "cftc-runner:latest")
TIME_LIMIT = int(os.getenv("RUNNER_TIMEOUT_SECONDS", "5"))
MAX_CODE = 20_000
MAX_STDIN = 10_000


def run(lang, code, stdin=""):
    if lang not in ("c", "python"):
        return {"ok": False, "stdout": "", "stderr": "Choose C or Python", "stage": "validation"}
    if not isinstance(code, str) or len(code) > MAX_CODE:
        return {"ok": False, "stdout": "", "stderr": "Code is too large", "stage": "validation"}
    if not isinstance(stdin, str) or len(stdin) > MAX_STDIN:
        return {"ok": False, "stdout": "", "stderr": "Input is too large", "stage": "validation"}
    docker = shutil.which("docker")
    if not docker:
        return {"ok": False, "stdout": "", "stderr": "Code runner unavailable: Docker is not installed. Ask the organiser to configure the isolated runner.", "stage": "unavailable"}

    with tempfile.TemporaryDirectory(prefix="cftc_") as work:
        filename = "main.c" if lang == "c" else "main.py"
        path = os.path.join(work, filename)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(code)
        os.chmod(work, 0o755)
        os.chmod(path, 0o644)
        command = "timeout --signal=KILL 5s sh -lc 'gcc -O2 -std=c11 main.c -o /tmp/cfc-program && /tmp/cfc-program'" if lang == "c" else "timeout --signal=KILL 5s python3 -I main.py"
        docker_cmd = [docker, "run", "--rm", "-i", "--network=none", "--read-only",
            "--cap-drop=ALL", "--security-opt=no-new-privileges", "--memory=192m",
            "--memory-swap=192m", "--cpus=0.5", "--pids-limit=32", "--user=65534:65534",
            "--tmpfs", "/tmp:rw,nosuid,exec,size=32m", "--mount", f"type=bind,src={work},dst=/work,readonly",
            "--workdir=/work", IMAGE, "sh", "-lc", command]
        try:
            proc = subprocess.run(docker_cmd, input=stdin, capture_output=True, text=True,
                timeout=TIME_LIMIT + 12, env={"PATH": "/usr/bin:/bin", "HOME": "/tmp"})
        except subprocess.TimeoutExpired:
            return {"ok": False, "stdout": "", "stderr": "Time limit exceeded", "stage": "timeout"}
        except OSError as exc:
            return {"ok": False, "stdout": "", "stderr": f"Runner error: {exc}", "stage": "unavailable"}

        stderr = proc.stderr[:2000]
        stage = "compile" if lang == "c" and ("error:" in stderr or "undefined reference" in stderr) else "run"
        return {"ok": proc.returncode == 0, "stdout": proc.stdout[:4000], "stderr": stderr,
                "stage": stage, "exit_code": proc.returncode}
