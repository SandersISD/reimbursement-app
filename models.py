"""
Database models for the Reimbursement Application
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()


class Claim(db.Model):
    """Main claim model for reimbursement requests"""
    __tablename__ = 'claims'
    
    claim_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alias_name = db.Column(db.String(100), nullable=True)  # User-defined alias for the claim
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    total_currency = db.Column(db.String(3), nullable=False, default='HKD')
    paid_amount = db.Column(db.Numeric(10, 2), nullable=True)
    paid_currency = db.Column(db.String(3), nullable=True)
    expense_group = db.Column(db.String(50), nullable=False)  # Moved from ClaimItem to Claim
    business_purpose = db.Column(db.Text, nullable=False)
    upload_file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.String(50), nullable=False, default='default_user')  # Hardcoded for now
    
    # Relationship with claim items
    items = db.relationship('ClaimItem', backref='claim', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Claim {self.claim_id}>'
    
    def get_total_items_amount(self):
        """Calculate total amount from all items"""
        return sum(item.amount for item in self.items)
    
    def amounts_match(self):
        """Check if total claim amount matches sum of item amounts"""
        return float(self.total_amount) == float(self.get_total_items_amount())


class ClaimItem(db.Model):
    """Individual items within a claim"""
    __tablename__ = 'claim_items'
    
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    claim_id = db.Column(db.String(36), db.ForeignKey('claims.claim_id'), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='HKD')
    paid_amount = db.Column(db.Numeric(10, 2), nullable=True)
    paid_currency = db.Column(db.String(3), nullable=True)
    justification = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ClaimItem {self.item_id}: {self.description}>'


# Constants for the application
EXPENSE_GROUPS = [
    ('Airfare', 'Airfare'),
    ('Books/Journals', 'Books/Journals'),
    ('Computer', 'Computer'),
    ('Delivery/Courier/Postage', 'Delivery/Courier/Postage'),
    ('Equipement', 'Equipement'),
    ('Ferry/Train (Overseas)', 'Ferry/Train (Overseas)'),
    ('Furniture & Fixture', 'Furniture & Fixture'),
    ('General Consumables', 'General Consumables'),
    ('Hotel', 'Hotel'),
    ('Lab Consumables/Electronic Components', 'Lab Consumables/Electronic Components'),
    ('Meal', 'Meal'),
    ('Membership Fee', 'Membership Fee'),
    ('Mobile Phone/Portable Electronic Device', 'Mobile Phone/Portable Electronic Device'),
    ('Others', 'Others'),
    ('Patent Fee', 'Patent Fee'),
    ('Publication/Submission Fee', 'Publication/Submission Fee'),
    ('Registration/Conference/Visa Fee', 'Registration/Conference/Visa Fee'),
    ('Rental Fee', 'Rental Fee'),
    ('Service Fee', 'Service Fee')
]

CURRENCIES = [
    ('HKD', 'HKD'),
    ('USD', 'USD'),
    ('EUR', 'EUR'),
    ('RMB', 'RMB'),
    ('GBP', 'GBP'),
    ('JPY', 'JPY')
]