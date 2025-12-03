"""
Payment Tracking Module
Track receivables (money to receive) and payables (money to pay)
Features: Invoice tracking, payment status, due dates, payment history, recording payments
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from .base_module import BaseModule
from .utilities import Formatters, Calculator, Validators
from .smart_widgets import (
    SmartEntry, SmartNumberEntry, SmartComboBox, 
    SmartDateEntry, ValidationLabel, validate_required
)
from .enhanced_form import EnhancedForm
from .performance_optimizer import debounce_search, run_async, show_loading_overlay, hide_loading_overlay, PerformanceOptimizer

class PaymentTracking(BaseModule):
    def __init__(self, root, company_data, user_data, app_controller):
        super().__init__(root, company_data, user_data, app_controller)
        self.company_name = company_data.get("company_name", "")
        self.invoices = []
        self.expenses = []
        self.filtered_receivables = []
        self.filtered_payables = []
        self.loading_overlay = None
        
        self.root.title(f"Payments - {self.company_name}")
        self.load_payments()

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main_frame.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(main_frame, fg_color="#00796b", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, 
            text="💰 Payment Tracking", 
            font=ctk.CTkFont(size=24, weight="bold"), 
            text_color="white"
        ).pack(side="left", padx=30, pady=18)

        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.pack(side="right", padx=20)
        
        ctk.CTkButton(
            nav_frame, 
            text="← Back", 
            command=self.go_back, 
            width=120,
            height=35,
            fg_color="#004d40",
            hover_color="#00695c"
        ).pack(side="left", padx=5)

        # Content
        content = ctk.CTkFrame(main_frame, fg_color=("white", "gray20"))
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Tab view for Receivables vs Payables
        self.tabview = ctk.CTkTabview(content)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_receivables = self.tabview.add("📥 Receivables (To Receive)")
        self.tab_payables = self.tabview.add("📤 Payables (To Pay)")

        # Receivables Tab
        self.setup_receivables_tab(self.tab_receivables)

        # Payables Tab
        self.setup_payables_tab(self.tab_payables)

    def setup_receivables_tab(self, parent):
        """Setup receivables (money to receive) tab"""
        # Toolbar
        toolbar = ctk.CTkFrame(parent, fg_color=("#e3f2fd", "gray25"), corner_radius=8)
        toolbar.pack(fill="x", padx=10, pady=10)

        # Search
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="left", padx=10, pady=8)
        
        ctk.CTkLabel(search_frame, text="🔍", font=("Arial", 16)).pack(side="left", padx=(0, 5))

        self.recv_search = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Search invoices... (F3)", 
            width=250,
            height=35
        )
        self.recv_search.pack(side="left")
        self.recv_search.bind("<KeyRelease>", self.filter_receivables)

        # Filter
        self.recv_status_filter = ctk.CTkComboBox(
            toolbar, 
            values=["All Status", "Pending", "Partial", "Paid", "Overdue"], 
            width=140,
            height=35,
            command=self.filter_receivables
        )
        self.recv_status_filter.set("All Status")
        self.recv_status_filter.pack(side="left", padx=10)

        ctk.CTkButton(
            toolbar, 
            text="↻ Refresh", 
            command=self.load_payments, 
            width=100,
            height=35,
            fg_color="#1976d2"
        ).pack(side="left", padx=10)

        self.recv_summary = ctk.CTkLabel(
            toolbar, 
            text="Total Receivable: ₹0.00",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.recv_summary.pack(side="right", padx=20)

        # Table
        table_frame = ctk.CTkFrame(parent, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Invoice No", "Client", "Amount", "Paid", "Balance", "Due Date", "Status", "Days Overdue")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=34, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        scrollbar = ctk.CTkScrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        self.recv_tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings", 
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        scrollbar.configure(command=self.recv_tree.yview)

        for col in columns:
            self.recv_tree.heading(col, text=col)
            
        self.recv_tree.column("Invoice No", width=100)
        self.recv_tree.column("Client", width=200)
        self.recv_tree.column("Amount", width=100, anchor="e")
        self.recv_tree.column("Paid", width=100, anchor="e")
        self.recv_tree.column("Balance", width=100, anchor="e")
        self.recv_tree.column("Due Date", width=100, anchor="center")
        self.recv_tree.column("Status", width=100, anchor="center")
        self.recv_tree.column("Days Overdue", width=100, anchor="center")

        self.recv_tree.pack(fill="both", expand=True)
        self.recv_tree.bind("<Double-1>", lambda e: self.record_payment_received())

        # Actions
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkButton(
            action_frame, 
            text="💵 Record Payment Received", 
            command=self.record_payment_received, 
            fg_color="#2e7d32", 
            width=200,
            height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_frame, 
            text="📊 Aging Report", 
            command=self.aging_report_receivables, 
            width=150,
            height=35
        ).pack(side="left", padx=5)

    def setup_payables_tab(self, parent):
        """Setup payables (money to pay) tab"""
        # Toolbar
        toolbar = ctk.CTkFrame(parent, fg_color=("#e3f2fd", "gray25"), corner_radius=8)
        toolbar.pack(fill="x", padx=10, pady=10)

        # Search
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="left", padx=10, pady=8)
        
        ctk.CTkLabel(search_frame, text="🔍", font=("Arial", 16)).pack(side="left", padx=(0, 5))

        self.pay_search = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Search expenses... (F3)", 
            width=250,
            height=35
        )
        self.pay_search.pack(side="left")
        self.pay_search.bind("<KeyRelease>", self.filter_payables)

        # Filter
        self.pay_status_filter = ctk.CTkComboBox(
            toolbar, 
            values=["All Status", "Pending", "Partial", "Paid"], 
            width=140,
            height=35,
            command=self.filter_payables
        )
        self.pay_status_filter.set("All Status")
        self.pay_status_filter.pack(side="left", padx=10)

        ctk.CTkButton(
            toolbar, 
            text="↻ Refresh", 
            command=self.load_payments, 
            width=100,
            height=35,
            fg_color="#1976d2"
        ).pack(side="left", padx=10)

        self.pay_summary = ctk.CTkLabel(
            toolbar, 
            text="Total Payable: ₹0.00",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.pay_summary.pack(side="right", padx=20)

        # Table
        table_frame = ctk.CTkFrame(parent, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Expense ID", "Vendor", "Amount", "Paid", "Balance", "Due Date", "Status", "Days Until Due")
        
        scrollbar = ctk.CTkScrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        self.pay_tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings", 
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        scrollbar.configure(command=self.pay_tree.yview)

        for col in columns:
            self.pay_tree.heading(col, text=col)
            
        self.pay_tree.column("Expense ID", width=100)
        self.pay_tree.column("Vendor", width=200)
        self.pay_tree.column("Amount", width=100, anchor="e")
        self.pay_tree.column("Paid", width=100, anchor="e")
        self.pay_tree.column("Balance", width=100, anchor="e")
        self.pay_tree.column("Due Date", width=100, anchor="center")
        self.pay_tree.column("Status", width=100, anchor="center")
        self.pay_tree.column("Days Until Due", width=100, anchor="center")

        self.pay_tree.pack(fill="both", expand=True)
        self.pay_tree.bind("<Double-1>", lambda e: self.record_payment_made())

        # Actions
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkButton(
            action_frame, 
            text="💸 Record Payment Made", 
            command=self.record_payment_made, 
            fg_color="#c62828", 
            width=200,
            height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            action_frame, 
            text="📊 Due Date Report", 
            command=self.due_date_report_payables, 
            width=150,
            height=35
        ).pack(side="left", padx=5)

    def load_payments(self):
        """Load payment data"""
        self.loading_overlay = show_loading_overlay(self.root, "Loading payments...")
        run_async(self._fetch_data)

    def _fetch_data(self):
        try:
            # Load invoices for receivables
            invoices = self.db.load_json(self.company_name, "invoices.json") or []
            
            # Load expenses for payables
            expenses = self.db.load_json(self.company_name, "expenses.json") or []

            self.root.after(0, lambda: self._update_ui_after_load(invoices, expenses))
        except Exception as e:
            self.root.after(0, lambda: self._handle_load_error(e))

    def _handle_load_error(self, error):
        hide_loading_overlay(self.loading_overlay)
        messagebox.showerror("Error", f"Failed to load payment data:\n{str(e)}")

    def _update_ui_after_load(self, invoices, expenses):
        self.invoices = invoices
        self.expenses = expenses
        
        self.filter_receivables()
        self.filter_payables()
        
        hide_loading_overlay(self.loading_overlay)

    @debounce_search(300)
    def filter_receivables(self, event=None):
        term = self.recv_search.get().lower().strip()
        status_filter = self.recv_status_filter.get()
        
        filtered = []
        total_receivable = 0
        today = datetime.now()
        
        for inv in self.invoices:
            # Calculate totals
            total = sum(item.get('line_total', 0) for item in inv.get('items', []))
            paid = inv.get('amount_paid', 0)
            balance = total - paid
            
            # Determine status
            due_date_str = inv.get('due_date', inv.get('date', ''))
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                days_overdue = (today - due_date).days
            except:
                days_overdue = 0
                
            if paid == 0:
                status = "Pending"
            elif paid < total:
                status = "Partial"
            else:
                status = "Paid"
                
            if days_overdue > 0 and status != "Paid":
                status = "Overdue"
                
            # Filter logic
            if status_filter != "All Status" and status != status_filter:
                continue
                
            if term and (term not in inv.get('client_name', '').lower() and term not in inv.get('invoice_id', '').lower()):
                continue
                
            filtered.append((
                inv.get('invoice_id', ''),
                inv.get('client_name', ''),
                Formatters.format_currency(total),
                Formatters.format_currency(paid),
                Formatters.format_currency(balance),
                due_date_str,
                status,
                f"{days_overdue} days" if days_overdue > 0 else "-"
            ))
            
            if status != "Paid":
                total_receivable += balance
                
        # Update Tree
        for item in self.recv_tree.get_children():
            self.recv_tree.delete(item)
            
        PerformanceOptimizer.batch_insert(self.recv_tree, filtered)
        self.recv_summary.configure(text=f"Total Receivable: {Formatters.format_currency(total_receivable)}")

    @debounce_search(300)
    def filter_payables(self, event=None):
        term = self.pay_search.get().lower().strip()
        status_filter = self.pay_status_filter.get()
        
        filtered = []
        total_payable = 0
        today = datetime.now()
        
        for exp in self.expenses:
            amount = float(exp.get('amount', 0))
            paid = exp.get('amount_paid', 0)
            balance = amount - paid
            
            due_date_str = exp.get('due_date', exp.get('date', ''))
            try:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                days_until = (due_date - today).days
            except:
                days_until = 0
                
            if paid == 0:
                status = "Pending"
            elif paid < amount:
                status = "Partial"
            else:
                status = "Paid"
                
            if status_filter != "All Status" and status != status_filter:
                continue
                
            if term and (term not in exp.get('vendor', '').lower() and term not in exp.get('expense_id', '').lower()):
                continue
                
            filtered.append((
                exp.get('expense_id', exp.get('id', 'N/A')),
                exp.get('vendor', exp.get('category', ''))[:30],
                Formatters.format_currency(amount),
                Formatters.format_currency(paid),
                Formatters.format_currency(balance),
                due_date_str,
                status,
                f"{days_until} days" if days_until != 0 else "Today"
            ))
            
            if status != "Paid":
                total_payable += balance
                
        for item in self.pay_tree.get_children():
            self.pay_tree.delete(item)
            
        PerformanceOptimizer.batch_insert(self.pay_tree, filtered)
        self.pay_summary.configure(text=f"Total Payable: {Formatters.format_currency(total_payable)}")

    def record_payment_received(self):
        """Record payment received from customer"""
        sel = self.recv_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select an invoice to record payment against.")
            return
            
        item = self.recv_tree.item(sel[0])
        invoice_id = item['values'][0]
        invoice = next((i for i in self.invoices if i.get('invoice_id') == invoice_id), None)
        
        if not invoice: return
        
        self.show_payment_form(invoice, is_receivable=True)

    def record_payment_made(self):
        """Record payment made to vendor"""
        sel = self.pay_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select an expense to record payment against.")
            return
            
        item = self.pay_tree.item(sel[0])
        expense_id = item['values'][0]
        expense = next((e for e in self.expenses if e.get('expense_id') == expense_id), None)
        
        if not expense: return
        
        self.show_payment_form(expense, is_receivable=False)

    def show_payment_form(self, record_data, is_receivable=True):
        """Show payment recording form"""
        dialog = ctk.CTkToplevel(self.root)
        title = "Record Payment Received" if is_receivable else "Record Payment Made"
        dialog.title(title)
        dialog.geometry("500x500")
        dialog.transient(self.root)
        
        # Ensure dialog is visible and centered
        from .enhanced_form import EnhancedForm
        EnhancedForm.ensure_dialog_visible(dialog, self.root)

        form = EnhancedForm(
            dialog,
            title=title,
            on_save=None,
            on_cancel=lambda: dialog.destroy(),
            auto_save=False
        )
        form.pack(fill="both", expand=True)

        # Calculate outstanding
        if is_receivable:
            total = sum(item.get('line_total', 0) for item in record_data.get('items', []))
            paid = record_data.get('amount_paid', 0)
            ref_id = record_data.get('invoice_id')
            party = record_data.get('client_name')
        else:
            total = float(record_data.get('amount', 0))
            paid = record_data.get('amount_paid', 0)
            ref_id = record_data.get('expense_id')
            party = record_data.get('vendor')

        outstanding = total - paid

        form.add_section(f"Payment for {ref_id}")
        
        ctk.CTkLabel(form.current_section, text=f"Party: {party}", font=("Arial", 12, "bold")).grid(row=form.current_row, column=0, sticky="w", padx=20)
        ctk.CTkLabel(form.current_section, text=f"Outstanding: {Formatters.format_currency(outstanding)}", font=("Arial", 12, "bold"), text_color="red").grid(row=form.current_row, column=1, sticky="e", padx=20)
        form.current_row += 1

        date_entry = SmartDateEntry(form.current_section)
        amount_entry = SmartNumberEntry(form.current_section, required=True)
        amount_entry.insert(0, str(outstanding))

        form.add_field_pair("Payment Date:", date_entry, "Amount:", amount_entry)

        method_combo = SmartComboBox(form.current_section, values=["Cash", "Bank Transfer", "Cheque", "UPI", "Credit Card"], allow_custom=True)
        method_combo.set("Bank Transfer")
        
        ref_entry = SmartEntry(form.current_section, placeholder_text="Cheque No / Transaction ID")

        form.add_field_pair("Payment Method:", method_combo, "Reference No:", ref_entry)

        notes_entry = SmartEntry(form.current_section, placeholder_text="Notes")
        form.add_field_pair("Notes:", notes_entry, "", None)

        def on_save(values):
            try:
                amount = float(amount_entry.get().replace(',', ''))
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
                return

            if amount <= 0:
                messagebox.showerror("Error", "Amount must be greater than 0")
                return
            
            if amount > outstanding:
                if not messagebox.askyesno("Warning", "Amount exceeds outstanding balance. Continue?"):
                    return

            # Update record
            record_data['amount_paid'] = paid + amount
            
            # Save to DB
            if is_receivable:
                self.db.save_json(self.company_name, "invoices.json", self.invoices)
            else:
                self.db.save_json(self.company_name, "expenses.json", self.expenses)

            messagebox.showinfo("Success", "Payment recorded successfully!")
            dialog.destroy()
            self.load_payments()

        form.save_btn.configure(command=lambda: on_save(None))

    def aging_report_receivables(self):
        """Show aging report"""
        messagebox.showinfo("Report", "Aging report generation coming soon!")

    def due_date_report_payables(self):
        """Show due date report"""
        messagebox.showinfo("Report", "Due date report generation coming soon!")
