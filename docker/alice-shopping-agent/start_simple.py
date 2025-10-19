#!/usr/bin/env python3
"""Ultra-simple startup script that logs startup info and starts gunicorn"""
import os
import sys
import subprocess

print("=" * 60)
print("CONTAINER STARTED")
print("=" * 60)
print(f"PORT = {os.getenv('PORT', 'UNSET')}")
print(f"PWD = {os.getcwd()}")
print(f"Python = {sys.version.split()[0]}")  # Version only, no build info
print("=" * 60)
print("Files in /app:")
subprocess.run(["ls", "-la", "/app"])
print("=" * 60)
print("STARTING GUNICORN...")
print("=" * 60)
print("⚠️  Secrets loaded from KMS (not displayed for security)")
print("=" * 60)
sys.stdout.flush()

# Start gunicorn
port = os.getenv("PORT", "8080")
os.execlp(
    "gunicorn",
    "gunicorn",
    "--bind", f"0.0.0.0:{port}",
    "--workers", "1",
    "--worker-class", "gthread",
    "--threads", "4",
    "--timeout", "180",
    "--access-logfile", "-",
    "--error-logfile", "-",
    "--log-level", "info",
    "alice_agent:app"
)

