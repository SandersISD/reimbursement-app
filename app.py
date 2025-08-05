"""
Main Flask Application for Employee Reimbursement System
"""
import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.utils import secure_filename
import uuid

# Import our modules
from models import db, Claim, ClaimItem, EXPENSE_GROUPS, CURRENCIES
from forms import ClaimForm, ClaimItemForm, ReportForm, EditClaimForm
from utils import (save_uploaded_file, generate_isd_reimbursement_csv, generate_financial_expense_csv, 
                   create_receipts_zip, get_available_claims, generate_multi_claim_isd_reports,
                   generate_multi_claim_financial_csv, create_multi_report_zip)


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///reimbursement.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Initialize extensions
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app


app = create_app()


@app.route('/')
def index():
    """Homepage with dashboard"""
    # Get recent claims for dashboard
    recent_claims = Claim.query.order_by(Claim.created_at.desc()).limit(10).all()
    total_claims = Claim.query.count()
    
    return render_template('index.html', 
                         recent_claims=recent_claims, 
                         total_claims=total_claims)


@app.route('/new_claim', methods=['GET', 'POST'])
def new_claim():
    """Create a new reimbursement claim"""
    form = ClaimForm()
    
    if form.validate_on_submit():
        # Generate unique claim ID
        claim_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_path = save_uploaded_file(
            form.receipt_file.data, 
            app.config['UPLOAD_FOLDER'], 
            claim_id
        )
        
        if not file_path:
            flash('Error saving uploaded file. Please try again.', 'error')
            return render_template('new_claim.html', form=form)
        
        # Create new claim
        claim = Claim(
            claim_id=claim_id,
            alias_name=form.alias_name.data,
            from_date=form.from_date.data,
            to_date=form.to_date.data,
            total_amount=form.total_amount.data,
            total_currency=form.total_currency.data,
            paid_amount=form.paid_amount.data,
            paid_currency=form.paid_currency.data,
            expense_group=form.expense_group.data,
            business_purpose=form.business_purpose.data,
            upload_file_path=file_path
        )
        
        try:
            db.session.add(claim)
            db.session.commit()
            flash(f'Claim created successfully! Claim ID: {claim_id}', 'success')
            return redirect(url_for('add_items', claim_id=claim_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating claim: {str(e)}', 'error')
    
    return render_template('new_claim.html', form=form)


@app.route('/claim/<claim_id>/add_items', methods=['GET', 'POST'])
def add_items(claim_id):
    """Add individual items to a claim"""
    claim = Claim.query.get_or_404(claim_id)
    form = ClaimItemForm()
    
    if form.validate_on_submit():
        # Create new item
        item = ClaimItem(
            claim_id=claim_id,
            description=form.description.data,
            amount=form.amount.data,
            currency=form.currency.data,
            paid_amount=form.paid_amount.data,
            paid_currency=form.paid_currency.data,
            justification=form.justification.data
        )
        
        try:
            db.session.add(item)
            db.session.commit()
            flash('Item added successfully!', 'success')
            return redirect(url_for('add_items', claim_id=claim_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding item: {str(e)}', 'error')
    
    # Get existing items for this claim
    items = ClaimItem.query.filter_by(claim_id=claim_id).order_by(ClaimItem.created_at).all()
    
    # Calculate totals for validation
    items_total = sum(float(item.amount) for item in items)
    claim_total = float(claim.total_amount)
    amounts_match = abs(items_total - claim_total) < 0.01  # Account for floating point precision
    
    return render_template('add_items.html', 
                         form=form, 
                         claim=claim, 
                         items=items,
                         items_total=items_total,
                         amounts_match=amounts_match)


@app.route('/claim/<claim_id>/confirmation')
def confirmation(claim_id):
    """Show confirmation page with claim summary"""
    claim = Claim.query.get_or_404(claim_id)
    items = ClaimItem.query.filter_by(claim_id=claim_id).order_by(ClaimItem.created_at).all()
    
    # Calculate totals for validation
    items_total = sum(float(item.amount) for item in items)
    claim_total = float(claim.total_amount)
    amounts_match = abs(items_total - claim_total) < 0.01
    
    return render_template('confirmation.html', 
                         claim=claim, 
                         items=items,
                         items_total=items_total,
                         amounts_match=amounts_match)


@app.route('/claims')
def claims_list():
    """List all claims"""
    page = request.args.get('page', 1, type=int)
    claims = Claim.query.order_by(Claim.created_at.desc()).paginate(
        page=page, 
        per_page=20, 
        error_out=False
    )
    return render_template('claims_list.html', claims=claims)


@app.route('/claim/<claim_id>')
def view_claim(claim_id):
    """View individual claim details"""
    claim = Claim.query.get_or_404(claim_id)
    items = ClaimItem.query.filter_by(claim_id=claim_id).order_by(ClaimItem.created_at).all()
    
    # Calculate totals for validation
    items_total = sum(float(item.amount) for item in items)
    claim_total = float(claim.total_amount)
    amounts_match = abs(items_total - claim_total) < 0.01
    
    return render_template('view_claim.html', 
                         claim=claim, 
                         items=items,
                         items_total=items_total,
                         amounts_match=amounts_match)


@app.route('/claim/<claim_id>/edit', methods=['GET', 'POST'])
def edit_claim(claim_id):
    """Edit an existing claim"""
    claim = Claim.query.get_or_404(claim_id)
    form = EditClaimForm(obj=claim)
    
    if form.validate_on_submit():
        # Update claim fields
        claim.alias_name = form.alias_name.data
        claim.from_date = form.from_date.data
        claim.to_date = form.to_date.data
        claim.total_amount = form.total_amount.data
        claim.total_currency = form.total_currency.data
        claim.paid_amount = form.paid_amount.data
        claim.paid_currency = form.paid_currency.data
        claim.expense_group = form.expense_group.data
        claim.business_purpose = form.business_purpose.data
        
        # Handle file upload if new file provided
        if form.receipt_file.data:
            file_path = save_uploaded_file(
                form.receipt_file.data, 
                app.config['UPLOAD_FOLDER'], 
                claim_id
            )
            if file_path:
                # Remove old file if it exists
                if claim.upload_file_path and os.path.exists(claim.upload_file_path):
                    try:
                        os.remove(claim.upload_file_path)
                    except:
                        pass  # Ignore errors when removing old file
                claim.upload_file_path = file_path
        
        try:
            db.session.commit()
            flash('Claim updated successfully!', 'success')
            return redirect(url_for('view_claim', claim_id=claim_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating claim: {str(e)}', 'error')
    
    return render_template('edit_claim.html', form=form, claim=claim)


@app.route('/claim/<claim_id>/item/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(claim_id, item_id):
    """Edit an existing item"""
    claim = Claim.query.get_or_404(claim_id)
    item = ClaimItem.query.get_or_404(item_id)
    
    # Ensure item belongs to this claim
    if item.claim_id != claim_id:
        flash('Item not found in this claim.', 'error')
        return redirect(url_for('view_claim', claim_id=claim_id))
    
    form = ClaimItemForm(obj=item)
    
    if form.validate_on_submit():
        # Update item fields
        item.description = form.description.data
        item.amount = form.amount.data
        item.currency = form.currency.data
        item.paid_amount = form.paid_amount.data
        item.paid_currency = form.paid_currency.data
        item.justification = form.justification.data
        
        try:
            db.session.commit()
            flash('Item updated successfully!', 'success')
            return redirect(url_for('view_claim', claim_id=claim_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating item: {str(e)}', 'error')
    
    return render_template('edit_item.html', form=form, claim=claim, item=item)


@app.route('/claim/<claim_id>/item/<int:item_id>/delete', methods=['POST'])
def delete_item(claim_id, item_id):
    """Delete an item"""
    item = ClaimItem.query.get_or_404(item_id)
    
    # Ensure item belongs to this claim
    if item.claim_id != claim_id:
        flash('Item not found in this claim.', 'error')
        return redirect(url_for('view_claim', claim_id=claim_id))
    
    try:
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting item: {str(e)}', 'error')
    
    return redirect(url_for('view_claim', claim_id=claim_id))


@app.route('/claim/<claim_id>/delete', methods=['POST'])
def delete_claim(claim_id):
    """Delete a claim and all its items"""
    claim = Claim.query.get_or_404(claim_id)
    
    try:
        # Delete uploaded file if it exists
        if claim.upload_file_path and os.path.exists(claim.upload_file_path):
            try:
                os.remove(claim.upload_file_path)
            except:
                pass  # Ignore errors when removing file
        
        # Delete claim (items will be deleted automatically due to cascade)
        db.session.delete(claim)
        db.session.commit()
        flash('Claim deleted successfully!', 'success')
        return redirect(url_for('claims_list'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting claim: {str(e)}', 'error')
        return redirect(url_for('view_claim', claim_id=claim_id))


@app.route('/reports', methods=['GET', 'POST'])
def reports():
    """Generate and download reports"""
    from utils import get_available_months
    
    form = ReportForm()
    
    # Get all available claims for the multi-select field
    form.selected_claims.choices = get_available_claims()
    
    # Populate month_year choices dynamically (for legacy single-month reports)
    form.month_year.choices = get_available_months()
    
    if form.validate_on_submit():
        report_type = form.report_type.data
        
        try:
            # Handle multi-claim reports
            if form.selected_claims.data:  # If claims are selected
                claim_ids = [int(claim_id) for claim_id in form.selected_claims.data]
                
                if report_type == 'comprehensive_report':
                    # Generate comprehensive ZIP with ISD reports per month, combined financial, and receipts
                    zip_path = create_multi_report_zip(claim_ids)
                    return send_file(zip_path, as_attachment=True, 
                                   download_name=f'comprehensive_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')
                    
                elif report_type == 'multi_isd_reimbursement':
                    # Generate separate ISD reports per month
                    isd_reports = generate_multi_claim_isd_reports(claim_ids)
                    if len(isd_reports) == 1:
                        # Single month, return CSV directly
                        month_key = list(isd_reports.keys())[0]
                        report_data = isd_reports[month_key]
                        response = make_response(report_data['content'])
                        response.headers['Content-Type'] = 'text/csv'
                        response.headers['Content-Disposition'] = f'attachment; filename={report_data["filename"]}'
                        return response
                    else:
                        # Multiple months, create ZIP
                        import tempfile
                        import zipfile
                        
                        zip_path = f"isd_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                        with zipfile.ZipFile(zip_path, 'w') as zip_file:
                            for month_key, report_data in isd_reports.items():
                                zip_file.writestr(report_data['filename'], report_data['content'])
                        
                        return send_file(zip_path, as_attachment=True, download_name=f'isd_reports_multi.zip')
                        
                elif report_type == 'multi_financial_expense':
                    # Generate combined financial report
                    csv_content = generate_multi_claim_financial_csv(claim_ids)
                    response = make_response(csv_content)
                    response.headers['Content-Type'] = 'text/csv'
                    response.headers['Content-Disposition'] = f'attachment; filename=financial_expense_combined_{datetime.now().strftime("%Y%m%d")}.csv'
                    return response
                    
            # Handle legacy single-month reports (if month_year is selected and no claims selected)
            elif form.month_year.data:
                month_year = form.month_year.data
                
                if report_type == 'isd_reimbursement':
                    # Generate ISD Reimbursement CSV
                    csv_content = generate_isd_reimbursement_csv(month_year)
                    response = make_response(csv_content)
                    response.headers['Content-Type'] = 'text/csv'
                    response.headers['Content-Disposition'] = f'attachment; filename=isd_reimbursement_{month_year.replace("-", "_")}.csv'
                    return response
                    
                elif report_type == 'financial_expense':
                    # Generate Financial Expense CSV
                    csv_content = generate_financial_expense_csv(month_year)
                    response = make_response(csv_content)
                    response.headers['Content-Type'] = 'text/csv'
                    response.headers['Content-Disposition'] = f'attachment; filename=financial_expense_{month_year.replace("-", "_")}.csv'
                    return response
                    
                elif report_type == 'receipts_export':
                    # Generate receipts ZIP
                    zip_path = create_receipts_zip(month_year, app.config['UPLOAD_FOLDER'])
                    return send_file(zip_path, as_attachment=True, download_name=f'receipts_{month_year.replace("-", "_")}.zip')
            else:
                flash('Please select either specific claims or a month/year for the report.', 'error')
                
        except Exception as e:
            flash(f'Error generating report: {str(e)}', 'error')
    
    return render_template('reports.html', form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
