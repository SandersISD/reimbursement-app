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


def parse_month_year(month_year_str):
    """Parse month-year string like '2024-01' into month and year integers"""
    try:
        if not month_year_str or '-' not in month_year_str:
            return None, None
        
        year_str, month_str = month_year_str.split('-')
        month = int(month_str)
        year = int(year_str)
        
        # Validate month range
        if 1 <= month <= 12 and year > 0:
            return month, year
        else:
            return None, None
    except (ValueError, AttributeError):
        return None, None


def get_available_months():
    """Get list of available months that have claims"""
    from models import Claim
    
    # Get all claims with their from_date
    claims = Claim.query.all()
    
    if not claims:
        return []
    
    # Extract unique year-month combinations
    months = set()
    for claim in claims:
        if claim.from_date:
            year_month = claim.from_date.strftime('%Y-%m')
            months.add(year_month)
    
    # Sort months and create choices list
    sorted_months = sorted(months, reverse=True)  # Most recent first
    
    # Format for display
    choices = []
    for month in sorted_months:
        year, month_num = month.split('-')
        month_names = [
            '', 'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        display_name = f"{month_names[int(month_num)]} {year}"
        choices.append((month, display_name))
    
    return choices


def get_available_claims():
    """Get list of available claims for selection"""
    from models import Claim
    
    claims = Claim.query.order_by(Claim.from_date.desc()).all()
    claim_choices = []
    
    for claim in claims:
        # Create a descriptive label for each claim
        date_range = f"{claim.from_date.strftime('%m/%d/%Y')}"
        if claim.from_date != claim.to_date:
            date_range += f" - {claim.to_date.strftime('%m/%d/%Y')}"
        
        alias_part = f" ({claim.alias_name})" if claim.alias_name else ""
        amount_part = f" - {claim.total_currency} {claim.total_amount}"
        group_part = f" [{claim.expense_group}]"
        
        label = f"{date_range}{alias_part}{amount_part}{group_part}"
        value = claim.claim_id
        
        claim_choices.append((value, label))
    
    return claim_choices


def get_months_from_claims(claim_ids):
    """Get unique months from selected claims"""
    from models import Claim
    
    claims = Claim.query.filter(Claim.claim_id.in_(claim_ids)).all()
    months = set()
    
    for claim in claims:
        year = claim.from_date.year
        month = claim.from_date.month
        months.add((year, month))
    
    return sorted(months)


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


def generate_multi_claim_isd_reports(claim_ids):
    """Generate ISD reports for multiple claims, one per month"""
    from models import Claim, ClaimItem
    
    # Get unique months from selected claims
    months = get_months_from_claims(claim_ids)
    reports = {}
    
    for year, month in months:
        # Query items for this specific month from selected claims
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        items = ClaimItem.query.join(Claim).filter(
            Claim.claim_id.in_(claim_ids),
            Claim.from_date >= start_date.date(),
            Claim.from_date < end_date.date()
        ).order_by(ClaimItem.created_at).all()
        
        if items:  # Only create report if there are items for this month
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
            
            month_key = f"{year:04d}_{month:02d}"
            reports[month_key] = {
                'filename': f'isd_reimbursement_{year}_{month:02d}.csv',
                'content': output.getvalue(),
                'month_name': datetime(year, month, 1).strftime('%B %Y')
            }
    
    return reports


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


def generate_multi_claim_financial_csv(claim_ids):
    """Generate combined Financial Office Expense CSV for multiple claims"""
    from models import Claim
    
    # Query selected claims
    claims = Claim.query.filter(Claim.claim_id.in_(claim_ids)).order_by(Claim.created_at).all()
    
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


def create_multi_claim_receipts_zip(claim_ids, upload_folder='uploads'):
    """Create ZIP file with receipts from selected claims"""
    from models import Claim
    
    # Query selected claims
    claims = Claim.query.filter(Claim.claim_id.in_(claim_ids)).all()
    
    # Create timestamp for unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_path = f"receipts_multi_claim_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        attachment_counter = 1
        
        for claim in claims:
            if claim.upload_file_path and os.path.exists(claim.upload_file_path):
                # Get original file extension
                original_filename = os.path.basename(claim.upload_file_path)
                name, ext = os.path.splitext(original_filename)
                
                # Create new filename: uuid_Attachment01.pdf format
                zip_filename = f"{claim.claim_id}_Attachment{attachment_counter:02d}{ext}"
                
                zip_file.write(claim.upload_file_path, zip_filename)
                attachment_counter += 1
    
    return zip_path


def create_multi_report_zip(claim_ids):
    """Create a comprehensive ZIP with ISD reports per month, combined financial report, and receipts"""
    import tempfile
    import shutil
    
    # Create timestamp for unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_path = f"comprehensive_report_{timestamp}.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        # 1. Generate ISD reports per month
        isd_reports = generate_multi_claim_isd_reports(claim_ids)
        for month_key, report_data in isd_reports.items():
            zip_file.writestr(report_data['filename'], report_data['content'])
        
        # 2. Generate combined financial report
        financial_csv = generate_multi_claim_financial_csv(claim_ids)
        zip_file.writestr('financial_expense_combined.csv', financial_csv)
        
        # 3. Add receipts with new naming convention
        from models import Claim
        claims = Claim.query.filter(Claim.claim_id.in_(claim_ids)).all()
        
        attachment_counter = 1
        for claim in claims:
            if claim.upload_file_path and os.path.exists(claim.upload_file_path):
                # Get original file extension
                original_filename = os.path.basename(claim.upload_file_path)
                name, ext = os.path.splitext(original_filename)
                
                # Create new filename: uuid_Attachment01.pdf format
                zip_filename = f"receipts/{claim.claim_id}_Attachment{attachment_counter:02d}{ext}"
                
                zip_file.write(claim.upload_file_path, zip_filename)
                attachment_counter += 1
    
    return zip_path