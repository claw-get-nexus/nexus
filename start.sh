#!/bin/bash
# Nexus Automation — Production Startup
# Guarantees clean state on every deploy

set -e  # Exit on error

echo "🚀 Nexus Automation Starting..."
echo "   Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "   Commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"

# 1. Clear Python bytecode cache
echo "   Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 2. Verify environment
echo "   Checking environment..."
: "${NEXUS_MODE:?Need to set NEXUS_MODE}"
: "${RESEND_API_KEY:?Need to set RESEND_API_KEY}"
: "${TWITTER_API_KEY:?Need to set TWITTER_API_KEY}"

echo "   NEXUS_MODE: $NEXUS_MODE"
echo "   RESEND_API_KEY: ${RESEND_API_KEY:0:5}..."
echo "   TWITTER_API_KEY: ${TWITTER_API_KEY:0:5}..."

# 3. Install dependencies fresh
echo "   Installing dependencies..."
pip install -q --no-cache-dir -r requirements.txt

# 4. Verify imports work
echo "   Verifying imports..."
python3 -c "from experiments import ExperimentTracker; print('   ✓ Experiments module OK')"
python3 -c "from job_boards import JobBoardScraper; print('   ✓ Job boards module OK')"

# 5. Create required directories
echo "   Creating directories..."
mkdir -p assets/pipeline
mkdir -p logs

# 6. Log startup
echo "$(date -u) - Startup complete" >> logs/startup.log

# 7. Start heartbeat server (foreground)
echo "   Starting server on port ${PORT:-8000}..."
exec python3 scripts/heartbeat_server.py
