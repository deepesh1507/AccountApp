import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule

class SDFIModule(ERPBaseModule):
    """
    ERP SD-FI Integration Module
    """
    
    def get_module_title(self) -> str:
        return "ERP Integration - SD -> FI (Sales)"

    def create_content(self):
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        items = [
            ("Revenue Account Determination (VKOA)", self.open_vkoa),
            ("Reconciliation Account Determination", self.open_recon),
            ("Tax Account Determination", self.open_tax),
            ("Deferred Revenue", self.open_deferred),
            ("Sales Deductions", self.open_deductions)
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

    def open_vkoa(self):
        form = self.show_form("Revenue Account Determination (VKOA)", self.save_generic)
        section = form.add_section("Determination")
        form.add_field("App", ctk.CTkEntry(section), help_text="V (Sales/Distribution)")
        form.add_field("Cond. Type", ctk.CTkEntry(section), help_text="KOFI")
        form.add_field("Chart of Accounts", ctk.CTkEntry(section))
        form.add_field("Sales Org", ctk.CTkEntry(section))
        form.add_field("Acct Key", ctk.CTkEntry(section), help_text="ERL")
        form.add_field("G/L Account", ctk.CTkEntry(section))

    def open_recon(self):
        form = self.show_form("Reconciliation Account Determination", self.save_generic)
        section = form.add_section("Customer")
        form.add_field("Account Group", ctk.CTkEntry(section))
        form.add_field("Reconciliation Account", ctk.CTkEntry(section))

    def open_tax(self):
        form = self.show_form("Tax Account Determination", self.save_generic)
        section = form.add_section("Tax")
        form.add_field("Tax Code", ctk.CTkEntry(section))
        form.add_field("Account Key", ctk.CTkEntry(section), help_text="MWS")
        form.add_field("G/L Account", ctk.CTkEntry(section))

    def open_deferred(self):
        form = self.show_form("Deferred Revenue", self.save_generic)
        section = form.add_section("Revenue Recognition")
        form.add_field("Item Category", ctk.CTkEntry(section))
        form.add_field("Deferred Revenue Account", ctk.CTkEntry(section))
        form.add_field("Revenue Account", ctk.CTkEntry(section))

    def open_deductions(self):
        form = self.show_form("Sales Deductions", self.save_generic)
        section = form.add_section("Deduction")
        form.add_field("Condition Type", ctk.CTkEntry(section))
        form.add_field("Account Key", ctk.CTkEntry(section), help_text="ERS")
        form.add_field("G/L Account", ctk.CTkEntry(section))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
