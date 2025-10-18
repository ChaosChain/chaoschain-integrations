FROM python:3.11-slim

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY alice_agent.py start_simple.py ./

# Set unbuffered output
ENV PYTHONUNBUFFERED=1

# Simple CMD - no complex ENTRYPOINT
CMD ["python", "-u", "/app/start_simple.py"]
