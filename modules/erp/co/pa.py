import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule

class COPAModule(ERPBaseModule):
    """
    ERP CO-PA (Profitability Analysis) Module
    """
    
    def get_module_title(self) -> str:
        return "ERP CO - Profitability Analysis (CO-PA)"

    def create_content(self):
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        items = [
            ("Operating Concern", self.open_operating_concern),
            ("Characteristics", self.open_characteristics),
            ("Value Fields", self.open_value_fields),
            ("Flow of Actual Values", self.open_flow_actual),
            ("Planning", self.open_planning),
            ("Reports", self.open_reports)
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

    def open_operating_concern(self):
        form = self.show_form("Operating Concern (KEA0)", self.save_generic)
        section = form.add_section("Definition")
        form.add_field("Operating Concern", ctk.CTkEntry(section))
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Type", ctk.CTkComboBox(section, values=["Costing-based", "Account-based"]))

    def open_characteristics(self):
        form = self.show_form("Characteristics (KEA5)", self.save_generic)
        section = form.add_section("Field")
        form.add_field("Characteristic", ctk.CTkEntry(section))
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Data Type", ctk.CTkEntry(section))

    def open_value_fields(self):
        form = self.show_form("Value Fields (KEA6)", self.save_generic)
        section = form.add_section("Field")
        form.add_field("Value Field", ctk.CTkEntry(section))
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Aggregation", ctk.CTkComboBox(section, values=["Summation", "Average"]))

    def open_flow_actual(self):
        form = self.show_form("Flow of Actual Values", self.save_generic)
        section = form.add_section("Mapping")
        form.add_field("Source (SD/MM/FI)", ctk.CTkEntry(section))
        form.add_field("Value Field", ctk.CTkEntry(section))

    def open_planning(self):
        form = self.show_form("Planning (KEPM)", self.save_generic)
        section = form.add_section("Layout")
        form.add_field("Planning Level", ctk.CTkEntry(section))
        form.add_field("Planning Package", ctk.CTkEntry(section))
        form.add_field("Method", ctk.CTkEntry(section))

    def open_reports(self):
        form = self.show_form("Profitability Reports (KE30)", self.save_generic)
        section = form.add_section("Report")
        form.add_field("Operating Concern", ctk.CTkEntry(section))
        form.add_field("Report", ctk.CTkEntry(section))
        form.add_field("Execute", ctk.CTkCheckBox(section, text="Execute"))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
