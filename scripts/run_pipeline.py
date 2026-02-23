#!/usr/bin/env python3
"""
Nexus Automation — Full Pipeline Runner
Executes complete business loop: Lead Gen → Outreach → Sales → Fulfillment → Ops
"""

import sys
import traceback
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

# Error log file
ERROR_LOG = SKILL_DIR / "assets" / "pipeline" / "errors.log"

def log_error(msg):
    """Log error to file."""
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(ERROR_LOG, "a") as f:
        f.write(f"{msg}\n")

def run_full_pipeline():
    """Execute complete autonomous business loop."""
    try:
        print("\n" + "="*60)
        print("🤖 NEXUS AUTOMATION — FULL PIPELINE EXECUTION")
        print("="*60)
        print("\n  Mode: LIVE (with experiments)")
        print("  4 tracks running: Support, E-commerce, Sales, Trade Business\n")
        
        # Step 1: Lead Generation
        print("\n" + "="*60)
        print("STEP 1/5: LEAD GENERATION")
        print("="*60)
        
        try:
            from lead_gen import LeadGenAgent
            lead_agent = LeadGenAgent()
            leads = lead_agent.run()
        except Exception as e:
            print(f"  ❌ Lead Gen failed: {e}")
            log_error(f"Lead Gen: {str(e)}\n{traceback.format_exc()}")
            leads = []
        
        if not leads:
            print("\n  ⚠️  No leads generated. Stopping pipeline.")
            return
        
        # Step 2: Outreach
        print("\n" + "="*60)
        print("STEP 2/5: OUTREACH")
        print("="*60)
        
        try:
            from outreach import OutreachAgent
            outreach_agent = OutreachAgent()
            meetings = outreach_agent.run(dry_run=True)
        except Exception as e:
            print(f"  ❌ Outreach failed: {e}")
            log_error(f"Outreach: {str(e)}")
            meetings = []
        
        if not meetings:
            print("\n  ⚠️  No meetings booked. Stopping pipeline.")
            # Still run ops to show current state
            print("\n" + "="*60)
            print("STEP 5/5: OPERATIONS")
            print("="*60)
            try:
                from ops import OpsAgent
                ops_agent = OpsAgent()
                ops_agent.run()
            except Exception as e:
                log_error(f"Ops: {str(e)}")
            return
        
        # Step 3: Sales
        print("\n" + "="*60)
        print("STEP 3/5: SALES")
        print("="*60)
        
        try:
            from sales import SalesAgent
            sales_agent = SalesAgent()
            deals = sales_agent.run()
        except Exception as e:
            print(f"  ❌ Sales failed: {e}")
            log_error(f"Sales: {str(e)}")
            deals = []
        
        if not deals:
            print("\n  ⚠️  No deals closed. Stopping pipeline.")
            print("\n" + "="*60)
            print("STEP 5/5: OPERATIONS")
            print("="*60)
            try:
                from ops import OpsAgent
                ops_agent = OpsAgent()
                ops_agent.run()
            except Exception as e:
                log_error(f"Ops: {str(e)}")
            return
        
        # Step 4: Fulfillment
        print("\n" + "="*60)
        print("STEP 4/5: FULFILLMENT")
        print("="*60)
        
        try:
            from fulfillment import FulfillmentAgent
            fulfillment_agent = FulfillmentAgent()
            fulfillment_agent.run()
        except Exception as e:
            print(f"  ❌ Fulfillment failed: {e}")
            log_error(f"Fulfillment: {str(e)}")
        
        # Step 5: Operations
        print("\n" + "="*60)
        print("STEP 5/5: OPERATIONS")
        print("="*60)
        
        try:
            from ops import OpsAgent
            ops_agent = OpsAgent()
            ops_agent.run(generate_invoices=True)
        except Exception as e:
            log_error(f"Ops final: {str(e)}")
        
        # Final summary
        print("\n" + "="*60)
        print("✅ PIPELINE COMPLETE")
        print("="*60)
        
    except Exception as e:
        error_msg = f"Pipeline crashed: {str(e)}\n{traceback.format_exc()}"
        print(f"\n  ❌ PIPELINE CRASH: {e}")
        log_error(error_msg)

if __name__ == "__main__":
    run_full_pipeline()
