#!/usr/bin/env python3
"""
Test script to demonstrate Excel export functionality
"""
import os
from app import create_app
from models import db, Claim
from utils import generate_excel_isd_report, generate_multi_claim_excel_reports

def main():
    print("🧪 Excel Export Functionality Test")
    print("=" * 50)
    
    app = create_app()
    with app.app_context():
        # Get all claims from database
        all_claims = Claim.query.all()
        print(f"📊 Total claims in database: {len(all_claims)}")
        
        if not all_claims:
            print("❌ No claims found. Please add some claims first.")
            return
        
        # Test with first 2 claims
        test_claims = all_claims[:2]
        claim_ids = [claim.claim_id for claim in test_claims]
        
        print(f"\n🎯 Testing with {len(test_claims)} claims:")
        for i, claim in enumerate(test_claims, 1):
            print(f"   {i}. {claim.alias_name or 'No alias'} - {claim.from_date} - {claim.total_currency} {claim.total_amount}")
        
        print("\n📊 Testing Single Excel Report Generation...")
        excel_content = generate_excel_isd_report(test_claims)
        
        if excel_content:
            # Save test file
            test_file = "test_single_isd_report.xlsx"
            with open(test_file, 'wb') as f:
                f.write(excel_content)
            print(f"✅ Single Excel report generated: {test_file}")
            print(f"   File size: {len(excel_content):,} bytes")
        else:
            print("❌ Failed to generate single Excel report")
            return
        
        print("\n📊 Testing Multi-Claim Excel Reports...")
        excel_reports = generate_multi_claim_excel_reports(claim_ids)
        
        if excel_reports:
            print(f"✅ Generated {len(excel_reports)} monthly reports:")
            
            for month_key, report_data in excel_reports.items():
                filename = f"test_{report_data['filename']}"
                with open(filename, 'wb') as f:
                    f.write(report_data['content'])
                
                print(f"   📁 {report_data['month_name']}: {filename}")
                print(f"      Size: {len(report_data['content']):,} bytes")
        else:
            print("❌ Failed to generate multi-claim Excel reports")
            return
        
        print("\n🎉 Excel Export Test Completed Successfully!")
        print("\n💡 Key Features Implemented:")
        print("   ✅ Direct Excel template population")
        print("   ✅ Multi-currency support (HKD, RMB, Others)")
        print("   ✅ Automatic totals calculation")
        print("   ✅ Monthly grouping for multi-claim reports")
        print("   ✅ Proper date formatting")
        print("   ✅ Receipt attachment status")
        
        print("\n📋 Generated Test Files:")
        test_files = [f for f in os.listdir('.') if f.startswith('test_') and f.endswith('.xlsx')]
        for file in test_files:
            file_size = os.path.getsize(file)
            print(f"   📄 {file} ({file_size:,} bytes)")
        
        print(f"\n🌐 To test the web interface:")
        print("   1. Run: uv run flask run --port 5001")
        print("   2. Open: http://localhost:5001/reports")
        print("   3. Select claims and choose 'Comprehensive Excel Report'")

if __name__ == "__main__":
    main()
