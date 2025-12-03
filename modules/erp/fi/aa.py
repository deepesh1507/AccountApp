import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule
from datetime import datetime

class FIAAModule(ERPBaseModule):
    """
    ERP FI-AA (Asset Accounting) Module
    """
    
    def get_module_title(self) -> str:
        return "ERP FI - Asset Accounting (FI-AA)"

    def __init__(self, root, company_data, user_data, app_controller):
        super().__init__(root, company_data, user_data, app_controller)
        self.asset_file = 'asset_master.json'
        self.asset_class_file = 'asset_classes.json'
        self.dep_area_file = 'depreciation_areas.json'
        self.dep_key_file = 'depreciation_keys.json'

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
            ("🏗️ Asset Acquisition (F-90)", self.show_f90, "#2e7d32"),
            ("🔄 Asset Transfer (ABUMN)", self.show_transfer, "#1565c0"),
            ("🗑️ Asset Retirement (ABAON)", self.show_retirement, "#c62828"),
            ("📉 Depreciation Run (AFAB)", self.show_dep_run, "#f57c00"),
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
            ("🏢 Asset Master Creation", self.show_assets),
            ("📂 Asset Classes", self.show_asset_classes),
            ("🔢 Number Ranges", self.open_number_ranges),
            ("📊 Depreciation Areas", self.show_dep_areas),
            ("🔑 Depreciation Keys", self.show_dep_keys),
            ("💰 Capitalization", self.open_capitalization),
            ("♻️ Asset Scrapping", self.open_scrapping),
            ("🏷️ Asset Sale", self.open_sale),
            ("📑 Asset History Sheet", self.open_history_sheet),
            ("🔍 Asset Explorer (AW01N)", self.open_asset_explorer)
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

    def show_assets(self):
        self.show_list_view(
            title="Asset Master Data (AS01)",
            columns=["Asset No", "Description", "Class", "Cap. Date", "Cost Center"],
            data_loader=lambda: self.load_json_data(self.asset_file),
            on_new=self.create_asset,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Asset: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.asset_file, v[0], "Asset No")
        )

    def create_asset(self):
        form = self.show_form("Asset Master Creation (AS01)", lambda d: self.generic_save(self.asset_file, d, "Asset No"))
        section = form.add_section("General Data")
        form.add_field("Asset No", ctk.CTkEntry(section), help_text="Leave blank for auto-number")
        form.add_field("Asset Class", ctk.CTkEntry(section))
        form.add_field("Company Code", ctk.CTkEntry(section))
        
        section2 = form.add_section("Master Data")
        form.add_field("Description", ctk.CTkEntry(section2))
        form.add_field("Cap. Date", ctk.CTkEntry(section2))
        form.add_field("Cost Center", ctk.CTkEntry(section2))
        form.add_field("Business Area", ctk.CTkEntry(section2))

    def show_asset_classes(self):
        self.show_list_view(
            title="Asset Classes",
            columns=["Asset Class", "Short Text", "Number Range", "Acct Det."],
            data_loader=lambda: self.load_json_data(self.asset_class_file),
            on_new=self.create_asset_class,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Class: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.asset_class_file, v[0], "Asset Class")
        )

    def create_asset_class(self):
        form = self.show_form("Asset Classes", lambda d: self.generic_save(self.asset_class_file, d, "Asset Class"))
        section = form.add_section("Class Definition")
        form.add_field("Asset Class", ctk.CTkEntry(section))
        form.add_field("Short Text", ctk.CTkEntry(section))
        form.add_field("Number Range", ctk.CTkEntry(section))
        form.add_field("Acct Det.", ctk.CTkEntry(section))

    def show_dep_areas(self):
        self.show_list_view(
            title="Depreciation Areas",
            columns=["Area", "Description", "Real Area", "Posting"],
            data_loader=lambda: self.load_json_data(self.dep_area_file),
            on_new=self.create_dep_area,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Area: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.dep_area_file, v[0], "Area")
        )

    def create_dep_area(self):
        form = self.show_form("Depreciation Areas", lambda d: self.generic_save(self.dep_area_file, d, "Area"))
        section = form.add_section("Area")
        form.add_field("Area", ctk.CTkEntry(section), help_text="01 - Book Depreciation")
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Real Area", ctk.CTkCheckBox(section, text="Real Area"))
        form.add_field("Posting", ctk.CTkComboBox(section, values=["Post in Realtime", "Post Periodically", "No Posting"]))

    def show_dep_keys(self):
        self.show_list_view(
            title="Depreciation Keys",
            columns=["Dep. Key", "Description", "Type", "Phase"],
            data_loader=lambda: self.load_json_data(self.dep_key_file),
            on_new=self.create_dep_key,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Key: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.dep_key_file, v[0], "Dep. Key")
        )

    def create_dep_key(self):
        form = self.show_form("Depreciation Keys", lambda d: self.generic_save(self.dep_key_file, d, "Dep. Key"))
        section = form.add_section("Key")
        form.add_field("Dep. Key", ctk.CTkEntry(section), help_text="e.g., LINA, DG10")
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Type", ctk.CTkComboBox(section, values=["Ordinary", "Special", "Unplanned"]))
        form.add_field("Phase", ctk.CTkEntry(section))

    # --- Other Forms (To be converted later) ---

    def show_f90(self):
        self.open_f90()

    def show_transfer(self):
        self.open_transfer()

    def show_retirement(self):
        self.open_retirement()

    def show_dep_run(self):
        self.open_dep_run()

    def open_number_ranges(self):
        form = self.show_form("Asset Number Ranges", self.save_generic)
        section = form.add_section("Range")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Range No", ctk.CTkEntry(section))
        form.add_field("From", ctk.CTkEntry(section))
        form.add_field("To", ctk.CTkEntry(section))

    def open_acquisition(self):
        form = self.show_form("Asset Acquisition", self.save_generic)
        section = form.add_section("Posting Data")
        form.add_field("Asset", ctk.CTkEntry(section))
        form.add_field("Document Date", ctk.CTkEntry(section))
        form.add_field("Posting Date", ctk.CTkEntry(section))
        form.add_field("Amount Posted", ctk.CTkEntry(section))
        form.add_field("Offsetting Account", ctk.CTkEntry(section))

    def open_f90(self):
        """Deep Form for F-90 - Asset Acquisition with Vendor"""
        form = self.show_form("Asset Acquisition with Vendor (F-90)", self.save_f90)
        
        # Header Data
        header = form.add_section("Vendor Invoice Data")
        form.add_field("Vendor", ctk.CTkEntry(header))
        form.add_field("Invoice Date", ctk.CTkEntry(header))
        form.add_field("Posting Date", ctk.CTkEntry(header))
        form.add_field("Invoice Amount", ctk.CTkEntry(header))
        form.add_field("Tax Amount", ctk.CTkEntry(header))
        form.add_field("Reference", ctk.CTkEntry(header))
        form.add_field("Company Code", ctk.CTkEntry(header))

        # Asset Items Grid
        form.add_line_item_grid("Asset Items", [
            "Asset Number", "Sub-number", "Description", "Amount", "Depreciation Key", "Cost Center", "Useful Life"
        ])

    def save_f90(self, data):
        """Custom save logic for F-90 with validation"""
        # 1. Extract Grid Data
        grid_keys = [k for k in data.keys() if k.startswith("grid_")]
        if not grid_keys:
            messagebox.showerror("Error", "No asset items found.")
            return
            
        asset_items = data.get(grid_keys[0], [])

        if not asset_items:
            messagebox.showerror("Error", "Please enter at least one asset item.")
            return
        
        # 2. Validate Header Amount
        try:
            invoice_amount = float(data.get("Invoice Amount", 0))
            tax_amount = float(data.get("Tax Amount", 0))
        except ValueError:
            messagebox.showerror("Error", "Invalid amount format.")
            return

        # 3. Calculate Asset Items Total
        total_assets = 0.0
        for item in asset_items:
            asset_number = item.get("Asset Number", "").strip()
            if not asset_number:
                messagebox.showerror("Error", "Asset Number is required for all items.")
                return
                
            try:
                amount = float(item.get("Amount", 0))
                total_assets += amount
            except ValueError:
                messagebox.showerror("Error", f"Invalid amount for asset {asset_number}.")
                return

        # 4. Validate Total (Invoice Amount should equal Asset Items + Tax)
        expected_total = total_assets + tax_amount
        if abs(invoice_amount - expected_total) > 0.01:
            messagebox.showerror(
                "Error", 
                f"Amount mismatch!\nInvoice Amount: {invoice_amount}\n"
                f"Asset Items Total: {total_assets}\nTax: {tax_amount}\n"
                f"Expected Total: {expected_total}"
            )
            return

        # 5. Save
        print(f"Saving F-90 Document: {data}")
        messagebox.showinfo("Success", f"Asset Acquisition saved successfully!\nTotal Assets: {total_assets}")
        super().save_generic(data)

    def open_capitalization(self):
        form = self.show_form("Capitalization of AUC", self.save_generic)
        section = form.add_section("Settlement")
        form.add_field("Sender Asset (AUC)", ctk.CTkEntry(section))
        form.add_field("Receiver Asset", ctk.CTkEntry(section))
        form.add_field("Amount/Percentage", ctk.CTkEntry(section))

    def open_transfer(self):
        form = self.show_form("Asset Transfer (ABUMN)", self.save_generic)
        section = form.add_section("Transfer Data")
        form.add_field("Sending Asset", ctk.CTkEntry(section))
        form.add_field("Receiving Asset", ctk.CTkEntry(section))
        form.add_field("Document Date", ctk.CTkEntry(section))
        form.add_field("Transfer Variant", ctk.CTkEntry(section))

    def open_retirement(self):
        form = self.show_form("Asset Retirement (ABAON)", self.save_generic)
        section = form.add_section("Retirement Data")
        form.add_field("Asset", ctk.CTkEntry(section))
        form.add_field("Document Date", ctk.CTkEntry(section))
        form.add_field("Asset Value Date", ctk.CTkEntry(section))
        form.add_field("Transaction Type", ctk.CTkEntry(section), help_text="200 - Retirement without revenue")

    def open_scrapping(self):
        form = self.show_form("Asset Scrapping", self.save_generic)
        section = form.add_section("Scrapping")
        form.add_field("Asset", ctk.CTkEntry(section))
        form.add_field("Date", ctk.CTkEntry(section))
        form.add_field("Text", ctk.CTkEntry(section))

    def open_sale(self):
        form = self.show_form("Asset Sale", self.save_generic)
        section = form.add_section("Sale Data")
        form.add_field("Asset", ctk.CTkEntry(section))
        form.add_field("Customer", ctk.CTkEntry(section))
        form.add_field("Revenue", ctk.CTkEntry(section))
        form.add_field("Date", ctk.CTkEntry(section))

    def open_dep_run(self):
        form = self.show_form("Depreciation Run (AFAB)", self.save_generic)
        section = form.add_section("Parameters")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Fiscal Year", ctk.CTkEntry(section))
        form.add_field("Posting Period", ctk.CTkEntry(section))
        form.add_field("Reason", ctk.CTkComboBox(section, values=["Planned Posting Run", "Repeat Run", "Restart", "Unplanned Posting Run"]))
        form.add_field("Test Run", ctk.CTkCheckBox(section, text="Test Run"))

    def open_settlement(self):
        form = self.show_form("Settlement of Assets", self.save_generic)
        section = form.add_section("Settlement")
        form.add_field("Sender", ctk.CTkEntry(section))
        form.add_field("Receiver", ctk.CTkEntry(section))
        form.add_field("Distribution Rule", ctk.CTkEntry(section))

    def open_history_sheet(self):
        form = self.show_form("Asset History Sheet", self.save_generic)
        section = form.add_section("Selection")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Asset Number", ctk.CTkEntry(section))
        form.add_field("Report Date", ctk.CTkEntry(section))
        form.add_field("Sort Variant", ctk.CTkEntry(section))

    def open_asset_explorer(self):
        form = self.show_form("Asset Explorer (AW01N)", self.save_generic)
        section = form.add_section("Asset")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Asset Number", ctk.CTkEntry(section))
        form.add_field("Fiscal Year", ctk.CTkEntry(section))
        
        section2 = form.add_section("Values")
        form.add_field("Planned Value", ctk.CTkEntry(section2))
        form.add_field("Posted Value", ctk.CTkEntry(section2))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
