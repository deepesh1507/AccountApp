"""
Enhanced Settings Module
- Theme switching (Light/Dark/System)
- Font size and font type customization
- Company profile settings
- Fiscal year configuration
- Number series setup
- Backup settings
- User preferences
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog, font as tkfont
import json
from pathlib import Path
from datetime import datetime


class SettingsScreen:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.settings_file = Path(__file__).parent.parent / "data" / "app_settings.json"
        self.current_settings = self.load_settings()
        self.setup_ui()

    def load_settings(self):
        """Load application settings from file"""
        default_settings = {
            "theme": "light",
            "color_scheme": "blue",
            "font_family": "Segoe UI",
            "font_size": 12,
            "auto_backup": False,
            "backup_interval_days": 7,
            "date_format": "DD-MM-YYYY",
            "currency_symbol": "INR",
            "fiscal_year_start": "04-01",
            "invoice_prefix": "INV-",
            "voucher_prefix": "JV-",
            "show_tooltips": True,
            "window_size": "1200x700"
        }
        
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    default_settings.update(loaded)
        except Exception:
            pass
        
        return default_settings

    def save_settings(self):
        """Save application settings to file"""
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings, f, indent=2)
            messagebox.showinfo("Success", "Settings saved successfully!\nSome changes may require application restart.")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings:\n{str(e)}")
            return False

    def setup_ui(self):
        self.root.title("Application Settings")
        
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Use theme-aware colors: (light_mode_color, dark_mode_color)
        main_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main_frame.pack(fill="both", expand=True)

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="#455a64", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        ctk.CTkLabel(
            header_frame,
            text="⚙️ Application Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=30, pady=20)

        # Navigation
        nav_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        nav_frame.pack(side="right", padx=20)
        
        ctk.CTkButton(
            nav_frame,
            text="⬅️ Back to Home",
            command=self.app.show_home_screen,
            width=140,
            fg_color="#263238",
            hover_color="#37474f"
        ).pack(side="left", padx=5)

        # Scrollable content
        content_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # ========== APPEARANCE SETTINGS ==========
        self.create_section(content_frame, "🎨 Appearance & Display")
        
        appearance_card = ctk.CTkFrame(content_frame, fg_color=("white", "gray20"), corner_radius=15)
        appearance_card.pack(fill="x", pady=10)
        
        # Theme Mode
        theme_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            theme_frame,
            text="Theme Mode:",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=180,
            anchor="w"
        ).pack(side="left", padx=(0, 20))

        self.theme_var = ctk.StringVar(value=self.current_settings.get("theme", "light").capitalize())
        theme_menu = ctk.CTkSegmentedButton(
            theme_frame,
            values=["Light", "Dark", "System"],
            variable=self.theme_var,
            command=self.change_theme
        )
        theme_menu.pack(side="left")
        
        # Color Scheme
        color_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
        color_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            color_frame,
            text="Color Scheme:",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=180,
            anchor="w"
        ).pack(side="left", padx=(0, 20))
        
        self.color_var = ctk.StringVar(value=self.current_settings.get("color_scheme", "blue"))
        color_menu = ctk.CTkOptionMenu(
            color_frame,
            values=["blue", "green", "dark-blue"],
            variable=self.color_var,
            width=200
        )
        color_menu.pack(side="left")
        
        # Font Family
        font_family_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
        font_family_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            font_family_frame,
            text="Font Family:",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=180,
            anchor="w"
        ).pack(side="left", padx=(0, 20))
        
        # Get available fonts
        available_fonts = sorted([
            "Segoe UI", "Arial", "Calibri", "Verdana", "Tahoma", 
            "Georgia", "Times New Roman", "Courier New", "Consolas"
        ])
        
        self.font_family_var = ctk.StringVar(value=self.current_settings.get("font_family", "Segoe UI"))
        font_family_menu = ctk.CTkOptionMenu(
            font_family_frame,
            values=available_fonts,
            variable=self.font_family_var,
            width=200,
            command=self.preview_font
        )
        font_family_menu.pack(side="left")
        
        # Font Size
        font_size_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
        font_size_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            font_size_frame,
            text="Font Size:",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=180,
            anchor="w"
        ).pack(side="left", padx=(0, 20))
        
        self.font_size_var = ctk.IntVar(value=self.current_settings.get("font_size", 12))
        
        # Font size slider
        font_size_slider = ctk.CTkSlider(
            font_size_frame,
            from_=10,
            to=18,
            number_of_steps=8,
            variable=self.font_size_var,
            width=200,
            command=lambda val: self.update_font_size_label(int(val))
        )
        font_size_slider.pack(side="left", padx=10)
        
        self.font_size_label = ctk.CTkLabel(
            font_size_frame,
            text=f"{self.font_size_var.get()}pt",
            font=ctk.CTkFont(size=12),
            width=50
        )
        self.font_size_label.pack(side="left")
        
        # Font Preview
        preview_frame = ctk.CTkFrame(appearance_card, fg_color=("gray95", "gray25"), corner_radius=8)
        preview_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            preview_frame,
            text="Preview:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.preview_label = ctk.CTkLabel(
            preview_frame,
            text="The quick brown fox jumps over the lazy dog\n1234567890",
            font=ctk.CTkFont(family=self.font_family_var.get(), size=self.font_size_var.get()),
            justify="left"
        )
        self.preview_label.pack(anchor="w", padx=10, pady=(5, 10))

        # ========== BUSINESS SETTINGS ==========
        self.create_section(content_frame, "🏢 Business Configuration")
        
        business_card = ctk.CTkFrame(content_frame, fg_color=("white", "gray20"), corner_radius=15)
        business_card.pack(fill="x", pady=10)
        
        # Currency
        self.currency_entry = self.create_setting_row(
            business_card,
            "Default Currency:",
            self.current_settings.get("currency_symbol", "INR")
        )
        
        # Date Format
        date_frame = ctk.CTkFrame(business_card, fg_color="transparent")
        date_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            date_frame,
            text="Date Format:",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=180,
            anchor="w"
        ).pack(side="left")
        
        self.date_format_var = ctk.StringVar(value=self.current_settings.get("date_format", "DD-MM-YYYY"))
        date_menu = ctk.CTkOptionMenu(
            date_frame,
            values=["DD-MM-YYYY", "MM-DD-YYYY", "YYYY-MM-DD"],
            variable=self.date_format_var,
            width=200
        )
        date_menu.pack(side="left")
        
        # Fiscal Year
        self.fiscal_year_entry = self.create_setting_row(
            business_card,
            "Fiscal Year Start (MM-DD):",
            self.current_settings.get("fiscal_year_start", "04-01")
        )

        # ========== NUMBER SERIES ==========
        self.create_section(content_frame, "🔢 Document Numbering")
        
        number_card = ctk.CTkFrame(content_frame, fg_color=("white", "gray20"), corner_radius=15)
        number_card.pack(fill="x", pady=10)
        
        self.invoice_prefix_entry = self.create_setting_row(
            number_card,
            "Invoice Prefix:",
            self.current_settings.get("invoice_prefix", "INV-")
        )
        
        self.voucher_prefix_entry = self.create_setting_row(
            number_card,
            "Voucher Prefix:",
            self.current_settings.get("voucher_prefix", "JV-")
        )

        # ========== BACKUP SETTINGS ==========
        self.create_section(content_frame, "💾 Backup & Data Management")
        
        backup_card = ctk.CTkFrame(content_frame, fg_color=("white", "gray20"), corner_radius=15)
        backup_card.pack(fill="x", pady=10)
        
        # Auto Backup
        auto_backup_frame = ctk.CTkFrame(backup_card, fg_color="transparent")
        auto_backup_frame.pack(fill="x", padx=20, pady=10)
        
        self.auto_backup_var = ctk.BooleanVar(value=self.current_settings.get("auto_backup", False))
        ctk.CTkCheckBox(
            auto_backup_frame,
            text="Enable Automatic Backup",
            variable=self.auto_backup_var,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")
        
        # Backup Interval
        self.backup_interval_entry = self.create_setting_row(
            backup_card,
            "Backup Interval (days):",
            str(self.current_settings.get("backup_interval_days", 7))
        )
        
        # Manual Backup Button
        backup_btn_frame = ctk.CTkFrame(backup_card, fg_color="transparent")
        backup_btn_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(
            backup_btn_frame,
            text="📦 Backup All Companies Now",
            command=self.manual_backup,
            fg_color="#7b1fa2",
            hover_color="#4a148c",
            height=45,
            width=250
        ).pack()

        # ========== ACTION BUTTONS ==========
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=30)
        
        ctk.CTkButton(
            button_frame,
            text="💾 Save All Settings",
            command=self.save_all_settings,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            height=45,
            width=200,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="🔄 Reset to Defaults",
            command=self.reset_to_defaults,
            fg_color="#f57c00",
            hover_color="#e65100",
            height=45,
            width=200,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=self.app.show_home_screen,
            fg_color="#455a64",
            hover_color="#263238",
            height=45,
            width=150,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10)

    def create_section(self, parent, title):
        """Create a section header"""
        section_label = ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1565c0",
            anchor="w"
        )
        section_label.pack(fill="x", pady=(25, 10))

    def create_setting_row(self, parent, label_text, default_value):
        """Create a labeled entry row"""
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            row_frame,
            text=label_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            width=180,
            anchor="w"
        ).pack(side="left")
        
        entry = ctk.CTkEntry(row_frame, width=250)
        entry.insert(0, default_value)
        entry.pack(side="left", padx=10)
        
        return entry

    def update_font_size_label(self, size):
        """Update font size label"""
        self.font_size_label.configure(text=f"{size}pt")
        self.preview_font()

    def preview_font(self, event=None):
        """Update font preview"""
        try:
            self.preview_label.configure(
                font=ctk.CTkFont(
                    family=self.font_family_var.get(),
                    size=self.font_size_var.get()
                )
            )
        except:
            pass

    def change_theme(self, new_theme):
        """Change the application theme"""
        theme = new_theme.lower()
        ctk.set_appearance_mode(theme)
        self.current_settings["theme"] = theme
        
        # Save immediately so it persists
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.current_settings, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save theme setting:\n{str(e)}")

    def save_all_settings(self):
        """Save all settings from the form"""
        self.current_settings.update({
            "theme": self.theme_var.get().lower(),
            "color_scheme": self.color_var.get(),
            "font_family": self.font_family_var.get(),
            "font_size": self.font_size_var.get(),
            "currency_symbol": self.currency_entry.get(),
            "date_format": self.date_format_var.get(),
            "fiscal_year_start": self.fiscal_year_entry.get(),
            "invoice_prefix": self.invoice_prefix_entry.get(),
            "voucher_prefix": self.voucher_prefix_entry.get(),
            "auto_backup": self.auto_backup_var.get(),
            "backup_interval_days": int(self.backup_interval_entry.get() or 7)
        })
        
        if self.save_settings():
            # Apply theme immediately
            ctk.set_appearance_mode(self.current_settings["theme"])
            
            # Note: Color scheme requires restart to take effect
            if self.color_var.get() != "blue":
                messagebox.showinfo(
                    "Settings Saved", 
                    "Settings saved successfully!\n\n"
                    "Note: Color scheme changes require restarting the application to take full effect."
                )

    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.current_settings = {
                "theme": "light",
                "color_scheme": "blue",
                "font_family": "Segoe UI",
                "font_size": 12,
                "auto_backup": False,
                "backup_interval_days": 7,
                "date_format": "DD-MM-YYYY",
                "currency_symbol": "INR",
                "fiscal_year_start": "04-01",
                "invoice_prefix": "INV-",
                "voucher_prefix": "JV-",
                "show_tooltips": True
            }
            self.save_settings()
            # Refresh UI
            self.app.show_settings()

    def manual_backup(self):
        """Trigger manual backup of all companies"""
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            companies = db.get_all_companies()
            
            if not companies:
                messagebox.showwarning("No Companies", "No companies found to backup.")
                return
            
            folder = filedialog.askdirectory(title="Select Backup Location")
            if folder:
                backed_up = 0
                for name in companies.keys():
                    if db.backup_company(name, folder):
                        backed_up += 1
                
                if backed_up > 0:
                    messagebox.showinfo("Success", f"Backed up {backed_up} companies successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed:\n{str(e)}")
