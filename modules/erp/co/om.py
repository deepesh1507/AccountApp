import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule

class COOMModule(ERPBaseModule):
    """
    ERP CO-OM (Overhead Management) Module
    """
    
    def get_module_title(self) -> str:
        return "ERP CO - Overhead Management (CO-OM)"

    def __init__(self, root, company_data, user_data, app_controller):
        super().__init__(root, company_data, user_data, app_controller)
        self.cost_center_file = 'cost_centers.json'
        self.cost_element_file = 'cost_elements.json'
        self.activity_type_file = 'activity_types.json'
        self.skf_file = 'statistical_key_figures.json'

    def create_content(self):
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        # Master Data
        ctk.CTkLabel(
            menu_scroll,
            text="Master Data",
            font=("Arial", 14, "bold"),
            text_color=("gray30", "gray70")
        ).pack(anchor="w", padx=20, pady=(10, 5))

        master_items = [
            ("Cost Center Master Data", self.show_cost_centers),
            ("Cost Element Master Data", self.show_cost_elements),
            ("Activity Type Master Data", self.show_activity_types),
            ("Statistical Key Figures", self.show_skf),
        ]

        for title, command in master_items:
            btn = ctk.CTkButton(
                menu_scroll,
                text=title,
                command=command,
                height=45,
                font=("Arial", 12),
                fg_color=("white", "gray20"),
                text_color=("black", "white"),
                hover_color=("gray90", "gray30"),
                anchor="w"
            )
            btn.pack(fill="x", padx=20, pady=3)

        # Planning & Allocation
        ctk.CTkLabel(
            menu_scroll,
            text="Planning & Allocation",
            font=("Arial", 14, "bold"),
            text_color=("gray30", "gray70")
        ).pack(anchor="w", padx=20, pady=(20, 5))

        planning_items = [
            ("Cost Center Planning", self.open_cc_planning),
            ("Activity Allocation", self.open_activity_allocation),
            ("Overhead Calculation", self.open_overhead_calc),
            ("Distribution & Assessment", self.open_distribution),
            ("Cost Center Reports", self.open_cc_reports)
        ]

        for title, command in planning_items:
            btn = ctk.CTkButton(
                menu_scroll,
                text=title,
                command=command,
                height=45,
                font=("Arial", 12),
                fg_color=("white", "gray20"),
                text_color=("black", "white"),
                hover_color=("gray90", "gray30"),
                anchor="w"
            )
            btn.pack(fill="x", padx=20, pady=3)

    # --- List Views & Forms ---

    def show_cost_centers(self):
        self.show_list_view(
            title="Cost Center Master Data (KS01)",
            columns=["Cost Center", "Name", "Person Responsible", "Category", "Hierarchy Area", "Valid From", "Valid To"],
            data_loader=lambda: self.load_json_data(self.cost_center_file),
            on_new=self.create_cost_center,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Cost Center: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.cost_center_file, v[0], "Cost Center")
        )

    def create_cost_center(self):
        form = self.show_form("Cost Center Master Data (KS01)", lambda d: self.generic_save(self.cost_center_file, d, "Cost Center"))
        section = form.add_section("Basic Data")
        form.add_field("Cost Center", ctk.CTkEntry(section))
        form.add_field("Valid From", ctk.CTkEntry(section))
        form.add_field("Valid To", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))
        form.add_field("Person Responsible", ctk.CTkEntry(section))
        form.add_field("Category", ctk.CTkEntry(section))
        form.add_field("Hierarchy Area", ctk.CTkEntry(section))
        form.add_field("Company Code", ctk.CTkEntry(section))
        form.add_field("Profit Center", ctk.CTkEntry(section))

    def show_cost_elements(self):
        self.show_list_view(
            title="Cost Element Master Data (KA01)",
            columns=["Cost Element", "Name", "Category", "Valid From"],
            data_loader=lambda: self.load_json_data(self.cost_element_file),
            on_new=self.create_cost_element,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Cost Element: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.cost_element_file, v[0], "Cost Element")
        )

    def create_cost_element(self):
        form = self.show_form("Cost Element Master Data (KA01)", lambda d: self.generic_save(self.cost_element_file, d, "Cost Element"))
        section = form.add_section("Basic Data")
        form.add_field("Cost Element", ctk.CTkEntry(section))
        form.add_field("Valid From", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))
        form.add_field("Category", ctk.CTkEntry(section), help_text="1 (Primary), 42 (Assessment), 43 (Allocation)")

    def show_activity_types(self):
        self.show_list_view(
            title="Activity Type Master Data (KL01)",
            columns=["Activity Type", "Name", "Activity Unit", "Category", "Valid From"],
            data_loader=lambda: self.load_json_data(self.activity_type_file),
            on_new=self.create_activity_type,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit Activity Type: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.activity_type_file, v[0], "Activity Type")
        )

    def create_activity_type(self):
        form = self.show_form("Activity Type Master Data (KL01)", lambda d: self.generic_save(self.activity_type_file, d, "Activity Type"))
        section = form.add_section("Basic Data")
        form.add_field("Activity Type", ctk.CTkEntry(section))
        form.add_field("Valid From", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))
        form.add_field("Activity Unit", ctk.CTkEntry(section))
        form.add_field("Cost Center Categories", ctk.CTkEntry(section))
        form.add_field("Category", ctk.CTkEntry(section))

    def show_skf(self):
        self.show_list_view(
            title="Statistical Key Figures (KK01)",
            columns=["Stat. Key Figure", "Name", "Unit", "Category"],
            data_loader=lambda: self.load_json_data(self.skf_file),
            on_new=self.create_skf,
            on_edit=lambda v: messagebox.showinfo("Edit", f"Edit SKF: {v[0]}"),
            on_delete=lambda v: self.generic_delete(self.skf_file, v[0], "Stat. Key Figure")
        )

    def create_skf(self):
        form = self.show_form("Statistical Key Figures (KK01)", lambda d: self.generic_save(self.skf_file, d, "Stat. Key Figure"))
        section = form.add_section("Basic Data")
        form.add_field("Stat. Key Figure", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))
        form.add_field("Unit", ctk.CTkEntry(section))
        form.add_field("Category", ctk.CTkComboBox(section, values=["Fixed Value", "Total Value"]))

    # --- Transactional Forms (Keep as forms for now, but could be lists later) ---

    def open_cc_planning(self):
        form = self.show_form("Cost Center Planning (KP06)", self.save_generic)
        section = form.add_section("Parameters")
        form.add_field("Version", ctk.CTkEntry(section))
        form.add_field("Period From", ctk.CTkEntry(section))
        form.add_field("Period To", ctk.CTkEntry(section))
        form.add_field("Fiscal Year", ctk.CTkEntry(section))
        form.add_field("Cost Center", ctk.CTkEntry(section))
        form.add_field("Cost Element", ctk.CTkEntry(section))

    def open_activity_allocation(self):
        form = self.show_form("Direct Activity Allocation (KB21N)", self.save_generic)
        section = form.add_section("Allocation")
        form.add_field("Sender Cost Center", ctk.CTkEntry(section))
        form.add_field("Activity Type", ctk.CTkEntry(section))
        form.add_field("Receiver Cost Center", ctk.CTkEntry(section))
        form.add_field("Quantity", ctk.CTkEntry(section))

    def open_overhead_calc(self):
        form = self.show_form("Overhead Calculation (KGI2)", self.save_generic)
        section = form.add_section("Parameters")
        form.add_field("Period", ctk.CTkEntry(section))
        form.add_field("Fiscal Year", ctk.CTkEntry(section))
        form.add_field("Cost Center", ctk.CTkEntry(section))
        form.add_field("Test Run", ctk.CTkCheckBox(section, text="Test Run"))

    def open_distribution(self):
        form = self.show_form("Distribution & Assessment (KSV5/KSU5)", self.save_generic)
        section = form.add_section("Cycle")
        form.add_field("Cycle", ctk.CTkEntry(section))
        form.add_field("Start Date", ctk.CTkEntry(section))
        form.add_field("Text", ctk.CTkEntry(section))
        
        section2 = form.add_section("Execution")
        form.add_field("Period", ctk.CTkEntry(section2))
        form.add_field("Fiscal Year", ctk.CTkEntry(section2))
        form.add_field("Test Run", ctk.CTkCheckBox(section2, text="Test Run"))

    def open_cc_reports(self):
        form = self.show_form("Cost Center Reports (KSB1)", self.save_generic)
        section = form.add_section("Selection")
        form.add_field("Cost Center", ctk.CTkEntry(section))
        form.add_field("Cost Element", ctk.CTkEntry(section))
        form.add_field("Posting Date", ctk.CTkEntry(section))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
