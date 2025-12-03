import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule

class PPCOModule(ERPBaseModule):
    """
    ERP PP-CO Integration Module
    """
    
    def get_module_title(self) -> str:
        return "ERP Integration - PP -> CO (Production)"

    def create_content(self):
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        items = [
            ("Work Center Costing", self.open_work_center),
            ("Activity Type Linking", self.open_activity_linking),
            ("Production Order Settlement", self.open_order_settlement),
            ("WIP Calculation", self.open_wip),
            ("Overhead Calculation", self.open_overhead)
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

    def open_work_center(self):
        form = self.show_form("Work Center Costing", self.save_generic)
        section = form.add_section("Work Center")
        form.add_field("Plant", ctk.CTkEntry(section))
        form.add_field("Work Center", ctk.CTkEntry(section))
        form.add_field("Cost Center", ctk.CTkEntry(section))
        form.add_field("Activity Type", ctk.CTkEntry(section))

    def open_activity_linking(self):
        form = self.show_form("Activity Type Linking", self.save_generic)
        section = form.add_section("Linking")
        form.add_field("Cost Center", ctk.CTkEntry(section))
        form.add_field("Activity Type", ctk.CTkEntry(section))
        form.add_field("Rate", ctk.CTkEntry(section))

    def open_order_settlement(self):
        form = self.show_form("Production Order Settlement", self.save_generic)
        section = form.add_section("Settlement")
        form.add_field("Order", ctk.CTkEntry(section))
        form.add_field("Settlement Profile", ctk.CTkEntry(section))
        form.add_field("Receiver (Material/G/L)", ctk.CTkEntry(section))

    def open_wip(self):
        form = self.show_form("WIP Calculation", self.save_generic)
        section = form.add_section("WIP")
        form.add_field("Order", ctk.CTkEntry(section))
        form.add_field("Period", ctk.CTkEntry(section))
        form.add_field("Result Analysis Key", ctk.CTkEntry(section))

    def open_overhead(self):
        form = self.show_form("Overhead Calculation", self.save_generic)
        section = form.add_section("Overhead")
        form.add_field("Costing Sheet", ctk.CTkEntry(section))
        form.add_field("Overhead Rate", ctk.CTkEntry(section))
        form.add_field("Credit Key", ctk.CTkEntry(section))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
