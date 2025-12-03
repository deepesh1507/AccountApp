import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule

class FICLModule(ERPBaseModule):
    """
    ERP FI-CL (Closing Operations) Module
    """
    
    def get_module_title(self) -> str:
        return "ERP FI - Closing Operations (FI-CL)"

    def create_content(self):
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(
            menu_scroll,
            text="Month-End / Year-End Closing",
            font=("Arial", 14, "bold"),
            text_color=("gray30", "gray70")
        ).pack(anchor="w", padx=20, pady=(10, 5))

        items = [
            ("📅 Open/Close Posting Periods (OB52)", self.open_ob52, "#2e7d32"),
            ("🔄 Balance Carry Forward (F.16)", self.open_balance_carry_forward, "#1565c0"),
            ("💱 Foreign Currency Valuation (F.05)", self.open_foreign_currency, "#f57c00"),
            ("📊 Financial Statements (F.01)", self.open_financial_statements, "#c62828"),
            ("📑 GR/IR Clearing (F.13)", self.open_gr_ir_clearing, "#6a1b9a"),
            ("🔢 Regrouping Receivables/Payables", self.open_regrouping, "#00695c"),
        ]

        for title, command, color in items:
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

    def _darken_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = max(0, r-30), max(0, g-30), max(0, b-30)
        return f'#{r:02x}{g:02x}{b:02x}'

    # --- Form Handlers ---

    def open_ob52(self):
        form = self.show_form("Open/Close Posting Periods (OB52)", self.save_generic)
        section = form.add_section("Period Control")
        form.add_field("Variant", ctk.CTkEntry(section))
        form.add_field("Account Type", ctk.CTkComboBox(section, values=["+", "A", "D", "K", "M", "S"]))
        form.add_field("From Period 1", ctk.CTkEntry(section))
        form.add_field("Year", ctk.CTkEntry(section))
        form.add_field("To Period 1", ctk.CTkEntry(section))
        form.add_field("Year", ctk.CTkEntry(section))

    def open_balance_carry_forward(self):
        form = self.show_form("Balance Carry Forward (F.16)", self.save_generic)
        section = form.add_section("Parameters")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Fiscal Year", ctk.CTkEntry(section))
        form.add_field("Test Run", ctk.CTkCheckBox(section, text="Test Run"))

    def open_foreign_currency(self):
        form = self.show_form("Foreign Currency Valuation (F.05)", self.save_generic)
        section = form.add_section("Valuation")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Key Date", ctk.CTkEntry(section))
        form.add_field("Valuation Area", ctk.CTkEntry(section))
        form.add_field("Create Postings", ctk.CTkCheckBox(section, text="Create Postings"))

    def open_financial_statements(self):
        form = self.show_form("Financial Statements (F.01)", self.save_generic)
        section = form.add_section("Selection")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Financial Statement Version", ctk.CTkEntry(section))
        form.add_field("Reporting Year", ctk.CTkEntry(section))
        form.add_field("Reporting Period", ctk.CTkEntry(section))

    def open_gr_ir_clearing(self):
        form = self.show_form("GR/IR Account Clearing (F.13)", self.save_generic)
        section = form.add_section("Parameters")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Fiscal Year", ctk.CTkEntry(section))
        form.add_field("GR/IR Account", ctk.CTkEntry(section))
        form.add_field("Test Run", ctk.CTkCheckBox(section, text="Test Run"))

    def open_regrouping(self):
        form = self.show_form("Regrouping Receivables/Payables", self.save_generic)
        section = form.add_section("Parameters")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Key Date", ctk.CTkEntry(section))
        form.add_field("Sort Method", ctk.CTkEntry(section))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
