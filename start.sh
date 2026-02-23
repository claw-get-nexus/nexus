#!/bin/bash
# Nexus Automation — Render Start Script
# Starts web server immediately, runs pipeline in background

echo "🚀 Starting Nexus Automation..."

# Run pipeline once in background (don't block startup)
python scripts/run_pipeline.py > /tmp/pipeline.log 2>&1 &
PIPELINE_PID=$!
echo "Pipeline started in background (PID: $PIPELINE_PID)"

# Start heartbeat server (foreground — this keeps container alive)
echo "Starting heartbeat server on port ${PORT:-8000}..."
exec python scripts/heartbeat_server.py
