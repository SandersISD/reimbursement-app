#!/bin/bash
# Startup script for the Reimbursement Management System using UV

echo "🚀 Starting Reimbursement Management System..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "Then restart your terminal and try again."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from the project root directory (where app.py is located)"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv
fi

# Install dependencies
echo "📥 Installing dependencies..."
uv sync

# Create uploads directory
echo "📁 Creating uploads directory..."
mkdir -p uploads

# Initialize database
echo "🗄️ Initializing database..."
uv run python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ Database initialized successfully!')
"

echo "✅ Setup complete!"
echo ""
echo "🌐 Starting the application..."
echo "📱 Open your browser to: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Run the application
uv run python app.py
