"""
Home Screen - Main Front Page
Connected with AccountingApp controller (main.py)
Options: Create Company, Select Company, Import, Export, Backup, Settings, Quit
"""

from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from tkinter import messagebox, filedialog

# Local imports
from .database_manager import DatabaseManager

if TYPE_CHECKING:
    from main import AccountingApp


class HomeScreen:
    def __init__(self, root: ctk.CTk, app: AccountingApp):
        self.root = root
        self.app = app
        self.root.title("Professional Accounting Software - Home")

        # Set theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.setup_ui()

    def setup_ui(self):
        # Configure grid layout for the root window
        # Column 0: Sidebar (fixed width), Column 1: Main Content (expandable)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self._create_sidebar()
        self._create_dashboard()

    def _create_sidebar(self):
        """Creates the left navigation sidebar."""
        self.sidebar_frame = ctk.CTkFrame(self.root, width=250, corner_radius=0, fg_color="#263238")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(8, weight=1) # Spacer at bottom

        # App Logo / Title in Sidebar
        logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="AccountApp\nPro", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        version_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="v1.0.0", 
            font=ctk.CTkFont(size=10),
            text_color="gray70"
        )
        version_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Navigation Buttons
        self._add_sidebar_button("🏠 Home", self.setup_ui, row=2) # Re-renders home
        self._add_sidebar_button("📝 Create Company", self.show_create_company, row=3)
        self._add_sidebar_button("🏢 Select Company", self.show_select_company, row=4)
        self._add_sidebar_button("⚙️ Settings", self.open_settings, row=5)
        
        # Separator
        separator = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color="gray50")
        separator.grid(row=6, column=0, padx=20, pady=10, sticky="ew")

        self._add_sidebar_button("❌ Exit", self.quit_application, row=7, fg_color="#c62828", hover_color="#8e0000")

    def _add_sidebar_button(self, text, command, row, fg_color="transparent", hover_color="#37474f"):
        btn = ctk.CTkButton(
            self.sidebar_frame,
            text=text,
            command=command,
            corner_radius=0,
            height=50,
            border_spacing=10,
            fg_color=fg_color,
            text_color=("gray90", "gray90"),
            hover_color=hover_color,
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn.grid(row=row, column=0, sticky="ew")

    def _create_dashboard(self):
        """Creates the main dashboard content area."""
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0, fg_color=("gray95", "gray10"))
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="white", height=80, corner_radius=0)
        header_frame.pack(fill="x", padx=0, pady=0)
        
        welcome_label = ctk.CTkLabel(
            header_frame, 
            text="Welcome to Your Dashboard", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#333"
        )
        welcome_label.pack(side="left", padx=30, pady=20)

        # Content Container
        content_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        content_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Quick Actions Grid
        grid_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        grid_frame.pack(fill="x")

        # Card 1: New Company
        self._create_action_card(
            grid_frame, 
            "Create New Company", 
            "Start a new business entity.\nSet up accounts, taxes, and more.", 
            "➕ Start Now", 
            "#2e7d32", 
            "#1b5e20",
            self.show_create_company,
            0, 0
        )

        # Card 2: Open Company
        self._create_action_card(
            grid_frame, 
            "Open Existing Company", 
            "Access your financial data.\nManage invoices, expenses, and reports.", 
            "📂 Open", 
            "#1565c0", 
            "#0d47a1",
            self.show_select_company,
            0, 1
        )

        # Data Management Section
        data_frame = ctk.CTkFrame(content_container, fg_color="white", corner_radius=10)
        data_frame.pack(fill="x", pady=30)
        
        data_title = ctk.CTkLabel(data_frame, text="Data Management", font=ctk.CTkFont(size=18, weight="bold"))
        data_title.pack(anchor="w", padx=20, pady=(20, 10))

        data_buttons_frame = ctk.CTkFrame(data_frame, fg_color="transparent")
        data_buttons_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(data_buttons_frame, text="📥 Import Data", command=self.import_data, width=150, height=40).pack(side="left", padx=(0, 10))
        ctk.CTkButton(data_buttons_frame, text="📤 Export Data", command=self.export_data, width=150, height=40).pack(side="left", padx=10)
        ctk.CTkButton(data_buttons_frame, text="💾 Backup All", command=self.backup_data, width=150, height=40, fg_color="#7b1fa2", hover_color="#4a148c").pack(side="left", padx=10)

    def _create_action_card(self, parent, title, desc, btn_text, btn_color, btn_hover, command, row, col):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, width=300, height=200)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        card.grid_propagate(False) # Fixed size
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=18, weight="bold"), text_color="#333").pack(pady=(25, 5))
        ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=12), text_color="gray50").pack(pady=5)
        
        ctk.CTkButton(
            card, 
            text=btn_text, 
            command=command, 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=btn_color, 
            hover_color=btn_hover,
            height=40,
            width=150
        ).pack(pady=20, side="bottom")

    def _perform_restore(self, file_path: str):
        if not file_path:
            return

        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            if db.restore_company(file_path):
                messagebox.showinfo("Success", "Company data imported successfully!")
            else:
                messagebox.showerror("Error", "Invalid backup file.")
        except Exception as e:
            messagebox.showerror("Error", f"Import failed:\n{str(e)}")

    # ---------- Command Methods ----------

    def import_data(self):
        """Import data from backup file"""
        file_path = filedialog.askopenfilename(
            title="Select Backup File",
            filetypes=[("Zip files", "*.zip"), ("All files", "*.*")]
        )
        self._perform_restore(file_path)

    def export_data(self):
        """Export/Backup company data"""
        try:
            db = DatabaseManager()
            companies = db.get_all_companies()

            if not companies:
                messagebox.showwarning("No Companies", "No companies found to export.")
                return

            self.show_export_dialog(companies)
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")

    def show_export_dialog(self, companies):
        """Show dialog to select company for export"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Select Company to Export")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        label = ctk.CTkLabel(dialog, text="Select Company:", font=ctk.CTkFont(size=14, weight="bold"))
        label.pack(pady=20)

        selected_company = ctk.StringVar()

        for name in companies.keys():
            radio = ctk.CTkRadioButton(
                dialog,
                text=name,
                variable=selected_company,
                value=name
            )
            radio.pack(pady=5)

        def export_selected():
            company_name = selected_company.get()
            if not company_name:
                messagebox.showwarning("Warning", "Please select a company")
                return

            folder = filedialog.askdirectory(title="Select Export Location")
            if folder:
                db = DatabaseManager()
                backup_file = db.backup_company(company_name, folder)
                if backup_file:
                    messagebox.showinfo("Success", f"Company exported to:\n{backup_file}")
                    dialog.destroy()
                # Else, the backup method already showed an error

        export_btn = ctk.CTkButton(dialog, text="Export", command=export_selected)
        export_btn.pack(pady=20)

    def backup_data(self):
        """Backup all companies"""
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            companies = db.get_all_companies()

            if not companies:
                messagebox.showwarning("No Companies", "No companies found to backup.")
                return

            folder = filedialog.askdirectory(title="Select Backup Location")
            if folder:
                backed_up_count = 0
                for name in companies.keys():
                    if db.backup_company(name, folder):
                        backed_up_count += 1
                
                if backed_up_count > 0:
                    messagebox.showinfo("Success", f"All {backed_up_count} companies backed up successfully!")
                else:
                    messagebox.showwarning("Backup", "No companies were backed up.")

        except Exception as e:
            messagebox.showerror("Error", f"Backup failed:\n{str(e)}")

    def open_settings(self):
        """Open Settings & Theme"""
        self.app.show_settings()

    def quit_application(self):
        """Quit the application"""
        if messagebox.askyesno("Quit", "Are you sure you want to exit the application?"):
            self.root.quit()
            self.root.destroy()

    def show_create_company(self):
        """Navigate to Create Company screen using the app controller."""
        self.app.show_create_company()

    def show_select_company(self):
        """Navigate to Select Company screen using the app controller."""
        self.app.show_select_company()
