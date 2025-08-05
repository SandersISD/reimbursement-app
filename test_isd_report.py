#!/usr/bin/env python3
"""
Test script to verify ISD report changes
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import generate_isd_reimbursement_csv
from models import db, Claim, ClaimItem
from app import create_app

def test_isd_report():
    """Test the ISD report generation with sample data"""
    app = create_app()
    
    with app.app_context():
        # Get a sample month that has data
        sample_claim = Claim.query.first()
        if not sample_claim:
            print("No claims found in database")
            return
            
        month_year = sample_claim.from_date.strftime('%Y-%m')
        print(f"Testing ISD report for {month_year}")
        
        # Generate the report
        csv_content = generate_isd_reimbursement_csv(month_year)
        
        # Print first few lines to verify format
        lines = csv_content.split('\n')
        print("\nFirst 10 lines of generated report:")
        for i, line in enumerate(lines[:10]):
            print(f"{i+1}: {line}")
        
        print(f"\nTotal lines in report: {len(lines)}")
        
        # Check if alias name column is removed
        header = lines[0] if lines else ""
        if "Alias Name" in header:
            print("❌ ERROR: Alias Name column still present!")
        else:
            print("✅ SUCCESS: Alias Name column removed")
            
        # Check if currency column is properly named
        if "EUR ($)" in header or "USD ($)" in header or "Others ($)" in header:
            print("✅ SUCCESS: Currency column properly formatted")
        else:
            print("❌ WARNING: Currency column format may need verification")
            
        # Check for totals row
        if any("TOTAL" in line for line in lines):
            print("✅ SUCCESS: Totals row found")
        else:
            print("❌ ERROR: Totals row missing")

if __name__ == "__main__":
    test_isd_report()
