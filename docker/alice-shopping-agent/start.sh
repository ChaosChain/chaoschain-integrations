#!/bin/sh
# Start script for Alice Shopping Agent in EigenCompute TEE

# Source Eigen's environment if available
if [ -f /usr/local/bin/compute-source-env.sh ]; then
    echo "Sourcing Eigen environment..."
    . /usr/local/bin/compute-source-env.sh
fi

# Start Gunicorn
echo "Starting Gunicorn on port ${PORT:-8080}..."
exec gunicorn \
    --bind "0.0.0.0:${PORT:-8080}" \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    alice_agent:app

