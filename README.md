# Reimbursement Management System

A complete Python-based local web application for handling employee reimbursement requests. Built with Flask, SQLAlchemy, and Bootstrap for a professional, user-friendly experience.

## Features

### 📋 Core Functionality
- **Complete Claim Management**: Create, edit, delete, and track reimbursement claims
- **Alias Names**: Give claims memorable names for easy identification
- **Comprehensive Expense Categories**: Support for 19 specific expense types (Airfare, Computer, Hotel, Meal, etc.)
- **Individual Item Tracking**: Break down expenses into detailed line items
- **File Upload Support**: Secure receipt and invoice uploads (PDF, JPG, PNG)
- **Amount Validation**: Automatic checking that item totals match claim totals
- **Multiple Currencies**: Support for HKD, USD, EUR, RMB, GBP, JPY

### 📊 Reporting & Export
- **Smart Month Detection**: Automatically detects which months have expense data
- **ISD Reimbursement Form**: Professional Excel export using official template with multi-month support, automatic totals, and professional formatting
- **Financial Office Export**: CSV export of claims with comprehensive details
- **Receipt Archive**: ZIP export of all receipts with organized naming including alias names
- **Multiple Export Formats**: Excel and CSV file generation with comprehensive ZIP bundles

### 🎨 User Interface
- **Responsive Design**: Bootstrap-based UI that works on all devices
- **Intuitive Navigation**: Clear workflow from claim creation to submission
- **Real-time Validation**: Live feedback on form inputs and totals
- **Professional Styling**: Clean, modern interface suitable for business use

## Quick Start

### Prerequisites
- Python 3.9 or higher
- `uv` package manager (recommended and required for this setup)

### Installation with UV (Recommended)

1. **Install UV** (if not already installed):
   ```bash
   # On macOS and Linux:
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows:
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Restart your terminal after installation
   ```

2. **Clone/Download the project** and navigate to the directory:
   ```bash
   cd reim-form
   ```

3. **Quick start using the provided scripts**:
   ```bash
   # On macOS/Linux:
   ./start.sh
   
   # On Windows:
   start.bat
   ```
   
   This will automatically:
   - Create a virtual environment
   - Install all dependencies
   - Initialize the database
   - Start the application

4. **Manual setup** (if you prefer step-by-step):
   ```bash
   # Create virtual environment
   uv venv
   
   # Install dependencies
   uv sync
   
   # Initialize database
   uv run python setup.py
   
   # Run the application
   uv run python app.py
   ```

5. **Open your browser** and go to: `http://localhost:5000`

### Why UV?
- **Fast**: UV is written in Rust and is significantly faster than pip
- **Reliable**: Better dependency resolution and lock files
- **Modern**: Uses modern Python packaging standards
- **Isolated**: Automatic virtual environment management

## Application Workflow

### 1. Create Main Claim
- Give your claim an optional alias name for easy identification
- Fill in expense date range (from/to dates)
- Enter total amount and currency
- Select the appropriate expense category (Airfare, Hotel, Meal, etc.)
- Optionally specify paid amount if different currency
- Provide business purpose/justification
- Upload receipt/invoice file

### 2. Add Individual Items
- Break down the total into specific expense items
- Each item inherits the claim's expense category automatically
- System validates that item totals match claim total
- Add justifications for specific items if needed

### 3. Review and Finalize
- View complete claim summary
- Check validation status
- Edit claim details or items if needed
- Generate reports for submission

### 4. Generate Reports
- **Smart Month Selection**: Only months with actual expense data are available
- **ISD Reimbursement Form**: Individual items with expense groups and alias names
- **Financial Expense Form**: Claim summaries with comprehensive details
- **Receipt Export**: ZIP file with all supporting documents

## Project Structure

```
reim-form/
├── app.py                 # Main Flask application
├── models.py              # Database models (Claims, Items)
├── forms.py               # WTForms for all forms
├── utils.py               # Utility functions (file handling, reports)
├── templates/             # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Dashboard/homepage
│   ├── new_claim.html    # Create new claim form
│   ├── add_items.html    # Add items to claim
│   ├── view_claim.html   # View claim details
│   ├── edit_claim.html   # Edit existing claim
│   ├── edit_item.html    # Edit individual item
│   ├── confirmation.html # Claim submission confirmation
│   ├── claims_list.html  # List all claims
│   ├── reports.html      # Generate reports
│   └── errors/           # Error pages (404, 500)
├── uploads/              # File storage (created automatically)
├── pyproject.toml        # Project dependencies and metadata
├── .env                  # Environment configuration
└── README.md            # This file
```

