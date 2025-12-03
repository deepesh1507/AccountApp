import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule

class HCMFIModule(ERPBaseModule):
    """
    ERP HCM-FI Integration Module
    """
    
    def get_module_title(self) -> str:
        return "ERP Integration - HCM -> FI (Payroll)"

    def create_content(self):
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        items = [
            ("Wage Type Posting", self.open_wage_type),
            ("Symbolic Accounts", self.open_symbolic),
            ("Posting Run", self.open_posting_run),
            ("Third Party Remittance", self.open_third_party)
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

    def open_wage_type(self):
        form = self.show_form("Wage Type Posting", self.save_generic)
        section = form.add_section("Mapping")
        form.add_field("Wage Type", ctk.CTkEntry(section))
        form.add_field("Symbolic Account", ctk.CTkEntry(section))
        form.add_field("Posting Type", ctk.CTkComboBox(section, values=["Balance Sheet", "Expense"]))

    def open_symbolic(self):
        form = self.show_form("Symbolic Accounts", self.save_generic)
        section = form.add_section("Definition")
        form.add_field("Symbolic Account", ctk.CTkEntry(section))
        form.add_field("G/L Account", ctk.CTkEntry(section))
        form.add_field("Account Type", ctk.CTkEntry(section))

    def open_posting_run(self):
        form = self.show_form("Posting Run", self.save_generic)
        section = form.add_section("Run")
        form.add_field("Payroll Area", ctk.CTkEntry(section))
        form.add_field("Period", ctk.CTkEntry(section))
        form.add_field("Posting Date", ctk.CTkEntry(section))
        form.add_field("Document Type", ctk.CTkEntry(section))

    def open_third_party(self):
        form = self.show_form("Third Party Remittance", self.save_generic)
        section = form.add_section("Remittance")
        form.add_field("Vendor", ctk.CTkEntry(section))
        form.add_field("Wage Type", ctk.CTkEntry(section))
        form.add_field("Amount", ctk.CTkEntry(section))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
