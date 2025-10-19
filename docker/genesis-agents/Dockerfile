FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY genesis_agents.py ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# ✅ CRITICAL: Expose port for EigenCompute routing
EXPOSE 8080

# Start the multi-agent application
# Use shell form to allow PORT variable expansion
CMD gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --worker-class gthread --threads 4 --timeout 180 --access-logfile - --error-logfile - --log-level info genesis_agents:app

