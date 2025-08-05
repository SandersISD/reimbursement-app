#!/usr/bin/env python3
"""
Setup script for the Reimbursement Management System
This script initializes the database and creates necessary directories.
Run this with: uv run python setup.py
"""
import os
import sys
import subprocess
from pathlib import Path

def check_uv():
    """Check if uv is installed"""
    try:
        subprocess.run(['uv', '--version'], capture_output=True, check=True)
        print("✓ UV is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ UV is not installed. Please install it first:")
        print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("  Then restart your terminal and try again.")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'instance']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def initialize_database():
    """Initialize the database with tables"""
    try:
        # Import after ensuring we're in the right directory
        from app import app, db
        
        with app.app_context():
            db.create_all()
            print("✓ Database initialized successfully")
            
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path('.env')
    if not env_file.exists():
        env_content = """# Flask Configuration
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///reimbursement.db

# Development Settings
FLASK_ENV=development
FLASK_DEBUG=True

# File Upload Settings
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
"""
        env_file.write_text(env_content)
        print("✓ Created .env file with default configuration")
    else:
        print("✓ .env file already exists")

def setup_uv_environment():
    """Set up UV virtual environment and install dependencies"""
    try:
        # Create virtual environment if it doesn't exist
        if not Path('.venv').exists():
            print("📦 Creating virtual environment with uv...")
            subprocess.run(['uv', 'venv'], check=True)
        else:
            print("✓ Virtual environment already exists")
        
        # Install dependencies
        print("📥 Installing dependencies with uv...")
        subprocess.run(['uv', 'sync'], check=True)
        print("✓ Dependencies installed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error setting up uv environment: {e}")
        sys.exit(1)

def main():
    """Main setup function"""
    print("🚀 Setting up Reimbursement Management System with UV...\n")
    
    # Check if we're in the right directory
    if not Path('app.py').exists():
        print("✗ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check if uv is installed
    if not check_uv():
        sys.exit(1)
    
    # Set up uv environment
    setup_uv_environment()
    
    # Create necessary files and directories
    create_env_file()
    create_directories()
    
    # Initialize database
    initialize_database()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Review the .env file and update settings if needed")
    print("2. Run the application:")
    print("   • On macOS/Linux: ./start.sh")
    print("   • On Windows: start.bat")
    print("   • Or manually: uv run python app.py")
    print("3. Open your browser to: http://localhost:5000")
    print("\nFor more information, see README.md")

if __name__ == '__main__':
    main()
