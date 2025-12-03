import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule

class COPCAModule(ERPBaseModule):
    """
    ERP CO-PCA (Profit Center Accounting) Module
    """
    
    def get_module_title(self) -> str:
        return "ERP CO - Profit Center Accounting (CO-PCA)"

    def create_content(self):
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        items = [
            ("Profit Center Master Data", self.open_pc_master),
            ("Standard Hierarchy", self.open_hierarchy),
            ("Dummy Profit Center", self.open_dummy_pc),
            ("Assignment Monitor", self.open_assignment),
            ("Profit Center Planning", self.open_planning),
            ("Actual Postings", self.open_actual_postings),
            ("Profit Center Reports", self.open_reports)
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

    def open_pc_master(self):
        form = self.show_form("Profit Center Master Data (KE51)", self.save_generic)
        section = form.add_section("Basic Data")
        form.add_field("Profit Center", ctk.CTkEntry(section))
        form.add_field("Valid From", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))
        form.add_field("Person Responsible", ctk.CTkEntry(section))
        form.add_field("Profit Center Group", ctk.CTkEntry(section))
        form.add_field("Segment", ctk.CTkEntry(section))

    def open_hierarchy(self):
        form = self.show_form("Standard Hierarchy (KCH1)", self.save_generic)
        section = form.add_section("Hierarchy")
        form.add_field("Controlling Area", ctk.CTkEntry(section))
        form.add_field("Hierarchy Group", ctk.CTkEntry(section))

    def open_dummy_pc(self):
        form = self.show_form("Dummy Profit Center (KE59)", self.save_generic)
        section = form.add_section("Definition")
        form.add_field("Controlling Area", ctk.CTkEntry(section))
        form.add_field("Profit Center", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))

    def open_assignment(self):
        form = self.show_form("Assignment Monitor (1KE4)", self.save_generic)
        section = form.add_section("Check")
        form.add_field("Controlling Area", ctk.CTkEntry(section))
        form.add_field("Object Type", ctk.CTkComboBox(section, values=["Cost Centers", "Material Master", "Internal Orders"]))
        form.add_field("Show Unassigned", ctk.CTkCheckBox(section, text="Show Unassigned Objects"))

    def open_planning(self):
        form = self.show_form("Profit Center Planning (7KE1)", self.save_generic)
        section = form.add_section("Parameters")
        form.add_field("Version", ctk.CTkEntry(section))
        form.add_field("Period From", ctk.CTkEntry(section))
        form.add_field("Fiscal Year", ctk.CTkEntry(section))
        form.add_field("Profit Center", ctk.CTkEntry(section))
        form.add_field("Account", ctk.CTkEntry(section))

    def open_actual_postings(self):
        form = self.show_form("Actual Postings (1KEL)", self.save_generic)
        section = form.add_section("Entry")
        form.add_field("Profit Center", ctk.CTkEntry(section))
        form.add_field("Account", ctk.CTkEntry(section))
        form.add_field("Amount", ctk.CTkEntry(section))

    def open_reports(self):
        form = self.show_form("Profit Center Reports (KE5Z)", self.save_generic)
        section = form.add_section("Selection")
        form.add_field("Profit Center", ctk.CTkEntry(section))
        form.add_field("Account", ctk.CTkEntry(section))
        form.add_field("Posting Date", ctk.CTkEntry(section))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
