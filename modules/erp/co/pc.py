import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule

class COPCModule(ERPBaseModule):
    """
    ERP CO-PC (Product Costing) Module
    """
    
    def get_module_title(self) -> str:
        return "ERP CO - Product Costing (CO-PC)"

    def create_content(self):
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        items = [
            ("Material Cost Estimate", self.open_cost_estimate),
            ("Costing Variant", self.open_costing_variant),
            ("Cost Component Structure", self.open_cost_component),
            ("Price Update", self.open_price_update),
            ("Cost Object Hierarchy", self.open_cost_object),
            ("WIP Calculation", self.open_wip),
            ("Variance Calculation", self.open_variance),
            ("Settlement", self.open_settlement)
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

    def open_cost_estimate(self):
        form = self.show_form("Material Cost Estimate (CK11N)", self.save_generic)
        section = form.add_section("Selection")
        form.add_field("Material", ctk.CTkEntry(section))
        form.add_field("Plant", ctk.CTkEntry(section))
        form.add_field("Costing Variant", ctk.CTkEntry(section))
        form.add_field("Costing Version", ctk.CTkEntry(section))
        form.add_field("Costing Date From", ctk.CTkEntry(section))

    def open_costing_variant(self):
        form = self.show_form("Costing Variant (OKKN)", self.save_generic)
        section = form.add_section("Definition")
        form.add_field("Costing Variant", ctk.CTkEntry(section))
        form.add_field("Valuation Variant", ctk.CTkEntry(section))
        form.add_field("Date Control", ctk.CTkEntry(section))
        form.add_field("Qty Structure Control", ctk.CTkEntry(section))

    def open_cost_component(self):
        form = self.show_form("Cost Component Structure (OKTZ)", self.save_generic)
        section = form.add_section("Structure")
        form.add_field("Structure", ctk.CTkEntry(section))
        form.add_field("Cost Component", ctk.CTkEntry(section))
        form.add_field("Cost Element From", ctk.CTkEntry(section))
        form.add_field("Cost Element To", ctk.CTkEntry(section))

    def open_price_update(self):
        form = self.show_form("Price Update (CK24)", self.save_generic)
        section = form.add_section("Update")
        form.add_field("Period/Year", ctk.CTkEntry(section))
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Plant", ctk.CTkEntry(section))
        form.add_field("Marking Allowance", ctk.CTkCheckBox(section, text="Allow Marking"))
        form.add_field("Release", ctk.CTkCheckBox(section, text="Release"))

    def open_cost_object(self):
        form = self.show_form("Cost Object Hierarchy (KKPH)", self.save_generic)
        section = form.add_section("Hierarchy")
        form.add_field("Controlling Area", ctk.CTkEntry(section))
        form.add_field("Cost Object ID", ctk.CTkEntry(section))
        form.add_field("Material", ctk.CTkEntry(section))

    def open_wip(self):
        form = self.show_form("WIP Calculation (KKAo)", self.save_generic)
        section = form.add_section("Parameters")
        form.add_field("Order", ctk.CTkEntry(section))
        form.add_field("Period", ctk.CTkEntry(section))
        form.add_field("Fiscal Year", ctk.CTkEntry(section))
        form.add_field("Test Run", ctk.CTkCheckBox(section, text="Test Run"))

    def open_variance(self):
        form = self.show_form("Variance Calculation (KKS1)", self.save_generic)
        section = form.add_section("Parameters")
        form.add_field("Order", ctk.CTkEntry(section))
        form.add_field("Period", ctk.CTkEntry(section))
        form.add_field("Target Cost Version", ctk.CTkEntry(section))

    def open_settlement(self):
        form = self.show_form("Settlement (KO88)", self.save_generic)
        section = form.add_section("Settlement")
        form.add_field("Order", ctk.CTkEntry(section))
        form.add_field("Period", ctk.CTkEntry(section))
        form.add_field("Processing Type", ctk.CTkComboBox(section, values=["Automatic", "Full"]))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
