"""
Vendors Management Module
Professional vendor/supplier management with CRUD operations
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional
from .base_module import BaseModule
from .database_manager import DatabaseManager
from .smart_widgets import (
    SmartEntry, SmartNumberEntry, SmartComboBox, 
    ValidationLabel, validate_required, validate_email, validate_phone
)
from .enhanced_form import EnhancedForm
from .performance_optimizer import debounce_search, run_async, show_loading_overlay, hide_loading_overlay, PerformanceOptimizer

class VendorsManagement(BaseModule):
    """Professional Vendors Management Module"""
    
    def __init__(self, root: ctk.CTk, company_data: Dict[str, Any], user_data: Dict[str, Any], app_controller: Any):
        super().__init__(root, company_data, user_data, app_controller)
        self.db = DatabaseManager()
        self.company_name = company_data.get("company_name", "Unknown")
        self.vendors = []
        self.filtered_vendors = []
        self.loading_overlay = None
        self.root.title(f"Vendors - {self.company_name}")
        self.load_vendors()
    
    def setup_ui(self):
        """Setup the main UI"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header = ctk.CTkFrame(main_frame, fg_color="#1976d2", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header, text="👥 Vendors Management",
            font=ctk.CTkFont(size=24, weight="bold"), text_color="white"
        ).pack(side="left", padx=30, pady=20)

        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.pack(side="right", padx=20)
        
        ctk.CTkButton(
            nav_frame, text="← Back", command=self.go_back,
            width=120, height=35, fg_color="#0d47a1", hover_color="#01579b"
        ).pack(side="left", padx=5)
        
        # Content
        content = ctk.CTkFrame(main_frame, fg_color=("white", "gray20"))
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Toolbar
        toolbar = ctk.CTkFrame(content, fg_color=("#e3f2fd", "gray25"), corner_radius=8)
        toolbar.pack(fill="x", padx=10, pady=10)
        
        # Search
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="left", padx=10, pady=8)
        
        ctk.CTkLabel(search_frame, text="🔍", font=("Arial", 16)).pack(side="left", padx=(0, 5))
        
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Search vendors... (F3)", 
            width=300, height=35
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.search_vendors)
        
        ctk.CTkButton(
            toolbar, text="↻ Refresh (F5)", command=self.load_vendors,
            width=120, height=35, fg_color="#1976d2"
        ).pack(side="left", padx=10)

        self.count_label = ctk.CTkLabel(
            toolbar, text="Total: 0 vendors",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.count_label.pack(side="right", padx=20)
        
        # Vendor list
        table_frame = ctk.CTkFrame(content, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ID", "Vendor Name", "Contact Person", "Email", "Phone", "Outstanding", "Status")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=34, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        scrollbar = ctk.CTkScrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            yscrollcommand=scrollbar.set, selectmode="browse"
        )
        scrollbar.configure(command=self.tree.yview)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("ID", width=100)
        self.tree.column("Vendor Name", width=200)
        self.tree.column("Contact Person", width=150)
        self.tree.column("Email", width=200)
        self.tree.column("Phone", width=120)
        self.tree.column("Outstanding", width=120, anchor="e")
        self.tree.column("Status", width=100, anchor="center")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self.edit_vendor())
        
        # Actions
        action_frame = ctk.CTkFrame(content, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk.CTkButton(
            action_frame, text="+ New Vendor (Ctrl+N)", command=self.add_vendor,
            fg_color="#2e7d32", width=160, height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_frame, text="✏️ Edit", command=self.edit_vendor,
            fg_color="#f57c00", width=100, height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_frame, text="🗑️ Delete", command=self.delete_vendor,
            fg_color="#c62828", width=100, height=35
        ).pack(side="left", padx=5)

        # Shortcuts
        self.root.bind("<Control-n>", lambda e: self.add_vendor())
        self.root.bind("<F3>", lambda e: self.search_entry.focus())
        self.root.bind("<F5>", lambda e: self.load_vendors())
    
    def load_vendors(self):
        """Load vendors from database"""
        self.loading_overlay = show_loading_overlay(self.root, "Loading vendors...")
        run_async(self._fetch_data)

    def _fetch_data(self):
        try:
            vendors = self.db.load_json(self.company_name, "vendors.json") or []
            self.root.after(0, lambda: self._update_ui_after_load(vendors))
        except Exception as e:
            self.root.after(0, lambda: self._handle_load_error(e))

    def _handle_load_error(self, error):
        hide_loading_overlay(self.loading_overlay)
        messagebox.showerror("Error", f"Failed to load vendors:\n{error}")

    def _update_ui_after_load(self, vendors):
        self.vendors = vendors
        self.filtered_vendors = self.vendors.copy()
        self.display_vendors()
        hide_loading_overlay(self.loading_overlay)
    
    def display_vendors(self):
        """Refresh the vendor list"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        items_to_insert = []
        for vendor in self.filtered_vendors:
            items_to_insert.append((
                vendor.get("id", ""),
                vendor.get("name", ""),
                vendor.get("contact_person", ""),
                vendor.get("email", ""),
                vendor.get("phone", ""),
                f"₹{float(vendor.get('outstanding', 0)):,.2f}",
                vendor.get("status", "Active")
            ))
            
        PerformanceOptimizer.batch_insert(self.tree, items_to_insert)
        self.count_label.configure(text=f"Total: {len(self.filtered_vendors)} vendors")
    
    @debounce_search(300)
    def search_vendors(self, event=None):
        """Search vendors"""
        query = self.search_entry.get().lower().strip()
        if not query:
            self.filtered_vendors = self.vendors.copy()
        else:
            self.filtered_vendors = [
                v for v in self.vendors
                if query in v.get("name", "").lower() or
                   query in v.get("contact_person", "").lower() or
                   query in v.get("email", "").lower() or
                   query in v.get("id", "").lower()
            ]
        self.display_vendors()
    
    def get_selected_vendor(self) -> Optional[Dict[str, Any]]:
        sel = self.tree.selection()
        if not sel:
            return None
        vendor_id = self.tree.item(sel[0])['values'][0]
        return next((v for v in self.vendors if v.get("id") == vendor_id), None)

    def add_vendor(self):
        """Add new vendor"""
        self.show_vendor_form(None)
    
    def edit_vendor(self):
        """Edit selected vendor"""
        vendor = self.get_selected_vendor()
        if not vendor:
            messagebox.showwarning("Warning", "Please select a vendor to edit")
            return
        self.show_vendor_form(vendor)
    
    def delete_vendor(self):
        """Delete selected vendor"""
        vendor = self.get_selected_vendor()
        if not vendor:
            messagebox.showwarning("Warning", "Please select a vendor to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete vendor {vendor.get('name')}?"):
            self.vendors = [v for v in self.vendors if v.get("id") != vendor.get("id")]
            self.db.save_json(self.company_name, "vendors.json", self.vendors)
            return
        
        if existing_data:
            vendor_id = existing_data.get("id")
        else:
            # Re-generate to be safe from concurrency (simple)
            max_id = max([int(v.get("id", "VEN-000").split("-")[1]) for v in self.vendors] + [0])
            vendor_id = f"VEN-{max_id + 1:03d}"

        try:
            credit_limit = float(values.get("credit_limit", "0").replace(',', ''))
        except ValueError:
            credit_limit = 0.0

        data = {
            "id": vendor_id,
            "name": name,
            "contact_person": values.get("contact_person", "").strip(),
            "email": values.get("email", "").strip(),
            "phone": values.get("phone", "").strip(),
            "address": values.get("address", "").strip(),
            "gst": values.get("gst_number", "").strip().upper(),
            "pan": values.get("pan_number", "").strip().upper(),
            "payment_terms": values.get("payment_terms", "Net 30"),
            "credit_limit": credit_limit,
            "outstanding": existing_data.get("outstanding", "0") if existing_data else "0",
            "status": existing_data.get("status", "Active") if existing_data else "Active"
        }

        if existing_data:
            for i, v in enumerate(self.vendors):
                if v.get("id") == vendor_id:
                    self.vendors[i] = data
                    break
        else:
            self.vendors.append(data)
        
        self.db.save_json(self.company_name, "vendors.json", self.vendors)
        self.load_vendors()
        dialog.destroy()
        messagebox.showinfo("Success", "Vendor saved successfully!")
