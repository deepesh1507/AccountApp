"""
Invoice Management Module
Professional invoice creation and listing system.
Features: Create, Edit, Delete, Search, Export with Enhanced UI
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading

from .base_module import BaseModule
from .smart_widgets import (
    SmartEntry, SmartNumberEntry, SmartDateEntry, SmartComboBox,
    ValidationLabel, validate_required
)
from .enhanced_form import EnhancedForm
from .performance_optimizer import debounce_search, run_async, show_loading_overlay, hide_loading_overlay, PerformanceOptimizer

class InvoiceManagement(BaseModule):
    def __init__(self, root, company_data, user_data, app_controller):
        super().__init__(root, company_data, user_data, app_controller)
        self.company_name = self.company_data.get('company_name', '')
        
        self.invoices = []
        self.filtered_invoices = []
        self.loading_overlay = None

        self.root.title(f"Invoices - {self.company_name}")
        self.load_invoices()

    def setup_ui(self):
        for w in self.root.winfo_children():
            w.destroy()

        main_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main_frame.pack(fill="both", expand=True)

        # --- Header ---
        header = ctk.CTkFrame(main_frame, fg_color="#1976d2", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header, 
            text="📄 Invoice Management", 
            font=ctk.CTkFont(size=24, weight="bold"), 
            text_color="white"
        )
        title.pack(side="left", padx=30, pady=18)

        # Navigation
        nav = ctk.CTkFrame(header, fg_color="transparent")
        nav.pack(side="right", padx=20)
        
        back_btn = ctk.CTkButton(
            nav, 
            text="← Back", 
            width=120, 
            height=35, 
            fg_color="#0d47a1", 
            hover_color="#01579b", 
            command=self.go_back
        )
        back_btn.pack(side="left", padx=5)
        
        add_btn = ctk.CTkButton(
            nav, 
            text="+ New Invoice (Ctrl+N)", 
            width=180, 
            height=35, 
            fg_color="#2e7d32", 
            hover_color="#1b5e20", 
            command=self.create_invoice
        )
        add_btn.pack(side="left", padx=5)

        # --- Content ---
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
            placeholder_text="Search by ID or Client... (F3)", 
            width=350, 
            height=35
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.search_invoices)

        refresh = ctk.CTkButton(
            toolbar, 
            text="↻ Refresh (F5)", 
            width=120, 
            height=35, 
            fg_color="#1976d2", 
            command=self.load_invoices
        )
        refresh.pack(side="left", padx=10)

        self.count_label = ctk.CTkLabel(
            toolbar, 
            text="Total: 0 invoices", 
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.count_label.pack(side="right", padx=15)

        # Table
        table_frame = ctk.CTkFrame(content, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=34, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        scroll = ctk.CTkScrollbar(table_frame)
        scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            table_frame, 
            columns=("InvID", "Client", "Date", "Total", "Status"), 
            show="headings", 
            yscrollcommand=scroll.set
        )
        scroll.configure(command=self.tree.yview)
        
        self.tree.heading("InvID", text="Invoice ID")
        self.tree.heading("Client", text="Client")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Total", text="Total")
        self.tree.heading("Status", text="Status")
        
        self.tree.column("InvID", width=120)
        self.tree.column("Client", width=250)
        self.tree.column("Date", width=120)
        self.tree.column("Total", width=150, anchor="e")
        self.tree.column("Status", width=120)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self.view_invoice())

        # Actions
        action = ctk.CTkFrame(content, fg_color="transparent")
        action.pack(fill="x", padx=10, pady=(5,10))
        
        view_btn = ctk.CTkButton(action, text="👁️ View", width=100, command=self.view_invoice)
        view_btn.pack(side="left", padx=5)
        
        edit_btn = ctk.CTkButton(action, text="✏️ Edit", width=100, command=self.edit_invoice, fg_color="#1976d2")
        edit_btn.pack(side="left", padx=5)
        
        del_btn = ctk.CTkButton(action, text="🗑️ Delete", width=100, command=self.delete_invoice, fg_color="#c62828")
        del_btn.pack(side="left", padx=5)
        
        export_btn = ctk.CTkButton(action, text="📊 Export CSV", width=120, fg_color="#7b1fa2", command=self.export_invoices)
        export_btn.pack(side="left", padx=5)

        # Shortcuts
        self.root.bind("<Control-n>", lambda e: self.create_invoice())
        self.root.bind("<F3>", lambda e: self.search_entry.focus())
        self.root.bind("<F5>", lambda e: self.load_invoices())

    def load_invoices(self):
        """Start background loading of invoices"""
        self.loading_overlay = show_loading_overlay(self.root, "Loading invoices...")
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        run_async(self._fetch_data)

    def _fetch_data(self):
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            data = db.load_json(self.company_name, "invoices.json")
            invoices = data if isinstance(data, list) else []
            self.root.after(0, lambda: self._update_ui_after_load(invoices))
        except Exception as e:
            self.root.after(0, lambda: self._handle_load_error(e))

    def _handle_load_error(self, error):
        hide_loading_overlay(self.loading_overlay)
        messagebox.showerror("Error", f"Failed to load invoices:\n{error}")

    def _update_ui_after_load(self, invoices):
        self.invoices = invoices
        self.filtered_invoices = self.invoices.copy()
        self.display_invoices()
        self.update_count()
        hide_loading_overlay(self.loading_overlay)

    def display_invoices(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        items_to_insert = []
        for inv in self.filtered_invoices:
            total = sum(item.get('line_total', 0) for item in inv.get('items', []))
            items_to_insert.append((
                inv.get('invoice_id', ''),
                inv.get('client_name', ''),
                (inv.get('date') or '')[:10],
                f"{self.company_data.get('currency', 'INR')} {total:,.2f}",
                inv.get('status', 'Draft')
            ))
            
        PerformanceOptimizer.batch_insert(self.tree, items_to_insert)

    def update_count(self):
        total = len(self.invoices)
        filtered = len(self.filtered_invoices)
        self.count_label.configure(text=f"Total: {filtered} invoices")

    @debounce_search(300)
    def search_invoices(self, event=None):
        term = self.search_entry.get().lower().strip()
        if not term:
            self.filtered_invoices = self.invoices.copy()
        else:
            self.filtered_invoices = [
                inv for inv in self.invoices 
                if term in inv.get('invoice_id', '').lower() or 
                   term in inv.get('client_name', '').lower()
            ]
        self.display_invoices()
        self.update_count()

    def get_selected_invoice(self) -> Optional[Dict[str, Any]]:
        sel = self.tree.selection()
        if not sel:
            return None
        invoice_id = self.tree.item(sel[0])['values'][0]
        return next((inv for inv in self.invoices if inv.get('invoice_id') == invoice_id), None)

    def view_invoice(self):
        inv = self.get_selected_invoice()
        if not inv:
            messagebox.showwarning("Warning", "Please select an invoice to view.")
            return
        self.show_invoice_form(inv, read_only=True)

    def edit_invoice(self):
        inv = self.get_selected_invoice()
        if not inv:
            messagebox.showwarning("Warning", "Please select an invoice to edit")
            return
        self.show_invoice_form(inv)
    
    def create_invoice(self):
        self.show_invoice_form(None)

    def show_invoice_form(self, invoice_data: Optional[Dict[str, Any]], read_only: bool = False):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("View Invoice" if read_only else ("Edit Invoice" if invoice_data else "Create Invoice"))
        dialog.geometry("900x750")
        dialog.transient(self.root)
        dialog.grab_set()

        # Current items list for this session
        current_items = invoice_data.get('items', []).copy() if invoice_data else []

        def on_save(values):
            self._save_invoice(values, current_items, invoice_data, dialog)

        def on_cancel():
            dialog.destroy()

        form = EnhancedForm(
            dialog,
            title="View Invoice" if read_only else ("Edit Invoice" if invoice_data else "New Invoice"),
            on_save=on_save,
            on_cancel=on_cancel,
            auto_save=not read_only
        )
        form.pack(fill="both", expand=True)

        # --- Section 1: Invoice Details ---
        form.add_section("📋 Invoice Details")

        # Invoice ID
        inv_id_val = invoice_data.get('invoice_id', '') if invoice_data else f"INV{len(self.invoices)+1:05d}"
        id_entry = SmartEntry(form.current_section, required=True)
        id_entry.insert(0, inv_id_val)
        if invoice_data:
            id_entry.configure(state="disabled")

        # Client Selection
        from .database_manager import DatabaseManager
        db = DatabaseManager()
        clients = db.load_json(self.company_name, 'clients.json') or []
        client_names = [c.get('client_name') for c in clients if c.get('client_name')]
        
        client_combo = SmartComboBox(form.current_section, values=client_names, allow_custom=False)
        if invoice_data:
            client_combo.set(invoice_data.get('client_name', ''))
        elif client_names:
            client_combo.set(client_names[0])

        form.add_field_pair(
            "Invoice ID:", id_entry,
            "Client:", client_combo,
            help_text1="Unique Invoice ID",
            help_text2="Select Client"
        )

        # Date and Status
        date_picker = SmartDateEntry(form.current_section)
        if invoice_data:
            date_picker.entry.delete(0, "end")
            date_picker.entry.insert(0, invoice_data.get('date', '')[:10])

        status_combo = SmartComboBox(
            form.current_section, 
            values=["Draft", "Unpaid", "Paid", "Partially Paid", "Cancelled"],
            allow_custom=False
        )
        status_combo.set(invoice_data.get('status', 'Unpaid') if invoice_data else 'Unpaid')

        form.add_field_pair(
            "Date:", date_picker,
            "Status:", status_combo,
            help_text1="Invoice Date",
            help_text2="Current Status"
        )

        # --- Section 2: Line Items ---
        items_section = form.add_section("🛒 Line Items")
        
        # Custom frame for line items
        items_frame = ctk.CTkFrame(items_section, fg_color="transparent")
        items_frame.pack(fill="x", padx=15, pady=5)

        # Item Entry Row (if not read-only)
        if not read_only:
            entry_row = ctk.CTkFrame(items_frame, fg_color=("gray95", "gray25"))
            entry_row.pack(fill="x", pady=(0, 10))

            ctk.CTkLabel(entry_row, text="Description").grid(row=0, column=0, padx=5, sticky="w")
            ctk.CTkLabel(entry_row, text="Qty").grid(row=0, column=1, padx=5, sticky="w")
            ctk.CTkLabel(entry_row, text="Price").grid(row=0, column=2, padx=5, sticky="w")

            desc_entry = SmartEntry(entry_row, placeholder_text="Item description", width=300)
            desc_entry.grid(row=1, column=0, padx=5, pady=5)

            qty_entry = SmartNumberEntry(entry_row, width=80, placeholder_text="1")
            qty_entry.grid(row=1, column=1, padx=5, pady=5)

            price_entry = SmartNumberEntry(entry_row, width=100, placeholder_text="0.00")
            price_entry.grid(row=1, column=2, padx=5, pady=5)

            def add_item():
                desc = desc_entry.get().strip()
                try:
                    qty = float(qty_entry.get().replace(',', ''))
                    price = float(price_entry.get().replace(',', ''))
                except ValueError:
                    messagebox.showwarning("Invalid Input", "Please check quantity and price")
                    return

                if not desc:
                    messagebox.showwarning("Missing Info", "Description is required")
                    return
                
                if qty <= 0 or price < 0:
                    messagebox.showwarning("Invalid Input", "Quantity must be > 0")
                    return

                current_items.append({
                    'description': desc,
                    'qty': qty,
                    'rate': price,
                    'line_total': qty * price
                })
                
                # Clear inputs
                desc_entry.delete(0, "end")
                qty_entry.delete(0, "end")
                price_entry.delete(0, "end")
                
                refresh_items_list()

            add_btn = ctk.CTkButton(entry_row, text="Add", width=60, command=add_item, fg_color="#2e7d32")
            add_btn.grid(row=1, column=3, padx=5, pady=5)

        # Items List
        list_frame = ctk.CTkScrollableFrame(items_frame, height=200, fg_color=("white", "gray15"))
        list_frame.pack(fill="x")

        def refresh_items_list():
            for w in list_frame.winfo_children():
                w.destroy()
            
            if not current_items:
                ctk.CTkLabel(list_frame, text="No items added").pack(pady=10)
                return

            # Header
            header = ctk.CTkFrame(list_frame, fg_color="transparent")
            header.pack(fill="x", pady=2)
            ctk.CTkLabel(header, text="Description", width=300, anchor="w", font=("Arial", 12, "bold")).pack(side="left", padx=5)
            ctk.CTkLabel(header, text="Total", width=100, anchor="e", font=("Arial", 12, "bold")).pack(side="right", padx=35)
            ctk.CTkLabel(header, text="Qty x Price", width=150, anchor="e", font=("Arial", 12, "bold")).pack(side="right", padx=5)

            for idx, item in enumerate(current_items):
                row = ctk.CTkFrame(list_frame, fg_color=("gray95", "gray20"))
                row.pack(fill="x", pady=2)
                
                ctk.CTkLabel(row, text=item['description'], width=300, anchor="w").pack(side="left", padx=5)
                
                if not read_only:
                    ctk.CTkButton(
                        row, text="✕", width=30, fg_color="#c62828", 
                        command=lambda i=idx: delete_item(i)
                    ).pack(side="right", padx=5)

                total = item['qty'] * item['rate']
                ctk.CTkLabel(row, text=f"{total:,.2f}", width=100, anchor="e").pack(side="right", padx=5)
                ctk.CTkLabel(row, text=f"{item['qty']} x {item['rate']:,.2f}", width=150, anchor="e").pack(side="right", padx=5)

        def delete_item(index):
            if messagebox.askyesno("Confirm", "Remove this item?"):
                del current_items[index]
                refresh_items_list()

        refresh_items_list()

        # Disable fields if read_only
        if read_only:
            form.save_btn.configure(state="disabled")
            id_entry.configure(state="disabled")
            client_combo.configure(state="disabled")
            date_picker.entry.configure(state="disabled")
            status_combo.configure(state="disabled")

    def _save_invoice(self, values, items, existing_data, dialog):
        # Extract values using field IDs (lowercase, spaces to underscores)
        inv_id = values.get('invoice_id', '').strip()
        client = values.get('client', '').strip()
        date_str = values.get('date', '').strip()
        status = values.get('status', '').strip()

        # Validation
        if not inv_id:
            messagebox.showerror("Error", "Invoice ID is required")
            return
        if not client:
            messagebox.showerror("Error", "Client is required")
            return
        if not items:
            messagebox.showerror("Error", "Please add at least one item")
            return
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format")
            return

        # Build invoice object
        invoice = {
            'invoice_id': inv_id,
            'client_name': client,
            'date': date_str,
            'items': items,
            'status': status,
            'created_date': existing_data.get('created_date', datetime.now().strftime("%Y-%m-%d %H:%M:%S")) if existing_data else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'last_modified': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()

            if existing_data:
                # Update existing
                for i, inv in enumerate(self.invoices):
                    if inv.get('invoice_id') == inv_id:
                        self.invoices[i] = invoice
                        break
                messagebox.showinfo("Success", f"Invoice {inv_id} updated")
            else:
                # Add new
                self.invoices.append(invoice)
                messagebox.showinfo("Success", f"Invoice {inv_id} created")

            db.save_json(self.company_name, "invoices.json", self.invoices)
            dialog.destroy()
            self.load_invoices()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save invoice:\n{e}")

    def delete_invoice(self):
        inv = self.get_selected_invoice()
        if not inv:
            messagebox.showwarning("Warning", "Please select an invoice to delete")
            return
        confirm = messagebox.askyesno("Delete Invoice", f"Delete invoice {inv.get('invoice_id')}?")
        if not confirm:
            return
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            self.invoices = [i for i in self.invoices if i.get('invoice_id') != inv.get('invoice_id')]
            db.save_json(self.company_name, "invoices.json", self.invoices)
            messagebox.showinfo("Success", "Invoice deleted")
            self.load_invoices()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete invoice:\n{e}")

    def export_invoices(self):
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            path = db.export_to_csv(self.company_name, "invoices.json")
            if path:
                messagebox.showinfo("Success", f"Invoices exported to:\n{path}")
            else:
                messagebox.showwarning("Warning", "No invoices to export")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{e}")

    def go_back(self):
        if self.app:
            self.app.show_dashboard(self.company_data, self.user_data)
