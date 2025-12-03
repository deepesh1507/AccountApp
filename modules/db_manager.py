"""
SQLite Database Manager for ERP Application
Handles all database operations with proper connection management
"""

import sqlite3
import json
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for ERP application"""
    
    def __init__(self, db_path: str = 'data/erp.db'):
        self.db_path = db_path
        self.ensure_data_directory()
        self.init_database()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Companies table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    code TEXT UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Transactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER,
                    module TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    document_number TEXT,
                    posting_date DATE,
                    document_date DATE,
                    amount DECIMAL(15,2),
                    currency TEXT DEFAULT 'USD',
                    status TEXT DEFAULT 'Posted',
                    reference TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    metadata TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(id)
                )
            ''')
            
            # Line Items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS line_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_id INTEGER NOT NULL,
                    line_number INTEGER,
                    account TEXT,
                    description TEXT,
                    debit DECIMAL(15,2) DEFAULT 0,
                    credit DECIMAL(15,2) DEFAULT 0,
                    amount DECIMAL(15,2),
                    cost_center TEXT,
                    profit_center TEXT,
                    tax_code TEXT,
                    FOREIGN KEY (transaction_id) REFERENCES transactions(id) ON DELETE CASCADE
                )
            ''')
            
            # Audit Log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    record_id INTEGER,
                    action TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    changed_by TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trans_module ON transactions(module)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_trans_date ON transactions(posting_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_line_trans ON line_items(transaction_id)')
            
            logger.info("Database initialized successfully")
    
    def save_transaction(self, data: Dict[str, Any], module: str, transaction_type: str) -> int:
        """
        Save a transaction with line items
        Returns transaction ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Extract grid data
            grid_keys = [k for k in data.keys() if k.startswith("grid_")]
            line_items = data.get(grid_keys[0], []) if grid_keys else []
            
            # Remove grid data from metadata
            metadata = {k: v for k, v in data.items() if not k.startswith("grid_")}
            
            # Insert transaction
            cursor.execute('''
                INSERT INTO transactions (
                    module, transaction_type, document_date, posting_date,
                    amount, reference, metadata, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                module,
                transaction_type,
                metadata.get('Document Date') or metadata.get('Invoice Date'),
                metadata.get('Posting Date'),
                metadata.get('Amount') or metadata.get('Invoice Amount'),
                metadata.get('Reference'),
                json.dumps(metadata),
                'system'  # TODO: Get from user session
            ))
            
            transaction_id = cursor.lastrowid
            
            # Insert line items
            for idx, item in enumerate(line_items, 1):
                amount = float(item.get('Amount') or item.get('Amount in Doc.Curr', 0))
                debit = amount if item.get('D/C', '').upper() in ['D', 'DEBIT'] else 0
                credit = amount if item.get('D/C', '').upper() in ['C', 'CREDIT'] else 0
                
                cursor.execute('''
                    INSERT INTO line_items (
                        transaction_id, line_number, account, description,
                        debit, credit, amount, cost_center, profit_center, tax_code
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    transaction_id,
                    idx,
                    item.get('G/L Acct') or item.get('Asset Number'),
                    item.get('Description') or item.get('Short Text'),
                    debit,
                    credit,
                    amount,
                    item.get('Cost Center'),
                    item.get('Profit Center'),
                    item.get('Tax Code')
                ))
            
            logger.info(f"Saved transaction {transaction_id} with {len(line_items)} line items")
            return transaction_id
    
    def get_transactions(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Get transactions with optional filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM transactions WHERE 1=1"
            params = []
            
            if filters:
                if 'module' in filters:
                    query += " AND module = ?"
                    params.append(filters['module'])
                if 'date_from' in filters:
                    query += " AND posting_date >= ?"
                    params.append(filters['date_from'])
                if 'date_to' in filters:
                    query += " AND posting_date <= ?"
                    params.append(filters['date_to'])
            
            query += " ORDER BY created_at DESC"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_line_items(self, transaction_id: int) -> List[Dict]:
        """Get line items for a transaction"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM line_items WHERE transaction_id = ? ORDER BY line_number",
                (transaction_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_trial_balance(self, date_from: str = None, date_to: str = None) -> List[Dict]:
        """Generate trial balance report"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT 
                    account,
                    SUM(debit) as total_debit,
                    SUM(credit) as total_credit,
                    SUM(debit - credit) as balance
                FROM line_items li
                JOIN transactions t ON li.transaction_id = t.id
                WHERE 1=1
            '''
            params = []
            
            if date_from:
                query += " AND t.posting_date >= ?"
                params.append(date_from)
            if date_to:
                query += " AND t.posting_date <= ?"
                params.append(date_to)
            
            query += " GROUP BY account ORDER BY account"
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]


# Singleton instance
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get singleton database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
