# Reimbursement Management System

A Flask-based web application for managing employee reimbursement requests with file upload support.

## Features

- Submit reimbursement claims with receipt uploads
- Add multiple items per claim
- Bootstrap-responsive UI
- SQLite database (easily switchable to PostgreSQL)
- Secure file handling
- UUID-based claim tracking

## Quick Start

### 1. Install uv (if not already installed)

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Set up the project

```bash
# Clone or download the project
cd reim-form

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Create required directories
mkdir -p uploads
mkdir -p instance
```

### 3. Initialize the database

```bash
python init_db.py
```

### 4. Run the application

```bash
# Development mode
python app.py

# The application will be available at http://localhost:5001
# (Port 5001 is used to avoid conflicts with macOS AirPlay)
```

## Testing the Application

You can test the full workflow:

1. **Create a Claim**: Go to http://localhost:5001 and click "Start New Claim"
2. **Fill the Form**: Add expense details, business purpose, and upload a receipt
3. **Add Items**: Break down your expenses into individual items
4. **View Summary**: See the complete claim with all items

## Project Structure

```
reim-form/
├── app.py              # Main Flask application
├── models.py           # Database models
├── forms.py            # WTForms form definitions
├── config.py           # Configuration settings
├── init_db.py          # Database initialization script
├── pyproject.toml      # Project dependencies (uv compatible)
├── uploads/            # File upload directory
├── instance/           # SQLite database location
└── templates/          # HTML templates
    ├── base.html
    ├── index.html
    ├── claim_form.html
    ├── item_form.html
    └── confirmation.html
```

## Deployment Options

### 1. Heroku

1. **Install Heroku CLI** and login:
   ```bash
   # Install Heroku CLI (macOS)
   brew tap heroku/brew && brew install heroku
   
   # Login
   heroku login
   ```

2. **Create Heroku app**:
   ```bash
   heroku create your-reimbursement-app
   
   # Add PostgreSQL database
   heroku addons:create heroku-postgresql:mini
   
   # Set environment variables
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(16))')
   ```

3. **Deploy**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   
   # Initialize database
   heroku run python init_db.py
   ```

### 2. Render.com

1. **Connect your GitHub repo** to Render
2. **Use the provided `render.yaml`** file for automatic deployment
3. **Set environment variables** in Render dashboard:
   - `FLASK_ENV=production`
   - `SECRET_KEY` (auto-generated)
4. **Deploy**: Render will automatically build and deploy

### 3. Fly.io

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create Fly app**:
   ```bash
   fly launch
   # Follow prompts to configure your app
   ```

3. **Deploy**:
   ```bash
   fly deploy
   ```

### 4. Vercel (Serverless)

For Vercel, you'll need to create a `vercel.json` configuration and use a serverless-compatible setup.

### Production Considerations

- **Database**: Switch from SQLite to PostgreSQL
- **File Storage**: Use cloud storage (AWS S3, Google Cloud Storage)
- **Security**: 
  - Set strong `SECRET_KEY`
  - Enable HTTPS
  - Implement rate limiting
  - Add user authentication (Flask-Login)
- **Monitoring**: Add logging and error tracking (Sentry)
- **Email**: Add SMTP configuration for notifications

## Future Enhancements

- **User Authentication**: Flask-Login for user accounts
- **Email Notifications**: SMTP integration for status updates
- **Admin Dashboard**: Approve/reject claims
- **Reporting**: Export claims to Excel/PDF
- **API**: REST API for mobile app integration
- **Audit Trail**: Track claim status changes
