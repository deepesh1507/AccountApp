# account_app/modules/database_manager.py

import json
import logging
import os
import shutil
import csv
import zipfile
import hashlib
from pathlib import Path
from typing import Optional, Any, Dict, Union, List
from datetime import datetime
from tkinter import messagebox, filedialog

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Handles all file system operations for the ERP application.
    - Manages the main data directory.
    - Creates and deletes company structures.
    - Reads and writes JSON data files for each company.
    - Handles data import/export operations.
    """

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent / "data"
        self.companies_file = self.base_dir / "companies.json"
        self.companies_dir = self.base_dir / "companies"
        self.backup_dir = self.base_dir / "backups"
        self.initialize_storage()

    def initialize_storage(self) -> None:
        """Initialize storage directories and files"""
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.companies_dir.mkdir(parents=True, exist_ok=True)
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            if not self.companies_file.exists():
                self.save_json_index({})
            
            logger.info("Storage initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize storage: {e}")
            raise

    # ------------------ Load Companies ------------------
    def get_all_companies(self) -> Dict[str, Any]:
        """Return list of companies (each is a metadata dict).

        Historically the on-disk `companies.json` is stored as a dict
        mapping company_name -> meta. For UI code we return a list of
        company metadata dicts. Use `_load_companies_index` to access the
        underlying dict when needed.
        """
        try:
            idx = self._load_companies_index()
            # Return the underlying dict mapping company_name -> meta for callers
            return idx
        except Exception:
            return {}

    def _load_companies_index(self) -> Dict[str, Any]:
        """Load the underlying companies index (dict) from disk."""
        try:
            with self.companies_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, dict):
                    data = {}
            return data
        except Exception:
            return {}

    def get_company_path(self, company_name: Optional[str]) -> Path:
        """Return Path for a company's folder (safe simple slugging)."""
        if not company_name:
            return self.companies_dir / "_invalid_name"
        safe = company_name.strip().replace(os.sep, "_")
        return self.companies_dir / safe

    def save_json_index(self, data: Dict[str, Any]) -> None:
        """Save the top-level companies index (`companies.json`)."""
        try:
            self.companies_file.parent.mkdir(parents=True, exist_ok=True)
            with self.companies_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write companies index: {e}")

    # ------------------ Create Company ------------------
    def create_company_structure(self, company_data: Union[str, Dict[str, Any]]) -> bool:
        """
        company_data: dict containing at least 'name' (or a string name).
        Creates folder and default json files for the company and updates companies.json.
        """
        if not isinstance(company_data, dict) or not company_data.get("company_name"):
            messagebox.showerror(
                "Create Company Error",
                f"company_data must include 'company_name'. Received: {repr(company_data)}"
            )
            return False

        name = str(company_data.get("company_name"))
        companies = self.get_all_companies()

        # Prevent duplicate
        if name in companies:
            messagebox.showwarning("Create Company", f"Company '{name}' already exists.")
            return False

        company_dir = self.get_company_path(name)
        try:
            # Create company folder
            company_dir.mkdir(parents=True, exist_ok=False)

            # Handle Logo
            logo_path = ""
            if company_data.get("logo_source_path"):
                try:
                    src_path = Path(company_data["logo_source_path"])
                    if src_path.exists():
                        dest_path = company_dir / "logo.png"
                        shutil.copy2(src_path, dest_path)
                        logo_path = "logo.png"
                except Exception as e:
                    logger.error(f"Failed to copy logo: {e}")

            # Default structure
            defaults = {
                "meta.json": {
                    **company_data,
                    "logo_path": logo_path,
                    "created_at": datetime.now().isoformat(),
                    "modified_at": datetime.now().isoformat()
                },
                "clients.json": [],
                "invoices.json": [],
                "expenses.json": [],
                "accounts.json": [
                    {"code": "1000", "name": "Assets", "type": "asset", "parent": None},
                    {"code": "2000", "name": "Liabilities", "type": "liability", "parent": None},
                    {"code": "3000", "name": "Equity", "type": "equity", "parent": None},
                    {"code": "4000", "name": "Revenue", "type": "revenue", "parent": None},
                    {"code": "5000", "name": "Expenses", "type": "expense", "parent": None}
                ],
                "users.json": [{
                    "username": "admin",
                    "full_name": "Administrator",
                    "password": hashlib.sha256("admin".encode()).hexdigest(),
                    "role": "admin",
                    "created_at": datetime.now().isoformat()
                }]
            }

            for fname, content in defaults.items():
                with (company_dir / fname).open("w", encoding="utf-8") as f:
                    json.dump(content, f, indent=2)

            # Update global companies index with key info
            companies[name] = {
                "company_name": company_data.get("company_name", name),
                "company_type": company_data.get("company_type", "Unknown"),
                "city": company_data.get("city", ""),
                "state": company_data.get("state", ""),
                "logo_path": logo_path,
                "created_at": company_data.get("created_at", datetime.now().isoformat()),
                "status": company_data.get("status", "Active"),
            }

            with self.companies_file.open("w", encoding="utf-8") as f:
                json.dump(companies, f, indent=2)

            return True

        except Exception as e:
            # Cleanup on failure
            try:
                if company_dir.exists():
                    shutil.rmtree(company_dir)
            except Exception:
                pass
            messagebox.showerror("Create Company Error", f"Failed to create company '{name}': {e}")
            return False

    # ------------------ Delete Company ------------------
    def delete_company(self, company_name: str) -> bool:
        """
        Remove company folder and update companies.json.
        Returns True if deleted, False if not found or error.
        """
        companies = self.get_all_companies()
        if company_name not in companies:
            return False
        company_dir = self.get_company_path(company_name)
        try:
            if company_dir.exists():
                shutil.rmtree(company_dir)
            companies.pop(company_name, None)
            with self.companies_file.open("w", encoding="utf-8") as f:
                json.dump(companies, f, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete company: {e}")
            return False

    # ------------------ JSON Operations ------------------
    def load_json(self, company_name: str, filename: str) -> Optional[Any]:
        """Read and return parsed JSON from a company file."""
        path = self.get_company_path(company_name) / filename
        try:
            if not path.exists():
                return None
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load {filename} for '{company_name}': {e}")
            return None

    def save_json(self, company_name: str, filename: str, data: Any) -> bool:
        """Write JSON data to a company file safely."""
        path = self.get_company_path(company_name) / filename
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(".tmp")
            with tmp.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            tmp.replace(path)
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save {filename} for '{company_name}': {e}")
            return False

    # ------------------ Export ------------------
    def export_to_csv(self, company_name: str, json_filename: str, csv_path: Optional[str] = None) -> Optional[str]:
        """
        Export a JSON list-of-dicts file (e.g., clients.json) to CSV.
        If csv_path is None, will prompt user with a save dialog.
        Returns the path to written CSV or None on failure.
        """
        data = self.load_json(company_name, json_filename)
        if not isinstance(data, list) or not data:
            messagebox.showinfo("Export", "No data available to export.")
            return None

        if csv_path is None:
            csv_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"{company_name}_{json_filename.replace('.json', '')}.csv"
            )
            if not csv_path:
                return None

        try:
            headers = set()
            for item in data:
                if isinstance(item, dict):
                    headers.update(item.keys())
            headers = list(headers)

            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for item in data:
                    writer.writerow({k: item.get(k, "") for k in headers})
            return csv_path
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export to CSV: {e}")
            return None

    # ------------------ Backup/Restore ------------------
    def backup_company(self, company_name: str, dest_folder: Union[str, Path]) -> Optional[str]:
        """Create a zip backup of a company folder. Returns path to zip or None."""
        try:
            company_dir = self.get_company_path(company_name)
            if not company_dir.exists():
                messagebox.showerror("Backup Error", f"Company '{company_name}' not found.")
                return None
            dest_folder = Path(dest_folder)
            dest_folder.mkdir(parents=True, exist_ok=True)
            zip_path = dest_folder / f"{company_name}.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(company_dir):
                    for f in files:
                        full = Path(root) / f
                        zf.write(full, full.relative_to(company_dir.parent))
            return str(zip_path)
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to backup company: {e}")
            return None

    def restore_company(self, zip_file: Union[str, Path]) -> bool:
        """Restore a company from a zip file into companies directory."""
        try:
            zip_file = Path(zip_file)
            if not zip_file.exists():
                return False
            
            # Extract company name from the zip filename (e.g., "MyCompany.zip" -> "MyCompany")
            company_name = zip_file.stem
            target_dir = self.get_company_path(company_name)

            if target_dir.exists():
                if not messagebox.askyesno("Overwrite Confirmation",
                                           f"The company '{company_name}' already exists. Do you want to overwrite it?"):
                    return False
                shutil.rmtree(target_dir)

            with zipfile.ZipFile(zip_file, "r") as zf:
                # Extract to the specific company directory
                zf.extractall(target_dir)

            # After restoring files, we need to re-sync the main companies.json index
            self.resync_companies_index()
            return True 
        except Exception as e:
            messagebox.showerror("Restore Error", f"Failed to restore backup: {e}")
            return False

    def resync_companies_index(self) -> None:
        """
        Scans the companies directory and rebuilds the `companies.json` index.
        This is useful after manual changes or restores.
        """
        synced_companies = {}
        for company_dir in self.companies_dir.iterdir():
            if not company_dir.is_dir():
                continue

            meta_file = company_dir / "meta.json"
            if meta_file.exists():
                try:
                    with meta_file.open("r", encoding="utf-8") as f:
                        meta_data = json.load(f)
                    
                    company_name = meta_data.get("company_name")
                    if company_name:
                        synced_companies[company_name] = {
                            "company_name": company_name,
                            "company_type": meta_data.get("company_type", "Unknown"),
                            "city": meta_data.get("city", ""),
                            "state": meta_data.get("state", ""),
                            "created_at": meta_data.get("created_at", ""),
                            "status": meta_data.get("status", "Active"),
                        }
                except (json.JSONDecodeError, KeyError):
                    # Ignore corrupted meta files during resync
                    continue
        self.save_json_index(synced_companies)
