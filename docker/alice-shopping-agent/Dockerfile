FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY alice_agent.py start_simple.py ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Expose port for EigenCompute routing
EXPOSE 8080

# Start the application
CMD ["python", "-u", "/app/start_simple.py"]
