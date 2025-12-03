import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule

class COIOModule(ERPBaseModule):
    """
    ERP CO-IO (Internal Orders) Module
    """
    
    def get_module_title(self) -> str:
        return "ERP CO - Internal Orders (CO-IO)"

    def create_content(self):
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        items = [
            ("Internal Order Master Data", self.open_order_master),
            ("Order Types", self.open_order_types),
            ("Budgeting", self.open_budgeting),
            ("Availability Control", self.open_availability_control),
            ("Actual Postings", self.open_actual_postings),
            ("Settlement Rules", self.open_settlement_rules),
            ("Order Settlement", self.open_order_settlement),
            ("Order Reports", self.open_order_reports)
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

    def open_order_master(self):
        form = self.show_form("Internal Order Master Data (KO01)", self.save_generic)
        section = form.add_section("Header")
        form.add_field("Order Type", ctk.CTkEntry(section))
        form.add_field("Order Number", ctk.CTkEntry(section))
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Business Area", ctk.CTkEntry(section))
        form.add_field("Profit Center", ctk.CTkEntry(section))
        form.add_field("Responsible Cost Center", ctk.CTkEntry(section))

    def open_order_types(self):
        form = self.show_form("Order Types (KOT2)", self.save_generic)
        section = form.add_section("Definition")
        form.add_field("Order Type", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))
        form.add_field("Settlement Profile", ctk.CTkEntry(section))
        form.add_field("Planning Profile", ctk.CTkEntry(section))

    def open_budgeting(self):
        form = self.show_form("Budgeting (KO22)", self.save_generic)
        section = form.add_section("Budget")
        form.add_field("Order", ctk.CTkEntry(section))
        form.add_field("Fiscal Year", ctk.CTkEntry(section))
        form.add_field("Overall Budget", ctk.CTkEntry(section))
        form.add_field("Current Budget", ctk.CTkEntry(section))

    def open_availability_control(self):
        form = self.show_form("Availability Control", self.save_generic)
        section = form.add_section("Settings")
        form.add_field("Order Type", ctk.CTkEntry(section))
        form.add_field("Action on Exhaustion", ctk.CTkComboBox(section, values=["Warning", "Error", "Mail"]))
        form.add_field("Tolerance Limit %", ctk.CTkEntry(section))

    def open_actual_postings(self):
        form = self.show_form("Actual Postings (KB11N)", self.save_generic)
        section = form.add_section("Reposting")
        form.add_field("Sender Cost Center", ctk.CTkEntry(section))
        form.add_field("Receiver Order", ctk.CTkEntry(section))
        form.add_field("Cost Element", ctk.CTkEntry(section))
        form.add_field("Amount", ctk.CTkEntry(section))

    def open_settlement_rules(self):
        form = self.show_form("Settlement Rules", self.save_generic)
        section = form.add_section("Rule")
        form.add_field("Order", ctk.CTkEntry(section))
        form.add_field("Category", ctk.CTkComboBox(section, values=["CTR (Cost Center)", "G/L (G/L Account)", "FXA (Asset)"]))
        form.add_field("Receiver", ctk.CTkEntry(section))
        form.add_field("Percentage", ctk.CTkEntry(section))

    def open_order_settlement(self):
        form = self.show_form("Order Settlement (KO88)", self.save_generic)
        section = form.add_section("Parameters")
        form.add_field("Order", ctk.CTkEntry(section))
        form.add_field("Period", ctk.CTkEntry(section))
        form.add_field("Fiscal Year", ctk.CTkEntry(section))
        form.add_field("Processing Type", ctk.CTkComboBox(section, values=["Automatic", "Full Settlement"]))
        form.add_field("Test Run", ctk.CTkCheckBox(section, text="Test Run"))

    def open_order_reports(self):
        form = self.show_form("Order Reports (KOB1)", self.save_generic)
        section = form.add_section("Selection")
        form.add_field("Order", ctk.CTkEntry(section))
        form.add_field("Cost Element", ctk.CTkEntry(section))
        form.add_field("Posting Date", ctk.CTkEntry(section))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
