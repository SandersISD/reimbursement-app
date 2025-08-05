#!/usr/bin/env python3
"""
Test production deployment locally using gunicorn.
This simulates how your app will run on production servers.
"""
import os
import subprocess
import sys

def test_production_locally():
    """Test the app with production settings locally."""
    print("🧪 Testing Production Configuration Locally")
    print("=" * 50)
    
    # Set production environment variables
    os.environ['FLASK_ENV'] = 'production'
    os.environ['SECRET_KEY'] = 'test-production-key-12345'
    
    print("✅ Environment variables set")
    print("✅ Using production configuration")
    print("✅ Database: SQLite (will be PostgreSQL in deployment)")
    print("")
    print("🚀 Starting production server with gunicorn...")
    print("📍 URL: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop")
    print("")
    
    try:
        # Run gunicorn (production WSGI server)
        subprocess.run([
            'gunicorn', 
            '--bind', '0.0.0.0:8000',
            '--workers', '2',
            '--timeout', '30',
            '--log-level', 'info',
            'app:app'
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Production test stopped")
    except FileNotFoundError:
        print("❌ Gunicorn not found. Install with: pip install gunicorn")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running gunicorn: {e}")
        sys.exit(1)

if __name__ == '__main__':
    test_production_locally()
