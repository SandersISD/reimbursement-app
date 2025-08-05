"""
Forms for the Reimbursement Application using WTForms
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, DecimalField, DateField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Length
from datetime import date
from models import EXPENSE_GROUPS, CURRENCIES


class ClaimForm(FlaskForm):
    """Form for creating/editing main claim"""
    alias_name = StringField('Alias Name (optional)', 
                            validators=[Optional(), Length(max=100)],
                            render_kw={"placeholder": "Give this claim a memorable name..."})
    from_date = DateField('Expense Incurred From', 
                         validators=[DataRequired()], 
                         default=date.today)
    to_date = DateField('Expense Incurred To', 
                       validators=[DataRequired()], 
                       default=date.today)
    total_amount = DecimalField('Total Amount', 
                               validators=[DataRequired(), NumberRange(min=0.01)], 
                               places=2)
    total_currency = SelectField('Currency', 
                                choices=CURRENCIES, 
                                default='HKD', 
                                validators=[DataRequired()])
    paid_amount = DecimalField('Total Paid Amount (if different)', 
                              validators=[Optional(), NumberRange(min=0.01)], 
                              places=2)
    paid_currency = SelectField('Paid Currency', 
                               choices=CURRENCIES, 
                               default='HKD', 
                               validators=[Optional()])
    expense_group = SelectField('Expense Group', 
                               choices=EXPENSE_GROUPS, 
                               validators=[DataRequired()])
    business_purpose = TextAreaField('Business Purpose', 
                                   validators=[DataRequired(), Length(min=10, max=1000)],
                                   render_kw={"rows": 4, "placeholder": "Describe the business reason for this expense..."})
    receipt_file = FileField('Receipt/Invoice Upload', 
                            validators=[FileRequired(), 
                                      FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 
                                                'Only PDF, JPG, JPEG, and PNG files are allowed!')])
    submit = SubmitField('Submit Claim')


class ClaimItemForm(FlaskForm):
    """Form for adding/editing individual claim items"""
    description = StringField('Expense Description', 
                             validators=[DataRequired(), Length(min=3, max=255)],
                             render_kw={"placeholder": "e.g., Business lunch, Train ticket..."})
    amount = DecimalField('Amount', 
                         validators=[DataRequired(), NumberRange(min=0.01)], 
                         places=2)
    currency = SelectField('Currency', 
                          choices=CURRENCIES, 
                          default='HKD', 
                          validators=[DataRequired()])
    paid_amount = DecimalField('Paid Amount (if different)', 
                              validators=[Optional(), NumberRange(min=0.01)], 
                              places=2)
    paid_currency = SelectField('Paid Currency', 
                               choices=CURRENCIES, 
                               default='HKD', 
                               validators=[Optional()])
    justification = TextAreaField('Justification (optional)', 
                                 validators=[Optional(), Length(max=500)],
                                 render_kw={"rows": 3, "placeholder": "Additional details or justification..."})
    submit = SubmitField('Add Item')


class ReportForm(FlaskForm):
    """Form for generating reports"""
    report_type = SelectField('Report Type', 
                             choices=[
                                 ('isd_reimbursement', 'ISD Reimbursement Form (Items)'),
                                 ('financial_expense', 'Financial Office Expense Form (Claims)'),
                                 ('receipts_export', 'Receipts Export (ZIP)')
                             ], 
                             validators=[DataRequired()])
    # Month and year will be dynamically populated based on available data
    month_year = SelectField('Select Month/Year', 
                            choices=[], 
                            validators=[DataRequired()])
    submit = SubmitField('Generate Report')


class EditClaimForm(ClaimForm):
    """Form for editing existing claims - inherits from ClaimForm but file is optional"""
    receipt_file = FileField('Receipt/Invoice Upload (optional - leave empty to keep current file)', 
                            validators=[Optional(), 
                                      FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 
                                                'Only PDF, JPG, JPEG, and PNG files are allowed!')])
    submit = SubmitField('Update Claim')
