"""
ERP Reporting Module
Provides Trial Balance, P&L, Balance Sheet, and other financial reports
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from .base_module import BaseModule
from .db_manager import get_db_manager
from datetime import datetime
import json


class ERPReports(BaseModule):
    """ERP Reporting Module"""
    
    def setup_ui(self):
        """Setup the reporting UI"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color=("gray95", "gray10"))
        self.main_frame.pack(fill="both", expand=True)

        # Header
        self.create_header()

        # Content Area
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Create menu
        self.create_menu()

    def create_header(self):
        """Create header with navigation"""
        header_frame = ctk.CTkFrame(self.main_frame, height=60, fg_color=("#1976d2", "#0d47a1"))
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # Back Button
        back_btn = ctk.CTkButton(
            header_frame,
            text="← Back",
            command=self.go_back,
            width=80,
            height=32,
            fg_color="transparent",
            border_width=1,
            border_color="white",
            text_color="white"
        )
        back_btn.pack(side="left", padx=(20, 10), pady=14)

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 ERP Reports & Analytics",
            font=("Arial", 20, "bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=10)

    def create_menu(self):
        """Create report menu"""
        menu_scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True)

        items = [
            ("📋 Trial Balance", self.show_trial_balance),
            ("💰 Profit & Loss Statement", self.show_pl_statement),
            ("📊 Balance Sheet", self.show_balance_sheet),
            ("💵 Cash Flow Statement", self.show_cash_flow),
            ("📈 Vendor Aging Report", self.show_vendor_aging),
            ("📉 Customer Aging Report", self.show_customer_aging),
            ("🔍 Transaction History", self.show_transaction_history),
            ("📁 Export Data", self.export_data)
        ]

        row = 0
        col = 0
        for title, command in items:
            btn = ctk.CTkButton(
                menu_scroll,
                text=title,
                command=command,
                height=60,
                font=("Arial", 14),
                fg_color=("white", "gray20"),
                text_color=("black", "white"),
                hover_color=("gray90", "gray30"),
                anchor="w"
            )
            btn.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            col += 1
            if col > 1:  # 2 columns
                col = 0
                row += 1

        menu_scroll.grid_columnconfigure(0, weight=1)
        menu_scroll.grid_columnconfigure(1, weight=1)

    def show_trial_balance(self):
        """Show trial balance report"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Title
        title = ctk.CTkLabel(
            self.content_frame,
            text="Trial Balance",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        # Date filters
        filter_frame = ctk.CTkFrame(self.content_frame)
        filter_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(filter_frame, text="From Date:").pack(side="left", padx=5)
        from_date = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD")
        from_date.pack(side="left", padx=5)

        ctk.CTkLabel(filter_frame, text="To Date:").pack(side="left", padx=5)
        to_date = ctk.CTkEntry(filter_frame, placeholder_text="YYYY-MM-DD")
        to_date.pack(side="left", padx=5)

        def generate_report():
            db = get_db_manager()
            data = db.get_trial_balance(from_date.get(), to_date.get())
            
            # Display results
            result_frame = ctk.CTkScrollableFrame(self.content_frame, height=400)
            result_frame.pack(fill="both", expand=True, padx=20, pady=10)

            if data:
                # Header
                header = f"{'Account':<15} {'Debit':>15} {'Credit':>15} {'Balance':>15}"
                ctk.CTkLabel(result_frame, text=header, font=("Courier", 12, "bold")).pack(anchor="w")
                
                total_debit = 0
                total_credit = 0
                
                for row in data:
                    account = row.get('account', 'N/A')
                    debit = float(row.get('total_debit', 0))
                    credit = float(row.get('total_credit', 0))
                    balance = float(row.get('balance', 0))
                    
                    total_debit += debit
                    total_credit += credit
                    
                    line = f"{account:<15} {debit:>15.2f} {credit:>15.2f} {balance:>15.2f}"
                    ctk.CTkLabel(result_frame, text=line, font=("Courier", 11)).pack(anchor="w")
                
                # Totals
                ctk.CTkLabel(result_frame, text="-" * 65, font=("Courier", 11)).pack(anchor="w")
                total_line = f"{'TOTAL':<15} {total_debit:>15.2f} {total_credit:>15.2f} {total_debit-total_credit:>15.2f}"
                ctk.CTkLabel(result_frame, text=total_line, font=("Courier", 12, "bold")).pack(anchor="w")
            else:
                ctk.CTkLabel(result_frame, text="No data found for the selected period").pack()

        ctk.CTkButton(filter_frame, text="Generate Report", command=generate_report).pack(side="left", padx=10)
        ctk.CTkButton(filter_frame, text="Back to Menu", command=self.create_menu).pack(side="left", padx=5)

    def show_pl_statement(self):
        """Show P&L statement"""
        messagebox.showinfo("Coming Soon", "Profit & Loss Statement will be available soon!")

    def show_balance_sheet(self):
        """Show balance sheet"""
        messagebox.showinfo("Coming Soon", "Balance Sheet will be available soon!")

    def show_cash_flow(self):
        """Show cash flow statement"""
        messagebox.showinfo("Coming Soon", "Cash Flow Statement will be available soon!")

    def show_vendor_aging(self):
        """Show vendor aging report"""
        messagebox.showinfo("Coming Soon", "Vendor Aging Report will be available soon!")

    def show_customer_aging(self):
        """Show customer aging report"""
        messagebox.showinfo("Coming Soon", "Customer Aging Report will be available soon!")

    def show_transaction_history(self):
        """Show transaction history"""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        title = ctk.CTkLabel(
            self.content_frame,
            text="Transaction History",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)

        # Get transactions
        db = get_db_manager()
        transactions = db.get_transactions()

        # Display
        result_frame = ctk.CTkScrollableFrame(self.content_frame, height=500)
        result_frame.pack(fill="both", expand=True, padx=20, pady=10)

        if transactions:
            for trans in transactions[:50]:  # Show last 50
                trans_text = f"ID: {trans['id']} | {trans['module']} | {trans['transaction_type']} | Amount: {trans['amount']} | Date: {trans['posting_date']}"
                ctk.CTkLabel(result_frame, text=trans_text, font=("Arial", 11)).pack(anchor="w", pady=2)
        else:
            ctk.CTkLabel(result_frame, text="No transactions found").pack()

        ctk.CTkButton(self.content_frame, text="Back to Menu", command=self.create_menu).pack(pady=10)

    def export_data(self):
        """Export data to file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            db = get_db_manager()
            transactions = db.get_transactions()
            
            with open(file_path, 'w') as f:
                json.dump(transactions, f, indent=2, default=str)
            
            messagebox.showinfo("Success", f"Data exported to {file_path}")

    def go_back(self):
        """Go back to dashboard"""
        self.app_controller.show_dashboard()