## Configuration

### Environment Variables
Create a `.env` file in the project root (already included):

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///reimbursement.db
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

### Database Configuration
- **Development**: Uses SQLite database (`reimbursement.db`)
- **Production**: Easily switchable to PostgreSQL by changing `DATABASE_URL`

### File Upload Settings
- **Supported formats**: PDF, JPG, JPEG, PNG
- **Maximum file size**: 16MB
- **Storage location**: `uploads/` directory (auto-created)
- **Naming convention**: Files prefixed with claim UUID

## Security Features

- **File Upload Validation**: Only allowed file types accepted
- **Secure Filename Handling**: Uses Werkzeug's secure_filename
- **CSRF Protection**: All forms protected with Flask-WTF tokens
- **Input Validation**: Server-side validation for all form inputs
- **SQL Injection Prevention**: SQLAlchemy ORM protects against SQL injection

## Deployment Options

### 1. Heroku (Free Tier Available)

1. **Prepare for deployment**:
   ```bash
   # Create Procfile
   echo "web: python app.py" > Procfile
   
   # Install gunicorn for production
   uv add gunicorn
   ```

2. **Deploy to Heroku**:
   ```bash
   # Install Heroku CLI, then:
   heroku create your-app-name
   heroku config:set SECRET_KEY=your-production-secret-key
   heroku config:set FLASK_ENV=production
   heroku addons:create heroku-postgresql:hobby-dev
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

### 2. Render (Modern Alternative)

1. **Create `render.yaml`**:
   ```yaml
   services:
     - type: web
       name: reimbursement-app
       env: python
       buildCommand: "uv sync"
       startCommand: "python app.py"
       envVars:
         - key: SECRET_KEY
           generateValue: true
         - key: FLASK_ENV
           value: production
   ```

2. **Connect your GitHub repo** to Render dashboard

### 3. Fly.io

1. **Install Fly CLI** and run:
   ```bash
   flyctl launch
   flyctl deploy
   ```

### 4. DigitalOcean App Platform

1. **Create app** from GitHub repository
2. **Set environment variables** in the dashboard
3. **Configure build** and run commands

## Production Considerations

### Database Migration
For production with PostgreSQL:

```python
# In app.py, change DATABASE_URL to:
DATABASE_URL=postgresql://user:password@host:port/database
```

### Security Enhancements
1. **Generate strong SECRET_KEY**:
   ```python
   import secrets
   print(secrets.token_hex(32))
   ```

2. **Use environment variables** for all secrets
3. **Enable HTTPS** in production
4. **Set up backup strategy** for database and files

### Performance Optimization
1. **Use production WSGI server** (Gunicorn)
2. **Configure reverse proxy** (Nginx)
3. **Implement file storage service** (AWS S3, etc.)
4. **Set up monitoring** and logging

## Future Enhancements

### User Authentication
```python
# Add Flask-Login for user management
from flask_login import LoginManager, login_required

# Modify routes to require authentication
@app.route('/claims')
@login_required
def claims_list():
    # existing code...
```

### Email Notifications
```python
# Add Flask-Mail for email notifications
from flask_mail import Mail, Message

# Send email when claim is submitted
def send_claim_notification(claim):
    # email implementation
```

### API Integration
```python
# Add RESTful API endpoints
@app.route('/api/claims', methods=['GET', 'POST'])
def api_claims():
    # JSON API implementation
```

### Desktop Version
For a non-web local application, consider:
- **Tkinter**: Built-in Python GUI framework
- **PyQt/PySide**: More advanced desktop applications
- **Kivy**: Cross-platform applications

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Database Errors**: Run database initialization command
3. **File Upload Issues**: Check file permissions in uploads/ directory
4. **Port Already in Use**: Change port in app.py or kill existing process

### Debug Mode
Set `FLASK_DEBUG=True` in `.env` for detailed error messages.

### Log Files
Check console output for errors and debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Review the code comments
3. Create an issue in the repository

---

**Built with ❤️ using Flask, SQLAlchemy, and Bootstrap**
