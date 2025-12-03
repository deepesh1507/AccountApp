import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule
from datetime import datetime
import json
import os

class FIGLModule(ERPBaseModule):
    """
    ERP FI-GL (General Ledger) Module - Professional Implementation
    """
    
    def get_module_title(self) -> str:
        return "ERP FI - General Ledger (FI-GL)"
    
    def __init__(self, root, company_data, user_data, app_controller):
        super().__init__(root, company_data, user_data, app_controller)
        self.gl_docs_file = 'gl_documents.json'
        self.fiscal_year_file = 'fiscal_year_variants.json'
        self.posting_periods_file = 'posting_periods.json'
        self.doc_types_file = 'document_types.json'
        self.field_status_file = 'field_status_variants.json'
        self.exchange_rates_file = 'exchange_rates.json'
        self.fsv_file = 'financial_statement_versions.json'
        self.recon_accounts_file = 'reconciliation_accounts.json'

    def create_content(self):
        """Creates the menu for FI-GL sub-components"""
        
        # Scrollable menu area
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)
        
        # Header
        ctk.CTkLabel(
            menu_scroll,
            text="📊 General Ledger Management",
            font=("Arial", 20, "bold"),
            text_color=("#1976d2", "white")
        ).pack(pady=20)

        # Main Transactional Items (Show Data Tables)
        transactional_items = [
            ("📝 G/L Account Documents (FB50)", self.show_gl_documents, "#2e7d32"),
            ("🔄 Recurring Entries", self.show_recurring_entries, "#1976d2"),
            ("📋 Accrual/Deferral Documents", self.show_accrual_documents, "#f57c00"),
        ]
        
        ctk.CTkLabel(
            menu_scroll,
            text="Transactional Data",
            font=("Arial", 14, "bold"),
            text_color=("gray30", "gray70")
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        for title, command, color in transactional_items:
            btn = ctk.CTkButton(
                menu_scroll,
                text=title,
                command=command,
                height=50,
                font=("Arial", 13),
                fg_color=color,
                hover_color=self._darken_color(color),
                anchor="w"
            )
            btn.pack(fill="x", padx=20, pady=5)

        # Configuration Items (Show List Views)
        config_items = [
            ("⚙️ Fiscal Year Variant", self.show_fiscal_year_variants),
            ("📅 Posting Periods", self.show_posting_periods),
            ("📄 Document Types & Number Ranges", self.show_doc_types),
            ("🔧 Field Status Variants", self.show_field_status),
            ("💱 Exchange Rate Types", self.show_exchange_rates),
            ("📊 Financial Statement Version", self.show_fsv),
            ("🔗 Reconciliation Accounts", self.show_reconciliation_accounts),
        ]
        
        ctk.CTkLabel(
            menu_scroll,
            text="Configuration & Setup",
            font=("Arial", 14, "bold"),
            text_color=("gray30", "gray70")
        ).pack(anchor="w", padx=20, pady=(20, 5))
        
        for title, command in config_items:
            btn = ctk.CTkButton(
                menu_scroll,
                text=title,
                command=command,
                height=45,
                font=("Arial", 12),
                fg_color=("white", "gray20"),
                text_color=("black", "white"),
                hover_color=("gray90", "gray30"),
                anchor="w"
            )
            btn.pack(fill="x", padx=20, pady=3)
    
    def _darken_color(self, hex_color):
        """Darken a hex color for hover effect"""
        # Simple darkening - reduce each RGB component
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = max(0, r-30), max(0, g-30), max(0, b-30)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    # === TRANSACTIONAL ITEMS ===
    
    def show_gl_documents(self):
        """Show list of G/L Account Documents"""
        self.show_list_view(
            title="G/L Account Documents (FB50)",
            columns=["Doc No", "Date", "Reference", "Description", "Debit", "Credit", "Status"],
            data_loader=lambda: self.load_json_data(self.gl_docs_file),
            on_new=self.create_new_gl_document,
            on_edit=self.edit_gl_document,
            on_delete=lambda v: self.generic_delete(self.gl_docs_file, v[0], "Doc No")
        )
    
    def create_new_gl_document(self):
        """Show form to create new GL document"""
        form = self.show_form("Enter G/L Account Document (FB50)", self.save_gl_document)
        
        # Header Data
        header = form.add_section("Header Data")
        form.add_field("Document Date", ctk.CTkEntry(header), help_text="Posting date (YYYY-MM-DD)")
        form.add_field("Reference", ctk.CTkEntry(header), help_text="External reference number")
        form.add_field("Description", ctk.CTkEntry(header), help_text="Document description")
        form.add_field("Company Code", ctk.CTkEntry(header))
        form.add_field("Currency", ctk.CTkEntry(header))

        # Line Items Grid
        form.add_line_item_grid("Line Items", [
            "G/L Acct", "Short Text", "D/C", "Amount in Doc.Curr", "Tax Code", "Cost Center"
        ])
    
    def save_gl_document(self, data):
        """Save GL document with validation"""
        # Extract grid data
        grid_key = [k for k in data.keys() if k.startswith("grid_")][0]
        line_items = data.get(grid_key, [])

        if not line_items:
            messagebox.showerror("Error", "Please enter at least one line item.")
            return

        # Calculate debits and credits
        total_debit = 0.0
        total_credit = 0.0
        
        for item in line_items:
            try:
                amount = float(item.get("Amount in Doc.Curr", 0))
                dc = item.get("D/C", "").upper()
                if dc == "D" or dc == "DEBIT":
                    total_debit += amount
                elif dc == "C" or dc == "CREDIT":
                    total_credit += amount
            except ValueError:
                pass

        # Validate balance
        if abs(total_debit - total_credit) > 0.01:
            messagebox.showerror("Error", f"Document is not balanced.\nDebits: {total_debit}\nCredits: {total_credit}\nDifference: {total_debit - total_credit}")
            return

        # Generate Doc No
        data["Doc No"] = f"1000{len(self.load_json_data(self.gl_docs_file)) + 1}"
        data["Date"] = data.get("Document Date", datetime.now().strftime("%Y-%m-%d"))
        data["Debit"] = str(total_debit)
        data["Credit"] = str(total_credit)
        data["Status"] = "Posted"
        
        self.generic_save(self.gl_docs_file, data, "Doc No")
    
    def edit_gl_document(self, values):
        """Edit existing GL document"""
        messagebox.showinfo("Edit", f"Editing document: {values[0]}\n\nThis feature will open the document for editing.")
    
    def show_recurring_entries(self):
        """Show list of recurring entries"""
        self.show_list_view(
            title="Recurring Entries",
            columns=["Entry ID", "Description", "Frequency", "Next Run", "Amount", "Status"],
            data_loader=lambda: [
                {"Entry ID": "REC-001", "Description": "Monthly Rent", "Frequency": "Monthly", "Next Run": "2025-12-01", "Amount": "50000.00", "Status": "Active"},
                {"Entry ID": "REC-002", "Description": "Quarterly Insurance", "Frequency": "Quarterly", "Next Run": "2026-01-01", "Amount": "15000.00", "Status": "Active"},
            ],
            on_new=lambda: messagebox.showinfo("New", "Create new recurring entry"),
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit: {v[0]}"),
            on_delete=lambda v: messagebox.showinfo("Delete", f"Deleted: {v[0]}")
        )
    
    def show_accrual_documents(self):
        """Show list of accrual/deferral documents"""
        self.show_list_view(
            title="Accrual/Deferral Documents",
            columns=["Doc No", "Type", "Date", "Reversal Date", "Amount", "Status"],
            data_loader=lambda: [
                {"Doc No": "ACC-001", "Type": "Accrual", "Date": "2025-11-30", "Reversal Date": "2025-12-01", "Amount": "25000.00", "Status": "Posted"},
                {"Doc No": "DEF-001", "Type": "Deferral", "Date": "2025-11-15", "Reversal Date": "2025-12-15", "Amount": "10000.00", "Status": "Posted"},
            ],
            on_new=lambda: messagebox.showinfo("New", "Create new accrual/deferral"),
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit: {v[0]}"),
            on_delete=lambda v: messagebox.showinfo("Delete", f"Deleted: {v[0]}")
        )
    
    # === CONFIGURATION ITEMS (List Views) ===
    
    def show_fiscal_year_variants(self):
        self.show_list_view(
            title="Fiscal Year Variants",
            columns=["Variant", "Description", "Year-Dependent", "Calendar Year", "Posting Periods", "Special Periods"],
            data_loader=lambda: self.load_json_data(self.fiscal_year_file),
            on_new=self.create_fiscal_year_variant,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Variant: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.fiscal_year_file, v[0], "Variant")
        )

    def create_fiscal_year_variant(self):
        form = self.show_form("Fiscal Year Variant", lambda d: self.generic_save(self.fiscal_year_file, d, "Variant"))
        section = form.add_section("Variant Settings")
        form.add_field("Variant", ctk.CTkEntry(section), help_text="2-character ID (e.g., V3)")
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Year-Dependent", ctk.CTkCheckBox(section, text="Is Year Dependent"))
        form.add_field("Calendar Year", ctk.CTkCheckBox(section, text="Is Calendar Year"))
        form.add_field("Posting Periods", ctk.CTkEntry(section))
        form.add_field("Special Periods", ctk.CTkEntry(section))

    def show_posting_periods(self):
        self.show_list_view(
            title="Posting Periods",
            columns=["Variant", "Description", "Account Type", "From Period", "To Period", "Year"],
            data_loader=lambda: self.load_json_data(self.posting_periods_file),
            on_new=self.create_posting_period,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Variant: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.posting_periods_file, v[0], "Variant")
        )

    def create_posting_period(self):
        form = self.show_form("Posting Periods", lambda d: self.generic_save(self.posting_periods_file, d, "Variant"))
        section = form.add_section("Posting Period Variant")
        form.add_field("Variant", ctk.CTkEntry(section))
        form.add_field("Description", ctk.CTkEntry(section))
        
        section2 = form.add_section("Open/Close Periods")
        form.add_field("Account Type", ctk.CTkComboBox(section2, values=["+", "A", "D", "K", "M", "S"]))
        form.add_field("From Period", ctk.CTkEntry(section2))
        form.add_field("To Period", ctk.CTkEntry(section2))
        form.add_field("Year", ctk.CTkEntry(section2))

    def show_doc_types(self):
        self.show_list_view(
            title="Document Types",
            columns=["Type", "Description", "Number Range", "Reverse DocType", "Auth. Group"],
            data_loader=lambda: self.load_json_data(self.doc_types_file),
            on_new=self.create_doc_type,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Type: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.doc_types_file, v[0], "Type")
        )

    def create_doc_type(self):
        form = self.show_form("Document Types & Number Ranges", lambda d: self.generic_save(self.doc_types_file, d, "Type"))
        section = form.add_section("Document Type")
        form.add_field("Type", ctk.CTkEntry(section), help_text="e.g., SA, KR, DR")
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Number Range", ctk.CTkEntry(section))
        form.add_field("Reverse DocType", ctk.CTkEntry(section))
        form.add_field("Auth. Group", ctk.CTkEntry(section))

    def show_field_status(self):
        self.show_list_view(
            title="Field Status Variants",
            columns=["FStV", "Field Status Group", "Text"],
            data_loader=lambda: self.load_json_data(self.field_status_file),
            on_new=self.create_field_status,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit FStV: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.field_status_file, v[0], "FStV")
        )

    def create_field_status(self):
        form = self.show_form("Field Status Variants", lambda d: self.generic_save(self.field_status_file, d, "FStV"))
        section = form.add_section("Field Status Variant")
        form.add_field("FStV", ctk.CTkEntry(section))
        form.add_field("Field Status Group", ctk.CTkEntry(section))
        form.add_field("Text", ctk.CTkEntry(section))

    def show_reconciliation_accounts(self):
        self.show_list_view(
            title="Reconciliation Accounts",
            columns=["G/L Account", "Recon. Account Type", "Description"],
            data_loader=lambda: self.load_json_data(self.recon_accounts_file),
            on_new=self.create_reconciliation_account,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Account: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.recon_accounts_file, v[0], "G/L Account")
        )

    def create_reconciliation_account(self):
        form = self.show_form("Reconciliation Accounts", lambda d: self.generic_save(self.recon_accounts_file, d, "G/L Account"))
        section = form.add_section("Account Definition")
        form.add_field("G/L Account", ctk.CTkEntry(section))
        form.add_field("Recon. Account Type", ctk.CTkComboBox(section, values=["Assets", "Customers", "Vendors"]))
        form.add_field("Description", ctk.CTkEntry(section))

    def show_exchange_rates(self):
        self.show_list_view(
            title="Exchange Rate Types",
            columns=["Type", "Usage", "Buying Rate", "Selling Rate", "Valid From"],
            data_loader=lambda: self.load_json_data(self.exchange_rates_file),
            on_new=self.create_exchange_rate,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Type: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.exchange_rates_file, v[0], "Type")
        )

    def create_exchange_rate(self):
        form = self.show_form("Exchange Rate Types", lambda d: self.generic_save(self.exchange_rates_file, d, "Type"))
        section = form.add_section("Rate Type")
        form.add_field("Type", ctk.CTkEntry(section), help_text="e.g., M, B, G")
        form.add_field("Usage", ctk.CTkComboBox(section, values=["Translation", "Valuation", "Conversion"]))
        form.add_field("Buying Rate", ctk.CTkEntry(section))
        form.add_field("Selling Rate", ctk.CTkEntry(section))
        form.add_field("Valid From", ctk.CTkEntry(section))

    def show_fsv(self):
        self.show_list_view(
            title="Financial Statement Versions",
            columns=["FSV", "Name", "Chart of Accounts", "Maint. Language"],
            data_loader=lambda: self.load_json_data(self.fsv_file),
            on_new=self.create_fsv,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit FSV: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.fsv_file, v[0], "FSV")
        )

    def create_fsv(self):
        form = self.show_form("Financial Statement Version", lambda d: self.generic_save(self.fsv_file, d, "FSV"))
        section = form.add_section("FSV Definition")
        form.add_field("FSV", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))
        form.add_field("Chart of Accounts", ctk.CTkEntry(section))
        form.add_field("Maint. Language", ctk.CTkEntry(section))
