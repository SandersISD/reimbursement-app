#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, Claim, ClaimItem
from decimal import Decimal
from datetime import date
import uuid

def create_many_months_test():
    """Create test data for many months to prove unlimited capability"""
    with app.app_context():
        months_data = [
            (1, 'Jan supplies', 'EUR', 25.50),
            (2, 'Feb equipment', 'HKD', 78.90), 
            (3, 'Mar materials', 'RMB', 156.75),
            (9, 'Sep tools', 'EUR', 89.25),
            (10, 'Oct software', 'USD', 199.00),
            (11, 'Nov travel', 'HKD', 345.60),
            (12, 'Dec supplies', 'RMB', 67.80)
        ]
        
        created_claims = []
        
        for month, purpose, currency, amount in months_data:
            claim = Claim(
                claim_id=str(uuid.uuid4()),
                from_date=date(2025, month, 15),
                to_date=date(2025, month, 15),
                total_amount=Decimal(str(amount)),
                total_currency=currency,
                expense_group='Test Items',
                business_purpose=f'{purpose} for testing multi-month capability',
                upload_file_path=f'uploads/test_{month:02d}.pdf'
            )
            
            db.session.add(claim)
            db.session.flush()
            
            # Add 1-2 items per claim
            item1 = ClaimItem(
                claim_id=claim.claim_id, 
                description=f'Item 1 for {purpose}', 
                amount=Decimal(str(amount * 0.6)), 
                currency=currency
            )
            item2 = ClaimItem(
                claim_id=claim.claim_id, 
                description=f'Item 2 for {purpose}', 
                amount=Decimal(str(amount * 0.4)), 
                currency=currency
            )
            
            db.session.add(item1)
            db.session.add(item2)
            created_claims.append((month, claim.claim_id))
        
        db.session.commit()
        
        print(f'✅ Created test data for {len(months_data)} additional months:')
        for month, claim_id in created_claims:
            print(f'   Month {month:2d}/2025: {claim_id}')

if __name__ == '__main__':
    create_many_months_test()
