"""
Enhanced SQLite Manager for AccountApp
Provides full CRUD operations, connection pooling, transaction management,
and comprehensive database operations for production use.
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Simple connection pool for SQLite"""
    
    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self._connections = []
        self._lock = threading.Lock()
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Create initial connection pool"""
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            self._connections.append(conn)
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a connection from the pool"""
        with self._lock:
            if self._connections:
                return self._connections.pop()
            else:
                # Create new connection if pool is empty
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                return conn
    
    def return_connection(self, conn: sqlite3.Connection):
        """Return a connection to the pool"""
        with self._lock:
            if len(self._connections) < self.pool_size:
                self._connections.append(conn)
            else:
                conn.close()
    
    def close_all(self):
        """Close all connections in the pool"""
        with self._lock:
            for conn in self._connections:
                conn.close()
            self._connections.clear()


class EnhancedSQLiteManager:
    """
    Enhanced SQLite backend for AccountApp with:
    - Connection pooling
    - Transaction management
    - Comprehensive CRUD operations
    - Schema versioning
    - Data validation
    - Performance optimization
    """
    
    SCHEMA_VERSION = 1
    
    def __init__(self, db_path: str = "data/accountapp.db", pool_size: int = 5):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize connection pool
        self.pool = ConnectionPool(str(self.db_path), pool_size)
        
        # Initialize schema
        self._initialize_schema()
        logger.info(f"Enhanced SQLite Manager initialized: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for getting and returning connections"""
        conn = self.pool.get_connection()
        try:
            yield conn
        finally:
            self.pool.return_connection(conn)
    
    @contextmanager
    def transaction(self):
        """Context manager for transactions with automatic commit/rollback"""
        conn = self.pool.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
        finally:
            self.pool.return_connection(conn)
    
    def _initialize_schema(self):
        """Initialize database schema with all required tables"""
        with self.transaction() as conn:
            cur = conn.cursor()
            
            # Schema version table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Companies table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    company_name TEXT NOT NULL,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    gst_number TEXT,
                    pan_number TEXT,
                    financial_year_start TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    email TEXT,
                    role TEXT DEFAULT 'user',
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    UNIQUE(company_id, username)
                )
            """)
            
            # Chart of Accounts
            cur.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    account_code TEXT NOT NULL,
                    account_name TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    parent_account TEXT,
                    opening_balance REAL DEFAULT 0,
                    current_balance REAL DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    UNIQUE(company_id, account_code)
                )
            """)
            
            # Journal Entries
            cur.execute("""
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    voucher_number TEXT NOT NULL,
                    entry_type TEXT NOT NULL,
                    entry_date DATE NOT NULL,
                    narration TEXT,
                    total_debit REAL NOT NULL,
                    total_credit REAL NOT NULL,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    FOREIGN KEY (created_by) REFERENCES users(id),
                    UNIQUE(company_id, voucher_number)
                )
            """)
            
            # Journal Entry Lines
            cur.execute("""
                CREATE TABLE IF NOT EXISTS journal_entry_lines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    journal_entry_id INTEGER NOT NULL,
                    account_code TEXT NOT NULL,
                    debit REAL DEFAULT 0,
                    credit REAL DEFAULT 0,
                    line_narration TEXT,
                    FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id) ON DELETE CASCADE
                )
            """)
            
            # Clients/Vendors
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    client_code TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    client_type TEXT DEFAULT 'customer',
                    contact_person TEXT,
                    email TEXT,
                    phone TEXT,
                    address TEXT,
                    gst_number TEXT,
                    pan_number TEXT,
                    opening_balance REAL DEFAULT 0,
                    current_balance REAL DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    UNIQUE(company_id, client_code)
                )
            """)
            
            # Invoices
            cur.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    invoice_number TEXT NOT NULL,
                    client_id INTEGER NOT NULL,
                    invoice_date DATE NOT NULL,
                    due_date DATE,
                    subtotal REAL NOT NULL,
                    tax_amount REAL DEFAULT 0,
                    discount_amount REAL DEFAULT 0,
                    total_amount REAL NOT NULL,
                    paid_amount REAL DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    FOREIGN KEY (client_id) REFERENCES clients(id),
                    UNIQUE(company_id, invoice_number)
                )
            """)
            
            # Invoice Items
            cur.execute("""
                CREATE TABLE IF NOT EXISTS invoice_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    description TEXT,
                    quantity REAL NOT NULL,
                    unit_price REAL NOT NULL,
                    tax_rate REAL DEFAULT 0,
                    amount REAL NOT NULL,
                    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
                )
            """)
            
            # Inventory
            cur.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    item_code TEXT NOT NULL,
                    item_name TEXT NOT NULL,
                    category TEXT,
                    unit TEXT,
                    purchase_price REAL DEFAULT 0,
                    selling_price REAL DEFAULT 0,
                    current_stock REAL DEFAULT 0,
                    reorder_level REAL DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    UNIQUE(company_id, item_code)
                )
            """)
            
            # Audit Trail
            cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    user_id INTEGER,
                    table_name TEXT NOT NULL,
                    record_id INTEGER,
                    action TEXT NOT NULL,
                    old_values TEXT,
                    new_values TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Create indexes for performance
            cur.execute("CREATE INDEX IF NOT EXISTS idx_journal_entries_date ON journal_entries(entry_date)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_journal_entries_company ON journal_entries(company_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(invoice_date)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_invoices_client ON invoices(client_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_trail_company ON audit_trail(company_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_trail_timestamp ON audit_trail(timestamp)")
            
            # Check and update schema version
            cur.execute("SELECT version FROM schema_version WHERE version = ?", (self.SCHEMA_VERSION,))
            if not cur.fetchone():
                cur.execute("INSERT INTO schema_version (version) VALUES (?)", (self.SCHEMA_VERSION,))
            
            logger.info("Database schema initialized successfully")
    
    # ==================== Company Operations ====================
    
    def create_company(self, company_data: Dict[str, Any]) -> Optional[int]:
        """Create a new company"""
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO companies (
                        name, company_name, address, phone, email,
                        gst_number, pan_number, financial_year_start
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    company_data.get('name'),
                    company_data.get('company_name'),
                    company_data.get('address'),
                    company_data.get('phone'),
                    company_data.get('email'),
                    company_data.get('gst_number'),
                    company_data.get('pan_number'),
                    company_data.get('financial_year_start')
                ))
                company_id = cur.lastrowid
                logger.info(f"Company created: {company_data.get('name')} (ID: {company_id})")
                return company_id
        except sqlite3.IntegrityError as e:
            logger.error(f"Company already exists: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating company: {e}")
            return None
    
    def get_all_companies(self) -> List[Dict[str, Any]]:
        """Get all companies"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM companies ORDER BY name")
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    
    def get_company_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get company by name"""
        with self.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM companies WHERE name = ?", (name,))
            row = cur.fetchone()
            return dict(row) if row else None
    
    def update_company(self, company_id: int, company_data: Dict[str, Any]) -> bool:
        """Update company information"""
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                cur.execute("""
                    UPDATE companies SET
                        company_name = ?, address = ?, phone = ?, email = ?,
                        gst_number = ?, pan_number = ?, financial_year_start = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    company_data.get('company_name'),
                    company_data.get('address'),
                    company_data.get('phone'),
                    company_data.get('email'),
                    company_data.get('gst_number'),
                    company_data.get('pan_number'),
                    company_data.get('financial_year_start'),
                    company_id
                ))
                logger.info(f"Company updated: ID {company_id}")
                return True
        except Exception as e:
            logger.error(f"Error updating company: {e}")
            return False
    
    def delete_company(self, company_id: int) -> bool:
        """Delete a company and all related data"""
        try:
            with self.transaction() as conn:
                cur = conn.cursor()
                cur.execute("DELETE FROM companies WHERE id = ?", (company_id,))
                logger.info(f"Company deleted: ID {company_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting company: {e}")
            return False
    
    # ==================== Generic CRUD Operations ====================
    
    def insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """Generic insert operation"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            values = tuple(data.values())
            
            with self.transaction() as conn:
                cur = conn.cursor()
                cur.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values)
                return cur.lastrowid
        except Exception as e:
            logger.error(f"Error inserting into {table}: {e}")
            return None
    
    def select(self, table: str, where: Optional[Dict[str, Any]] = None,
               order_by: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Generic select operation"""
        try:
            query = f"SELECT * FROM {table}"
            params = []
            
            if where:
                conditions = ' AND '.join([f"{k} = ?" for k in where.keys()])
                query += f" WHERE {conditions}"
                params = list(where.values())
            
            if order_by:
                query += f" ORDER BY {order_by}"
            
            if limit:
                query += f" LIMIT {limit}"
            
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, params)
                rows = cur.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error selecting from {table}: {e}")
            return []
    
    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> bool:
        """Generic update operation"""
        try:
            set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
            where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
            values = list(data.values()) + list(where.values())
            
            with self.transaction() as conn:
                cur = conn.cursor()
                cur.execute(f"UPDATE {table} SET {set_clause} WHERE {where_clause}", values)
                return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating {table}: {e}")
            return False
    
    def delete(self, table: str, where: Dict[str, Any]) -> bool:
        """Generic delete operation"""
        try:
            where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
            values = list(where.values())
            
            with self.transaction() as conn:
                cur = conn.cursor()
                cur.execute(f"DELETE FROM {table} WHERE {where_clause}", values)
                return cur.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting from {table}: {e}")
            return False
    
    # ==================== Bulk Operations ====================
    
    def bulk_insert(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """Bulk insert operation for better performance"""
        if not data_list:
            return 0
        
        try:
            columns = ', '.join(data_list[0].keys())
            placeholders = ', '.join(['?' for _ in data_list[0]])
            values_list = [tuple(d.values()) for d in data_list]
            
            with self.transaction() as conn:
                cur = conn.cursor()
                cur.executemany(
                    f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                    values_list
                )
                return cur.rowcount
        except Exception as e:
            logger.error(f"Error bulk inserting into {table}: {e}")
            return 0
    
    # ==================== Audit Trail ====================
    
    def log_audit(self, company_id: int, user_id: Optional[int], table_name: str,
                  record_id: Optional[int], action: str, old_values: Optional[Dict] = None,
                  new_values: Optional[Dict] = None):
        """Log an audit trail entry"""
        try:
            self.insert('audit_trail', {
                'company_id': company_id,
                'user_id': user_id,
                'table_name': table_name,
                'record_id': record_id,
                'action': action,
                'old_values': json.dumps(old_values) if old_values else None,
                'new_values': json.dumps(new_values) if new_values else None
            })
        except Exception as e:
            logger.error(f"Error logging audit trail: {e}")
    
    # ==================== Utility Methods ====================
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a custom query"""
        try:
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, params)
                rows = cur.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def get_table_count(self, table: str, where: Optional[Dict[str, Any]] = None) -> int:
        """Get count of records in a table"""
        try:
            query = f"SELECT COUNT(*) as count FROM {table}"
            params = []
            
            if where:
                conditions = ' AND '.join([f"{k} = ?" for k in where.keys()])
                query += f" WHERE {conditions}"
                params = list(where.values())
            
            with self.get_connection() as conn:
                cur = conn.cursor()
                cur.execute(query, params)
                return cur.fetchone()['count']
        except Exception as e:
            logger.error(f"Error getting count from {table}: {e}")
            return 0
    
    def close(self):
        """Close all connections"""
        self.pool.close_all()
        logger.info("SQLite Manager closed")
