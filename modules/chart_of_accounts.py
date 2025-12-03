"""
Chart of Accounts Module
Minimal, single-copy implementation providing a simple UI shell and
basic data operations (load/save/export) used by the rest of the app.
This file intentionally keeps the UI minimal so it is easy to maintain
and avoids the earlier duplicated/garbled content.
"""

from typing import Any, Dict, List, Optional
from tkinter import messagebox, ttk
import customtkinter as ctk
from datetime import datetime

from .base_module import BaseModule


class ChartOfAccounts(BaseModule):
    def __init__(self, root: ctk.CTk, company_data: Dict[str, Any], user_data: Dict[str, Any], app_controller: Any):
        self.company_name = company_data.get("company_name") or company_data.get("name") or ""
        self.accounts: List[Dict[str, Any]] = []
        self.filtered_accounts: List[Dict[str, Any]] = []
        self.tree: Optional[ttk.Treeview] = None
        super().__init__(root, company_data, user_data, app_controller) # This will call setup_ui() after attributes are set

    def setup_ui(self) -> None:
        # Clear existing widgets
        for w in list(self.root.winfo_children()):
            w.destroy()

        main = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main.pack(fill="both", expand=True)

        header = ctk.CTkFrame(main, fg_color="#1976d2", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        title = ctk.CTkLabel(header, text="🧾 Chart of Accounts", font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
        title.pack(side="left", padx=20)

        nav = ctk.CTkFrame(header, fg_color="transparent")
        nav.pack(side="right", padx=20)
        ctk.CTkButton(nav, text="← Back to Dashboard", command=self.go_back, width=160).pack(side="left", padx=6)
        ctk.CTkButton(nav, text="🏠 Home", command=self.go_home, width=80).pack(side="left", padx=6)

        content = ctk.CTkFrame(main, fg_color=("white", "gray20"))
        content.pack(fill="both", expand=True, padx=20, pady=20)

        toolbar = ctk.CTkFrame(content, fg_color="#e8f5e9")
        toolbar.pack(fill="x", padx=10, pady=8)
        toolbar.grid_columnconfigure(0, weight=1) # Allow search entry to expand

        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="Search by name or code...")
        self.search_entry.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_accounts())
        self.filter_combo = ctk.CTkComboBox(toolbar, values=["All Types", "Asset", "Liability", "Equity", "Income", "Expense"], command=self.filter_accounts) 
        self.filter_combo.set("All Types")
        self.filter_combo.grid(row=0, column=1, padx=8, pady=8)

        self.count_label = ctk.CTkLabel(toolbar, text="Total: 0 accounts")
        self.count_label.grid(row=0, column=2, padx=12, pady=8)

        table_frame = ctk.CTkFrame(content, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Treeview", rowheight=28)

        self.tree = ttk.Treeview(table_frame, columns=("Code", "Name", "Type", "Balance"), show="headings", selectmode="browse")
        for col in ("Code", "Name", "Type", "Balance"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())

        actions = ctk.CTkFrame(content, fg_color="transparent")
        actions.pack(fill="x", padx=10, pady=8)
        ctk.CTkButton(actions, text="+ Add", command=self.show_add_form).pack(side="left", padx=6)
        ctk.CTkButton(actions, text="Edit", command=self.edit_selected).pack(side="left", padx=6)
        ctk.CTkButton(actions, text="Delete", command=self.delete_selected).pack(side="left", padx=6)
        ctk.CTkButton(actions, text="Export", command=self.export_accounts).pack(side="left", padx=6)

        # Load data after the entire UI has been constructed
        self.load_accounts()

    def load_accounts(self) -> None:
        try:
            data = self.db.load_json(self.company_name, "accounts.json") or []
            if isinstance(data, list):
                self.accounts = data
            elif isinstance(data, dict):
                self.accounts = list(data.values())
            else:
                self.accounts = []
        except Exception:
            self.accounts = []
        
        # Clear any active search filter to ensure all accounts are visible after load/refresh
        if self.search_entry:
            self.search_entry.delete(0, 'end')

        # Re-apply the current filter to the newly loaded data
        self.filter_accounts()

    def display_accounts(self) -> None:
        if self.tree is None:
            return
        for it in self.tree.get_children():
            self.tree.delete(it)
        for a in self.filtered_accounts:
            bal = a.get("balance", 0.0) # 'balance' is added by the _save function, not initially present in db_manager defaults
            self.tree.insert("", "end", values=(a.get("code",""), a.get("name",""), a.get("type",""), f"{bal}"))

    def search_accounts(self):
        term = self.search_entry.get().lower().strip()
        if not term:
            self.filtered_accounts = self.accounts.copy()
        else:
            self.filtered_accounts = [a for a in self.accounts if term in (a.get("name","") or "").lower() or term in (a.get("code","") or "").lower()]
        self.update_count()
        self.display_accounts()

    def filter_accounts(self, event=None):
        t = self.filter_combo.get()
        if t == "All Types":
            self.filtered_accounts = self.accounts.copy()
        else:
            self.filtered_accounts = [a for a in self.accounts if (a.get("type","") or "").lower() == t.lower()]
        self.display_accounts()
        self.update_count()

    def update_count(self):
        total = len(self.accounts)
        filtered = len(self.filtered_accounts)
        if total == filtered:
            self.count_label.configure(text=f"Total: {total} accounts")
        else:
            self.count_label.configure(text=f"Showing: {filtered} of {total} accounts")

    def show_add_form(self):
        self.show_account_form("Add Account", None)

    def edit_selected(self):
        if self.tree is None:
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Select an account first")
            return
        item = self.tree.item(sel[0])
        code = item['values'][0] # This is the 'code' from the treeview
        acc = next((a for a in self.accounts if a.get('code') == code), None)
        if acc:
            self.show_account_form("Edit Account", acc)

    def show_account_form(self, title, account_data):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("450x500")
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=12, pady=12)
        frame.grid_columnconfigure(1, weight=1)

        # Helper to create a labeled entry
        def create_labeled_widget(row, label_text, widget_class, **widget_kwargs):
            label = ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(weight="bold"))
            label.grid(row=row, column=0, padx=(0, 10), pady=10, sticky="e")
            widget = widget_class(frame, **widget_kwargs)
            widget.grid(row=row, column=1, padx=(0, 10), pady=10, sticky="ew")
            return widget

        # Create form fields with labels
        code = create_labeled_widget(0, "Account Code:", ctk.CTkEntry, width=300)
        name = create_labeled_widget(1, "Account Name:", ctk.CTkEntry, width=300)
        typ = create_labeled_widget(2, "Account Type:", ctk.CTkComboBox, values=["Asset", "Liability", "Equity", "Revenue", "Expense"])
        bal = create_labeled_widget(3, "Balance:", ctk.CTkEntry, width=300)

        if account_data:
            code.insert(0, account_data.get('code','')) # Line 243
            code.configure(state='disabled')
            name.insert(0, account_data.get('name',''))
            # Capitalize type to match combobox values
            account_type = (account_data.get('type', '') or '').capitalize()
            if account_type in typ.cget("values"):
                typ.set(account_type)
            else:
                typ.set("Asset") # Default fallback

            # Ensure balance is a string for the entry widget
            bal.insert(0, str(account_data.get('balance', 0.0))) # Line 250
        else:
            # Set defaults for a new account
            typ.set("Asset")
            bal.insert(0, "0.0")

        def _save():
            acc_code = code.get().strip()
            acc_name = name.get().strip()

            if not acc_code or not acc_name:
                messagebox.showwarning("Validation Error", "Account Code and Name are required.")
                return

            try:
                # Ensure balance is treated as float, defaulting to 0.0 if empty
                balance_val = float(bal.get().strip() or 0.0)
                data = { # Use consistent keys for saving
                    'code': acc_code,
                    'name': acc_name,
                    'type': typ.get().lower(), # Save type as lowercase for consistency
                    'balance': balance_val,
                    'created_date': datetime.now().isoformat()
                }
            except ValueError:
                messagebox.showerror("Input Error", "Balance must be a valid number.")
                return

            if account_data:
                for i,a in enumerate(self.accounts):
                    if a.get('code') == acc_code:
                        self.accounts[i] = data
                        break
            else:
                if any(a.get('code') == acc_code for a in self.accounts):
                    messagebox.showerror("Error", "Account code already exists!")
                    return
                self.accounts.append(data)
            self.db.save_json(self.company_name, 'accounts.json', self.accounts)
            dialog.destroy()
            self.load_accounts()

        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(button_frame, text="✓ Save", command=_save, fg_color="#2e7d32").pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="✕ Cancel", command=dialog.destroy, fg_color="#c62828").pack(side="left", padx=10)


    def delete_selected(self):
        if self.tree is None:
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Warning","Select an account to delete")
            return
        item = self.tree.item(sel[0])
        code = item['values'][0] # This is the 'code' from the treeview
        if messagebox.askyesno("Confirm","Delete selected account?"):
            self.accounts = [a for a in self.accounts if a.get('code') != code]
            self.db.save_json(self.company_name, 'accounts.json', self.accounts)
            self.load_accounts()

    def export_accounts(self):
        try:
            if self.db.export_to_csv(self.company_name, 'accounts.json'):
                messagebox.showinfo('Export','Exported successfully')
        except Exception as e:
            messagebox.showerror('Error', str(e))
