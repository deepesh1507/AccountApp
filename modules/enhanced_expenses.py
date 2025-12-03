"""
Enhanced Expenses Management Module
Professional expense tracking with improved UI/UX
Features: Smart forms, keyboard shortcuts, real-time validation, auto-save
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from .base_module import BaseModule
from .smart_widgets import (
    SmartEntry, SmartNumberEntry, SmartDateEntry, SmartComboBox,
    ValidationLabel, validate_required
)
from .enhanced_form import EnhancedForm


class EnhancedExpensesManagement(BaseModule):
    def __init__(self, root, company_data, user_data, app_controller):
        super().__init__(root, company_data, user_data, app_controller)
        self.company_name = self.company_data.get('company_name', '')

        self.expenses = []
        self.filtered = []
        
        # Expense categories
        self.categories = [
            "Office Supplies",
            "Travel",
            "Utilities",
            "Rent",
            "Salaries",
            "Marketing",
            "Equipment",
            "Professional Fees",
            "Insurance",
            "Maintenance",
            "Other"
        ]

        self.root.title(f"Expenses - {self.company_name}")
        self.load_expenses()

    def setup_ui(self):
        for w in self.root.winfo_children():
            w.destroy()
        
        main = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(main, fg_color="#c62828", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(
            header,
            text="💰 Expenses Management",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        )
        title.pack(side="left", padx=30, pady=15)

        # Navigation buttons
        nav = ctk.CTkFrame(header, fg_color="transparent")
        nav.pack(side="right", padx=20)
        
        add_btn = ctk.CTkButton(
            nav,
            text="➕ Add Expense (Ctrl+N)",
            width=180,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            command=self.show_add_form,
            font=("Arial", 13, "bold")
        )
        add_btn.pack(side="left", padx=5)
        
        back_btn = ctk.CTkButton(
            nav,
            text="⬅️ Back",
            width=100,
            fg_color="#0d47a1",
            hover_color="#01579b",
            command=self.go_back
        )
        back_btn.pack(side="left", padx=5)

        # Content area
        content = ctk.CTkFrame(main, fg_color=("white", "gray20"))
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Toolbar
        toolbar = ctk.CTkFrame(content, fg_color=("#e3f2fd", "#1e3a5f"), corner_radius=8)
        toolbar.pack(fill="x", padx=10, pady=8)
        
        # Search
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="left", padx=10, pady=8)
        
        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=("Arial", 16)
        ).pack(side="left", padx=(0, 5))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search by payee or note... (F3)",
            width=320
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.search)
        
        # Filter by category
        ctk.CTkLabel(
            toolbar,
            text="Category:",
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=(20, 5))
        
        self.category_filter = ctk.CTkComboBox(
            toolbar,
            values=["All"] + self.categories,
            width=150,
            command=self.filter_by_category
        )
        self.category_filter.set("All")
        self.category_filter.pack(side="left", padx=5)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            toolbar,
            text="🔄 Refresh (F5)",
            command=self.load_expenses,
            width=120
        )
        refresh_btn.pack(side="left", padx=10)
        
        # Count label
        self.count_label = ctk.CTkLabel(
            toolbar,
            text="Total: 0 | Amount: ₹0.00",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.count_label.pack(side="right", padx=12)

        # Table
        table_frame = ctk.CTkFrame(content, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=36, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
        
        scroll = ctk.CTkScrollbar(table_frame)
        scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Date", "Payee", "Category", "Amount", "Note"),
            show="headings",
            yscrollcommand=scroll.set
        )
        scroll.configure(command=self.tree.yview)
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Payee", text="Payee")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Note", text="Note")
        
        self.tree.column("ID", width=100)
        self.tree.column("Date", width=100)
        self.tree.column("Payee", width=200)
        self.tree.column("Category", width=150)
        self.tree.column("Amount", width=120)
        self.tree.column("Note", width=300)
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self.view_expense())

        # Action buttons
        action = ctk.CTkFrame(content, fg_color="transparent")
        action.pack(fill="x", padx=10, pady=(5, 10))
        
        view_btn = ctk.CTkButton(
            action,
            text="👁️ View",
            command=self.view_expense,
            width=100
        )
        view_btn.pack(side="left", padx=5)
        
        edit_btn = ctk.CTkButton(
            action,
            text="✏️ Edit",
            command=self.edit_expense,
            fg_color="#1976d2",
            width=100
        )
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            action,
            text="🗑️ Delete",
            command=self.delete_expense,
            fg_color="#c62828",
            width=100
        )
        delete_btn.pack(side="left", padx=5)
        
        export_btn = ctk.CTkButton(
            action,
            text="📊 Export CSV",
            fg_color="#7b1fa2",
            command=self.export_expenses,
            width=130
        )
        export_btn.pack(side="left", padx=5)
        
        # Bind keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.show_add_form())
        self.root.bind("<F3>", lambda e: self.search_entry.focus())
        self.root.bind("<F5>", lambda e: self.load_expenses())

    def load_expenses(self):
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            data = db.load_json(self.company_name, "expenses.json")
            self.expenses = data if isinstance(data, list) else []
            self.filtered = self.expenses.copy()
            self.display()
            self.update_count()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expenses:\n{e}")

    def display(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        for ex in self.filtered:
            self.tree.insert("", "end", values=(
                ex.get('expense_id', ''),
                ex.get('date', '')[:10],
                ex.get('payee', ''),
                ex.get('category', ''),
                f"₹{ex.get('amount', 0):,.2f}",
                ex.get('note', '')[:50]
            ))

    def update_count(self):
        total_amount = sum(ex.get('amount', 0) for ex in self.filtered)
        self.count_label.configure(
            text=f"Total: {len(self.filtered)} | Amount: ₹{total_amount:,.2f}"
        )

    def search(self, event=None):
        term = self.search_entry.get().lower().strip()
        category = self.category_filter.get()
        
        if not term and category == "All":
            self.filtered = self.expenses.copy()
        else:
            self.filtered = []
            for e in self.expenses:
                # Search filter
                matches_search = (not term or 
                                term in e.get('payee', '').lower() or 
                                term in e.get('note', '').lower())
                
                # Category filter
                matches_category = (category == "All" or 
                                  e.get('category', '') == category)
                
                if matches_search and matches_category:
                    self.filtered.append(e)
        
        self.display()
        self.update_count()
    
    def filter_by_category(self, event=None):
        self.search()

    def get_selected(self) -> Optional[Dict[str, Any]]:
        sel = self.tree.selection()
        if not sel:
            return None
        expense_id = self.tree.item(sel[0])['values'][0]
        return next((ex for ex in self.expenses if ex.get('expense_id') == expense_id), None)

    def show_add_form(self):
        self.show_expense_form(None)

    def view_expense(self):
        ex = self.get_selected()
        if not ex:
            messagebox.showwarning("Warning", "Please select an expense to view")
            return
        self.show_expense_form(ex, read_only=True)

    def edit_expense(self):
        ex = self.get_selected()
        if not ex:
            messagebox.showwarning("Warning", "Please select an expense to edit")
            return
        self.show_expense_form(ex)

    def show_expense_form(self, expense_data: Optional[Dict[str, Any]], read_only: bool = False):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("View Expense" if read_only else ("Edit Expense" if expense_data else "New Expense"))
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()

        def on_save(values):
            self._save_expense(values, expense_data, dialog)

        def on_cancel():
            dialog.destroy()

        form = EnhancedForm(
            dialog,
            title="View Expense" if read_only else ("Edit Expense" if expense_data else "New Expense"),
            on_save=on_save,
            on_cancel=on_cancel,
            auto_save=not read_only
        )
        form.pack(fill="both", expand=True)

        form.add_section("💰 Expense Details")

        # Payee
        payee_entry = SmartEntry(form.current_section, required=True, placeholder_text="Payee Name")
        if expense_data: payee_entry.insert(0, expense_data.get('payee', ''))
        form.add_field_pair("Payee:", payee_entry, "", None)

        # Date
        from .smart_widgets import SmartDateEntry
        date_entry = SmartDateEntry(form.current_section)
        if expense_data: date_entry.set_date(expense_data.get('date', datetime.now().strftime("%Y-%m-%d")))
        form.add_field_pair("Date:", date_entry, "", None)

        # Category
        categories = ["Office Supplies", "Travel", "Utilities", "Rent", "Salaries", "Maintenance", "Other"]
        cat_combo = SmartComboBox(form.current_section, values=categories)
        cat_combo.set(expense_data.get('category', 'Office Supplies') if expense_data else 'Office Supplies')
        
        # Amount
        amount_entry = SmartNumberEntry(form.current_section, placeholder_text="0.00")
        if expense_data: amount_entry.insert(0, str(expense_data.get('amount', '')))
        
        form.add_field_pair("Category:", cat_combo, "Amount:", amount_entry)

        # Note
        note_entry = ctk.CTkEntry(form.current_section, width=400)
        if expense_data: note_entry.insert(0, expense_data.get('note', ''))
        form.add_field_pair("Note:", note_entry, "", None)

        if read_only:
            form.save_btn.configure(state="disabled")
            payee_entry.configure(state="disabled")
            date_entry.entry.configure(state="disabled")
            cat_combo.configure(state="disabled")
            amount_entry.configure(state="disabled")
            note_entry.configure(state="disabled")

    def _save_expense(self, values, existing_expense, dialog):
        payee = values.get('payee', '').strip()
        date_str = values.get('date', '')
        category = values.get('category', '')
        amount_str = values.get('amount', '')
        note = values.get('note', '').strip()

        if not payee:
            messagebox.showerror("Error", "Payee is required")
            return
        
        if not amount_str:
            messagebox.showerror("Error", "Amount is required")
            return
        
        # Parse amount
        try:
            amount = float(amount_str.replace(',', ''))
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        
        # Validate date
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
            return
        
        # Prepare expense data
        expense_record = {
            'payee': payee,
            'date': date_str,
            'amount': amount,
            'category': category,
            'note': note
        }
        
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            
            if existing_expense:
                # Update existing
                expense_record['expense_id'] = existing_expense.get('expense_id')
                expense_record['created_date'] = existing_expense.get('created_date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                expense_record['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                for i, exp in enumerate(self.expenses):
                    if exp.get('expense_id') == existing_expense.get('expense_id'):
                        self.expenses[i] = expense_record
                        break
                
                messagebox.showinfo("Success", "Expense updated successfully!")
            else:
                # Create new
                expense_record['expense_id'] = f"EXP{len(self.expenses) + 1:05d}"
                expense_record['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.expenses.append(expense_record)
                messagebox.showinfo("Success", "Expense added successfully!")
            
            db.save_json(self.company_name, "expenses.json", self.expenses)
            dialog.destroy()
            self.load_expenses()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save expense:\n{e}")

    def delete_expense(self):
        ex = self.get_selected()
        if not ex:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return
        
        if not messagebox.askyesno("Delete", f"Delete expense '{ex.get('payee')}'?"):
            return
        
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            self.expenses = [e for e in self.expenses if e.get('expense_id') != ex.get('expense_id')]
            db.save_json(self.company_name, "expenses.json", self.expenses)
            messagebox.showinfo("Success", "Expense deleted")
            self.load_expenses()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete expense:\n{e}")

    def export_expenses(self):
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            path = db.export_to_csv(self.company_name, "expenses.json")
            if path:
                messagebox.showinfo("Success", f"Expenses exported to:\n{path}")
            else:
                messagebox.showwarning("Warning", "No expenses to export")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{e}")

    def go_back(self):
        if self.app:
            self.app.show_dashboard(self.company_data, self.user_data)
