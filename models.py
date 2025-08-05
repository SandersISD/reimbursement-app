"""
Database models for the Reimbursement Management System.
"""
import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Claim(db.Model):
    """Main reimbursement claim model."""
    __tablename__ = 'claims'
    
    # Primary key using UUID
    claim_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Date range for expenses
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    
    # Total amounts and currencies
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    total_currency = db.Column(db.String(3), nullable=False, default='HKD')
    paid_amount = db.Column(db.Numeric(10, 2), nullable=True)
    paid_currency = db.Column(db.String(3), nullable=True)
    
    # Business purpose and file upload
    business_purpose = db.Column(db.Text, nullable=False)
    upload_file_path = db.Column(db.String(255), nullable=False)
    
    # Timestamps and user tracking
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.String(50), nullable=False, default='dummy_user')  # For future user authentication
    
    # Relationship to claim items
    items = db.relationship('ClaimItem', backref='claim', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Claim {self.claim_id}>'
    
    @property
    def total_items_amount(self):
        """Calculate total amount from all items."""
        return sum(item.amount for item in self.items)
    
    @property
    def items_count(self):
        """Get count of items in this claim."""
        return len(self.items)

class ClaimItem(db.Model):
    """Individual items within a reimbursement claim."""
    __tablename__ = 'claim_items'
    
    # Primary key
    item_id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key to claim
    claim_id = db.Column(db.String(36), db.ForeignKey('claims.claim_id'), nullable=False)
    
    # Item details
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='HKD')
    paid_amount = db.Column(db.Numeric(10, 2), nullable=True)
    paid_currency = db.Column(db.String(3), nullable=True)
    
    # Categorization
    expense_group = db.Column(db.String(50), nullable=False)
    justification = db.Column(db.Text, nullable=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ClaimItem {self.item_id}: {self.description}>'

# Predefined expense groups
EXPENSE_GROUPS = [
    ('Travel', 'Travel'),
    ('Meals', 'Meals'),
    ('Office Supplies', 'Office Supplies'),
    ('Training', 'Training'),
    ('Other', 'Other')
]

# Supported currencies
CURRENCIES = [
    ('HKD', 'Hong Kong Dollar (HKD)'),
    ('USD', 'US Dollar (USD)'),
    ('EUR', 'Euro (EUR)'),
    ('GBP', 'British Pound (GBP)'),
    ('JPY', 'Japanese Yen (JPY)'),
    ('CNY', 'Chinese Yuan (CNY)'),
]
