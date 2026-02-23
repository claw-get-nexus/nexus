#!/bin/bash
# Nexus Automation — Production Startup
# Guarantees clean state on every deploy

set -e

echo "🚀 Nexus Automation Starting..."
echo "   Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# PULL LATEST CODE (force update)
echo "   Pulling latest code..."
cd /app || cd /workspace || cd .
git pull origin main 2>/dev/null || echo "   (Git pull failed, using existing code)"

# Clear Python cache
echo "   Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Verify environment
echo "   Checking environment..."
: "${NEXUS_MODE:?Need to set NEXUS_MODE}"
echo "   NEXUS_MODE: $NEXUS_MODE"

# Install dependencies
echo "   Installing dependencies..."
pip install -q --no-cache-dir -r requirements.txt

# Create directories
mkdir -p assets/pipeline logs

# Log startup
echo "$(date -u) - Startup complete" >> logs/startup.log

# Start server
echo "   Starting server on port ${PORT:-8000}..."
exec python3 scripts/heartbeat_server.py
