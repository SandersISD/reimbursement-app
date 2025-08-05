"""
WTForms form definitions for the Reimbursement Management System.
"""
from datetime import date
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from models import EXPENSE_GROUPS, CURRENCIES

class ClaimForm(FlaskForm):
    """Form for creating a new reimbursement claim."""
    
    # Date range
    from_date = DateField('From Date', 
                         validators=[DataRequired()], 
                         default=date.today)
    to_date = DateField('To Date', 
                       validators=[DataRequired()], 
                       default=date.today)
    
    # Total amounts
    total_amount = DecimalField('Total Amount', 
                               validators=[DataRequired(), NumberRange(min=0.01)],
                               places=2)
    total_currency = SelectField('Total Currency', 
                                choices=CURRENCIES, 
                                default='HKD')
    
    # Optional paid amounts (for different currency scenarios)
    paid_amount = DecimalField('Total Paid Amount (if different)', 
                              validators=[Optional(), NumberRange(min=0.01)],
                              places=2)
    paid_currency = SelectField('Paid Currency', 
                               choices=CURRENCIES, 
                               default='HKD')
    
    # Business purpose
    business_purpose = TextAreaField('Business Purpose', 
                                   validators=[DataRequired(), Length(min=10, max=1000)])
    
    # File upload
    receipt_file = FileField('Receipt/Invoice File', 
                           validators=[
                               FileRequired(),
                               FileAllowed(['pdf', 'png', 'jpg', 'jpeg'], 
                                         'Only PDF, PNG, JPG files are allowed!')
                           ])
    
    submit = SubmitField('Submit Claim')
    
    def validate(self, extra_validators=None):
        """Custom validation for the form."""
        if not super().validate(extra_validators):
            return False
        
        # Validate date range
        if self.from_date.data > self.to_date.data:
            self.to_date.errors.append('To date must be after from date.')
            return False
        
        return True

class ClaimItemForm(FlaskForm):
    """Form for adding individual items to a claim."""
    
    description = StringField('Expense Description', 
                             validators=[DataRequired(), Length(min=3, max=255)])
    
    amount = DecimalField('Amount', 
                         validators=[DataRequired(), NumberRange(min=0.01)],
                         places=2)
    currency = SelectField('Currency', 
                          choices=CURRENCIES, 
                          default='HKD')
    
    # Optional paid amounts (for different currency scenarios)
    paid_amount = DecimalField('Paid Amount (if different)', 
                              validators=[Optional(), NumberRange(min=0.01)],
                              places=2)
    paid_currency = SelectField('Paid Currency', 
                               choices=CURRENCIES, 
                               default='HKD')
    
    expense_group = SelectField('Expense Group', 
                               choices=EXPENSE_GROUPS, 
                               validators=[DataRequired()])
    
    justification = TextAreaField('Justification (optional)', 
                                 validators=[Optional(), Length(max=500)])
    
    # Action buttons
    add_item = SubmitField('Add Item')
    add_another = SubmitField('Add Item & Add Another')
    finish = SubmitField('Finish & View Summary')
