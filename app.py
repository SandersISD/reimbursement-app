"""
Main Flask application for the Reimbursement Management System.
"""
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from config import config
from models import db, Claim, ClaimItem
from forms import ClaimForm, ClaimItemForm

def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    return app

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Create app instance
app = create_app()

@app.route('/')
def index():
    """Homepage - start new claim."""
    return render_template('index.html')

@app.route('/claim', methods=['GET', 'POST'])
def create_claim():
    """Create a new reimbursement claim."""
    form = ClaimForm()
    
    if form.validate_on_submit():
        # Handle file upload
        file = form.receipt_file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to avoid filename conflicts
            import time
            timestamp = str(int(time.time()))
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Create new claim
            claim = Claim(
                from_date=form.from_date.data,
                to_date=form.to_date.data,
                total_amount=form.total_amount.data,
                total_currency=form.total_currency.data,
                paid_amount=form.paid_amount.data,
                paid_currency=form.paid_currency.data,
                business_purpose=form.business_purpose.data,
                upload_file_path=file_path
            )
            
            try:
                db.session.add(claim)
                db.session.commit()
                flash(f'Claim created successfully! Claim ID: {claim.claim_id}', 'success')
                return redirect(url_for('add_items', claim_id=claim.claim_id))
            except Exception as e:
                db.session.rollback()
                flash('Error creating claim. Please try again.', 'danger')
                app.logger.error(f'Error creating claim: {str(e)}')
        else:
            flash('Invalid file type. Please upload PDF, PNG, or JPG files only.', 'danger')
    
    return render_template('claim_form.html', form=form)

@app.route('/claim/<claim_id>/items', methods=['GET', 'POST'])
def add_items(claim_id):
    """Add items to an existing claim."""
    # Verify claim exists
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
            expense_group=form.expense_group.data,
            justification=form.justification.data
        )
        
        try:
            db.session.add(item)
            db.session.commit()
            flash('Item added successfully!', 'success')
            
            # Determine next action based on button clicked
            if form.add_another.data:
                # Clear form and stay on same page
                return redirect(url_for('add_items', claim_id=claim_id))
            elif form.finish.data:
                # Go to confirmation page
                return redirect(url_for('confirmation', claim_id=claim_id))
            else:
                # Default: add_item button - stay on page
                return redirect(url_for('add_items', claim_id=claim_id))
                
        except Exception as e:
            db.session.rollback()
            flash('Error adding item. Please try again.', 'danger')
            app.logger.error(f'Error adding item: {str(e)}')
    
    # Get existing items for display
    items = ClaimItem.query.filter_by(claim_id=claim_id).order_by(ClaimItem.created_at).all()
    
    return render_template('item_form.html', form=form, claim=claim, items=items)

@app.route('/claim/<claim_id>/confirmation')
def confirmation(claim_id):
    """Show confirmation page with claim summary."""
    claim = Claim.query.get_or_404(claim_id)
    items = ClaimItem.query.filter_by(claim_id=claim_id).order_by(ClaimItem.created_at).all()
    
    # Calculate totals
    items_total = sum(item.amount for item in items)
    
    return render_template('confirmation.html', claim=claim, items=items, items_total=items_total)

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5001)
