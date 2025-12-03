'''
Create Company Module - Enhanced UI
Complete Company Registration Form with Smart Widgets
'''

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from .database_manager import DatabaseManager
from .smart_widgets import SmartEntry, SmartComboBox
import re
import requests
from typing import TYPE_CHECKING
from tkinter import filedialog
from PIL import Image, ImageTk

if TYPE_CHECKING:
    from main import AccountingApp

import json
from pathlib import Path

# Load countries and states from JSON
def load_country_data():
    try:
        data_path = Path(__file__).parent.parent / "data" / "countries_states.json"
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading country data: {e}")
        return {
            "India": ["Delhi", "Maharashtra", "Karnataka", "Tamil Nadu"],
            "United States": ["California", "New York", "Texas"],
            "United Kingdom": ["England", "Scotland"]
        }

COUNTRY_STATES = load_country_data()

# ISO 3166-1 alpha-2 codes for Zippopotam API
COUNTRY_CODES = {
    "India": "IN", "United States": "US", "United Kingdom": "GB", "Canada": "CA",
    "Australia": "AU", "United Arab Emirates": "AE", "Singapore": "SG", "Germany": "DE",
    "France": "FR", "China": "CN", "Japan": "JP", "Brazil": "BR", "Russia": "RU",
    "South Africa": "ZA"
}

