"""
Utility Functions for AccountApp
Validators, formatters, and helper functions
"""

import re
from datetime import datetime
from typing import Any, Optional
from tkinter import messagebox


class Validators:
    """Form validation functions"""
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> bool:
        """Check if a required field has a value"""
        if value is None or str(value).strip() == "":
            messagebox.showerror("Validation Error", f"{field_name} is required.")
            return False
        return True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            messagebox.showerror("Validation Error", "Invalid email format.")
            return False
        return True
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number (10 digits)"""
        pattern = r'^\d{10}$'
        if not re.match(pattern, phone.replace("-", "").replace(" ", "")):
            messagebox.showerror("Validation Error", "Phone number must be 10 digits.")
            return False
        return True
    
    @staticmethod
    def validate_number(value: str, field_name: str, allow_negative: bool = False) -> Optional[float]:
        """Validate and convert numeric input"""
        try:
            num = float(value)
            if not allow_negative and num < 0:
                messagebox.showerror("Validation Error", f"{field_name} cannot be negative.")
                return None
            return num
        except ValueError:
            messagebox.showerror("Validation Error", f"{field_name} must be a valid number.")
            return None
    
    @staticmethod
    def validate_date(date_str: str, field_name: str = "Date") -> Optional[datetime]:
        """Validate date format (YYYY-MM-DD)"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation Error", f"{field_name} must be in YYYY-MM-DD format.")
            return None
    
    @staticmethod
    def validate_gst_number(gst: str) -> bool:
        """Validate GST number format (15 characters)"""
        pattern = r'^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$'
        if not re.match(pattern, gst.upper()):
            messagebox.showerror("Validation Error", "Invalid GST number format.")
            return False
        return True
    
    @staticmethod
    def validate_pan_number(pan: str) -> bool:
        """Validate PAN number format"""
        pattern = r'^[A-Z]{5}\d{4}[A-Z]{1}$'
        if not re.match(pattern, pan.upper()):
            messagebox.showerror("Validation Error", "Invalid PAN number format.")
            return False
        return True


class Formatters:
    """Data formatting functions"""
    
    @staticmethod
    def format_currency(amount: float, currency: str = "INR") -> str:
        """Format number as currency"""
        return f"{currency} {amount:,.2f}"
    
    @staticmethod
    def format_date(date_obj: datetime, format_str: str = "%d-%m-%Y") -> str:
        """Format datetime object to string"""
        if isinstance(date_obj, str):
            try:
                date_obj = datetime.fromisoformat(date_obj)
            except:
                return date_obj
        return date_obj.strftime(format_str)
    
    @staticmethod
    def format_number(number: float, decimals: int = 2) -> str:
        """Format number with thousand separators"""
        return f"{number:,.{decimals}f}"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        """Format number as percentage"""
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """Parse date string to datetime object"""
        # Try multiple formats
        formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_str}")
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number with dashes"""
        clean = phone.replace("-", "").replace(" ", "")
        if len(clean) == 10:
            return f"{clean[:3]}-{clean[3:6]}-{clean[6:]}"
        return phone


class Calculator:
    """Business calculation helpers"""
    
    @staticmethod
    def calculate_tax(amount: float, tax_rate: float) -> float:
        """Calculate tax amount"""
        return round(amount * tax_rate / 100, 2)
    
    @staticmethod
    def calculate_total_with_tax(amount: float, tax_rate: float) -> float:
        """Calculate total including tax"""
        tax = Calculator.calculate_tax(amount, tax_rate)
        return round(amount + tax, 2)
    
    @staticmethod
    def calculate_gst_components(amount: float, gst_rate: float, is_intra_state: bool = True) -> dict:
        """Calculate CGST, SGST, or IGST"""
        total_tax = Calculator.calculate_tax(amount, gst_rate)
        
        if is_intra_state:
            # Intra-state: CGST + SGST (split equally)
            return {
                "CGST": round(total_tax / 2, 2),
                "SGST": round(total_tax / 2, 2),
                "IGST": 0,
                "total_tax": total_tax
            }
        else:
            # Inter-state: IGST
            return {
                "CGST": 0,
                "SGST": 0,
                "IGST": total_tax,
                "total_tax": total_tax
            }
    
    @staticmethod
    def calculate_discount(amount: float, discount_percent: float) -> float:
        """Calculate discount amount"""
        return round(amount * discount_percent / 100, 2)
    
    @staticmethod
    def calculate_aging_buckets(date_obj: datetime, today: Optional[datetime] = None) -> str:
        """Calculate aging bucket for receivables/payables"""
        if today is None:
            today = datetime.now()
        
        days = (today - date_obj).days
        
        if days <= 30:
            return "0-30 days"
        elif days <= 60:
            return "31-60 days"
        elif days <= 90:
            return "61-90 days"
        else:
            return "90+ days"


class IDGenerator:
    """Generate unique IDs for various entities"""
    
    @staticmethod
    def generate_id(prefix: str, last_id: Optional[str] = None) -> str:
        """Generate sequential ID with prefix"""
        if last_id:
            try:
                # Extract number from last ID
                num_part = int(last_id.replace(prefix, ""))
                new_num = num_part + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f"{prefix}{new_num:05d}"
    
    @staticmethod
    def generate_invoice_number(last_invoice: Optional[str] = None) -> str:
        """Generate invoice number"""
        return IDGenerator.generate_id("INV-", last_invoice)
    
    @staticmethod
    def generate_voucher_number(last_voucher: Optional[str] = None) -> str:
        """Generate voucher number"""
        return IDGenerator.generate_id("JV-", last_voucher)
    
    @staticmethod
    def generate_po_number(last_po: Optional[str] = None) -> str:
        """Generate purchase order number"""
        return IDGenerator.generate_id("PO-", last_po)
