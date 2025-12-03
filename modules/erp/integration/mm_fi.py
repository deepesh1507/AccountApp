import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule

class MMFIModule(ERPBaseModule):
    """
    ERP MM-FI Integration Module
    """
    
    def get_module_title(self) -> str:
        return "ERP Integration - MM -> FI (Procurement)"

    def create_content(self):
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        items = [
            ("Automatic Account Determination (OBYC)", self.open_obyc),
            ("GR/IR Clearing Account", self.open_gr_ir),
            ("Material Valuation", self.open_valuation),
            ("Inventory Posting", self.open_inventory_posting),
            ("Invoice Verification (MIRO)", self.open_miro),
            ("Purchase Price Variance", self.open_ppv)
        ]

        row = 0
        col = 0
        for title, command in items:
            btn = ctk.CTkButton(
                menu_scroll,
                text=title,
                command=command,
                height=50,
                font=("Arial", 13),
                fg_color=("white", "gray20"),
                text_color=("black", "white"),
                hover_color=("gray90", "gray30"),
                anchor="w"
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            col += 1
            if col > 2:
                col = 0
                row += 1

        menu_scroll.grid_columnconfigure(0, weight=1)
        menu_scroll.grid_columnconfigure(1, weight=1)
        menu_scroll.grid_columnconfigure(2, weight=1)

    # --- Form Handlers ---

    def open_obyc(self):
        form = self.show_form("Automatic Account Determination (OBYC)", self.save_generic)
        section = form.add_section("Configuration")
        form.add_field("Chart of Accounts", ctk.CTkEntry(section))
        form.add_field("Transaction Key", ctk.CTkEntry(section), help_text="BSX, WRX, PRD, etc.")
        form.add_field("Valuation Class", ctk.CTkEntry(section))
        form.add_field("G/L Account", ctk.CTkEntry(section))

    def open_gr_ir(self):
        form = self.show_form("GR/IR Clearing Account", self.save_generic)
        section = form.add_section("Account")
        form.add_field("Chart of Accounts", ctk.CTkEntry(section))
        form.add_field("GR/IR Account", ctk.CTkEntry(section))
        form.add_field("Reconciliation Date", ctk.CTkEntry(section))

    def open_valuation(self):
        form = self.show_form("Material Valuation", self.save_generic)
        section = form.add_section("Valuation")
        form.add_field("Valuation Area", ctk.CTkEntry(section))
        form.add_field("Material Type", ctk.CTkEntry(section))
        form.add_field("Valuation Class", ctk.CTkEntry(section))

    def open_inventory_posting(self):
        form = self.show_form("Inventory Posting", self.save_generic)
        section = form.add_section("Posting")
        form.add_field("Movement Type", ctk.CTkEntry(section))
        form.add_field("G/L Account", ctk.CTkEntry(section))
        form.add_field("Debit/Credit", ctk.CTkComboBox(section, values=["Debit", "Credit"]))

    def open_miro(self):
        form = self.show_form("Invoice Verification (MIRO)", self.save_generic)
        section = form.add_section("Invoice")
        form.add_field("Purchase Order", ctk.CTkEntry(section))
        form.add_field("Invoice Date", ctk.CTkEntry(section))
        form.add_field("Amount", ctk.CTkEntry(section))
        form.add_field("Tax Amount", ctk.CTkEntry(section))

    def open_ppv(self):
        form = self.show_form("Purchase Price Variance", self.save_generic)
        section = form.add_section("Variance")
        form.add_field("Material", ctk.CTkEntry(section))
        form.add_field("Standard Price", ctk.CTkEntry(section))
        form.add_field("Purchase Price", ctk.CTkEntry(section))
        form.add_field("Variance Account", ctk.CTkEntry(section))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
