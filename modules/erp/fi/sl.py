import customtkinter as ctk
from tkinter import messagebox
from ..base_erp_module import ERPBaseModule

class FISLModule(ERPBaseModule):
    """
    ERP FI-SL (Special Purpose Ledger) Module
    """
    
    def get_module_title(self) -> str:
        return "ERP FI - Special Purpose Ledger (FI-SL)"

    def create_content(self):
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(
            menu_scroll,
            text="Special Purpose Ledger",
            font=("Arial", 14, "bold"),
            text_color=("gray30", "gray70")
        ).pack(anchor="w", padx=20, pady=(10, 5))

        items = [
            ("📋 Define Ledgers (GCL2)", self.open_define_ledgers, "#2e7d32"),
            ("🔢 Define Field Movements", self.open_field_movements, "#1565c0"),
            ("📝 Enter Direct Posting (GB01)", self.open_direct_posting, "#f57c00"),
            ("📊 Report Writer", self.open_report_writer, "#c62828"),
            ("🔄 Rollup", self.open_rollup, "#6a1b9a"),
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

    def open_define_ledgers(self):
        form = self.show_form("Define Ledgers (GCL2)", self.save_generic)
        section = form.add_section("Ledger Definition")
        form.add_field("Ledger", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))
        form.add_field("Table Group", ctk.CTkEntry(section))
        form.add_field("Total Table", ctk.CTkEntry(section))

    def open_field_movements(self):
        form = self.show_form("Define Field Movements", self.save_generic)
        section = form.add_section("Movement")
        form.add_field("Field Movement", ctk.CTkEntry(section))
        form.add_field("Description", ctk.CTkEntry(section))
        form.add_field("Sender Table", ctk.CTkEntry(section))
        form.add_field("Receiver Table", ctk.CTkEntry(section))

    def open_direct_posting(self):
        form = self.show_form("Enter Direct Posting (GB01)", self.save_generic)
        section = form.add_section("Header")
        form.add_field("Ledger", ctk.CTkEntry(section))
        form.add_field("Document Date", ctk.CTkEntry(section))
        form.add_field("Posting Date", ctk.CTkEntry(section))
        form.add_field("Currency", ctk.CTkEntry(section))
        
        section2 = form.add_section("Line Item")
        form.add_field("Account", ctk.CTkEntry(section2))
        form.add_field("Amount", ctk.CTkEntry(section2))
        form.add_field("Cost Center", ctk.CTkEntry(section2))

    def open_report_writer(self):
        form = self.show_form("Report Writer", self.save_generic)
        section = form.add_section("Report Definition")
        form.add_field("Report Group", ctk.CTkEntry(section))
        form.add_field("Report Name", ctk.CTkEntry(section))
        form.add_field("Library", ctk.CTkEntry(section))

    def open_rollup(self):
        form = self.show_form("Rollup", self.save_generic)
        section = form.add_section("Rollup Definition")
        form.add_field("Rollup", ctk.CTkEntry(section))
        form.add_field("Name", ctk.CTkEntry(section))
        form.add_field("Sender Ledger", ctk.CTkEntry(section))
        form.add_field("Receiver Ledger", ctk.CTkEntry(section))

    def save_generic(self, data):
        print(f"Saving Data: {data}")
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()
