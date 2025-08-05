"""
Database initialization script for the Reimbursement Management System.
Run this script to create the database tables.
"""
from app import create_app
from models import db

def init_database():
    """Initialize the database with all tables."""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Optionally, you can add some sample data here for testing
        # create_sample_data()

def create_sample_data():
    """Create some sample data for testing (optional)."""
    from models import Claim, ClaimItem
    from datetime import date, datetime
    import uuid
    
    # Check if sample data already exists
    if Claim.query.first():
        print("Sample data already exists, skipping...")
        return
    
    # Create a sample claim
    sample_claim = Claim(
        claim_id=str(uuid.uuid4()),
        from_date=date.today(),
        to_date=date.today(),
        total_amount=150.00,
        total_currency='HKD',
        business_purpose='Sample business trip expenses for testing',
        upload_file_path='uploads/sample_receipt.pdf',
        user_id='sample_user'
    )
    
    db.session.add(sample_claim)
    db.session.commit()
    
    # Create sample items for the claim
    sample_items = [
        ClaimItem(
            claim_id=sample_claim.claim_id,
            description='Taxi fare to airport',
            amount=80.00,
            currency='HKD',
            expense_group='Travel'
        ),
        ClaimItem(
            claim_id=sample_claim.claim_id,
            description='Business lunch',
            amount=70.00,
            currency='HKD',
            expense_group='Meals',
            justification='Client meeting over lunch'
        )
    ]
    
    for item in sample_items:
        db.session.add(item)
    
    db.session.commit()
    print(f"Sample data created! Sample Claim ID: {sample_claim.claim_id}")

if __name__ == '__main__':
    init_database()
