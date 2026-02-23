#!/usr/bin/env python3
"""
Nexus Automation — Pipeline Runner
Executes complete business loop with full error isolation.
"""

import sys
import os
import json
import traceback
import subprocess
from datetime import datetime
from pathlib import Path

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

SKILL_DIR = Path(__file__).parent.parent
PIPELINE_DIR = SKILL_DIR / "assets" / "pipeline"
LOG_DIR = SKILL_DIR / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)
PIPELINE_DIR.mkdir(parents=True, exist_ok=True)

RUN_LOG = LOG_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def log(msg, level="INFO"):
    """Log to stdout and file."""
    line = f"{datetime.now().isoformat()} [{level}] {msg}"
    print(line)
    with open(RUN_LOG, "a") as f:
        f.write(line + "\n")

def log_error(msg, exc=None):
    """Log error with traceback."""
    log(msg, "ERROR")
    if exc:
        with open(RUN_LOG, "a") as f:
            f.write(traceback.format_exc() + "\n")
    
    # Also write to error log for /status endpoint
    error_log = PIPELINE_DIR / "errors.log"
    with open(error_log, "a") as f:
        f.write(f"{datetime.now().isoformat()}: {msg}\n")

def run_step(name, module_name, class_name, **kwargs):
    """Run a pipeline step with full error isolation."""
    log(f"=" * 60)
    log(f"STEP: {name}")
    log(f"=" * 60)
    
    try:
        # Import fresh (no cached modules)
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        module = __import__(module_name, fromlist=[class_name])
        agent_class = getattr(module, class_name)
        agent = agent_class()
        
        # Run
        result = agent.run(**kwargs) if kwargs else agent.run()
        
        log(f"✓ {name} completed: {len(result) if isinstance(result, list) else 'OK'}")
        return result
        
    except Exception as e:
        log_error(f"{name} failed: {e}", e)
        return None

def main():
    """Execute full pipeline."""
    log("NEXUS AUTOMATION PIPELINE")
    log(f"Mode: {os.environ.get('NEXUS_MODE', 'unknown')}")
    log(f"Log: {RUN_LOG}")
    
    # Step 1: Lead Generation
    leads = run_step("Lead Generation", "lead_gen", "LeadGenAgent")
    
    if not leads:
        log("No leads generated. Stopping.", "WARN")
        return 1
    
    # Step 2: Outreach
    meetings = run_step("Outreach", "outreach", "OutreachAgent", dry_run=True)
    
    if not meetings:
        log("No meetings booked. Running ops only.", "WARN")
        run_step("Operations", "ops", "OpsAgent")
        return 0
    
    # Step 3: Sales
    deals = run_step("Sales", "sales", "SalesAgent")
    
    if not deals:
        log("No deals closed. Running ops only.", "WARN")
        run_step("Operations", "ops", "OpsAgent")
        return 0
    
    # Step 4: Fulfillment
    run_step("Fulfillment", "fulfillment", "FulfillmentAgent")
    
    # Step 5: Operations
    run_step("Operations", "ops", "OpsAgent", generate_invoices=True)
    
    log("=" * 60)
    log("PIPELINE COMPLETE")
    log("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
