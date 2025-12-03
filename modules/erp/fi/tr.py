import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule

class FITRModule(ERPBaseModule):
    """
    ERP FI-TR (Treasury) Module
    """
    
    def get_module_title(self) -> str:
        return "ERP FI - Treasury (FI-TR)"

    def create_content(self):
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(
            menu_scroll,
            text="Treasury Management",
            font=("Arial", 14, "bold"),
            text_color=("gray30", "gray70")
        ).pack(anchor="w", padx=20, pady=(10, 5))

        items = [
            ("💰 Cash Management", self.open_cash_mgmt, "#2e7d32"),
            ("📉 Liquidity Forecast", self.open_liquidity_forecast, "#1565c0"),
            ("🏦 Bank Account Management", self.open_bank_acct_mgmt, "#f57c00"),
            ("📊 Market Risk Analyzer", self.open_market_risk, "#c62828"),
            ("💸 Debt & Investment Mgmt", self.open_debt_investment, "#6a1b9a"),
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

    def open_cash_mgmt(self):
        form = self.show_form("Cash Management", self.save_generic)
        section = form.add_section("Cash Position")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Planning Date", ctk.CTkEntry(section))
        form.add_field("Currency", ctk.CTkEntry(section))
        form.add_field("Grouping", ctk.CTkEntry(section))

    def open_liquidity_forecast(self):
        form = self.show_form("Liquidity Forecast", self.save_generic)
        section = form.add_section("Forecast Parameters")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Date From", ctk.CTkEntry(section))
        form.add_field("Date To", ctk.CTkEntry(section))
        form.add_field("Display Currency", ctk.CTkEntry(section))

    def open_bank_acct_mgmt(self):
        form = self.show_form("Bank Account Management", self.save_generic)
        section = form.add_section("Bank Account")
        form.add_field("Bank Country", ctk.CTkEntry(section))
        form.add_field("Bank Key", ctk.CTkEntry(section))
        form.add_field("Account Number", ctk.CTkEntry(section))
        form.add_field("IBAN", ctk.CTkEntry(section))
        form.add_field("Account Holder", ctk.CTkEntry(section))

    def open_market_risk(self):
        form = self.show_form("Market Risk Analyzer", self.save_generic)
        section = form.add_section("Risk Analysis")
        form.add_field("Evaluation Type", ctk.CTkEntry(section))
        form.add_field("Evaluation Date", ctk.CTkEntry(section))
        form.add_field("Horizon", ctk.CTkEntry(section))
        form.add_field("Portfolio", ctk.CTkEntry(section))

    def open_debt_investment(self):
        form = self.show_form("Debt & Investment Mgmt", self.save_generic)
        section = form.add_section("Transaction")
        form.add_field("Product Type", ctk.CTkEntry(section))
        form.add_field("Transaction Type", ctk.CTkEntry(section))
        form.add_field("Partner", ctk.CTkEntry(section))
        form.add_field("Amount", ctk.CTkEntry(section))
        form.add_field("Interest Rate", ctk.CTkEntry(section))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
