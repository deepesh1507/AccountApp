"""
Smart Widgets Module
Contains enhanced widgets with validation, keyboard shortcuts, and better UX.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from typing import List, Optional, Callable, Any
import re

class SmartEntry(ctk.CTkEntry):
    """
    Enhanced Entry widget with validation and formatting
    """
    def __init__(self, master, validation_func=None, required=False, help_text=None, **kwargs):
        self.validation_func = validation_func
        self.required = required
        self.help_text = help_text  # Store help text
        
        # Remove help_text from kwargs if it somehow got in there (though it shouldn't with explicit arg)
        if 'help_text' in kwargs:
            kwargs.pop('help_text')
            
        self.is_valid = True
        self.error_message = ""
        
        super().__init__(master, **kwargs)
        
        # Bind events
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<KeyRelease>", self._on_key_release)
        
        # Add help tooltip if help_text is provided
        if self.help_text:
            self._create_tooltip()
    
    def _create_tooltip(self):
        """Create a tooltip for this widget"""
        # Simple tooltip implementation - shown on hover
        pass
    
    def _on_focus_out(self, event=None):
        """Validate on focus out"""
        return self._validate()
    
    def _on_key_release(self, event=None):
        """Optional: validate on key release for instant feedback"""
        pass
    
    def _validate(self, event=None):
        """Validate the entry value"""
        value = self.get().strip()
        
        # Check if required
        if self.required and not value:
            self.configure(border_color="red")
            self.is_valid = False
            self.error_message = "This field is required"
            return False
        
        # Run custom validation if provided
        if self.validation_func and value:
            result = self.validation_func(value)
            if isinstance(result, tuple):
                is_valid, error_msg = result
            else:
                is_valid = result
                error_msg = "Invalid value"
            
            if not is_valid:
                self.configure(border_color="red")
                self.is_valid = False
                self.error_message = error_msg
                return False
        
        # Valid
        self.configure(border_color=("gray70", "gray30"))
        self.is_valid = True
        self.error_message = ""
        return True
    
    def validate(self) -> bool:
        return self._validate()


class SmartNumberEntry(ctk.CTkEntry):
    """
    Number entry widget with automatic formatting
    """
    def __init__(self, master, allow_negative: bool = True, decimal_places: int = 2, 
                 min_value: float = None, decimals: int = None, required: bool = False, **kwargs):
        self.help_text = kwargs.pop("help_text", "")
        super().__init__(master, **kwargs)
        self.allow_negative = allow_negative
        # Support both decimal_places and decimals parameters
        self.decimal_places = decimals if decimals is not None else decimal_places
        self.min_value = min_value
        self.required = required
        self.error_label = None
        self.bind("<FocusOut>", self._format_number)
        self.bind("<KeyRelease>", self._validate_number)
    
    def set_error_label(self, label):
        """Set the error label for this entry"""
        self.error_label = label
    
    def _validate_number(self, event=None):
        """Validate that input is a number"""
        value = self.get()
        if not value:
            return True
        
        try:
            num = float(value.replace(",", ""))
            if not self.allow_negative and num < 0:
                self.configure(border_color="red")
                if self.error_label:
                    self.error_label.show_error("Negative values not allowed")
                return False
            if self.min_value is not None and num < self.min_value:
                self.configure(border_color="red")
                if self.error_label:
                    self.error_label.show_error(f"Value must be at least {self.min_value}")
                return False
            self.configure(border_color=("gray70", "gray30"))
            if self.error_label:
                self.error_label.clear()
            return True
        except ValueError:
            self.configure(border_color="red")
            if self.error_label:
                self.error_label.show_error("Invalid number")
            return False
    
    def _format_number(self, event=None):
        """Format number on focus out"""
        value = self.get()
        if not value:
            return
        
        try:
            num = float(value.replace(",", ""))
            formatted = f"{num:,.{self.decimal_places}f}"
            self.delete(0, "end")
            self.insert(0, formatted)
        except ValueError:
            pass
    
    def get_value(self) -> float:
        """Get the numeric value"""
        value = self.get().replace(",", "")
        try:
            return float(value)
        except ValueError:
            return 0.0
    
    def validate(self) -> bool:
        return self._validate_number()


class SmartDateEntry(ctk.CTkFrame):
    """
    Date Entry widget with calendar popup and shortcuts
    """
    
    def __init__(self, master, date_format: str = "%Y-%m-%d", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.date_format = date_format
        self.selected_date = None
        
        # Date entry
        self.entry = SmartEntry(
            self,
            validation_func=self._validate_date,
            placeholder_text=f"Date ({date_format})"
        )
        self.entry.pack(side="left", fill="x", expand=True)
        
        # Calendar button
        self.calendar_btn = ctk.CTkButton(
            self,
            text="📅",
            width=40,
            command=self._show_calendar
        )
        self.calendar_btn.pack(side="left", padx=(5, 0))
        
        # Bind shortcuts
        self.entry.bind("<KeyPress-t>", lambda e: self._set_today())
        self.entry.bind("<KeyPress-y>", lambda e: self._set_yesterday())
        self.entry.bind("<F4>", lambda e: self._show_calendar())
        
        # Set today as default
        self._set_today()
    
    def _validate_date(self, value: str) -> tuple:
        """Validate date format"""
        try:
            datetime.strptime(value, self.date_format)
            return True, ""
        except ValueError:
            return False, f"Invalid date format. Use {self.date_format}"
    
    def _set_today(self):
        """Set date to today"""
        self.entry.delete(0, "end")
        self.entry.insert(0, datetime.now().strftime(self.date_format))
        self.selected_date = datetime.now()
    
    def _set_yesterday(self):
        """Set date to yesterday"""
        yesterday = datetime.now() - timedelta(days=1)
        self.entry.delete(0, "end")
        self.entry.insert(0, yesterday.strftime(self.date_format))
        self.selected_date = yesterday
    
    def _show_calendar(self):
        """Show calendar popup"""
        try:
            from tkcalendar import Calendar
            
            # Create popup
            popup = ctk.CTkToplevel(self)
            popup.title("Select Date")
            popup.geometry("300x300")
            popup.transient(self.winfo_toplevel())
            popup.grab_set()
            
            # Calendar widget
            cal = Calendar(
                popup,
                selectmode='day',
                date_pattern=self.date_format.replace("%Y", "yyyy").replace("%m", "mm").replace("%d", "dd")
            )
            cal.pack(padx=10, pady=10, fill="both", expand=True)
            
            def select_date():
                selected = cal.get_date()
                self.entry.delete(0, "end")
                self.entry.insert(0, selected)
                try:
                    self.selected_date = datetime.strptime(selected, self.date_format)
                except:
                    pass
                popup.destroy()
            
            # Select button
            ctk.CTkButton(
                popup,
                text="Select",
                command=select_date
            ).pack(pady=10)
            
        except ImportError:
            messagebox.showinfo(
                "Calendar",
                "Calendar widget not available.\n"
                "Install tkcalendar: pip install tkcalendar"
            )
    
    def get_date(self) -> str:
        """Get the date string"""
        return self.entry.get().strip()
    
    def get_value(self) -> str:
        """Get the date string (alias for compatibility)"""
        return self.get_date()
    
    def get_datetime(self) -> Optional[datetime]:
        """Get the date as datetime object"""
        try:
            return datetime.strptime(self.get_date(), self.date_format)
        except ValueError:
            return None
    
    def validate(self) -> bool:
        """Validate the date"""
        return self.entry.validate()


class SmartComboBox(ctk.CTkComboBox):
    """
    Enhanced combobox with:
    - Searchable dropdown
    - Recent items first
    - Add new inline
    - Keyboard navigation
    """
    
    def __init__(self, master, values: List[str] = None,
                 allow_custom: bool = True, recent_count: int = 5, **kwargs):
        self.all_values = values or []
        self.allow_custom = allow_custom
        self.recent_count = recent_count
        self.recent_items = []
        
        self.help_text = kwargs.pop("help_text", "")
        super().__init__(master, values=self._get_display_values(), **kwargs)
        
        # Bind search
        self.bind("<KeyRelease>", self._on_key_release)
    
    def _get_display_values(self) -> List[str]:
        """Get values with recent items first"""
        display = []
        
        # Add recent items
        for item in self.recent_items:
            if item in self.all_values:
                display.append(f"⭐ {item}")
        
        # Add separator if we have recent items
        if display:
            display.append("─" * 20)
        
        # Add all values
        display.extend(self.all_values)
        
        # Add "Add New" option if allowed
        if self.allow_custom:
            display.append("─" * 20)
            display.append("➕ Add New...")
        
        return display
    
    def _on_key_release(self, event):
        """Filter values as user types"""
        typed = self.get().lower()
        if not typed:
            self.configure(values=self._get_display_values())
            return
        
        # Filter values
        filtered = [v for v in self.all_values if typed in v.lower()]
        self.configure(values=filtered)
    
    def add_to_recent(self, value: str):
        """Add value to recent items"""
        if value in self.recent_items:
            self.recent_items.remove(value)
        
        self.recent_items.insert(0, value)
        self.recent_items = self.recent_items[:self.recent_count]
        
        # Update display
        self.configure(values=self._get_display_values())
    
    def get_value(self) -> str:
        """Get the selected value (without emoji)"""
        value = self.get()
        # Remove emoji prefixes
        value = value.replace("⭐ ", "").replace("➕ ", "")
        return value.strip()


class ValidationLabel(ctk.CTkLabel):
    """Label for displaying validation errors"""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            text="",
            text_color="red",
            font=("Arial", 10),
            **kwargs
        )
    
    def show_error(self, message: str):
        """Show error message"""
        self.configure(text=f"❌ {message}")
    
    def show_warning(self, message: str):
        """Show warning message"""
        self.configure(text=f"⚠️ {message}", text_color="orange")
    
    def show_success(self, message: str = ""):
        """Show success message"""
        if message:
            self.configure(text=f"✅ {message}", text_color="green")
        else:
            self.configure(text="")
    
    def clear(self):
        """Clear the message"""
        self.configure(text="")


# Validation functions for common use cases

def validate_email(value: str) -> tuple:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, value):
        return True, ""
    return False, "Invalid email format"


def validate_phone(value: str) -> tuple:
    """Validate phone number"""
    # Remove spaces and dashes
    clean = value.replace(" ", "").replace("-", "")
    if len(clean) >= 10 and clean.isdigit():
        return True, ""
    return False, "Invalid phone number (10+ digits required)"


def validate_gst(value: str) -> tuple:
    """Validate GST number format"""
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    if re.match(pattern, value.upper()):
        return True, ""
    return False, "Invalid GST format (e.g., 22AAAAA0000A1Z5)"


def validate_pan(value: str) -> tuple:
    """Validate PAN number format"""
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    if re.match(pattern, value.upper()):
        return True, ""
    return False, "Invalid PAN format (e.g., ABCDE1234F)"


def validate_required(value: str) -> tuple:
    """Validate required field"""
    if value.strip():
        return True, ""
    return False, "This field is required"


def validate_min_length(min_len: int):
    """Create min length validator"""
    def validator(value: str) -> tuple:
        if len(value) >= min_len:
            return True, ""
        return False, f"Minimum {min_len} characters required"
    return validator


def validate_max_length(max_len: int):
    """Create max length validator"""
    def validator(value: str) -> tuple:
        if len(value) <= max_len:
            return True, ""
        return False, f"Maximum {max_len} characters allowed"
    return validator
