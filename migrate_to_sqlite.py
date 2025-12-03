"""
Migration script to convert JSON data to SQLite database
Run this once to migrate existing data
"""

import json
import os
import sys
from datetime import datetime
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.db_manager import get_db_manager


def backup_json_file():
    """Create backup of JSON file before migration"""
    json_path = 'data/erp_data.json'
    if os.path.exists(json_path):
        backup_path = f'data/erp_data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        shutil.copy2(json_path, backup_path)
        print(f"✅ Backed up JSON data to: {backup_path}")
        return True
    else:
        print("ℹ️  No existing JSON data to migrate")
        return False


def load_json_data():
    """Load data from JSON file"""
    json_path = 'data/erp_data.json'
    if not os.path.exists(json_path):
        return []
    
    with open(json_path, 'r') as f:
        try:
            data = json.load(f)
            print(f"📂 Loaded {len(data)} records from JSON")
            return data
        except json.JSONDecodeError:
            print("⚠️  JSON file is empty or corrupted")
            return []


def migrate_data():
    """Migrate JSON data to SQLite"""
    print("\n🚀 Starting data migration...\n")
    
    # Step 1: Backup
    has_data = backup_json_file()
    if not has_data:
        print("\n✅ Migration complete (no data to migrate)")
        return
    
    # Step 2: Load JSON data
    json_data = load_json_data()
    if not json_data:
        print("\n✅ Migration complete (no records found)")
        return
    
    # Step 3: Get database manager
    db = get_db_manager()
    
    # Step 4: Migrate each record
    migrated = 0
    errors = 0
    
    for record in json_data:
        try:
            module = record.get('module', 'Unknown')
            timestamp = record.get('timestamp', '')
            data = record.get('data', {})
            
            # Determine transaction type from module
            transaction_type = 'Generic'
            if 'FB50' in module or 'G/L' in module:
                transaction_type = 'FB50'
            elif 'FB60' in module or 'Vendor Invoice' in module:
                transaction_type = 'FB60'
            elif 'FB70' in module or 'Customer Invoice' in module:
                transaction_type = 'FB70'
            elif 'F-90' in module or 'Asset Acquisition' in module:
                transaction_type = 'F-90'
            
            # Save to database
            transaction_id = db.save_transaction(data, module, transaction_type)
            migrated += 1
            print(f"✓ Migrated record {migrated}: {module} (ID: {transaction_id})")
            
        except Exception as e:
            errors += 1
            print(f"✗ Error migrating record: {e}")
    
    # Step 5: Summary
    print(f"\n{'='*50}")
    print(f"📊 Migration Summary:")
    print(f"   Total records: {len(json_data)}")
    print(f"   Successfully migrated: {migrated}")
    print(f"   Errors: {errors}")
    print(f"{'='*50}\n")
    
    if errors == 0:
        print("✅ Migration completed successfully!")
    else:
        print(f"⚠️  Migration completed with {errors} errors")


def verify_migration():
    """Verify migrated data"""
    print("\n🔍 Verifying migration...\n")
    
    db = get_db_manager()
    
    # Get transaction count
    transactions = db.get_transactions()
    print(f"📝 Total transactions in database: {len(transactions)}")
    
    if transactions:
        print("\n📋 Sample transactions:")
        for trans in transactions[:5]:
            print(f"   - ID: {trans['id']}, Module: {trans['module']}, "
                  f"Type: {trans['transaction_type']}, Amount: {trans['amount']}")
            
            # Show line items
            line_items = db.get_line_items(trans['id'])
            print(f"     Line items: {len(line_items)}")
    
    print("\n✅ Verification complete")


if __name__ == '__main__':
    print("="*60)
    print("  ERP Application - JSON to SQLite Migration")
    print("="*60)
    
    # Run migration
    migrate_data()
    
    # Verify
    verify_migration()
    
    print("\n💡 Next steps:")
    print("   1. Test the application")
    print("   2. Verify data integrity")
    print("   3. If everything works, you can delete the JSON backup")
    print("\n")
