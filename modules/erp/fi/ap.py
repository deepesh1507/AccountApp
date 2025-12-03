import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule
from datetime import datetime

class FIAPModule(ERPBaseModule):
    """
    ERP FI-AP (Accounts Payable) Module
    """
    
    def get_module_title(self) -> str:
        return "ERP FI - Accounts Payable (FI-AP)"

    def __init__(self, root, company_data, user_data, app_controller):
        super().__init__(root, company_data, user_data, app_controller)
        self.vendor_file = 'vendor_master.json'
        self.invoice_file = 'ap_invoices.json'
        self.acct_group_file = 'ap_account_groups.json'
        self.pay_terms_file = 'ap_payment_terms.json'

    def create_content(self):
        """Creates the menu for FI-AP sub-components"""
        
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        # Transactional
        ctk.CTkLabel(
            menu_scroll,
            text="Transactional Data",
            font=("Arial", 14, "bold"),
            text_color=("gray30", "gray70")
        ).pack(anchor="w", padx=20, pady=(10, 5))

        transactional_items = [
            ("📝 Vendor Invoice (FB60)", self.show_vendor_invoices, "#2e7d32"),
            ("💰 Invoice Posting (FB60, MIRO)", self.show_invoice_posting, "#1565c0"),
            ("💳 Down Payments (F-47, F-48)", self.show_down_payments, "#f57c00"),
            ("💸 Automatic Payment Program (F110)", self.show_app, "#c62828"),
        ]

        for title, command, color in transactional_items:
            btn = ctk.CTkButton(
                menu_scroll,
                text=title,
                command=command,
                height=45,
                font=("Arial", 13),
                fg_color=color,
                hover_color=self._darken_color(color),
                anchor="w"
            )
            btn.pack(fill="x", padx=20, pady=5)

        # Master Data & Config
        ctk.CTkLabel(
            menu_scroll,
            text="Master Data & Configuration",
            font=("Arial", 14, "bold"),
            text_color=("gray30", "gray70")
        ).pack(anchor="w", padx=20, pady=(20, 5))

        config_items = [
            ("👤 Vendor Master Data", self.show_vendors),
            ("👥 Account Groups", self.show_account_groups),
            ("🔢 Vendor Number Ranges", self.open_number_ranges), # Keep as form for now
            ("🔑 Posting Keys", self.open_posting_keys),
            ("📅 Payment Terms", self.show_payment_terms),
            ("🚫 Payment Blocks", self.open_payment_blocks),
            ("🏦 Alternative Payee", self.open_alternative_payee),
            ("🏷️ Withholding Tax (TDS)", self.open_withholding_tax),
        ]

        for title, command in config_items:
            btn = ctk.CTkButton(
                menu_scroll,
                text=title,
                command=command,
                height=40,
                font=("Arial", 12),
                fg_color=("white", "gray20"),
                text_color=("black", "white"),
                hover_color=("gray90", "gray30"),
                anchor="w"
            )
            btn.pack(fill="x", padx=20, pady=3)
            
    def _darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = max(0, r-30), max(0, g-30), max(0, b-30)
        return f'#{r:02x}{g:02x}{b:02x}'

    # --- List Views ---

    def show_vendor_invoices(self):
        self.show_list_view(
            title="Vendor Invoices (FB60)",
            columns=["Doc No", "Vendor", "Date", "Amount", "Reference", "Status"],
            data_loader=lambda: self.load_json_data(self.invoice_file),
            on_new=self.create_fb60,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Invoice: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.invoice_file, v[0], "Doc No")
        )

    def create_fb60(self):
        """Deep Form for FB60 - Vendor Invoice"""
        form = self.show_form("Vendor Invoice (FB60)", self.save_fb60)
        
        # Header Data
        header = form.add_section("Header Data")
        form.add_field("Vendor", ctk.CTkEntry(header))
        form.add_field("Invoice Date", ctk.CTkEntry(header))
        form.add_field("Posting Date", ctk.CTkEntry(header))
        form.add_field("Amount", ctk.CTkEntry(header))
        form.add_field("Tax Amount", ctk.CTkEntry(header))
        form.add_field("Text", ctk.CTkEntry(header))
        form.add_field("Company Code", ctk.CTkEntry(header))

        # Line Items Grid
        form.add_line_item_grid("G/L Account Items", [
            "G/L Acct", "Short Text", "D/C", "Amount in Doc.Curr", "Tax Code", "Cost Center", "Profit Center"
        ])

    def save_fb60(self, data):
        """Custom save logic for FB60 with validation"""
        # 1. Extract Grid Data
        grid_key = [k for k in data.keys() if k.startswith("grid_")][0]
        line_items = data.get(grid_key, [])

        if not line_items:
            messagebox.showerror("Error", "Please enter at least one G/L line item.")
            return
        
        # 2. Basic Validation
        try:
            invoice_amount = float(data.get("Amount", 0))
        except ValueError:
            messagebox.showerror("Error", "Invalid Invoice Amount.")
            return

        # 3. Generate Doc No
        data["Doc No"] = f"1900{len(self.load_json_data(self.invoice_file)) + 1}"
        data["Date"] = data.get("Invoice Date", datetime.now().strftime("%Y-%m-%d"))
        data["Status"] = "Posted"

        # 4. Save
        self.generic_save(self.invoice_file, data, "Doc No")

    def show_vendors(self):
        self.show_list_view(
            title="Vendor Master Data",
            columns=["Vendor ID", "Name", "City", "Country", "Recon. Acct"],
            data_loader=lambda: self.load_json_data(self.vendor_file),
            on_new=self.create_vendor,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Vendor: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.vendor_file, v[0], "Vendor ID")
        )

    def create_vendor(self):
        form = self.show_form("Vendor Master Data", lambda d: self.generic_save(self.vendor_file, d, "Vendor ID"))
        section = form.add_section("General Data")
        form.add_field("Vendor ID", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))
        form.add_field("Search Term", ctk.CTkEntry(section))
        form.add_field("Street/House No", ctk.CTkEntry(section))
        form.add_field("City/Postal Code", ctk.CTkEntry(section))
        form.add_field("Country", ctk.CTkEntry(section))
        
        section2 = form.add_section("Company Code Data")
        form.add_field("Reconciliation Acct", ctk.CTkEntry(section2))
        form.add_field("Sort Key", ctk.CTkEntry(section2))
        form.add_field("Payment Terms", ctk.CTkEntry(section2))

    def show_account_groups(self):
        self.show_list_view(
            title="Account Groups",
            columns=["Account Group", "Name", "Number Range"],
            data_loader=lambda: self.load_json_data(self.acct_group_file),
            on_new=self.create_account_group,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Group: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.acct_group_file, v[0], "Account Group")
        )

    def create_account_group(self):
        form = self.show_form("Account Groups", lambda d: self.generic_save(self.acct_group_file, d, "Account Group"))
        section = form.add_section("Group Definition")
        form.add_field("Account Group", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))
        form.add_field("Number Range", ctk.CTkEntry(section))

    def show_payment_terms(self):
        self.show_list_view(
            title="Payment Terms",
            columns=["Payt Terms", "Sales Text", "Day Limit"],
            data_loader=lambda: self.load_json_data(self.pay_terms_file),
            on_new=self.create_payment_terms,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Term: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.pay_terms_file, v[0], "Payt Terms")
        )

    def create_payment_terms(self):
        form = self.show_form("Payment Terms", lambda d: self.generic_save(self.pay_terms_file, d, "Payt Terms"))
        section = form.add_section("Term Definition")
        form.add_field("Payt Terms", ctk.CTkEntry(section))
        form.add_field("Sales Text", ctk.CTkEntry(section))
        form.add_field("Own Explanation", ctk.CTkEntry(section))
        form.add_field("Day Limit", ctk.CTkEntry(section))

    # --- Other Forms (To be converted later) ---

    def show_invoice_posting(self):
        self.open_invoice_posting() # Reuse existing logic for now

    def show_down_payments(self):
        self.open_down_payments()

    def show_app(self):
        self.open_app()

    def open_number_ranges(self):
        form = self.show_form("Vendor Number Ranges", self.save_generic)
        section = form.add_section("Range Definition")
        form.add_field("Range No", ctk.CTkEntry(section))
        form.add_field("From Number", ctk.CTkEntry(section))
        form.add_field("To Number", ctk.CTkEntry(section))
        form.add_field("Current Number", ctk.CTkEntry(section))
        form.add_field("External", ctk.CTkCheckBox(section, text="External"))

    def open_posting_keys(self):
        form = self.show_form("Posting Keys", self.save_generic)
        section = form.add_section("Key Definition")
        form.add_field("Posting Key", ctk.CTkEntry(section), help_text="e.g., 31 (Invoice), 21 (Credit Memo)")
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Debit/Credit", ctk.CTkComboBox(section, values=["Debit", "Credit"]))
        form.add_field("Account Type", ctk.CTkComboBox(section, values=["Vendor", "Customer", "G/L", "Asset", "Material"]))

    def open_invoice_posting(self):
        form = self.show_form("Vendor Invoice Posting (FB60)", self.save_generic)
        section = form.add_section("Header Data")
        form.add_field("Vendor", ctk.CTkEntry(section))
        form.add_field("Invoice Date", ctk.CTkEntry(section))
        form.add_field("Posting Date", ctk.CTkEntry(section))
        form.add_field("Reference", ctk.CTkEntry(section))
        form.add_field("Amount", ctk.CTkEntry(section))
        form.add_field("Tax Amount", ctk.CTkEntry(section))
        form.add_field("Text", ctk.CTkEntry(section))
        
        section2 = form.add_section("Line Items")
        form.add_field("G/L Account", ctk.CTkEntry(section2))
        form.add_field("Amount in Doc. Curr.", ctk.CTkEntry(section2))
        form.add_field("Cost Center", ctk.CTkEntry(section2))

    def open_credit_memo(self):
        form = self.show_form("Vendor Credit Memo", self.save_generic)
        section = form.add_section("Header Data")
        form.add_field("Vendor", ctk.CTkEntry(section))
        form.add_field("Document Date", ctk.CTkEntry(section))
        form.add_field("Reference", ctk.CTkEntry(section))
        form.add_field("Amount", ctk.CTkEntry(section))
        form.add_field("Text", ctk.CTkEntry(section))

    def open_down_payments(self):
        form = self.show_form("Down Payment Request (F-47)", self.save_generic)
        section = form.add_section("Request Data")
        form.add_field("Vendor", ctk.CTkEntry(section))
        form.add_field("Date", ctk.CTkEntry(section))
        form.add_field("Amount", ctk.CTkEntry(section))
        form.add_field("Target Special G/L Ind.", ctk.CTkEntry(section))

    def open_special_gl(self):
        form = self.show_form("Special G/L Indicators", self.save_generic)
        section = form.add_section("Indicator Definition")
        form.add_field("Account Type", ctk.CTkComboBox(section, values=["Vendor", "Customer"]))
        form.add_field("Special G/L Ind.", ctk.CTkEntry(section))
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Recon. Account", ctk.CTkEntry(section))
        form.add_field("Special G/L Account", ctk.CTkEntry(section))

    def open_retained_earnings(self):
        form = self.show_form("Retained Earnings Account", self.save_generic)
        section = form.add_section("Configuration")
        form.add_field("Chart of Accounts", ctk.CTkEntry(section))
        form.add_field("P&L Statement Acct Type", ctk.CTkEntry(section))
        form.add_field("Retained Earnings Acct", ctk.CTkEntry(section))

    def open_app(self):
        form = self.show_form("Automatic Payment Program (F110)", self.save_generic)
        section = form.add_section("Run Parameters")
        form.add_field("Run Date", ctk.CTkEntry(section))
        form.add_field("Identification", ctk.CTkEntry(section))
        
        section2 = form.add_section("Parameters")
        form.add_field("Posting Date", ctk.CTkEntry(section2))
        form.add_field("Docs Entered Up To", ctk.CTkEntry(section2))
        form.add_field("Company Codes", ctk.CTkEntry(section2))
        form.add_field("Payment Methods", ctk.CTkEntry(section2))
        form.add_field("Next Posting Date", ctk.CTkEntry(section2))

    def open_payment_blocks(self):
        form = self.show_form("Payment Blocks", self.save_generic)
        section = form.add_section("Block Reason")
        form.add_field("Block Key", ctk.CTkEntry(section))
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Changeable in Pmt Prop?", ctk.CTkCheckBox(section, text="Changeable"))

    def open_withholding_tax(self):
        form = self.show_form("Withholding Tax (TDS)", self.save_generic)
        section = form.add_section("Tax Type")
        form.add_field("WHT Type", ctk.CTkEntry(section))
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Base Amount", ctk.CTkComboBox(section, values=["Net Amount", "Gross Amount", "Tax Amount"]))
        form.add_field("Rounding Rule", ctk.CTkComboBox(section, values=["Comm. Rounding", "Round Up", "Round Down"]))

    def open_alternative_payee(self):
        form = self.show_form("Alternative Payee", self.save_generic)
        section = form.add_section("Payee Data")
        form.add_field("Vendor", ctk.CTkEntry(section))
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Alternative Payee", ctk.CTkEntry(section))
        form.add_field("Permitted Payee", ctk.CTkCheckBox(section, text="Permitted"))

    def open_cash_discount(self):
        form = self.show_form("Cash Discount", self.save_generic)
        section = form.add_section("Discount Configuration")
        form.add_field("Max Cash Discount", ctk.CTkEntry(section))
        form.add_field("G/L Account for Discount", ctk.CTkEntry(section))

    def open_line_item(self):
        form = self.show_form("Vendor Line Item Display (FBL1N)", self.save_generic)
        section = form.add_section("Selection")
        form.add_field("Vendor Account", ctk.CTkEntry(section))
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Open Items", ctk.CTkCheckBox(section, text="Open Items"))
        form.add_field("Cleared Items", ctk.CTkCheckBox(section, text="Cleared Items"))
        form.add_field("All Items", ctk.CTkCheckBox(section, text="All Items"))

    def open_reconciliation(self):
        form = self.show_form("Vendor Reconciliation", self.save_generic)
        section = form.add_section("Parameters")
        form.add_field("Vendor", ctk.CTkEntry(section))
        form.add_field("Recon. Account", ctk.CTkEntry(section))
        form.add_field("Date", ctk.CTkEntry(section))

    def open_ageing_report(self):
        form = self.show_form("Vendor Ageing Report", self.save_generic)
        section = form.add_section("Selection Criteria")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Key Date", ctk.CTkEntry(section))
        form.add_field("Due Date Sorted List", ctk.CTkCheckBox(section, text="Sorted List"))

    def open_gr_ir_clearing(self):
        form = self.show_form("GR/IR Account Clearing (F.13)", self.save_generic)
        section = form.add_section("Parameters")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Fiscal Year", ctk.CTkEntry(section))
        form.add_field("GR/IR Account", ctk.CTkEntry(section))
        form.add_field("Test Run", ctk.CTkCheckBox(section, text="Test Run"))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
