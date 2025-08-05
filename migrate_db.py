#!/usr/bin/env python3
"""
Database migration script to update the schema for the new structure:
1. Add alias_name column to claims table
2. Add expense_group column to claims table  
3. Remove expense_group column from claim_items table
4. Update expense_group values with new categories
"""

import os
import sys
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrate_database():
    """Perform database migration"""
    
    try:
        # Import after adding to path
        from app import app, db
        from models import Claim, ClaimItem
        
        with app.app_context():
            print("🔄 Starting database migration...")
            
            # Check if migration is needed by looking at table structure
            inspector = db.inspect(db.engine)
            claims_columns = [col['name'] for col in inspector.get_columns('claims')]
            items_columns = [col['name'] for col in inspector.get_columns('claim_items')]
            
            print(f"📋 Current claims columns: {claims_columns}")
            print(f"📋 Current items columns: {items_columns}")
            
            migration_needed = False
            
            # Check if we need to add columns to claims table
            if 'alias_name' not in claims_columns:
                print("➕ Adding alias_name column to claims table...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE claims ADD COLUMN alias_name VARCHAR(100)"))
                    conn.commit()
                migration_needed = True
                
            if 'expense_group' not in claims_columns:
                print("➕ Adding expense_group column to claims table...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE claims ADD COLUMN expense_group VARCHAR(50) NOT NULL DEFAULT 'Others'"))
                    conn.commit()
                migration_needed = True
                
            # Check if we need to remove expense_group from items table
            if 'expense_group' in items_columns:
                print("🔄 Migrating expense_group data from items to claims...")
                
                # For each claim, find the most common expense group from its items
                claims = Claim.query.all()
                for claim in claims:
                    # Get all expense groups from this claim's items
                    item_groups = [item.expense_group for item in claim.items if hasattr(item, 'expense_group')]
                    
                    if item_groups:
                        # Use the first (most recent) expense group as the claim's expense group
                        # Or you could use the most common one
                        from collections import Counter
                        most_common_group = Counter(item_groups).most_common(1)[0][0]
                        claim.expense_group = map_old_to_new_group(most_common_group)
                    else:
                        claim.expense_group = 'Others'
                
                # Commit the changes
                db.session.commit()
                print("✅ Expense group data migrated from items to claims")
                
                # Now drop the expense_group column from claim_items
                print("➖ Removing expense_group column from claim_items table...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE claim_items DROP COLUMN expense_group"))
                    conn.commit()
                migration_needed = True
            
            if migration_needed:
                print("✅ Database migration completed successfully!")
                
                # Print summary
                updated_claims = Claim.query.count()
                updated_items = ClaimItem.query.count()
                print(f"📊 Updated {updated_claims} claims and {updated_items} items")
                
                # Show some examples
                print("\n📋 Sample of updated claims:")
                sample_claims = Claim.query.limit(5).all()
                for claim in sample_claims:
                    alias = claim.alias_name or "(no alias)"
                    print(f"  • {claim.claim_id[:8]}... | {alias} | {claim.expense_group}")
                    
            else:
                print("✅ Database is already up to date - no migration needed")
                
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        print("🔄 Rolling back changes...")
        try:
            db.session.rollback()
        except:
            pass  # Ignore rollback errors
        return False
        
    return True


def map_old_to_new_group(old_group):
    """Map old expense group names to new ones"""
    mapping = {
        'Travel': 'Airfare',
        'Meals': 'Meal', 
        'Office Supplies': 'General Consumables',
        'Training': 'Registration/Conference/Visa Fee',
        'Other': 'Others'
    }
    return mapping.get(old_group, 'Others')


if __name__ == '__main__':
    print("🚀 Reimbursement System Database Migration")
    print("=" * 50)
    
    # Backup reminder
    print("⚠️  IMPORTANT: Make sure you have a backup of your database before proceeding!")
    response = input("Do you want to continue with the migration? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        success = migrate_database()
        if success:
            print("\n🎉 Migration completed successfully!")
            print("You can now restart your application with the new schema.")
        else:
            print("\n💥 Migration failed. Please check the error messages above.")
            sys.exit(1)
    else:
        print("❌ Migration cancelled by user.")
        sys.exit(0)
