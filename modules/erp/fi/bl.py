import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule
from datetime import datetime

class FIBLModule(ERPBaseModule):
    """
    ERP FI-BL (Bank Ledger) Module
    """
    
    def get_module_title(self) -> str:
        return "ERP FI - Bank Ledger (FI-BL)"
    
    def __init__(self, root, company_data, user_data, app_controller):
        super().__init__(root, company_data, user_data, app_controller)
        # JSON file paths for data storage
        self.bank_master_file = 'bank_master.json'
        self.house_banks_file = 'house_banks.json'
        self.check_lots_file = 'check_lots.json'
    
    def create_content(self):
        """Creates the menu for FI-BL sub-components"""
        
        # Scrollable menu area
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)
        
        # Header
        ctk.CTkLabel(
            menu_scroll,
            text="🏦 Bank Ledger Management",
            font=("Arial", 20, "bold"),
            text_color=("#1976d2", "white")
        ).pack(pady=20)

        # Transactional Data
        transactional_items = [
            ("💳 Incoming Payments (F-28)", self.open_incoming_payments, "#2e7d32"),
            ("💸 Outgoing Payments (F-53)", self.open_outgoing_payments, "#c62828"),
            ("✅ Check Management (FCH5)", self.open_check_management, "#1976d2"),
            ("📊 Bank Statement (FF67)", self.open_bank_statement, "#f57c00"),
            ("💵 Cash Journal (FBCJ)", self.open_cash_journal, "#7b1fa2"),
            ("📥 Lockbox Processing", self.open_lockbox, "#00796b"),
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

        # Master Data & Configuration
        config_items = [
            ("🏦 Bank Master Data (FI01)", self.show_bank_master),
            ("🏢 House Banks (FI12)", self.show_house_banks),
            ("📋 Check Lots (FCHI)", self.show_check_lots),
        ]
        
        ctk.CTkLabel(
            menu_scroll,
            text="Master Data & Configuration",
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
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = max(0, r-30), max(0, g-30), max(0, b-30)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    # === TRANSACTIONAL ITEMS ===
    
    def open_incoming_payments(self):
        """Open incoming payments form"""
        messagebox.showinfo("Incoming Payments", "Incoming Payments (F-28) form will open here")
    
    def open_outgoing_payments(self):
        """Open outgoing payments form"""
        messagebox.showinfo("Outgoing Payments", "Outgoing Payments (F-53) form will open here")
    
    def open_check_management(self):
        """Open check management"""
        messagebox.showinfo("Check Management", "Check Management (FCH5) will open here")
    
    def open_bank_statement(self):
        """Open bank statement"""
        messagebox.showinfo("Bank Statement", "Bank Statement (FF67) will open here")
    
    def open_cash_journal(self):
        """Open cash journal"""
        messagebox.showinfo("Cash Journal", "Cash Journal (FBCJ) will open here")
    
    def open_lockbox(self):
        """Open lockbox processing"""
        messagebox.showinfo("Lockbox", "Lockbox Processing will open here")
    
    # === MASTER DATA & CONFIGURATION (List Views) ===
    
    def show_bank_master(self):
        """Show list of bank master data"""
        self.show_list_view(
            title="Bank Master Data (FI01)",
            columns=["Bank Key", "Bank Name", "Bank Country", "SWIFT Code", "Bank Number"],
            data_loader=lambda: self.load_json_data(self.bank_master_file),
            on_new=self.create_bank_master,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Bank: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.bank_master_file, v[0], "Bank Key")
        )
    
    def create_bank_master(self):
        """Create new bank master record"""
        form = self.show_form("Bank Master Data (FI01)", lambda d: self.generic_save(self.bank_master_file, d, "Bank Key"))
        section = form.add_section("Bank Information")
        form.add_field("Bank Key", ctk.CTkEntry(section), help_text="Unique bank identifier")
        form.add_field("Bank Name", ctk.CTkEntry(section))
        form.add_field("Bank Country", ctk.CTkEntry(section))
        form.add_field("SWIFT Code", ctk.CTkEntry(section))
        form.add_field("Bank Number", ctk.CTkEntry(section))
    
    def show_house_banks(self):
        """Show list of house banks"""
        self.show_list_view(
            title="House Banks (FI12)",
            columns=["House Bank", "Bank Key", "Account ID", "Account Number", "Currency"],
            data_loader=lambda: self.load_json_data(self.house_banks_file),
            on_new=self.create_house_bank,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit House Bank: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.house_banks_file, v[0], "House Bank")
        )
    
    def create_house_bank(self):
        """Create new house bank"""
        form = self.show_form("House Bank (FI12)", lambda d: self.generic_save(self.house_banks_file, d, "House Bank"))
        section = form.add_section("House Bank Details")
        form.add_field("House Bank", ctk.CTkEntry(section), help_text="House bank ID")
        form.add_field("Bank Key", ctk.CTkEntry(section))
        form.add_field("Account ID", ctk.CTkEntry(section))
        form.add_field("Account Number", ctk.CTkEntry(section))
        form.add_field("Currency", ctk.CTkEntry(section))
    
    def show_check_lots(self):
        """Show list of check lots"""
        self.show_list_view(
            title="Check Lots (FCHI)",
            columns=["Lot Number", "Check Number From", "Check Number To", "Status", "House Bank"],
            data_loader=lambda: self.load_json_data(self.check_lots_file),
            on_new=self.create_check_lot,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Check Lot: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.check_lots_file, v[0], "Lot Number")
        )
    
    def create_check_lot(self):
        """Create new check lot"""
        form = self.show_form("Check Lot (FCHI)", lambda d: self.generic_save(self.check_lots_file, d, "Lot Number"))
        section = form.add_section("Check Lot Information")
        form.add_field("Lot Number", ctk.CTkEntry(section))
        form.add_field("Check Number From", ctk.CTkEntry(section))
        form.add_field("Check Number To", ctk.CTkEntry(section))
        form.add_field("Status", ctk.CTkComboBox(section, values=["Active", "Inactive", "Exhausted"]))
        form.add_field("House Bank", ctk.CTkEntry(section))
