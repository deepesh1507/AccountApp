import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule

class COOMLModule(ERPBaseModule):
    """
    ERP CO-ML (Material Ledger) Module
    """
    
    def get_module_title(self) -> str:
        return "ERP CO - Material Ledger (CO-ML)"

    def create_content(self):
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        items = [
            ("Activate Material Ledger", self.open_activate),
            ("Material Price Analysis", self.open_price_analysis),
            ("Actual Costing Run", self.open_actual_costing),
            ("Material Price Change", self.open_price_change),
            ("Value Flow Monitor", self.open_value_flow),
            ("ML Cockpit", self.open_cockpit)
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

    def open_activate(self):
        form = self.show_form("Activate Material Ledger (CKMSTART)", self.save_generic)
        section = form.add_section("Activation")
        form.add_field("Plant", ctk.CTkEntry(section))
        form.add_field("Price Determination", ctk.CTkComboBox(section, values=["2 - Transaction-based", "3 - Single/Multi-level"]))
        form.add_field("Binding", ctk.CTkCheckBox(section, text="Price Det. Binding"))

    def open_price_analysis(self):
        form = self.show_form("Material Price Analysis (CKM3)", self.save_generic)
        section = form.add_section("Selection")
        form.add_field("Material", ctk.CTkEntry(section))
        form.add_field("Plant", ctk.CTkEntry(section))
        form.add_field("Period/Year", ctk.CTkEntry(section))
        form.add_field("Currency Type", ctk.CTkEntry(section))

    def open_actual_costing(self):
        form = self.show_form("Actual Costing Run (CKMLCP)", self.save_generic)
        section = form.add_section("Run")
        form.add_field("Costing Run Name", ctk.CTkEntry(section))
        form.add_field("Period/Year", ctk.CTkEntry(section))
        form.add_field("Plants", ctk.CTkEntry(section))
        form.add_field("Step", ctk.CTkComboBox(section, values=["Selection", "Determine Sequence", "Single-Level", "Multi-Level", "Revaluation", "Post Closing"]))

    def open_price_change(self):
        form = self.show_form("Material Price Change (MR21)", self.save_generic)
        section = form.add_section("Change")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Plant", ctk.CTkEntry(section))
        form.add_field("Posting Date", ctk.CTkEntry(section))
        form.add_field("Material", ctk.CTkEntry(section))
        form.add_field("New Price", ctk.CTkEntry(section))

    def open_value_flow(self):
        form = self.show_form("Value Flow Monitor (CKMVFM)", self.save_generic)
        section = form.add_section("Monitor")
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Plant", ctk.CTkEntry(section))
        form.add_field("Year/Period", ctk.CTkEntry(section))

    def open_cockpit(self):
        form = self.show_form("ML Cockpit (CKMCOCKPIT)", self.save_generic)
        section = form.add_section("Cockpit")
        form.add_field("Plant", ctk.CTkEntry(section))
        form.add_field("Material", ctk.CTkEntry(section))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
