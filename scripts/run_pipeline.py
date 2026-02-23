#!/usr/bin/env python3
"""
Nexus Automation — Full Pipeline Runner
Executes complete business loop: Lead Gen → Outreach → Sales → Fulfillment → Ops
"""

import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

from lead_gen import LeadGenAgent
from outreach import OutreachAgent
from sales import SalesAgent
from fulfillment import FulfillmentAgent
from ops import OpsAgent

def run_full_pipeline():
    """Execute complete autonomous business loop."""
    print("\n" + "="*60)
    print("🤖 NEXUS AUTOMATION — FULL PIPELINE EXECUTION")
    print("="*60)
    print("\n  Mode: DRY RUN (no external communications)")
    print("  All data simulated for demonstration\n")
    
    # Step 1: Lead Generation
    print("\n" + "="*60)
    print("STEP 1/5: LEAD GENERATION")
    print("="*60)
    lead_agent = LeadGenAgent()
    leads = lead_agent.run()
    
    if not leads:
        print("\n  ⚠️  No leads generated. Stopping pipeline.")
        return
    
    # Step 2: Outreach
    print("\n" + "="*60)
    print("STEP 2/5: OUTREACH")
    print("="*60)
    outreach_agent = OutreachAgent()
    meetings = outreach_agent.run(dry_run=True)
    
    if not meetings:
        print("\n  ⚠️  No meetings booked. Stopping pipeline.")
        # Still run ops to show current state
        print("\n" + "="*60)
        print("STEP 5/5: OPERATIONS")
        print("="*60)
        ops_agent = OpsAgent()
        ops_agent.run()
        return
    
    # Step 3: Sales
    print("\n" + "="*60)
    print("STEP 3/5: SALES")
    print("="*60)
    sales_agent = SalesAgent()
    deals = sales_agent.run()
    
    if not deals:
        print("\n  ⚠️  No deals closed. Stopping pipeline.")
        print("\n" + "="*60)
        print("STEP 5/5: OPERATIONS")
        print("="*60)
        ops_agent = OpsAgent()
        ops_agent.run()
        return
    
    # Step 4: Fulfillment
    print("\n" + "="*60)
    print("STEP 4/5: FULFILLMENT")
    print("="*60)
    fulfillment_agent = FulfillmentAgent()
    fulfillment_agent.run()
    
    # Step 5: Operations
    print("\n" + "="*60)
    print("STEP 5/5: OPERATIONS")
    print("="*60)
    ops_agent = OpsAgent()
    ops_agent.run(generate_invoices=True)
    
    # Final summary
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE")
    print("="*60)
    print("\n  The Nexus Automation loop has executed successfully.")
    print("  All data saved to: assets/pipeline/")
    print("\n  Next steps:")
    print("    1. Review generated invoice requests")
    print("    2. Send invoices manually")
    print("    3. Run pipeline again to simulate next cycle")
    print()

if __name__ == "__main__":
    run_full_pipeline()
