#!/usr/bin/env bash
set -Eeuo pipefail

echo "[entrypoint] uname: $(uname -a)"
echo "[entrypoint] python: $(python -V)"
echo "[entrypoint] date: $(date -Is)"
echo "[entrypoint] env PORT=${PORT:-<unset>}"
echo "[entrypoint] cwd: $(pwd)"
echo "[entrypoint] listing /app:"
ls -la /app || true

# Hard fail if PORT is missing (so we see it in logs)
if [[ -z "${PORT:-}" ]]; then
  echo "[entrypoint][FATAL] PORT is not set by platform. Defaulting to 8080 for debug."
  export PORT=8080
fi

# Minimal import test with full traceback
cat > /tmp/_import_test.py <<'PY'
import sys, os, traceback
sys.path.insert(0, '/app')  # Add /app to Python path
print("[import-test] PYTHONPATH:", sys.path)
try:
    import alice_agent
    print("[import-test] imported alice_agent OK; app:", hasattr(alice_agent, "app"))
except Exception as e:
    print("[import-test][FATAL] Import failed:", e)
    traceback.print_exc()
    # keep container alive for inspection rather than crash
    import time
    time.sleep(300)
    raise
PY
python -u /tmp/_import_test.py

# Start an ultra-simple /health fallback in background (never die)
python - <<'PY' &
import os, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer
PORT=int(os.getenv("PORT","8080"))
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=="/health":
            self.send_response(200); self.end_headers(); self.wfile.write(b"OK"); return
        self.send_response(404); self.end_headers()
server=HTTPServer(("0.0.0.0", PORT), H)
threading.Thread(target=server.serve_forever, daemon=True).start()
print(f"[health] serving /health on :{PORT}")
while True: time.sleep(5)
PY

# Start gunicorn (single process, threaded). If it fails, print and sleep.
echo "[entrypoint] starting gunicorn on :${PORT}"
exec bash -lc 'gunicorn --bind 0.0.0.0:${PORT} \
  --workers 1 --worker-class gthread --threads 4 \
  --timeout 180 --access-logfile - --error-logfile - --log-level info \
  alice_agent:app' || {
  echo "[entrypoint][FATAL] gunicorn exited with $?"
  sleep 300
}

