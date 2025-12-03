import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule
from datetime import datetime

class FIARModule(ERPBaseModule):
    """
    ERP FI-AR (Accounts Receivable) Module
    """
    
    def get_module_title(self) -> str:
        return "ERP FI - Accounts Receivable (FI-AR)"

    def __init__(self, root, company_data, user_data, app_controller):
        super().__init__(root, company_data, user_data, app_controller)
        self.customer_file = 'customer_master.json'
        self.invoice_file = 'ar_invoices.json'
        self.acct_group_file = 'ar_account_groups.json'
        self.pay_terms_file = 'ar_payment_terms.json'

    def create_content(self):
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
            ("📝 Customer Invoice (FB70)", self.show_customer_invoices, "#2e7d32"),
            ("💰 Customer Payments (F-28)", self.show_customer_payments, "#1565c0"),
            ("💳 Customer Clearing", self.show_customer_clearing, "#f57c00"),
            ("📨 Dunning Program", self.show_dunning, "#c62828"),
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
            ("👤 Customer Master Data", self.show_customers),
            ("👥 Account Groups", self.show_account_groups),
            ("🔢 Customer Number Ranges", self.open_number_ranges),
            ("📅 Payment Terms", self.show_payment_terms),
            ("💳 Credit Management", self.open_credit_mgmt),
            ("🔗 Billing -> FI Integration", self.open_billing_integration),
            ("📊 Sales Tax Calculation", self.open_sales_tax),
            ("📝 Instalment Plans", self.open_instalment_plans),
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

    def show_customer_invoices(self):
        self.show_list_view(
            title="Customer Invoices (FB70)",
            columns=["Doc No", "Customer", "Date", "Amount", "Reference", "Status"],
            data_loader=lambda: self.load_json_data(self.invoice_file),
            on_new=self.create_fb70,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Invoice: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.invoice_file, v[0], "Doc No")
        )

    def create_fb70(self):
        """Deep Form for FB70 - Customer Invoice"""
        form = self.show_form("Customer Invoice (FB70)", self.save_fb70)
        
        # Header Data
        header = form.add_section("Header Data")
        form.add_field("Customer", ctk.CTkEntry(header))
        form.add_field("Invoice Date", ctk.CTkEntry(header))
        form.add_field("Posting Date", ctk.CTkEntry(header))
        form.add_field("Amount", ctk.CTkEntry(header))
        form.add_field("Tax Amount", ctk.CTkEntry(header))
        form.add_field("Payment Terms", ctk.CTkEntry(header))
        form.add_field("Reference", ctk.CTkEntry(header))
        form.add_field("Company Code", ctk.CTkEntry(header))

        # Line Items Grid
        form.add_line_item_grid("Revenue/G/L Items", [
            "G/L Acct", "Description", "Amount", "Tax Code", "Cost Center", "Profit Center", "Sales Order"
        ])

    def save_fb70(self, data):
        """Custom save logic for FB70 with validation"""
        # 1. Extract Grid Data
        grid_keys = [k for k in data.keys() if k.startswith("grid_")]
        if not grid_keys:
            messagebox.showerror("Error", "No line items found.")
            return
            
        line_items = data.get(grid_keys[0], [])

        if not line_items:
            messagebox.showerror("Error", "Please enter at least one line item.")
            return
        
        # 2. Validate Header Amount
        try:
            invoice_amount = float(data.get("Amount", 0))
        except ValueError:
            messagebox.showerror("Error", "Invalid amount format.")
            return

        # 3. Generate Doc No
        data["Doc No"] = f"1800{len(self.load_json_data(self.invoice_file)) + 1}"
        data["Date"] = data.get("Invoice Date", datetime.now().strftime("%Y-%m-%d"))
        data["Status"] = "Posted"

        # 4. Save
        messagebox.showinfo("Success", f"Customer Invoice saved successfully!\nDocument Amount: {invoice_amount}")
        self.generic_save(self.invoice_file, data, "Doc No")

    def show_customers(self):
        self.show_list_view(
            title="Customer Master Data",
            columns=["Customer ID", "Name", "City", "Country", "Recon. Acct"],
            data_loader=lambda: self.load_json_data(self.customer_file),
            on_new=self.create_customer,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Customer: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.customer_file, v[0], "Customer ID")
        )

    def create_customer(self):
        form = self.show_form("Customer Master Data", lambda d: self.generic_save(self.customer_file, d, "Customer ID"))
        section = form.add_section("General Data")
        form.add_field("Customer ID", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))
        form.add_field("Street", ctk.CTkEntry(section))
        form.add_field("City", ctk.CTkEntry(section))
        form.add_field("Country", ctk.CTkEntry(section))
        
        section2 = form.add_section("Company Code Data")
        form.add_field("Reconciliation Acct", ctk.CTkEntry(section2))
        form.add_field("Sort Key", ctk.CTkEntry(section2))
        form.add_field("Payment Terms", ctk.CTkEntry(section2))

    def show_account_groups(self):
        self.show_list_view(
            title="Account Groups",
            columns=["Account Group", "Description", "Number Range"],
            data_loader=lambda: self.load_json_data(self.acct_group_file),
            on_new=self.create_account_group,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Group: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.acct_group_file, v[0], "Account Group")
        )

    def create_account_group(self):
        form = self.show_form("Account Groups", lambda d: self.generic_save(self.acct_group_file, d, "Account Group"))
        section = form.add_section("Group Definition")
        form.add_field("Account Group", ctk.CTkEntry(section))
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Number Range", ctk.CTkEntry(section))

    def show_payment_terms(self):
        self.show_list_view(
            title="Payment Terms",
            columns=["Key", "Limit Days", "Discount %"],
            data_loader=lambda: self.load_json_data(self.pay_terms_file),
            on_new=self.create_payment_terms,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Term: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.pay_terms_file, v[0], "Key")
        )

    def create_payment_terms(self):
        form = self.show_form("Payment Terms", lambda d: self.generic_save(self.pay_terms_file, d, "Key"))
        section = form.add_section("Term")
        form.add_field("Key", ctk.CTkEntry(section))
        form.add_field("Limit Days", ctk.CTkEntry(section))
        form.add_field("Discount %", ctk.CTkEntry(section))

    # --- Other Forms (To be converted later) ---

    def show_customer_payments(self):
        self.open_customer_payments()

    def show_customer_clearing(self):
        self.open_customer_clearing()

    def show_dunning(self):
        self.open_dunning()

    def open_number_ranges(self):
        form = self.show_form("Customer Number Ranges", self.save_generic)
        section = form.add_section("Range Definition")
        form.add_field("Range No", ctk.CTkEntry(section))
        form.add_field("From Number", ctk.CTkEntry(section))
        form.add_field("To Number", ctk.CTkEntry(section))
        form.add_field("Current Number", ctk.CTkEntry(section))

    def open_dunning(self):
        form = self.show_form("Dunning Program", self.save_generic)
        section = form.add_section("Dunning Procedure")
        form.add_field("Procedure", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))
        form.add_field("Dunning Interval (Days)", ctk.CTkEntry(section))
        form.add_field("No. of Dunning Levels", ctk.CTkEntry(section))
        form.add_field("Grace Periods", ctk.CTkEntry(section))

    def open_credit_mgmt(self):
        form = self.show_form("Credit Management Integration", self.save_generic)
        section = form.add_section("Credit Control Area")
        form.add_field("Credit Control Area", ctk.CTkEntry(section))
        form.add_field("Currency", ctk.CTkEntry(section))
        form.add_field("Update Group", ctk.CTkEntry(section))
        form.add_field("Risk Category", ctk.CTkEntry(section))

    def open_billing_integration(self):
        form = self.show_form("Billing -> FI Integration", self.save_generic)
        section = form.add_section("Account Determination")
        form.add_field("Chart of Accounts", ctk.CTkEntry(section))
        form.add_field("Sales Org", ctk.CTkEntry(section))
        form.add_field("Account Key", ctk.CTkEntry(section))
        form.add_field("G/L Account", ctk.CTkEntry(section))

    def open_customer_payments(self):
        form = self.show_form("Customer Incoming Payments (F-28)", self.save_generic)
        section = form.add_section("Header Data")
        form.add_field("Document Date", ctk.CTkEntry(section))
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Currency/Rate", ctk.CTkEntry(section))
        
        section2 = form.add_section("Bank Data")
        form.add_field("Account", ctk.CTkEntry(section2))
        form.add_field("Amount", ctk.CTkEntry(section2))
        form.add_field("Value Date", ctk.CTkEntry(section2))
        
        section3 = form.add_section("Open Item Selection")
        form.add_field("Account", ctk.CTkEntry(section3))
        form.add_field("Account Type", ctk.CTkEntry(section3))

    def open_payment_allocation(self):
        form = self.show_form("Incoming Payment Allocation", self.save_generic)
        section = form.add_section("Allocation")
        form.add_field("Payment Document", ctk.CTkEntry(section))
        form.add_field("Customer", ctk.CTkEntry(section))
        form.add_field("Invoice Reference", ctk.CTkEntry(section))
        form.add_field("Allocated Amount", ctk.CTkEntry(section))

    def open_customer_clearing(self):
        form = self.show_form("Customer Clearing (F-32)", self.save_generic)
        section = form.add_section("Selection")
        form.add_field("Account", ctk.CTkEntry(section))
        form.add_field("Clearing Date", ctk.CTkEntry(section))
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Currency", ctk.CTkEntry(section))

    def open_instalment_plans(self):
        form = self.show_form("Instalment Plans", self.save_generic)
        section = form.add_section("Plan Definition")
        form.add_field("Payment Term", ctk.CTkEntry(section))
        form.add_field("Instalment No", ctk.CTkEntry(section))
        form.add_field("Percent", ctk.CTkEntry(section))
        form.add_field("Payment Term for Instalment", ctk.CTkEntry(section))

    def open_sales_tax(self):
        form = self.show_form("Sales Tax Calculation", self.save_generic)
        section = form.add_section("Tax Code")
        form.add_field("Country", ctk.CTkEntry(section))
        form.add_field("Tax Code", ctk.CTkEntry(section))
        form.add_field("Rate", ctk.CTkEntry(section))

    def open_line_item(self):
        form = self.show_form("Customer Line Item Display (FBL5N)", self.save_generic)
        section = form.add_section("Selection")
        form.add_field("Customer Account", ctk.CTkEntry(section))
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Open Items", ctk.CTkCheckBox(section, text="Open Items"))
        form.add_field("Cleared Items", ctk.CTkCheckBox(section, text="Cleared Items"))

    def open_reconciliation(self):
        form = self.show_form("Customer Reconciliation", self.save_generic)
        section = form.add_section("Parameters")
        form.add_field("Customer", ctk.CTkEntry(section))
        form.add_field("Recon. Account", ctk.CTkEntry(section))

    def open_aging_report(self):
        form = self.show_form("Customer Aging Report", self.save_generic)
        section = form.add_section("Criteria")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Key Date", ctk.CTkEntry(section))
        form.add_field("Interval (Days)", ctk.CTkEntry(section))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
