"""
Utility functions for the Reimbursement Application
"""
import os
import csv
import zipfile
from io import StringIO
from werkzeug.utils import secure_filename
from datetime import datetime


def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file, upload_folder, claim_id):
    """Save uploaded file with secure filename and return the path"""
    if file and allowed_file(file.filename):
        # Create secure filename with claim_id prefix
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        secure_filename_with_id = f"{claim_id}_{name}{ext}"
        
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_folder, secure_filename_with_id)
        file.save(file_path)
        return file_path
    return None


def get_available_months():
    """Get list of available months/years based on existing claims"""
    from models import Claim, db
    
    # Get distinct year-month combinations
    claims = Claim.query.all()
    month_years = set()
    
    for claim in claims:
        year = claim.from_date.year
        month = claim.from_date.month
        month_years.add((year, month))
    
    # Sort and format for display
    month_choices = []
    for year, month in sorted(month_years):
        month_name = datetime(year, month, 1).strftime('%B %Y')
        value = f"{month:02d}-{year}"
        month_choices.append((value, month_name))
    
    return month_choices


def parse_month_year(month_year_str):
    """Parse month-year string into month and year integers"""
    try:
        month, year = month_year_str.split('-')
        return int(month), int(year)
    except:
        return None, None


def generate_isd_reimbursement_csv(month_year_str):
    """Generate CSV for ISD Reimbursement Form (individual items)"""
    from models import Claim, ClaimItem
    
    month, year = parse_month_year(month_year_str)
    if not month or not year:
        raise ValueError("Invalid month/year format")
    
    # Query items for the specified month/year
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    items = ClaimItem.query.join(Claim).filter(
        Claim.from_date >= start_date.date(),
        Claim.from_date < end_date.date()
    ).order_by(ClaimItem.created_at).all()
    
    # Create CSV content
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Receipt Order',
        'Payment Date',
        'Particulars',
        'HKD ($)',
        'RMB ($)',
        'Others (Specify:EUR)',
        'Expense Group',
        'Alias Name',
        'Receipt Attached?'
    ])
    
    # Write data rows
    for i, item in enumerate(items, 1):
        payment_date = item.claim.from_date.strftime('%d-%m-%Y')
        
        # Determine amounts by currency
        hkd_amount = str(item.amount) if item.currency == 'HKD' else ''
        rmb_amount = str(item.amount) if item.currency == 'RMB' else ''
        other_amount = f"{item.amount} {item.currency}" if item.currency not in ['HKD', 'RMB'] else ''
        
        receipt_attached = 'Yes' if item.claim.upload_file_path else 'No'
        alias_name = item.claim.alias_name or ''
        expense_group = item.claim.expense_group
        
        writer.writerow([
            i,
            payment_date,
            item.description,
            hkd_amount,
            rmb_amount,
            other_amount,
            expense_group,
            alias_name,
            receipt_attached
        ])
    
    return output.getvalue()


def generate_financial_expense_csv(month_year_str=None):
    """Generate CSV for Financial Office Expense Form (claims)"""
    from models import Claim
    
    # Query claims for the specified month/year or all if not specified
    query = Claim.query
    
    if month_year_str:
        month, year = parse_month_year(month_year_str)
        if month and year:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            query = query.filter(
                Claim.from_date >= start_date.date(),
                Claim.from_date < end_date.date()
            )
    
    claims = query.order_by(Claim.created_at).all()
    
    # Create CSV content
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Incurred Date From',
        'Incurred Date To',
        'Description',
        'Paid Currency',
        'Paid Total Amount',
        'Expense Group',
        'Alias Name',
        'Business Purpose',
        'Justifications',
        'UUID'
    ])
    
    # Write data rows
    for claim in claims:
        # Combine all item descriptions
        descriptions = '; '.join([item.description for item in claim.items])
        
        # Combine all justifications
        justifications = '; '.join([item.justification for item in claim.items if item.justification])
        
        paid_currency = claim.paid_currency or claim.total_currency
        paid_amount = claim.paid_amount or claim.total_amount
        alias_name = claim.alias_name or ''
        
        writer.writerow([
            claim.from_date.strftime('%d-%m-%Y'),
            claim.to_date.strftime('%d-%m-%Y'),
            descriptions,
            paid_currency,
            str(paid_amount),
            claim.expense_group,
            alias_name,
            claim.business_purpose,
            justifications,
            claim.claim_id
        ])
    
    return output.getvalue()


def create_receipts_zip(month_year_str=None, upload_folder='uploads'):
    """Create ZIP file with all receipts for specified period"""
    from models import Claim
    
    # Query claims for the specified month/year or all if not specified
    query = Claim.query
    
    if month_year_str:
        month, year = parse_month_year(month_year_str)
        if month and year:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)
            
            query = query.filter(
                Claim.from_date >= start_date.date(),
                Claim.from_date < end_date.date()
            )
    
    claims = query.all()
    
    # Create ZIP file
    zip_path = f"receipts_{month_year_str.replace('-', '_')}.zip" if month_year_str else "receipts_all.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        for claim in claims:
            if claim.upload_file_path and os.path.exists(claim.upload_file_path):
                # Get original filename and add claim ID
                original_filename = os.path.basename(claim.upload_file_path)
                name, ext = os.path.splitext(original_filename)
                alias_prefix = f"{claim.alias_name}_" if claim.alias_name else ""
                zip_filename = f"receipt_{alias_prefix}{claim.claim_id}{ext}"
                
                zip_file.write(claim.upload_file_path, zip_filename)
    
    return zip_path