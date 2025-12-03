"""
Journal Entries Module
Complete double-entry bookkeeping system with Enhanced UI
Features: Create, Edit, View, Delete journal vouchers with real-time validation
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading

from .base_module import BaseModule
from .smart_widgets import (
    SmartEntry, SmartNumberEntry, SmartDateEntry, SmartComboBox,
    ValidationLabel
)
from .enhanced_form import EnhancedForm
from .performance_optimizer import debounce_search, run_async, show_loading_overlay, hide_loading_overlay, PerformanceOptimizer
from .utilities import Formatters, IDGenerator

class JournalEntries(BaseModule):
    def __init__(self, root, company_data, user_data, app_controller):
        super().__init__(root, company_data, user_data, app_controller)
        self.company_name = company_data.get("company_name", "")
        self.entries = []
        self.filtered_entries = []
        self.accounts = []
        self.loading_overlay = None
        
        self.root.title(f"Journal Entries - {self.company_name}")
        self.load_data()

    def setup_ui(self):
        for w in self.root.winfo_children():
            w.destroy()

        main_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main_frame.pack(fill="both", expand=True)

        # --- Header ---
        header = ctk.CTkFrame(main_frame, fg_color="#1976d2", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="📝 Journal Entries",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=30, pady=18)

        # Navigation
        nav = ctk.CTkFrame(header, fg_color="transparent")
        nav.pack(side="right", padx=20)

        ctk.CTkButton(
            nav,
            text="← Back",
            width=120,
            height=35,
            fg_color="#0d47a1",
            hover_color="#01579b",
            command=self.go_back
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            nav,
            text="+ New Entry",
            width=150,
            height=35,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            command=self.create_entry
        ).pack(side="left", padx=5)

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
            placeholder_text="Search by Voucher No or Narration... (F3)",
            width=300,
            height=35
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.search_entries)

        # Filter
        self.type_filter = ctk.CTkComboBox(
            toolbar,
            values=["All Types", "Journal", "Payment", "Receipt", "Contra"],
            width=150,
            height=35,
            command=self.filter_entries
        )
        self.type_filter.set("All Types")
        self.type_filter.pack(side="left", padx=10)

        refresh = ctk.CTkButton(
            toolbar,
            text="↻ Refresh (F5)",
            width=100,
            height=35,
            fg_color="#1976d2",
            command=self.load_entries
        )
        refresh.pack(side="left", padx=10)

        self.count_label = ctk.CTkLabel(
            toolbar,
            text="Total: 0 entries",
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

        columns = ("Entry No", "Date", "Type", "Amount", "Narration")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scroll.set
        )
        scroll.configure(command=self.tree.yview)

        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("Entry No", width=120)
        self.tree.column("Date", width=120)
        self.tree.column("Type", width=100)
        self.tree.column("Amount", width=150, anchor="e")
        self.tree.column("Narration", width=400)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self.view_entry())

        # Actions
        action = ctk.CTkFrame(content, fg_color="transparent")
        action.pack(fill="x", padx=10, pady=(5,10))
        
        ctk.CTkButton(action, text="👁️ View", width=100, command=self.view_entry).pack(side="left", padx=5)
        ctk.CTkButton(action, text="✏️ Edit", width=100, command=self.edit_entry, fg_color="#1976d2").pack(side="left", padx=5)
        ctk.CTkButton(action, text="🗑️ Delete", width=100, command=self.delete_entry, fg_color="#c62828").pack(side="left", padx=5)
        ctk.CTkButton(action, text="📊 Export CSV", width=120, fg_color="#7b1fa2", command=self.export_entries).pack(side="left", padx=5)

        # Shortcuts
        self.root.bind("<Control-n>", lambda e: self.create_entry())
        self.root.bind("<F3>", lambda e: self.search_entry.focus())
        self.root.bind("<F5>", lambda e: self.load_entries())

    def load_data(self):
        self.loading_overlay = show_loading_overlay(self.root, "Loading data...")
        run_async(self._fetch_data)

    def _fetch_data(self):
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            
            # Load accounts
            acc_data = db.load_json(self.company_name, "accounts.json")
            accounts = acc_data if isinstance(acc_data, list) else []
            
            # Load entries
            ent_data = db.load_json(self.company_name, "journal_entries.json")
            entries = ent_data if isinstance(ent_data, list) else []
            
            self.root.after(0, lambda: self._update_ui_after_load(accounts, entries))
        except Exception as e:
            self.root.after(0, lambda: self._handle_load_error(e))

    def _handle_load_error(self, error):
        hide_loading_overlay(self.loading_overlay)
        messagebox.showerror("Error", f"Failed to load data:\n{error}")

    def _update_ui_after_load(self, accounts, entries):
        self.accounts = accounts
        self.entries = entries
        self.filtered_entries = self.entries.copy()
        self.display_entries()
        self.update_count()
        hide_loading_overlay(self.loading_overlay)

    def load_entries(self):
        """Reload just entries"""
        self.load_data()

    def display_entries(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        items_to_insert = []
        for entry in self.filtered_entries:
            total = sum(line.get("debit", 0) for line in entry.get("lines", []))
            items_to_insert.append((
                entry.get("entry_id", ""),
                (entry.get("date") or "")[:10],
                entry.get("type", ""),
                f"{self.company_data.get('currency', 'INR')} {total:,.2f}",
                entry.get("narration", "")
            ))
            
        PerformanceOptimizer.batch_insert(self.tree, items_to_insert)

    def update_count(self):
        total = len(self.entries)
        filtered = len(self.filtered_entries)
        self.count_label.configure(text=f"Total: {filtered} entries")

    @debounce_search(300)
    def search_entries(self, event=None):
        term = self.search_entry.get().lower().strip()
        self._apply_filters(term)

    def filter_entries(self, event=None):
        term = self.search_entry.get().lower().strip()
        self._apply_filters(term)

    def _apply_filters(self, term):
        entry_type = self.type_filter.get()
        
        filtered = self.entries
        
        # Apply type filter
        if entry_type != "All Types":
            filtered = [e for e in filtered if e.get("type") == entry_type]
            
        # Apply search term
        if term:
            filtered = [
                e for e in filtered 
                if term in e.get("entry_id", "").lower() or 
                   term in e.get("narration", "").lower()
            ]
            
        self.filtered_entries = filtered
        self.display_entries()
        self.update_count()

    def get_selected_entry(self) -> Optional[Dict[str, Any]]:
        sel = self.tree.selection()
        if not sel:
            return None
        entry_id = self.tree.item(sel[0])['values'][0]
        return next((e for e in self.entries if e.get("entry_id") == entry_id), None)

    def create_entry(self):
        self.show_entry_form(None)

    def view_entry(self):
        entry = self.get_selected_entry()
        if not entry:
            messagebox.showwarning("Warning", "Please select an entry to view.")
            return
        self.show_entry_form(entry, read_only=True)

    def edit_entry(self):
        entry = self.get_selected_entry()
        if not entry:
            messagebox.showwarning("Warning", "Please select an entry to edit")
            return
        self.show_entry_form(entry)

    def show_entry_form(self, entry_data: Optional[Dict[str, Any]], read_only: bool = False):
        try:
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("View Entry" if read_only else ("Edit Entry" if entry_data else "New Journal Entry"))
            dialog.geometry("1000x800")
            dialog.transient(self.root)
            
            # Ensure dialog is visible and centered
            from .enhanced_form import EnhancedForm
            EnhancedForm.ensure_dialog_visible(dialog, self.root)

            # Current lines for this session
            current_lines = entry_data.get('lines', []).copy() if entry_data else []
            if not current_lines and not read_only:
                # Start with 2 empty lines for new entry
                current_lines = [{}, {}]

            def on_save(values):
                self._save_entry(values, current_lines, entry_data, dialog)

            def on_cancel():
                dialog.destroy()

            form = EnhancedForm(
                dialog,
                title="View Entry" if read_only else ("Edit Entry" if entry_data else "New Entry"),
                on_save=on_save,
                on_cancel=on_cancel,
                auto_save=not read_only
            )
            form.pack(fill="both", expand=True)

            # --- Section 1: Header ---
            form.add_section("📋 Entry Details")

            # Entry ID
            entry_id_val = entry_data.get('entry_id', '') if entry_data else IDGenerator.generate_voucher_number(self.entries[-1].get('entry_id') if self.entries else None)
            id_entry = SmartEntry(form.current_section, required=True)
            id_entry.insert(0, entry_id_val)
            if entry_data:
                id_entry.configure(state="disabled")

            # Date
            date_picker = SmartDateEntry(form.current_section)
            if entry_data:
                date_picker.entry.delete(0, "end")
                date_picker.entry.insert(0, entry_data.get('date', '')[:10])

            form.add_field_pair(
                "Entry No:", id_entry,
                "Date:", date_picker,
                help_text1="Auto-generated ID",
                help_text2="Transaction Date"
            )

            # Type and Narration
            type_combo = SmartComboBox(
                form.current_section,
                values=["Journal", "Payment", "Receipt", "Contra"],
                allow_custom=False
            )
            type_combo.set(entry_data.get('type', 'Journal') if entry_data else 'Journal')

            narration_entry = SmartEntry(form.current_section, width=400, placeholder_text="Enter narration")
            if entry_data:
                narration_entry.insert(0, entry_data.get('narration', ''))

            form.add_field_pair(
                "Entry Type:", type_combo,
                "Narration:", narration_entry,
                help_text1="Voucher Type",
                help_text2="Description of transaction"
            )

            # --- Section 2: Line Items ---
            lines_section = form.add_section("💰 Debit & Credit Lines")
            
            # Custom frame for lines
            lines_frame = ctk.CTkScrollableFrame(lines_section, height=300, fg_color=("white", "gray15"))
            lines_frame.pack(fill="both", expand=True, padx=15, pady=5)

            # Totals Display
            totals_frame = ctk.CTkFrame(lines_section, fg_color="#e8f5e9", corner_radius=5)
            totals_frame.pack(fill="x", padx=15, pady=10)
            
            lbl_debit = ctk.CTkLabel(totals_frame, text="Total Debit: 0.00", font=("Arial", 12, "bold"))
            lbl_debit.pack(side="left", padx=20, pady=5)
            
            lbl_credit = ctk.CTkLabel(totals_frame, text="Total Credit: 0.00", font=("Arial", 12, "bold"))
            lbl_credit.pack(side="left", padx=20, pady=5)
            
            lbl_diff = ctk.CTkLabel(totals_frame, text="Difference: 0.00", font=("Arial", 12, "bold"))
            lbl_diff.pack(side="right", padx=20, pady=5)

            # Account options
            account_options = [f"{acc.get('code')} - {acc.get('name')}" for acc in self.accounts]

            line_widgets = []

            def update_totals(*args):
                total_d = 0.0
                total_c = 0.0
                
                for w in line_widgets:
                    try:
                        d = float(w['debit'].get().replace(',', '') or 0)
                        c = float(w['credit'].get().replace(',', '') or 0)
                        total_d += d
                        total_c += c
                    except ValueError:
                        pass
                
                lbl_debit.configure(text=f"Total Debit: {total_d:,.2f}")
                lbl_credit.configure(text=f"Total Credit: {total_c:,.2f}")
                
                diff = total_d - total_c
                lbl_diff.configure(
                    text=f"Difference: {abs(diff):,.2f}",
                    text_color="green" if abs(diff) < 0.01 else "red"
                )

            def add_line_row(line_data=None):
                row = ctk.CTkFrame(lines_frame, fg_color="transparent")
                row.pack(fill="x", pady=2)
                
                # Account
                acc_combo = SmartComboBox(row, values=account_options, width=300)
                acc_combo.pack(side="left", padx=5)
                if line_data and line_data.get('account_code'):
                    # Find matching option
                    code = line_data.get('account_code')
                    match = next((opt for opt in account_options if opt.startswith(code)), None)
                    if match:
                        acc_combo.set(match)
                
                # Debit
                debit_entry = SmartNumberEntry(row, width=120, placeholder_text="Debit")
                debit_entry.pack(side="left", padx=5)
                if line_data:
                    debit_entry.insert(0, str(line_data.get('debit', 0)))
                
                # Credit
                credit_entry = SmartNumberEntry(row, width=120, placeholder_text="Credit")
                credit_entry.pack(side="left", padx=5)
                if line_data:
                    credit_entry.insert(0, str(line_data.get('credit', 0)))
                
                # Bind for totals
                debit_entry.bind("<KeyRelease>", update_totals)
                credit_entry.bind("<KeyRelease>", update_totals)
                
                # Delete button
                if not read_only:
                    del_btn = ctk.CTkButton(
                        row, text="✕", width=30, fg_color="#c62828",
                        command=lambda: remove_line(row)
                    )
                    del_btn.pack(side="left", padx=5)

                line_widgets.append({
                    'row': row,
                    'account': acc_combo,
                    'debit': debit_entry,
                    'credit': credit_entry
                })

            def remove_line(row_widget):
                for w in line_widgets:
                    if w['row'] == row_widget:
                        line_widgets.remove(w)
                        row_widget.destroy()
                        update_totals()
                        break

            # Populate lines
            for line in current_lines:
                add_line_row(line)
            
            update_totals()

            if not read_only:
                ctk.CTkButton(
                    lines_section, 
                    text="+ Add Line", 
                    command=lambda: add_line_row(),
                    fg_color="#2e7d32"
                ).pack(pady=10)

            # Disable fields if read-only
            if read_only:
                form.save_btn.configure(state="disabled")
                id_entry.configure(state="disabled")
                date_picker.entry.configure(state="disabled")
                type_combo.configure(state="disabled")
                narration_entry.configure(state="disabled")
                for w in line_widgets:
                    w['account'].configure(state="disabled")
                    w['debit'].configure(state="disabled")
                    w['credit'].configure(state="disabled")

            # Store references for save
            self._current_form_widgets = {
                'id': id_entry,
                'date': date_picker,
                'type': type_combo,
                'narration': narration_entry,
                'lines': line_widgets
            }
            
        except Exception as e:
            error_msg = f"Failed to create journal entry form: {e}"
            print(error_msg)
            messagebox.showerror("Form Error", error_msg)
            import traceback
            traceback.print_exc()

    def _save_entry(self, values, current_lines, existing_data, dialog):
        # Extract values manually from widgets since lines are dynamic
        widgets = self._current_form_widgets
        
        # Get values from the form dictionary (populated by EnhancedForm)
        # Keys are derived from labels: "Entry No:" -> "entry_no", "Date:" -> "date", etc.
        entry_id = values.get('entry_no', '').strip()
        date_str = values.get('date', '').strip()
        entry_type = values.get('entry_type', '').strip()
        narration = values.get('narration', '').strip()

        # Fallback to widgets if values are missing (just in case)
        if not entry_id: entry_id = widgets['id'].get().strip()
        if not date_str: date_str = widgets['date'].get_date()
        if not entry_type: entry_type = widgets['type'].get()
        if not narration: narration = widgets['narration'].get().strip()

        # Validation
        if not entry_id:
            messagebox.showerror("Error", "Entry ID is required")
            return
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format")
            return

        # Process lines
        lines = []
        total_debit = 0.0
        total_credit = 0.0
        
        for w in widgets['lines']:
            acc_text = w['account'].get()
            if not acc_text:
                continue
            
            acc_code = acc_text.split(" - ")[0].strip()
            try:
                debit = float(w['debit'].get().replace(',', '') or 0)
                credit = float(w['credit'].get().replace(',', '') or 0)
            except ValueError:
                messagebox.showerror("Error", "Invalid amount in lines")
                return
            
            if debit == 0 and credit == 0:
                continue
                
            lines.append({
                'account_code': acc_code,
                'debit': debit,
                'credit': credit
            })
            total_debit += debit
            total_credit += credit

        if len(lines) < 2:
            messagebox.showerror("Error", "At least two lines are required")
            return
            
        if abs(total_debit - total_credit) > 0.01:
            messagebox.showerror("Error", f"Debits ({total_debit:,.2f}) and Credits ({total_credit:,.2f}) must match")
            return

        # Build entry object
        entry = {
            'entry_id': entry_id,
            'date': date_str,
            'type': entry_type,
            'narration': narration,
            'lines': lines,
            'created_at': existing_data.get('created_at', datetime.now().isoformat()) if existing_data else datetime.now().isoformat(),
            'modified_at': datetime.now().isoformat()
        }

        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()

            if existing_data:
                for i, e in enumerate(self.entries):
                    if e.get('entry_id') == entry_id:
                        self.entries[i] = entry
                        break
                messagebox.showinfo("Success", "Entry updated")
            else:
                self.entries.append(entry)
                messagebox.showinfo("Success", "Entry created")

            db.save_json(self.company_name, "journal_entries.json", self.entries)
            dialog.destroy()
            self.load_entries()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save entry:\n{e}")

    def delete_entry(self):
        entry = self.get_selected_entry()
        if not entry:
            messagebox.showwarning("Warning", "Please select an entry to delete")
            return
        if messagebox.askyesno("Confirm", f"Delete entry {entry.get('entry_id')}?"):
            try:
                from .database_manager import DatabaseManager
                db = DatabaseManager()
                self.entries = [e for e in self.entries if e.get('entry_id') != entry.get('entry_id')]
                db.save_json(self.company_name, "journal_entries.json", self.entries)
                messagebox.showinfo("Success", "Entry deleted")
                self.load_entries()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete:\n{e}")

    def export_entries(self):
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            path = db.export_to_csv(self.company_name, "journal_entries.json")
            if path:
                messagebox.showinfo("Success", f"Exported to:\n{path}")
            else:
                messagebox.showwarning("Warning", "Nothing to export")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{e}")

    def go_back(self):
        if self.app:
            self.app.show_dashboard(self.company_data, self.user_data)
