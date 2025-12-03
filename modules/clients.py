"""
Clients Management Module
Complete client/customer management system with Enhanced UI
Features: Add, Edit, Delete, Search, View Details, Contact Info
Client Types: Individual, Business, Government
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
import re
from typing import Dict, Any, Optional, List
import threading

from .base_module import BaseModule
from .smart_widgets import (
    SmartEntry, SmartNumberEntry, SmartComboBox, 
    ValidationLabel, validate_required, validate_email, validate_phone
)
from .enhanced_form import EnhancedForm
from .performance_optimizer import debounce_search, run_async, show_loading_overlay, hide_loading_overlay, PerformanceOptimizer

class ClientsManagement(BaseModule):
    def __init__(self, root: ctk.CTk, company_data: Dict[str, Any], user_data: Dict[str, Any], app_controller: Any):
        super().__init__(root, company_data, user_data, app_controller=app_controller)
        self.company_name = company_data.get('company_name', '')
        self.clients = []
        self.filtered_clients = []
        self.loading_overlay = None
        
        self.root.title(f"Clients - {self.company_name}")
        self.load_clients()

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main_frame.pack(fill="both", expand=True)

        # --- Header ---
        header_frame = ctk.CTkFrame(main_frame, fg_color="#1976d2", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="👥 Clients Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=30, pady=20)

        nav_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        nav_frame.pack(side="right", padx=20)

        back_btn = ctk.CTkButton(
            nav_frame,
            text="← Back",
            width=120,
            height=35,
            fg_color="#0d47a1",
            hover_color="#01579b",
            command=self.go_back
        )
        back_btn.pack(side="left", padx=5)

        # --- Content ---
        content_frame = ctk.CTkFrame(main_frame, fg_color=("white", "gray20"))
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Toolbar
        toolbar_frame = ctk.CTkFrame(content_frame, fg_color=("#e3f2fd", "gray25"), corner_radius=8)
        toolbar_frame.pack(fill="x", padx=10, pady=10)

        # Search
        search_frame = ctk.CTkFrame(toolbar_frame, fg_color="transparent")
        search_frame.pack(side="left", padx=10, pady=8)
        
        ctk.CTkLabel(search_frame, text="🔍", font=("Arial", 16)).pack(side="left", padx=(0, 5))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by name, email, phone... (F3)",
            width=300,
            height=35
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.search_clients)

        # Filter
        self.filter_combo = ctk.CTkComboBox(
            toolbar_frame,
            values=["All Types", "Individual", "Business", "Government"],
            width=150,
            height=35,
            command=self.filter_clients
        )
        self.filter_combo.set("All Types")
        self.filter_combo.pack(side="left", padx=10)

        refresh_btn = ctk.CTkButton(
            toolbar_frame,
            text="↻ Refresh (F5)",
            width=120,
            height=35,
            fg_color="#1976d2",
            command=self.load_clients
        )
        refresh_btn.pack(side="left", padx=10)

        self.count_label = ctk.CTkLabel(
            toolbar_frame,
            text="Total: 0 clients",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.count_label.pack(side="right", padx=15)

        # Table
        table_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=34, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        scrollbar = ctk.CTkScrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Name", "Type", "Email", "Phone", "City", "Balance", "Status"),
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        scrollbar.configure(command=self.tree.yview)

        self.tree.heading("ID", text="Client ID")
        self.tree.heading("Name", text="Client Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Phone", text="Phone")
        self.tree.heading("City", text="City")
        self.tree.heading("Balance", text="Outstanding")
        self.tree.heading("Status", text="Status")

        self.tree.column("ID", width=100)
        self.tree.column("Name", width=200)
        self.tree.column("Type", width=100)
        self.tree.column("Email", width=200)
        self.tree.column("Phone", width=120)
        self.tree.column("City", width=120)
        self.tree.column("Balance", width=120, anchor="e")
        self.tree.column("Status", width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self.view_selected())

        # Actions
        action_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkButton(action_frame, text="+ Add Client (Ctrl+N)", command=self.show_add_form, fg_color="#2e7d32", width=160).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="👁️ View", command=self.view_selected, width=100).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="✏️ Edit", command=self.edit_selected, fg_color="#f57c00", width=100).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Delete", command=self.delete_selected, fg_color="#c62828", width=100).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📊 Export CSV", command=self.export_clients, fg_color="#7b1fa2", width=120).pack(side="left", padx=5)

        # Shortcuts
        self.root.bind("<Control-n>", lambda e: self.show_add_form())
        self.root.bind("<F3>", lambda e: self.search_entry.focus())
        self.root.bind("<F5>", lambda e: self.load_clients())

    def load_clients(self):
        self.loading_overlay = show_loading_overlay(self.root, "Loading clients...")
        run_async(self._fetch_data)

    def _fetch_data(self):
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            data = db.load_json(self.company_name, "clients.json")
            clients = data if isinstance(data, list) else []
            self.root.after(0, lambda: self._update_ui_after_load(clients))
        except Exception as e:
            self.root.after(0, lambda: self._handle_load_error(e))

    def _handle_load_error(self, error):
        hide_loading_overlay(self.loading_overlay)
        messagebox.showerror("Error", f"Failed to load clients:\n{error}")

    def _update_ui_after_load(self, clients):
        self.clients = clients
        self.filtered_clients = self.clients.copy()
        self.display_clients()
        self.update_count()
        hide_loading_overlay(self.loading_overlay)

    def display_clients(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        currency = self.company_data.get('currency', 'INR')
        items_to_insert = []
        
        for client in self.filtered_clients:
            balance = client.get('outstanding_balance', 0.0)
            formatted_balance = f"{currency} {balance:,.2f}"
            items_to_insert.append((
                client.get('client_id', ''),
                client.get('client_name', ''),
                client.get('client_type', ''),
                client.get('email', ''),
                client.get('phone', ''),
                client.get('city', ''),
                formatted_balance,
                client.get('status', 'Active')
            ))
            
        PerformanceOptimizer.batch_insert(self.tree, items_to_insert)

    @debounce_search(300)
    def search_clients(self, event=None):
        term = self.search_entry.get().lower().strip()
        self._apply_filters(term)

    def filter_clients(self, event=None):
        term = self.search_entry.get().lower().strip()
        self._apply_filters(term)

    def _apply_filters(self, term):
        filter_type = self.filter_combo.get()
        
        filtered = self.clients
        
        if filter_type != "All Types":
            filtered = [c for c in filtered if c.get('client_type') == filter_type]
            
        if term:
            filtered = [
                c for c in filtered
                if term in c.get('client_name', '').lower() or
                   term in c.get('email', '').lower() or
                   term in c.get('phone', '').lower()
            ]
            
        self.filtered_clients = filtered
        self.display_clients()
        self.update_count()

    def update_count(self):
        total = len(self.clients)
        filtered = len(self.filtered_clients)
        self.count_label.configure(text=f"Total: {filtered} clients")

    def get_selected_client(self) -> Optional[Dict[str, Any]]:
        sel = self.tree.selection()
        if not sel:
            return None
        client_id = self.tree.item(sel[0])['values'][0]
        return next((c for c in self.clients if c.get('client_id') == client_id), None)

    def show_add_form(self):
        self.show_client_form(None)

    def view_selected(self):
        client = self.get_selected_client()
        if not client:
            messagebox.showwarning("Warning", "Please select a client to view")
            return
        self.show_client_form(client, read_only=True)

    def edit_selected(self):
        client = self.get_selected_client()
        if not client:
            messagebox.showwarning("Warning", "Please select a client to edit")
            return
        self.show_client_form(client)

    def show_client_form(self, client_data: Optional[Dict[str, Any]], read_only: bool = False):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("View Client" if read_only else ("Edit Client" if client_data else "Add New Client"))
        dialog.geometry("800x750")
        dialog.transient(self.root)
        dialog.grab_set()

        form = EnhancedForm(
            dialog,
            title="View Client" if read_only else ("Edit Client" if client_data else "New Client"),
            on_save=None, # Set later
            on_cancel=lambda: dialog.destroy(),
            auto_save=not read_only
        )
        form.pack(fill="both", expand=True)

        # --- Section 1: Basic Info ---
        form.add_section("📋 Basic Information")

        # Client ID
        client_id_val = client_data.get('client_id', '') if client_data else f"CLI{len(self.clients)+1:04d}"
        id_entry = SmartEntry(form.current_section, required=True)
        id_entry.insert(0, client_id_val)
        id_entry.configure(state="disabled")

        # Client Type
        type_combo = SmartComboBox(
            form.current_section,
            values=["Individual", "Business", "Government"],
            allow_custom=False
        )
        type_combo.set(client_data.get('client_type', 'Individual') if client_data else 'Individual')
        form.add_field_pair(
            "Client ID:", id_entry,
            "Client Type:", type_combo,
            help_text1="Auto-generated ID",
            help_text2="Type of client entity"
        )

        # Name and Email
        name_entry = SmartEntry(form.current_section, required=True, placeholder_text="Full Name or Company Name")
        if client_data: name_entry.insert(0, client_data.get('client_name', ''))

        email_entry = SmartEntry(form.current_section, validation_func=validate_email, placeholder_text="email@example.com")
        if client_data: email_entry.insert(0, client_data.get('email', ''))

        form.add_field_pair("Client Name:", name_entry, "Email:", email_entry)

        # Phone and Mobile
        phone_entry = SmartEntry(form.current_section, required=True, validation_func=validate_phone)
        if client_data: phone_entry.insert(0, client_data.get('phone', ''))

        mobile_entry = SmartEntry(form.current_section, validation_func=validate_phone)
        if client_data: mobile_entry.insert(0, client_data.get('mobile', ''))

        form.add_field_pair("Phone:", phone_entry, "Mobile:", mobile_entry)

        # Website
        website_entry = SmartEntry(form.current_section, placeholder_text="https://")
        if client_data: website_entry.insert(0, client_data.get('website', ''))
        form.add_field_pair("Website:", website_entry, "", None)

        # --- Section 2: Address ---
        form.add_section("🏢 Address Details")
        addr_entry = SmartEntry(form.current_section, width=400)
        if client_data: addr_entry.insert(0, client_data.get('address', ''))
        
        city_entry = SmartEntry(form.current_section)
        if client_data: city_entry.insert(0, client_data.get('city', ''))

        form.add_field_pair("Address:", addr_entry, "City:", city_entry)

        state_entry = SmartEntry(form.current_section)
        if client_data: state_entry.insert(0, client_data.get('state', ''))

        pin_entry = SmartEntry(form.current_section)
        if client_data: pin_entry.insert(0, client_data.get('pincode', ''))

        form.add_field_pair("State:", state_entry, "Pincode:", pin_entry)

        country_entry = SmartEntry(form.current_section)
        if client_data: country_entry.insert(0, client_data.get('country', ''))
        form.add_field_pair("Country:", country_entry, "", None)

        # --- Section 3: Tax & Financial ---
        form.add_section("💰 Financial & Tax")

        gst_entry = SmartEntry(form.current_section)
        if client_data: gst_entry.insert(0, client_data.get('gst_number', ''))

        pan_entry = SmartEntry(form.current_section)
        if client_data: pan_entry.insert(0, client_data.get('pan_number', ''))

        form.add_field_pair("GST Number:", gst_entry, "PAN Number:", pan_entry)

        limit_entry = SmartNumberEntry(form.current_section)
        if client_data: limit_entry.insert(0, str(client_data.get('credit_limit', 0)))
        else: limit_entry.insert(0, "0")

        terms_entry = SmartNumberEntry(form.current_section)
        if client_data: terms_entry.insert(0, str(client_data.get('payment_terms', 30)))
        else: terms_entry.insert(0, "30")

        form.add_field_pair("Credit Limit:", limit_entry, "Payment Terms (Days):", terms_entry)

        # Status and Notes
        status_combo = SmartComboBox(form.current_section, values=["Active", "Inactive", "Suspended"], allow_custom=False)
        status_combo.set(client_data.get('status', 'Active') if client_data else 'Active')

        notes_entry = ctk.CTkTextbox(form.current_section, height=60)
        if client_data: notes_entry.insert("1.0", client_data.get('notes', ''))

        form.add_field_pair("Status:", status_combo, "", None)
        
        ctk.CTkLabel(form.current_section, text="Notes:", font=ctk.CTkFont(weight="bold")).grid(row=form.current_row, column=0, sticky="ne", padx=20, pady=10)
        notes_entry.grid(row=form.current_row, column=1, columnspan=3, sticky="ew", padx=10, pady=10)
        form.current_row += 1

        if read_only:
            form.save_btn.configure(state="disabled")
            for w in [name_entry, email_entry, phone_entry, mobile_entry, website_entry, 
                      addr_entry, city_entry, state_entry, pin_entry, country_entry,
                      gst_entry, pan_entry, limit_entry, terms_entry, type_combo, status_combo]:
                w.configure(state="disabled")
            notes_entry.configure(state="disabled")

        # Define save handler with access to notes
        def on_save(values):
            notes = notes_entry.get("1.0", "end-1c")
            values['client_id'] = id_entry.get()
            values['notes'] = notes
            self._save_client(values, client_data, dialog)

        form.save_btn.configure(command=form.save)
        form.on_save = on_save

    def _save_client(self, values, existing_data, dialog):
        client_id = values.get('client_id')
        client_name = values.get('client_name', '').strip()
        
        if not client_name:
            messagebox.showerror("Error", "Client Name is required")
            return

        try:
            credit_limit = float(values.get('credit_limit', '0').replace(',', ''))
            payment_terms = int(values.get('payment_terms_days', '30').replace(',', ''))
        except ValueError:
             credit_limit = 0.0
             payment_terms = 30

        client_data = {
            'client_id': client_id,
            'client_name': client_name,
            'client_type': values.get('client_type', 'Individual'),
            'email': values.get('email', '').strip(),
            'phone': values.get('phone', '').strip(),
            'mobile': values.get('mobile', '').strip(),
            'website': values.get('website', '').strip(),
            'address': values.get('address', '').strip(),
            'city': values.get('city', '').strip(),
            'state': values.get('state', '').strip(),
            'pincode': values.get('pincode', '').strip(),
            'country': values.get('country', '').strip(),
            'gst_number': values.get('gst_number', '').strip().upper(),
            'pan_number': values.get('pan_number', '').strip().upper(),
            'credit_limit': credit_limit,
            'payment_terms': payment_terms,
            'outstanding_balance': existing_data.get('outstanding_balance', 0.0) if existing_data else 0.0,
            'status': values.get('status', 'Active'),
            'notes': values.get('notes', '').strip(),
            'created_date': existing_data.get('created_date') if existing_data else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()

            if existing_data:
                for i, c in enumerate(self.clients):
                    if c.get('client_id') == client_id:
                        self.clients[i] = client_data
                        break
                messagebox.showinfo("Success", "Client updated successfully!")
            else:
                self.clients.append(client_data)
                messagebox.showinfo("Success", "Client created successfully!")

            db.save_json(self.company_name, "clients.json", self.clients)
            dialog.destroy()
            self.load_clients()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save client:\\n{str(e)}")

    def delete_selected(self):
        client = self.get_selected_client()
        if not client:
            messagebox.showwarning("Warning", "Please select a client to delete")
            return

        if messagebox.askyesno("Confirm", f"Delete client {client.get('client_name')}?"):
            try:
                from .database_manager import DatabaseManager
                db = DatabaseManager()
                self.clients = [c for c in self.clients if c.get('client_id') != client.get('client_id')]
                db.save_json(self.company_name, "clients.json", self.clients)
                messagebox.showinfo("Success", "Client deleted")
                self.load_clients()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete:\n{e}")

    def export_clients(self):
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            path = db.export_to_csv(self.company_name, "clients.json")
            if path:
                messagebox.showinfo("Success", f"Exported to:\n{path}")
            else:
                messagebox.showwarning("Warning", "Nothing to export")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{e}")

    def go_back(self):
        if self.app:
            self.app.show_dashboard(self.company_data, self.user_data)
