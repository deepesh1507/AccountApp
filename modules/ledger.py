"""
Ledger Module - Account-wise transaction view
Shows all transactions for a selected account
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from .base_module import BaseModule
from .utilities import Formatters


class Ledger(BaseModule):
    def __init__(self, root, company_data, user_data, app_controller):
        self.company_name = company_data.get("company_name", "")
        self.accounts = []
        self.selected_account = None
        self.transactions = []
        super().__init__(root, company_data, user_data, app_controller)

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main_frame.pack(fill="both", expand=True)

        header = ctk.CTkFrame(main_frame, fg_color="#7b1fa2", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="📖 Ledger", font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(side="left", padx=30)

        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.pack(side="right", padx=20)
        ctk.CTkButton(nav_frame, text="← Back", command=self.go_back, width=100).pack(side="left", padx=5)
        ctk.CTkButton(nav_frame, text="🏠 Home", command=self.go_home, width=80).pack(side="left", padx=5)

        content = ctk.CTkFrame(main_frame, fg_color=("white", "gray20"))
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Account selection
        select_frame = ctk.CTkFrame(content, fg_color=("#e3f2fd", "gray25"), corner_radius=10)
        select_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(select_frame, text="Select Account:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)

        self.account_var = ctk.StringVar()
        self.account_combo = ctk.CTkComboBox(select_frame, variable=self.account_var, width=400, command=self.load_ledger)
        self.account_combo.pack(side="left", padx=10, pady=10)

        # Date range
        ctk.CTkLabel(select_frame, text="From:").pack(side="left", padx=5)
        self.from_date = ctk.CTkEntry(select_frame, width=100)
        self.from_date.insert(0, datetime.now().replace(day=1).strftime("%Y-%m-%d"))
        self.from_date.pack(side="left", padx=5)

        ctk.CTkLabel(select_frame, text="To:").pack(side="left", padx=5)
        self.to_date = ctk.CTkEntry(select_frame, width=100)
        self.to_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.to_date.pack(side="left", padx=5)

        ctk.CTkButton(select_frame, text="🔍 View", command=self.load_ledger, width=80).pack(side="left", padx=10)

        # Ledger Table
        table_frame = ctk.CTkFrame(content, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Date", "Particulars", "Voucher No", "Debit", "Credit", "Balance")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Summary
        summary_frame = ctk.CTkFrame(content, fg_color="#e8f5e9", corner_radius=10)
        summary_frame.pack(fill="x", padx=10, pady=10)

        self.summary_label = ctk.CTkLabel(summary_frame, text="Select an account to view ledger", font=ctk.CTkFont(size=14))
        self.summary_label.pack(pady=15)

        self.load_accounts()

    def load_accounts(self):
        """Load chart of accounts"""
        try:
            data = self.db.load_json(self.company_name, "accounts.json")
            self.accounts = data if isinstance(data, list) else []
            
            account_options = [f"{acc.get('code')} - {acc.get('name')}" for acc in self.accounts]
            self.account_combo.configure(values=account_options)
        except:
            self.accounts = []

    def load_ledger(self, event=None):
        """Load ledger for selected account"""
        account_text = self.account_var.get()
        if not account_text:
            return

        account_code = account_text.split(" - ")[0].strip()
        from_dt = self.from_date.get()
        to_dt = self.to_date.get()

        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Load journal entries
        journal_entries = self.db.load_json(self.company_name, "journal_entries.json") or []

        # Filter transactions for this account
        transactions = []
        for entry in journal_entries:
            if from_dt <= entry.get("date", "") <= to_dt:
                for line in entry.get("lines", []):
                    if line.get("account_code") == account_code:
                        transactions.append({
                            "date": entry.get("date"),
                            "particulars": entry.get("narration"),
                            "voucher_no": entry.get("entry_id"),
                            "debit": line.get("debit", 0),
                            "credit": line.get("credit", 0)
                        })

        # Sort by date
        transactions.sort(key=lambda x: x["date"])

        # Display with running balance
        balance = 0
        total_debit = 0
        total_credit = 0

        for txn in transactions:
            debit = txn["debit"]
            credit = txn["credit"]
            balance += debit - credit
            total_debit += debit
            total_credit += credit

            self.tree.insert("", "end", values=(
                Formatters.format_date(datetime.fromisoformat(txn["date"])),
                txn["particulars"][:40],
                txn["voucher_no"],
                Formatters.format_number(debit) if debit > 0 else "",
                Formatters.format_number(credit) if credit > 0 else "",
                Formatters.format_number(balance)
            ))

        # Update summary
        self.summary_label.configure(
            text=f"Total Debit: {Formatters.format_currency(total_debit)} | " +
                 f"Total Credit: {Formatters.format_currency(total_credit)} | " +
                 f"Closing Balance: {Formatters.format_currency(balance)}"
        )
