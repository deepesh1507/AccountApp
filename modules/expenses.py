"""
Expenses Management Module
Features: Add/Edit/Delete expenses, search, export.
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from typing import Dict, Any, Optional

from .base_module import BaseModule


class ExpensesManagement(BaseModule):
    def __init__(self, root, company_data, user_data, app_controller):
        super().__init__(root, company_data, user_data, app_controller)
        self.company_name = self.company_data.get('company_name', '')

        self.expenses = []
        self.filtered = []

        self.root.title(f"Expenses - {self.company_name}")
        # setup_ui is called by BaseModule
        self.load_expenses()

    def setup_ui(self):
        for w in self.root.winfo_children():
            w.destroy()
        main = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main.pack(fill="both", expand=True)

        header = ctk.CTkFrame(main, fg_color="#c62828", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        title = ctk.CTkLabel(header, text="💰 Expenses", font=ctk.CTkFont(size=22, weight="bold"), text_color="white")
        title.pack(side="left", padx=30, pady=15)

        nav = ctk.CTkFrame(header, fg_color="transparent")
        nav.pack(side="right", padx=20)
        add = ctk.CTkButton(nav, text="+ Add Expense", width=140, fg_color="#2e7d32", command=self.show_add_form)
        add.pack(side="left", padx=5)
        back = ctk.CTkButton(nav, text="← Back", width=100, fg_color="#0d47a1", command=self.go_back)
        back.pack(side="left", padx=5)

        content = ctk.CTkFrame(main, fg_color=("white", "gray20"))
        content.pack(fill="both", expand=True, padx=20, pady=20)
        toolbar = ctk.CTkFrame(content, fg_color="#ffe0b2", corner_radius=8)
        toolbar.pack(fill="x", padx=10, pady=8)
        self.search_entry = ctk.CTkEntry(toolbar, placeholder_text="Search by payee or note...", width=320)
        self.search_entry.pack(side="left", padx=8)
        self.search_entry.bind("<KeyRelease>", self.search)
        refresh = ctk.CTkButton(toolbar, text="↻ Refresh", command=self.load_expenses)
        refresh.pack(side="left", padx=8)
        self.count_label = ctk.CTkLabel(toolbar, text="Total: 0", font=ctk.CTkFont(size=12, weight="bold"))
        self.count_label.pack(side="right", padx=12)

        table_frame = ctk.CTkFrame(content, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=34, font=("Arial", 11))
        scroll = ctk.CTkScrollbar(table_frame)
        scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(table_frame, columns=("ID","Payee","Date","Amount","Category","Note"), show="headings", yscrollcommand=scroll.set)
        scroll.configure(command=self.tree.yview)
        for h in ("ID","Payee","Date","Amount","Category","Note"):
            self.tree.heading(h, text=h)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self.view_expense())

        action = ctk.CTkFrame(content, fg_color="transparent")
        action.pack(fill="x", padx=10, pady=(5,10))
        view = ctk.CTkButton(action, text="View", command=lambda: self.view_expense())
        view.pack(side="left", padx=5)
        edit = ctk.CTkButton(action, text="Edit", command=self.edit_expense)
        edit.pack(side="left", padx=5)
        delete = ctk.CTkButton(action, text="Delete", command=self.delete_expense)
        delete.pack(side="left", padx=5)
        export = ctk.CTkButton(action, text="Export CSV", fg_color="#7b1fa2", command=self.export_expenses)
        export.pack(side="left", padx=5)

    def load_expenses(self):
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            data = db.load_json(self.company_name, "expenses.json")
            self.expenses = data if isinstance(data,list) else []
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
                ex.get('expense_id',''),
                ex.get('payee',''),
                ex.get('date','')[:10],
                f"{self.company_data.get('currency','INR')} {ex.get('amount',0):,.2f}",
                ex.get('category',''),
                ex.get('note','')[:40]
            ))

    def update_count(self):
        self.count_label.configure(text=f"Total: {len(self.filtered)}")


    def search(self, event=None):
        """Search expenses with debouncing for better performance"""
        # Cancel previous search timer if exists
        if hasattr(self, '_search_timer') and self._search_timer:
            self.root.after_cancel(self._search_timer)
        
        # Schedule search after 300ms delay
        self._search_timer = self.root.after(300, self._do_search)
    
    def _do_search(self):
        """Actual search implementation"""
        term = self.search_entry.get().lower().strip()
        if not term:
            self.filtered = self.expenses.copy()
        else:
            self.filtered = [e for e in self.expenses if term in e.get('payee','').lower() or term in e.get('note','').lower()]
        self.display()
        self.update_count()

    def get_selected(self) -> Optional[Dict[str, Any]]:
        """Returns the data for the selected expense in the tree."""
        sel = self.tree.selection()
        if not sel:
            return None
        expense_id = self.tree.item(sel[0])['values'][0]
        return next((ex for ex in self.expenses if ex.get('expense_id') == expense_id), None)

    def view_expense(self, expense_data: Optional[Dict[str, Any]] = None) -> None:
        """Shows a read-only view of the selected expense."""
        ex = expense_data or self.get_selected()
        if not ex:
            messagebox.showwarning("Warning", "Please select an expense to view.")
            return
        
        # For simplicity, we reuse the form in a disabled state.
        # A dedicated view dialog would be better for a production app.
        self.show_expense_form(ex, read_only=True)

    def edit_expense(self):
        ex = self.get_selected()
        if not ex:
            messagebox.showwarning("Warning","Please select an expense to edit")
            return
        self.show_expense_form(ex, read_only=False)
    
    def show_add_form(self):
        self.show_expense_form(None)

    def show_expense_form(self, expense_data: Optional[Dict[str, Any]], read_only: bool = False):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Edit Expense" if expense_data else "Add Expense")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()
        frm = ctk.CTkScrollableFrame(dialog, fg_color=("white", "gray20"))
        frm.pack(fill="both", expand=True, padx=15, pady=15)

        # Widgets
        ctk.CTkLabel(frm, text="Payee:").pack(anchor="w", pady=(5,0))
        payee_entry = ctk.CTkEntry(frm, width=400)
        payee_entry.pack(pady=(0,5))

        ctk.CTkLabel(frm, text="Date (YYYY-MM-DD):").pack(anchor="w", pady=(5,0))
        date_entry = ctk.CTkEntry(frm, width=200)
        date_entry.pack(pady=(0,5))

        ctk.CTkLabel(frm, text="Amount:").pack(anchor="w", pady=(5,0))
        amount_entry = ctk.CTkEntry(frm, width=200)
        amount_entry.pack(pady=(0,5))

        ctk.CTkLabel(frm, text="Category:").pack(anchor="w", pady=(5,0))
        category_entry = ctk.CTkEntry(frm, width=300)
        category_entry.pack(pady=(0,5))

        ctk.CTkLabel(frm, text="Note:").pack(anchor="w", pady=(5,0))
        note_textbox = ctk.CTkTextbox(frm, width=420, height=120)
        note_textbox.pack(pady=(0,5))

        original_expense_id = None
        if expense_data:
            original_expense_id = expense_data.get('expense_id')
            payee_entry.insert(0, expense_data.get('payee', ''))
            date_entry.insert(0, expense_data.get('date', '')[:10])
            amount_entry.insert(0, str(expense_data.get('amount', 0.0)))
            category_entry.insert(0, expense_data.get('category', ''))
            note_textbox.insert("1.0", expense_data.get('note', ''))
        else:
            date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
            amount_entry.insert(0, "0.00")

        if read_only:
            dialog.title("View Expense")
            # Disable all entry widgets
            for widget in [payee_entry, date_entry, amount_entry, category_entry, note_textbox]:
                if isinstance(widget, (ctk.CTkEntry, ctk.CTkTextbox)):
                    widget.configure(state="disabled")
            # Hide save button, show only a close button
            ctk.CTkButton(frm, text="✕ Close", fg_color="#c62828", command=dialog.destroy).pack(pady=10)
            return

        def save_it():
            try:
                amount_val = float(amount_entry.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Invalid amount. Please enter a number.")
                return
            
            # Simple date validation (YYYY-MM-DD)
            try:
                datetime.strptime(date_entry.get().strip(), "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
                return

            new_expense_data = {
                'payee': payee_entry.get().strip(),
                'date': date_entry.get().strip(),
                'amount': amount_val,
                'category': category_entry.get().strip(),
                'note': note_textbox.get("1.0", "end-1c").strip(),
            }
            
            try:
                from .database_manager import DatabaseManager
                db = DatabaseManager()

                if original_expense_id: # Editing existing expense
                    if expense_data: # Ensure expense_data is not None
                        new_expense_data['expense_id'] = original_expense_id
                        new_expense_data['created_date'] = expense_data.get('created_date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        new_expense_data['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # This branch should not be reachable if expense_data is None, but the check adds safety.
                    
                    for i, exp in enumerate(self.expenses):
                        if exp.get('expense_id') == original_expense_id:
                            self.expenses[i] = new_expense_data
                            break
                    messagebox.showinfo("Success", "Expense updated successfully!")
                else: # Adding new expense
                    new_expense_data['expense_id'] = f"EXP{len(self.expenses)+1:05d}"
                    new_expense_data['created_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.expenses.append(new_expense_data)
                    messagebox.showinfo("Success", "Expense added successfully!")

                db.save_json(self.company_name, "expenses.json", self.expenses)
                dialog.destroy()
                self.load_expenses()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save expense:\n{e}")

        save_button = ctk.CTkButton(frm, text="✓ Save", fg_color="#2e7d32", command=save_it)
        save_button.pack(pady=10)
        cancel_button = ctk.CTkButton(frm, text="✕ Cancel", fg_color="#c62828", command=dialog.destroy)
        cancel_button.pack(pady=5)

    def delete_expense(self):
        ex = self.get_selected()
        if not ex:
            messagebox.showwarning("Warning","Please select an expense to delete")
            return
        if not messagebox.askyesno("Delete","Delete selected expense?"): return
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            self.expenses = [e for e in self.expenses if e.get('expense_id')!=ex.get('expense_id')]
            db.save_json(self.company_name, "expenses.json", self.expenses)
            messagebox.showinfo("Success","Expense deleted")
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
        """Navigate back to the dashboard."""
        if self.app:
            self.app.show_dashboard(self.company_data, self.user_data)
