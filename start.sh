#!/bin/bash
# Nexus Automation — Render Start Script
# Runs heartbeat server in background + executes pipeline

echo "🚀 Starting Nexus Automation..."

# Start heartbeat server (keeps Render instance warm)
python scripts/heartbeat_server.py &
HEARTBEAT_PID=$!
echo "Heartbeat server started (PID: $HEARTBEAT_PID)"

# Run initial pipeline
python scripts/run_pipeline.py

# Keep container alive
echo "Nexus Automation running. Waiting..."
wait $HEARTBEAT_PID
