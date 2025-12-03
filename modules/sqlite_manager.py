import sqlite3
import json
from pathlib import Path

class SQLiteManager:
    """A lightweight SQLite backend for AccountApp.
    Stores JSON blobs for each company and file name.
    This is a stub implementation sufficient for basic CRUD operations.
    """
    def __init__(self, db_path: str = "data/accountapp.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._initialize_schema()

    def _initialize_schema(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS json_data (
                company TEXT NOT NULL,
                filename TEXT NOT NULL,
                data TEXT NOT NULL,
                PRIMARY KEY (company, filename)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS companies (
                name TEXT PRIMARY KEY,
                meta TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    # ------------------ Company Index ------------------
    def get_all_companies(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name, meta FROM companies")
        rows = cur.fetchall()
        return {name: json.loads(meta) for name, meta in rows}

    def create_company_structure(self, company_data):
        # Simplified: just insert into companies table
        name = company_data.get("company_name")
        if not name:
            return False
        meta = json.dumps(company_data)
        try:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO companies (name, meta) VALUES (?, ?)", (name, meta))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception:
            return False

    def delete_company(self, company_name: str):
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM companies WHERE name = ?", (company_name,))
            cur.execute("DELETE FROM json_data WHERE company = ?", (company_name,))
            self.conn.commit()
            return True
        except Exception:
            return False

    # ------------------ JSON Operations ------------------
    def load_json(self, company_name: str, filename: str):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT data FROM json_data WHERE company = ? AND filename = ?",
            (company_name, filename),
        )
        row = cur.fetchone()
        if row:
            try:
                return json.loads(row[0])
            except json.JSONDecodeError:
                return None
        return None

    def save_json(self, company_name: str, filename: str, data):
        try:
            json_str = json.dumps(data, indent=2)
            cur = self.conn.cursor()
            cur.execute(
                "REPLACE INTO json_data (company, filename, data) VALUES (?, ?, ?)",
                (company_name, filename, json_str),
            )
            self.conn.commit()
            return True
        except Exception:
            return False

    # ------------------ Backup/Restore (stub) ------------------
    def backup_company(self, company_name: str, dest_folder: str):
        # For SQLite, a simple file copy of the DB can serve as backup
        try:
            import shutil
            dest = Path(dest_folder) / f"{company_name}_backup.db"
            shutil.copy(self.db_path, dest)
            return str(dest)
        except Exception:
            return None

    def restore_company(self, backup_path: str):
        # Replace current DB with backup (dangerous, used for demo only)
        try:
            import shutil
            shutil.copy(backup_path, self.db_path)
            self.conn = sqlite3.connect(self.db_path)
            return True
        except Exception:
            return False
