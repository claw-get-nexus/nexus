#!/bin/bash
# Nexus Automation — Dynamic Execution Server
# Bypasses Render deploy cache by executing code from GitHub raw URLs

echo "🚀 Nexus Automation Dynamic Server"
echo "   Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Clear cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Start dynamic server
exec python3 scripts/dynamic_server.py