class CreateCompany:
    def __init__(self, root: ctk.CTk, app_controller: "AccountingApp") -> None:
        self.root = root
        self.app = app_controller
        self.root.title("Create New Company")
        self.logo_path = None # Store selected logo path
        self.setup_ui()

    def setup_ui(self) -> None:
        try:
            # Clear existing widgets
            for widget in self.root.winfo_children():
                widget.destroy()

            # Main container
            container = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
            container.pack(fill="both", expand=True)

            # Header (Fixed at top)
            header_frame = ctk.CTkFrame(container, fg_color="#2e7d32", height=80)
            header_frame.pack(fill="x", side="top")
            header_frame.pack_propagate(False)

            title_label = ctk.CTkLabel(
                header_frame,
                text="📝 Create New Company",
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color="white"
            )
            title_label.pack(side="left", padx=30, pady=20)

            back_btn = ctk.CTkButton(
                header_frame,
                text="← Back to Home",
                font=ctk.CTkFont(size=14),
                width=150,
                height=40,
                fg_color="#1b5e20",
                hover_color="#0d3d12",
                command=self.go_back
            )
            back_btn.pack(side="right", padx=30)

            # Scrollable Content
            self.scroll_frame = ctk.CTkScrollableFrame(
                container,
                fg_color=("white", "gray20"),
                scrollbar_button_color="#2e7d32"
            )
            self.scroll_frame.pack(fill="both", expand=True, padx=40, pady=20)

            # Configure scroll_frame grid
            self.scroll_frame.grid_columnconfigure(0, weight=1, minsize=200)
            self.scroll_frame.grid_columnconfigure(1, weight=2, minsize=300)

            # Section 1: Basic Company Information
            row = 0
            self.create_section_header(self.scroll_frame, "📋 Basic Company Information", row)

            row += 1
            # Logo Upload
            logo_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            logo_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
            
            self.logo_preview = ctk.CTkLabel(logo_frame, text="No Logo Selected", width=100, height=100, fg_color="gray80", corner_radius=10)
            self.logo_preview.pack(side="left", padx=(0, 20))
            
            btn_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
            btn_frame.pack(side="left")
            
            ctk.CTkButton(btn_frame, text="📷 Upload Logo", command=self.select_logo, width=150).pack(pady=5)
            ctk.CTkLabel(btn_frame, text="Supported: PNG, JPG (Max 2MB)", font=ctk.CTkFont(size=11), text_color="gray60").pack()

            row += 1
            self.company_name = SmartEntry(self.scroll_frame, required=True, help_text="Unique company identifier", width=300)
            self.create_field_row(self.scroll_frame, "Company Name *", self.company_name, row)

            row += 1
            self.company_alias = SmartEntry(self.scroll_frame, help_text="Display name for the company", width=300)
            self.create_field_row(self.scroll_frame, "Company Alias", self.company_alias, row)

            row += 1
            self.company_type = SmartComboBox(self.scroll_frame, values=["Private Limited", "Public Limited", "Partnership", "Sole Proprietorship", "LLP"], width=300, allow_custom=False)
            self.company_type.set("Private Limited")
            self.create_field_row(self.scroll_frame, "Company Type *", self.company_type, row)

            row += 1
            self.industry = SmartEntry(self.scroll_frame, width=300, placeholder_text="e.g., Manufacturing, IT Services")
            self.create_field_row(self.scroll_frame, "Industry/Sector", self.industry, row)

            row += 1
            self.business_nature = SmartEntry(self.scroll_frame, width=300, placeholder_text="Brief description")
            self.create_field_row(self.scroll_frame, "Nature of Business", self.business_nature, row)
        except Exception as e:
            print(f"Error in setup_ui: {e}")
            messagebox.showerror("UI Error", f"Error setting up UI: {str(e)}")
            import traceback
            traceback.print_exc()

        # Section 2: Contact Information
        row += 1
        self.create_section_header(self.scroll_frame, "📞 Contact Information", row)

        row += 1
        self.email = SmartEntry(self.scroll_frame, required=True, validation_func=self.validate_email, help_text="Primary email address", width=300)
        self.create_field_row(self.scroll_frame, "Email Address *", self.email, row)

        row += 1
        self.phone = SmartEntry(self.scroll_frame, required=True, validation_func=self.validate_phone, help_text="Primary contact number", width=300)
        self.create_field_row(self.scroll_frame, "Phone Number *", self.phone, row)

        row += 1
        self.mobile = SmartEntry(self.scroll_frame, width=300, placeholder_text="Mobile number")
        self.create_field_row(self.scroll_frame, "Mobile Number", self.mobile, row)

        row += 1
        self.website = SmartEntry(self.scroll_frame, width=300, placeholder_text="https://example.com")
        self.create_field_row(self.scroll_frame, "Website", self.website, row)

        # Section 3: Address Information
        row += 1
        self.create_section_header(self.scroll_frame, "🏢 Address Information", row)

        row += 1
        self.address_line1 = SmartEntry(self.scroll_frame, required=True, width=300)
        self.create_field_row(self.scroll_frame, "Address Line 1 *", self.address_line1, row)

        row += 1
        self.address_line2 = SmartEntry(self.scroll_frame, width=300)
        self.create_field_row(self.scroll_frame, "Address Line 2", self.address_line2, row)

        row += 1
        self.city = SmartEntry(self.scroll_frame, required=True, width=300)
        self.create_field_row(self.scroll_frame, "City *", self.city, row)

        row += 1
        # State dropdown, populated based on selected country
        self.state = SmartComboBox(self.scroll_frame, values=COUNTRY_STATES.get("India", []), width=300, allow_custom=False)
        self.create_field_row(self.scroll_frame, "State *", self.state, row)

        row += 1
        self.pincode = SmartEntry(self.scroll_frame, required=True, width=300)
        self.create_field_row(self.scroll_frame, "Pincode/ZIP *", self.pincode, row)
        self.pincode.bind("<FocusOut>", lambda e: self.handle_pincode_focus_out())

        row += 1
        self.country = SmartComboBox(self.scroll_frame, values=list(COUNTRY_STATES.keys()), width=300, allow_custom=False)
        self.country.set("India")
        self.create_field_row(self.scroll_frame, "Country *", self.country, row)
        self.country.bind("<<ComboboxSelected>>", lambda e: self.update_state_options())

        # Section 4: Tax & Registration Details
        row += 1
        self.create_section_header(self.scroll_frame, "📄 Tax & Registration Details", row)

        row += 1
        self.pan = SmartEntry(self.scroll_frame, width=300, validation_func=self.validate_pan, help_text="10-character PAN number")
        self.create_field_row(self.scroll_frame, "PAN Number", self.pan, row)

        row += 1
        self.gst = SmartEntry(self.scroll_frame, width=300, validation_func=self.validate_gst, help_text="15-character GST number")
        self.create_field_row(self.scroll_frame, "GST Number", self.gst, row)

        row += 1
        self.tan = SmartEntry(self.scroll_frame, width=300)
        self.create_field_row(self.scroll_frame, "TAN Number", self.tan, row)

        row += 1
        self.cin = SmartEntry(self.scroll_frame, width=300)
        self.create_field_row(self.scroll_frame, "CIN Number", self.cin, row)

        # Section 5: Banking Details
        row += 1
        self.create_section_header(self.scroll_frame, "🏦 Banking Details", row)

        row += 1
        self.bank_name = SmartEntry(self.scroll_frame, width=300)
        self.create_field_row(self.scroll_frame, "Bank Name", self.bank_name, row)

        row += 1
        self.account_number = SmartEntry(self.scroll_frame, width=300)
        self.create_field_row(self.scroll_frame, "Account Number", self.account_number, row)

        row += 1
        self.ifsc_code = SmartEntry(self.scroll_frame, width=300, validation_func=self.validate_ifsc, help_text="11-character IFSC code")
        self.create_field_row(self.scroll_frame, "IFSC Code", self.ifsc_code, row)

        row += 1
        self.branch = SmartEntry(self.scroll_frame, width=300)
        self.create_field_row(self.scroll_frame, "Branch Name", self.branch, row)

        # Section 6: Financial Settings
        row += 1
        self.create_section_header(self.scroll_frame, "💰 Financial Settings", row)

        row += 1
        self.fy_start = SmartComboBox(self.scroll_frame, values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"], width=300, allow_custom=False)
        self.fy_start.set("April")
        self.create_field_row(self.scroll_frame, "Financial Year Start *", self.fy_start, row)

        row += 1
        self.currency = SmartComboBox(self.scroll_frame, values=["INR - Indian Rupee", "USD - US Dollar", "EUR - Euro", "GBP - British Pound", "AED - UAE Dirham"], width=300, allow_custom=False)
        self.currency.set("INR - Indian Rupee")
        self.create_field_row(self.scroll_frame, "Base Currency *", self.currency, row)

        # Section 7: Additional Settings
        row += 1
        self.create_section_header(self.scroll_frame, "⚙️ Additional Settings", row)

        row += 1
        self.gst_enabled = ctk.CTkCheckBox(self.scroll_frame, text="Enable GST/Tax Management", font=ctk.CTkFont(size=13))
        self.gst_enabled.select()
        self.gst_enabled.grid(row=row, column=0, columnspan=2, sticky="w", pady=10, padx=10)

        row += 1
        self.inventory_enabled = ctk.CTkCheckBox(self.scroll_frame, text="Enable Inventory Management", font=ctk.CTkFont(size=13))
        self.inventory_enabled.select()
        self.inventory_enabled.grid(row=row, column=0, columnspan=2, sticky="w", pady=10, padx=10)

        row += 1
        notes_label = ctk.CTkLabel(self.scroll_frame, text="Notes/Remarks", font=ctk.CTkFont(size=13, weight="bold"))
        notes_label.grid(row=row, column=0, sticky="ne", pady=10, padx=(20, 10))
        self.notes = ctk.CTkTextbox(self.scroll_frame, width=300, height=80)
        self.notes.grid(row=row, column=1, sticky="w", pady=10, padx=10)

        # Action Buttons
        row += 1
        button_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        button_frame.grid(row=row, column=0, columnspan=2, pady=30)

        save_btn = ctk.CTkButton(button_frame, text="✓ Create Company", font=ctk.CTkFont(size=16, weight="bold"), width=200, height=50, fg_color="#2e7d32", hover_color="#1b5d20", command=self.save_company)
        save_btn.pack(side="left", padx=10)

        reset_btn = ctk.CTkButton(button_frame, text="↻ Reset Form", font=ctk.CTkFont(size=16, weight="bold"), width=150, height=50, fg_color="#f57c00", hover_color="#e65100", command=self.reset_form)
        reset_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(button_frame, text="✕ Cancel", font=ctk.CTkFont(size=16, weight="bold"), width=150, height=50, fg_color="#c62828", hover_color="#8e0000", command=self.go_back)
        cancel_btn.pack(side="left", padx=10)

    def select_logo(self):
        """Open file dialog to select logo"""
        file_path = filedialog.askopenfilename(
            title="Select Company Logo",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]
        )
        if file_path:
            self.logo_path = file_path
            self.update_logo_preview(file_path)

    def update_logo_preview(self, image_path):
        try:
            img = Image.open(image_path)
            img = img.resize((100, 100), Image.Resampling.LANCZOS)
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
            self.logo_preview.configure(image=photo, text="")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")

    # Helper methods for dynamic location
    def fetch_address_by_pin(self, pincode: str):
        """Fetch address details using Zippopotam API. Returns dict with city, state, country or None."""
        country_name = self.country.get()
        country_code = COUNTRY_CODES.get(country_name, "IN")  # Default to IN if not found
        try:
            resp = requests.get(f"https://api.zippopotam.us/{country_code}/{pincode}")
            if resp.status_code == 200:
                data = resp.json()
                place = data["places"][0]
                return {
                    "city": place.get("place name", ""),
                    "state": place.get("state", ""),
                    "country": data.get("country", "")
                }
        except Exception:
            pass
        return None

    def handle_pincode_focus_out(self):
        pincode = self.pincode.get().strip()
        if not pincode:
            return
        address = self.fetch_address_by_pin(pincode)
        if not address:
            return
        if address["city"]:
            self.city.delete(0, "end")
            self.city.insert(0, address["city"])
        if address["state"]:
            self.state.configure(values=[address["state"]])
            self.state.set(address["state"])
        if address["country"]:
            self.country.set(address["country"])
            self.update_state_options()

    def update_state_options(self):
        selected_country = self.country.get()
        states = COUNTRY_STATES.get(selected_country, [])
        self.state.configure(values=states)
        if states:
            self.state.set(states[0])
        else:
            self.state.set("")

    # Validation functions
    def validate_email(self, value):
        if not value:
            return False, "Email is required"
        if bool(re.match(r"[^@]+@[^@]+\.[^@]+", value)):
            return True, ""
        return False, "Invalid email format"

    def validate_phone(self, value):
        if not value:
            return False, "Phone number is required"
        if bool(re.match(r"^\+?[\d\s\-()]{10,}$", value)):
            return True, ""
        return False, "Invalid phone number format"

    def validate_pan(self, value):
        if not value:
            return True, ""  # Optional
        if bool(re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", value.upper())):
            return True, ""
        return False, "Invalid PAN format (e.g., ABCDE1234F)"

    def validate_gst(self, value):
        if not value:
            return True, ""  # Optional
        if len(value) == 15 and value.isalnum():
            return True, ""
        return False, "Invalid GST format (15 alphanumeric characters)"

    def validate_ifsc(self, value):
        if not value:
            return True, ""  # Optional
        if bool(re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", value.upper())):
            return True, ""
        return False, "Invalid IFSC code format"

    def validate_form(self):
        errors = []
        if not self.company_name.get().strip():
            errors.append("Company Name is required")
        if not self.email.validate():
            errors.append("Valid email is required")
        if not self.phone.validate():
            errors.append("Valid phone number is required")
        if not self.address_line1.get().strip():
            errors.append("Address Line 1 is required")
        if not self.city.get().strip():
            errors.append("City is required")
        if not self.state.get().strip():
            errors.append("State is required")
        if not self.pincode.get().strip():
            errors.append("Pincode is required")
        if not self.country.get().strip():
            errors.append("Country is required")
        if self.pan.get() and not self.pan.validate():
            errors.append("Invalid PAN format (e.g., ABCDE1234F)")
        if self.gst.get() and not self.gst.validate():
            errors.append("Invalid GST format (15 characters)")
        if self.ifsc_code.get() and not self.ifsc_code.validate():
            errors.append("Invalid IFSC code format")
        return errors

    def save_company(self) -> bool:
        errors = self.validate_form()
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return False
        db = DatabaseManager()
        existing = db.get_all_companies()
        name = self.company_name.get().strip()
        if name in existing.keys():
            messagebox.showerror("Error", f"Company '{name}' already exists!")
            return False
        data = {
            'company_name': name,
            'display_name': self.company_alias.get().strip() or name,
            'company_type': self.company_type.get(),
            'industry': self.industry.get().strip(),
            'business_nature': self.business_nature.get().strip(),
            'email': self.email.get().strip(),
            'phone': self.phone.get().strip(),
            'mobile': self.mobile.get().strip(),
            'website': self.website.get().strip(),
            'address_line1': self.address_line1.get().strip(),
            'address_line2': self.address_line2.get().strip(),
            'city': self.city.get().strip(),
            'state': self.state.get().strip(),
            'pincode': self.pincode.get().strip(),
            'country': self.country.get().strip(),
            'pan': self.pan.get().strip().upper(),
            'gst': self.gst.get().strip().upper(),
            'tan': self.tan.get().strip().upper(),
            'cin': self.cin.get().strip().upper(),
            'bank_name': self.bank_name.get().strip(),
            'account_number': self.account_number.get().strip(),
            'ifsc_code': self.ifsc_code.get().strip().upper(),
            'branch': self.branch.get().strip(),
            'fy_start': self.fy_start.get(),
            'currency': self.currency.get().split(" - ")[0],
            'gst_enabled': self.gst_enabled.get(),
            'inventory_enabled': self.inventory_enabled.get(),
            'notes': self.notes.get("1.0", "end-1c"),
            'logo_source_path': self.logo_path, # Pass logo path
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'Active'
        }
        try:
            success = db.create_company_structure(data)
            if success:
                messagebox.showinfo("Success", f"Company '{name}' created successfully!")
                self.go_back()
                return True
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create company:\n{str(e)}")
            return False

    def reset_form(self):
        """Reset all form fields to their default state."""
        if not messagebox.askyesno("Reset", "Are you sure you want to reset the form? All unsaved data will be lost."):
            return
        entries = [
            self.company_name, self.company_alias, self.industry, self.business_nature,
            self.email, self.phone, self.mobile, self.website,
            self.address_line1, self.address_line2, self.city, self.state, self.pincode,
            self.pan, self.gst, self.tan, self.cin,
            self.bank_name, self.account_number, self.ifsc_code, self.branch
        ]
        for entry in entries:
            entry.delete(0, 'end')
        self.country.set("India")
        self.update_state_options()
        self.company_type.set("Private Limited")
        self.fy_start.set("April")
        self.currency.set("INR - Indian Rupee")
        self.gst_enabled.select()
        self.inventory_enabled.select()
        self.notes.delete("1.0", "end")
        messagebox.showinfo("Reset", "Form has been reset.")

    def go_back(self):
        """Return to home screen"""
        self.app.show_home_screen()

    def create_section_header(self, parent, text, row=0):
        header_frame = ctk.CTkFrame(parent, fg_color="#e8f5e9", height=40)
        header_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(20, 10), padx=5)
        header_frame.grid_columnconfigure(0, weight=1)
        header_label = ctk.CTkLabel(header_frame, text=text, font=ctk.CTkFont(size=16, weight="bold"), text_color="#2e7d32")
        header_label.pack(pady=10, padx=10, anchor="w")

    def create_field_row(self, parent, label_text, widget, row):
        label = ctk.CTkLabel(parent, text=label_text, font=ctk.CTkFont(size=13, weight="bold"), anchor="e", width=180)
        label.grid(row=row, column=0, sticky="e", pady=10, padx=(20, 10))
        widget.grid(row=row, column=1, sticky="w", pady=10, padx=10)
