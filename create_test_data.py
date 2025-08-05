#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Claim, ClaimItem
from decimal import Decimal
from datetime import date
import uuid

def create_test_data():
    """Create test data for multiple months"""
    with app.app_context():
        # Create claims for April 2025
        april_claim = Claim(
            claim_id=str(uuid.uuid4()),
            from_date=date(2025, 4, 15),
            to_date=date(2025, 4, 15),
            total_amount=Decimal('45.50'),
            total_currency='EUR',
            expense_group='Office Supplies',
            business_purpose='April office supplies for research project',
            upload_file_path='uploads/april_receipt.pdf'
        )
        
        # Create claims for July 2025
        july_claim = Claim(
            claim_id=str(uuid.uuid4()),
            from_date=date(2025, 7, 10),
            to_date=date(2025, 7, 10),
            total_amount=Decimal('89.25'),
            total_currency='HKD',
            expense_group='Lab Equipment',
            business_purpose='July lab equipment purchase',
            upload_file_path='uploads/july_receipt.pdf'
        )
        
        # Create claims for August 2025
        august_claim = Claim(
            claim_id=str(uuid.uuid4()),
            from_date=date(2025, 8, 2),
            to_date=date(2025, 8, 2),
            total_amount=Decimal('156.80'),
            total_currency='RMB',
            expense_group='Travel',
            business_purpose='August travel expenses',
            upload_file_path='uploads/august_receipt.pdf'
        )
        
        db.session.add(april_claim)
        db.session.add(july_claim)
        db.session.add(august_claim)
        db.session.flush()  # Get the IDs
        
        # Add items for April claim
        april_items = [
            ClaimItem(claim_id=april_claim.claim_id, description='Pens and pencils', amount=Decimal('12.30'), currency='EUR'),
            ClaimItem(claim_id=april_claim.claim_id, description='Notebooks', amount=Decimal('18.50'), currency='EUR'),
            ClaimItem(claim_id=april_claim.claim_id, description='Folders', amount=Decimal('14.70'), currency='EUR'),
        ]
        
        # Add items for July claim
        july_items = [
            ClaimItem(claim_id=july_claim.claim_id, description='Beakers', amount=Decimal('45.00'), currency='HKD'),
            ClaimItem(claim_id=july_claim.claim_id, description='Test tubes', amount=Decimal('28.50'), currency='HKD'),
            ClaimItem(claim_id=july_claim.claim_id, description='pH strips', amount=Decimal('15.75'), currency='HKD'),
        ]
        
        # Add items for August claim
        august_items = [
            ClaimItem(claim_id=august_claim.claim_id, description='Train ticket', amount=Decimal('89.40'), currency='RMB'),
            ClaimItem(claim_id=august_claim.claim_id, description='Hotel booking', amount=Decimal('67.40'), currency='RMB'),
        ]
        
        # Add all items
        for item in april_items + july_items + august_items:
            db.session.add(item)
        
        db.session.commit()
        
        print(f'✅ Created test data:')
        print(f'   April 2025: {april_claim.claim_id} with {len(april_items)} items')
        print(f'   July 2025: {july_claim.claim_id} with {len(july_items)} items')
        print(f'   August 2025: {august_claim.claim_id} with {len(august_items)} items')

if __name__ == '__main__':
    create_test_data()
