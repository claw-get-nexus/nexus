#!/bin/bash
# Nexus Automation — Debug Mode
# Logs everything, exposes logs via /logs endpoint

set -e

echo "🚀 Nexus Automation Debug Mode"
echo "   Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Create log directory
mkdir -p logs

# Log startup
echo "$(date -u) - Starting up" >> logs/startup.log
echo "$(date -u) - NEXUS_MODE: $NEXUS_MODE" >> logs/startup.log
echo "$(date -u) - PORT: ${PORT:-8000}" >> logs/startup.log

# Clear old Python cache
echo "$(date -u) - Clearing cache" >> logs/startup.log
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Test imports and log result
echo "$(date -u) - Testing imports" >> logs/startup.log
python3 -c "from lead_gen import LeadGenAgent; print('LeadGenAgent OK')" 2>&1 >> logs/startup.log || echo "IMPORT FAILED" >> logs/startup.log

# Run pipeline once and capture ALL output
echo "$(date -u) - Running pipeline" >> logs/startup.log
python3 scripts/run_pipeline.py > logs/pipeline_$(date +%Y%m%d_%H%M%S).log 2>&1 &
PIPELINE_PID=$!
echo "$(date -u) - Pipeline PID: $PIPELINE_PID" >> logs/startup.log

# Start debug server (shows logs via web)
echo "$(date -u) - Starting debug server on port ${PORT:-8000}" >> logs/startup.log
exec python3 scripts/debug_server.py
