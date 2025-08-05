#!/usr/bin/env python3
"""
Production database initialization script.
This script initializes the database tables for production deployment.
"""
import os
from app import create_app
from models import db

def init_production_db():
    """Initialize production database."""
    app = create_app('production')
    
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Production database tables created successfully!")
            
            # Test database connection
            from models import Claim
            test_query = Claim.query.first()
            print("✅ Database connection test successful!")
            
        except Exception as e:
            print(f"❌ Error initializing production database: {str(e)}")
            raise

if __name__ == '__main__':
    init_production_db()
