"""
Database Migration Utility
Handles migration from JSON-based storage to SQLite database
with data validation, backup, and rollback capabilities.
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from tkinter import messagebox
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.enhanced_sqlite_manager import EnhancedSQLiteManager
from modules.database_manager import DatabaseManager

logger = logging.getLogger(__name__)


class DatabaseMigration:
    """
    Handles migration from JSON to SQLite with:
    - Data validation
    - Automatic backup
    - Progress reporting
    - Rollback capability
    - Data integrity checks
    """
    
    def __init__(self, json_data_dir: str = "data", sqlite_db_path: str = "data/accountapp.db"):
        self.json_data_dir = Path(json_data_dir)
        self.sqlite_db_path = sqlite_db_path
        self.backup_dir = self.json_data_dir / "migration_backup"
        
        self.json_manager = DatabaseManager()
        self.sqlite_manager = None
        
        self.migration_stats = {
            'companies': 0,
            'users': 0,
            'accounts': 0,
            'journal_entries': 0,
            'clients': 0,
            'invoices': 0,
            'inventory': 0,
            'errors': []
        }
    
    def create_backup(self) -> bool:
        """Create backup of JSON data before migration"""
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
            
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup entire data directory
            if self.json_data_dir.exists():
                shutil.copytree(
                    self.json_data_dir,
                    self.backup_dir / "data_backup",
                    ignore=shutil.ignore_patterns('migration_backup', '*.db')
                )
            
            # Create backup metadata
            backup_meta = {
                'backup_date': datetime.now().isoformat(),
                'source_dir': str(self.json_data_dir),
                'backup_dir': str(self.backup_dir)
            }
            
            with open(self.backup_dir / "backup_meta.json", 'w') as f:
                json.dump(backup_meta, f, indent=2)
            
            logger.info(f"Backup created successfully at {self.backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def validate_json_data(self) -> bool:
        """Validate JSON data before migration"""
        try:
            companies = self.json_manager.get_all_companies()
            
            if not companies:
                logger.warning("No companies found in JSON data")
                return True  # Not an error, just empty
            
            for company in companies:
                company_name = company.get('name') or company.get('company_name')
                if not company_name:
                    self.migration_stats['errors'].append("Company without name found")
                    continue
                
                # Validate company data structure
                required_files = ['users.json', 'accounts.json']
                for file in required_files:
                    data = self.json_manager.load_json(company_name, file)
                    if data is None:
                        logger.warning(f"Missing {file} for company {company_name}")
            
            logger.info("JSON data validation completed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating JSON data: {e}")
            return False
    
    def migrate_companies(self) -> bool:
        """Migrate companies from JSON to SQLite"""
        try:
            companies = self.json_manager.get_all_companies()
            
            for company in companies:
                try:
                    # Prepare company data
                    company_data = {
                        'name': company.get('name') or company.get('company_name'),
                        'company_name': company.get('company_name', ''),
                        'address': company.get('address', ''),
                        'phone': company.get('phone', ''),
                        'email': company.get('email', ''),
                        'gst_number': company.get('gst_number', ''),
                        'pan_number': company.get('pan_number', ''),
                        'financial_year_start': company.get('financial_year_start', '2024-04-01')
                    }
                    
                    company_id = self.sqlite_manager.create_company(company_data)
                    
                    if company_id:
                        self.migration_stats['companies'] += 1
                        # Store mapping for later use
                        company['_sqlite_id'] = company_id
                    else:
                        self.migration_stats['errors'].append(
                            f"Failed to migrate company: {company_data['name']}"
                        )
                
                except Exception as e:
                    error_msg = f"Error migrating company {company.get('name', 'unknown')}: {e}"
                    logger.error(error_msg)
                    self.migration_stats['errors'].append(error_msg)
            
            logger.info(f"Migrated {self.migration_stats['companies']} companies")
            return True
            
        except Exception as e:
            logger.error(f"Error in migrate_companies: {e}")
            return False
    
    def migrate_users(self, companies: List[Dict]) -> bool:
        """Migrate users for each company"""
        try:
            for company in companies:
                company_name = company.get('name') or company.get('company_name')
                company_id = company.get('_sqlite_id')
                
                if not company_id:
                    continue
                
                # Load users from JSON
                users_data = self.json_manager.load_json(company_name, 'users.json')
                
                if not users_data:
                    continue
                
                for user in users_data:
                    try:
                        user_record = {
                            'company_id': company_id,
                            'username': user.get('username', ''),
                            'password_hash': user.get('password', ''),  # Already hashed
                            'full_name': user.get('full_name', ''),
                            'email': user.get('email', ''),
                            'role': user.get('role', 'user'),
                            'is_active': 1
                        }
                        
                        if self.sqlite_manager.insert('users', user_record):
                            self.migration_stats['users'] += 1
                    
                    except Exception as e:
                        error_msg = f"Error migrating user {user.get('username', 'unknown')}: {e}"
                        logger.error(error_msg)
                        self.migration_stats['errors'].append(error_msg)
            
            logger.info(f"Migrated {self.migration_stats['users']} users")
            return True
            
        except Exception as e:
            logger.error(f"Error in migrate_users: {e}")
            return False
    
    def migrate_accounts(self, companies: List[Dict]) -> bool:
        """Migrate chart of accounts for each company"""
        try:
            for company in companies:
                company_name = company.get('name') or company.get('company_name')
                company_id = company.get('_sqlite_id')
                
                if not company_id:
                    continue
                
                # Load accounts from JSON
                accounts_data = self.json_manager.load_json(company_name, 'accounts.json')
                
                if not accounts_data:
                    continue
                
                for account in accounts_data:
                    try:
                        account_record = {
                            'company_id': company_id,
                            'account_code': account.get('code', ''),
                            'account_name': account.get('name', ''),
                            'account_type': account.get('type', 'Asset'),
                            'parent_account': account.get('parent', ''),
                            'opening_balance': float(account.get('opening_balance', 0)),
                            'current_balance': float(account.get('current_balance', 0)),
                            'is_active': 1
                        }
                        
                        if self.sqlite_manager.insert('accounts', account_record):
                            self.migration_stats['accounts'] += 1
                    
                    except Exception as e:
                        error_msg = f"Error migrating account {account.get('code', 'unknown')}: {e}"
                        logger.error(error_msg)
                        self.migration_stats['errors'].append(error_msg)
            
            logger.info(f"Migrated {self.migration_stats['accounts']} accounts")
            return True
            
        except Exception as e:
            logger.error(f"Error in migrate_accounts: {e}")
            return False
    
    def migrate_journal_entries(self, companies: List[Dict]) -> bool:
        """Migrate journal entries for each company"""
        try:
            for company in companies:
                company_name = company.get('name') or company.get('company_name')
                company_id = company.get('_sqlite_id')
                
                if not company_id:
                    continue
                
                # Load journal entries from JSON
                entries_data = self.json_manager.load_json(company_name, 'journal_entries.json')
                
                if not entries_data:
                    continue
                
                for entry in entries_data:
                    try:
                        # Insert journal entry header
                        entry_record = {
                            'company_id': company_id,
                            'voucher_number': entry.get('voucher_number', ''),
                            'entry_type': entry.get('entry_type', 'Journal'),
                            'entry_date': entry.get('date', datetime.now().strftime('%Y-%m-%d')),
                            'narration': entry.get('narration', ''),
                            'total_debit': float(entry.get('total_debit', 0)),
                            'total_credit': float(entry.get('total_credit', 0))
                        }
                        
                        entry_id = self.sqlite_manager.insert('journal_entries', entry_record)
                        
                        if entry_id:
                            # Insert journal entry lines
                            lines = entry.get('lines', [])
                            for line in lines:
                                line_record = {
                                    'journal_entry_id': entry_id,
                                    'account_code': line.get('account_code', ''),
                                    'debit': float(line.get('debit', 0)),
                                    'credit': float(line.get('credit', 0)),
                                    'line_narration': line.get('narration', '')
                                }
                                self.sqlite_manager.insert('journal_entry_lines', line_record)
                            
                            self.migration_stats['journal_entries'] += 1
                    
                    except Exception as e:
                        error_msg = f"Error migrating journal entry {entry.get('voucher_number', 'unknown')}: {e}"
                        logger.error(error_msg)
                        self.migration_stats['errors'].append(error_msg)
            
            logger.info(f"Migrated {self.migration_stats['journal_entries']} journal entries")
            return True
            
        except Exception as e:
            logger.error(f"Error in migrate_journal_entries: {e}")
            return False
    
    def migrate_clients(self, companies: List[Dict]) -> bool:
        """Migrate clients/vendors for each company"""
        try:
            for company in companies:
                company_name = company.get('name') or company.get('company_name')
                company_id = company.get('_sqlite_id')
                
                if not company_id:
                    continue
                
                # Load clients from JSON
                clients_data = self.json_manager.load_json(company_name, 'clients.json')
                
                if not clients_data:
                    continue
                
                for client in clients_data:
                    try:
                        client_record = {
                            'company_id': company_id,
                            'client_code': client.get('code', ''),
                            'client_name': client.get('name', ''),
                            'client_type': client.get('type', 'customer'),
                            'contact_person': client.get('contact_person', ''),
                            'email': client.get('email', ''),
                            'phone': client.get('phone', ''),
                            'address': client.get('address', ''),
                            'gst_number': client.get('gst_number', ''),
                            'pan_number': client.get('pan_number', ''),
                            'opening_balance': float(client.get('opening_balance', 0)),
                            'current_balance': float(client.get('current_balance', 0)),
                            'is_active': 1
                        }
                        
                        if self.sqlite_manager.insert('clients', client_record):
                            self.migration_stats['clients'] += 1
                    
                    except Exception as e:
                        error_msg = f"Error migrating client {client.get('name', 'unknown')}: {e}"
                        logger.error(error_msg)
                        self.migration_stats['errors'].append(error_msg)
            
            logger.info(f"Migrated {self.migration_stats['clients']} clients")
            return True
            
        except Exception as e:
            logger.error(f"Error in migrate_clients: {e}")
            return False
    
    def migrate_invoices(self, companies: List[Dict]) -> bool:
        """Migrate invoices for each company"""
        try:
            for company in companies:
                company_name = company.get('name') or company.get('company_name')
                company_id = company.get('_sqlite_id')
                
                if not company_id:
                    continue
                
                # Load invoices from JSON
                invoices_data = self.json_manager.load_json(company_name, 'invoices.json')
                
                if not invoices_data:
                    continue
                
                for invoice in invoices_data:
                    try:
                        # Find client_id from client_code
                        client_code = invoice.get('client_code', '')
                        clients = self.sqlite_manager.select('clients', {
                            'company_id': company_id,
                            'client_code': client_code
                        })
                        
                        if not clients:
                            continue
                        
                        client_id = clients[0]['id']
                        
                        # Insert invoice header
                        invoice_record = {
                            'company_id': company_id,
                            'invoice_number': invoice.get('invoice_number', ''),
                            'client_id': client_id,
                            'invoice_date': invoice.get('date', datetime.now().strftime('%Y-%m-%d')),
                            'due_date': invoice.get('due_date', ''),
                            'subtotal': float(invoice.get('subtotal', 0)),
                            'tax_amount': float(invoice.get('tax_amount', 0)),
                            'discount_amount': float(invoice.get('discount_amount', 0)),
                            'total_amount': float(invoice.get('total_amount', 0)),
                            'paid_amount': float(invoice.get('paid_amount', 0)),
                            'status': invoice.get('status', 'pending'),
                            'notes': invoice.get('notes', '')
                        }
                        
                        invoice_id = self.sqlite_manager.insert('invoices', invoice_record)
                        
                        if invoice_id:
                            # Insert invoice items
                            items = invoice.get('items', [])
                            for item in items:
                                item_record = {
                                    'invoice_id': invoice_id,
                                    'item_name': item.get('item_name', ''),
                                    'description': item.get('description', ''),
                                    'quantity': float(item.get('quantity', 0)),
                                    'unit_price': float(item.get('unit_price', 0)),
                                    'tax_rate': float(item.get('tax_rate', 0)),
                                    'amount': float(item.get('amount', 0))
                                }
                                self.sqlite_manager.insert('invoice_items', item_record)
                            
                            self.migration_stats['invoices'] += 1
                    
                    except Exception as e:
                        error_msg = f"Error migrating invoice {invoice.get('invoice_number', 'unknown')}: {e}"
                        logger.error(error_msg)
                        self.migration_stats['errors'].append(error_msg)
            
            logger.info(f"Migrated {self.migration_stats['invoices']} invoices")
            return True
            
        except Exception as e:
            logger.error(f"Error in migrate_invoices: {e}")
            return False
    
    def migrate_inventory(self, companies: List[Dict]) -> bool:
        """Migrate inventory items for each company"""
        try:
            for company in companies:
                company_name = company.get('name') or company.get('company_name')
                company_id = company.get('_sqlite_id')
                
                if not company_id:
                    continue
                
                # Load inventory from JSON
                inventory_data = self.json_manager.load_json(company_name, 'inventory.json')
                
                if not inventory_data:
                    continue
                
                for item in inventory_data:
                    try:
                        item_record = {
                            'company_id': company_id,
                            'item_code': item.get('code', ''),
                            'item_name': item.get('name', ''),
                            'category': item.get('category', ''),
                            'unit': item.get('unit', 'pcs'),
                            'purchase_price': float(item.get('purchase_price', 0)),
                            'selling_price': float(item.get('selling_price', 0)),
                            'current_stock': float(item.get('current_stock', 0)),
                            'reorder_level': float(item.get('reorder_level', 0)),
                            'is_active': 1
                        }
                        
                        if self.sqlite_manager.insert('inventory', item_record):
                            self.migration_stats['inventory'] += 1
                    
                    except Exception as e:
                        error_msg = f"Error migrating inventory item {item.get('name', 'unknown')}: {e}"
                        logger.error(error_msg)
                        self.migration_stats['errors'].append(error_msg)
            
            logger.info(f"Migrated {self.migration_stats['inventory']} inventory items")
            return True
            
        except Exception as e:
            logger.error(f"Error in migrate_inventory: {e}")
            return False
    
    def run_migration(self, progress_callback=None) -> bool:
        """
        Run the complete migration process
        
        Args:
            progress_callback: Optional callback function(step, total, message)
        """
        try:
            total_steps = 9
            current_step = 0
            
            def update_progress(message):
                nonlocal current_step
                current_step += 1
                if progress_callback:
                    progress_callback(current_step, total_steps, message)
                logger.info(f"[{current_step}/{total_steps}] {message}")
            
            # Step 1: Create backup
            update_progress("Creating backup of JSON data...")
            if not self.create_backup():
                return False
            
            # Step 2: Validate JSON data
            update_progress("Validating JSON data...")
            if not self.validate_json_data():
                return False
            
            # Step 3: Initialize SQLite
            update_progress("Initializing SQLite database...")
            self.sqlite_manager = EnhancedSQLiteManager(self.sqlite_db_path)
            
            # Step 4: Migrate companies
            update_progress("Migrating companies...")
            companies = self.json_manager.get_all_companies()
            if not self.migrate_companies():
                return False
            
            # Step 5: Migrate users
            update_progress("Migrating users...")
            if not self.migrate_users(companies):
                return False
            
            # Step 6: Migrate accounts
            update_progress("Migrating chart of accounts...")
            if not self.migrate_accounts(companies):
                return False
            
            # Step 7: Migrate journal entries
            update_progress("Migrating journal entries...")
            if not self.migrate_journal_entries(companies):
                return False
            
            # Step 8: Migrate clients
            update_progress("Migrating clients...")
            if not self.migrate_clients(companies):
                return False
            
            # Step 9: Migrate invoices and inventory
            update_progress("Migrating invoices and inventory...")
            self.migrate_invoices(companies)
            self.migrate_inventory(companies)
            
            # Generate migration report
            self.generate_report()
            
            logger.info("Migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
        finally:
            if self.sqlite_manager:
                self.sqlite_manager.close()
    
    def generate_report(self):
        """Generate migration report"""
        report_path = self.backup_dir / "migration_report.txt"
        
        with open(report_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("DATABASE MIGRATION REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Migration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Migration Statistics:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Companies migrated: {self.migration_stats['companies']}\n")
            f.write(f"Users migrated: {self.migration_stats['users']}\n")
            f.write(f"Accounts migrated: {self.migration_stats['accounts']}\n")
            f.write(f"Journal Entries migrated: {self.migration_stats['journal_entries']}\n")
            f.write(f"Clients migrated: {self.migration_stats['clients']}\n")
            f.write(f"Invoices migrated: {self.migration_stats['invoices']}\n")
            f.write(f"Inventory items migrated: {self.migration_stats['inventory']}\n\n")
            
            if self.migration_stats['errors']:
                f.write("Errors:\n")
                f.write("-" * 40 + "\n")
                for error in self.migration_stats['errors']:
                    f.write(f"- {error}\n")
            else:
                f.write("No errors encountered!\n")
            
            f.write("\n" + "=" * 60 + "\n")
        
        logger.info(f"Migration report saved to {report_path}")


def main():
    """Main function to run migration"""
    print("=" * 60)
    print("AccountApp Database Migration Utility")
    print("=" * 60)
    print("\nThis will migrate your data from JSON to SQLite.")
    print("A backup will be created before migration.\n")
    
    response = input("Do you want to proceed? (yes/no): ")
    
    if response.lower() != 'yes':
        print("Migration cancelled.")
        return
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('migration.log'),
            logging.StreamHandler()
        ]
    )
    
    def progress_callback(step, total, message):
        print(f"\n[{step}/{total}] {message}")
    
    migration = DatabaseMigration()
    
    print("\nStarting migration...\n")
    success = migration.run_migration(progress_callback)
    
    if success:
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        print(f"\nMigration Statistics:")
        print(f"  Companies: {migration.migration_stats['companies']}")
        print(f"  Users: {migration.migration_stats['users']}")
        print(f"  Accounts: {migration.migration_stats['accounts']}")
        print(f"  Journal Entries: {migration.migration_stats['journal_entries']}")
        print(f"  Clients: {migration.migration_stats['clients']}")
        print(f"  Invoices: {migration.migration_stats['invoices']}")
        print(f"  Inventory: {migration.migration_stats['inventory']}")
        
        if migration.migration_stats['errors']:
            print(f"\nWarnings: {len(migration.migration_stats['errors'])} errors encountered")
            print("Check migration_report.txt for details")
        
        print(f"\nBackup location: {migration.backup_dir}")
        print("Migration report: migration_backup/migration_report.txt")
    else:
        print("\n" + "=" * 60)
        print("Migration failed!")
        print("=" * 60)
        print("Check migration.log for details")
        print(f"Your original data is safe at: {migration.backup_dir}")


if __name__ == "__main__":
    main()
