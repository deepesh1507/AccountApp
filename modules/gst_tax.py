"""
GST and Tax Management Module
Features: Tax configuration, automatic calculation, GST reports
Supports: CGST, SGST, IGST, TDS
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from typing import Dict, Any, List
from .base_module import BaseModule
from .utilities import Validators, Formatters, Calculator


class GSTTaxManagement(BaseModule):
    def __init__(self, root, company_data, user_data, app_controller):
        self.company_name = company_data.get("company_name", "")
        self.tax_configs = []
        super().__init__(root, company_data, user_data, app_controller)

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main_frame.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(main_frame, fg_color="#f57c00", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header,
            text="📊 GST & Tax Management",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=30)

        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.pack(side="right", padx=20)

        ctk.CTkButton(nav_frame, text="← Back", command=self.go_back, width=100).pack(side="left", padx=5)
        ctk.CTkButton(nav_frame, text="🏠 Home", command=self.go_home, width=80).pack(side="left", padx=5)

        # Content
        content = ctk.CTkFrame(main_frame, fg_color=("white", "gray20"))
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Tax Configurations List
        config_label = ctk.CTkLabel(
            content,
            text="Tax Configurations",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        config_label.pack(pady=10)

        # Table
        table_frame = ctk.CTkFrame(content)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Tax Code", "Tax Name", "Type", "Rate %", "Status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Action buttons
        action_frame = ctk.CTkFrame(content, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            action_frame,
            text="+ Add Tax Config",
            command=self.add_tax_config,
            fg_color="#2e7d32",
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(action_frame, text="✏️ Edit", command=self.edit_tax_config, width=100).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Delete", command=self.delete_tax_config, fg_color="#c62828", width=100).pack(side="left", padx=5)

        # GST Reports Section
        reports_label = ctk.CTkLabel(
            content,
            text="GST Reports",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        reports_label.pack(pady=(30, 10))

        reports_frame = ctk.CTkFrame(content, fg_color="#e8f5e9", corner_radius=10)
        reports_frame.pack(fill="x", padx=10, pady=10)

        # Date range
        date_frame = ctk.CTkFrame(reports_frame, fg_color="transparent")
        date_frame.pack(pady=15)

        ctk.CTkLabel(date_frame, text="From:").pack(side="left", padx=5)
        self.from_date = ctk.CTkEntry(date_frame, width=120)
        self.from_date.insert(0, datetime.now().replace(day=1).strftime("%Y-%m-%d"))
        self.from_date.pack(side="left", padx=5)

        ctk.CTkLabel(date_frame, text="To:").pack(side="left", padx=5)
        self.to_date = ctk.CTkEntry(date_frame, width=120)
        self.to_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.to_date.pack(side="left",padx=5)

        # Report buttons
        report_btn_frame = ctk.CTkFrame(reports_frame, fg_color="transparent")
        report_btn_frame.pack(pady=10)

        ctk.CTkButton(
            report_btn_frame,
            text="📋 GSTR-1 (Sales)",
            command=self.generate_gstr1,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            report_btn_frame,
            text="📋 GSTR-3B Summary",
            command=self.generate_gstr3b,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            report_btn_frame,
            text="📊 Tax Summary",
            command=self.tax_summary,
            width=150
        ).pack(side="left", padx=5)

        self.load_tax_configs()

    def load_tax_configs(self):
        """Load tax configurations"""
        try:
            data = self.db.load_json(self.company_name, "tax_config.json")
            self.tax_configs = data if isinstance(data, list) else []
        except:
            # Create default tax configs
            self.tax_configs = [
                {
                    "tax_code": "GST18",
                    "tax_name": "GST @ 18%",
                    "tax_type": "GST",
                    "rate": 18,
                    "components": [
                        {"name": "CGST", "rate": 9},
                        {"name": "SGST", "rate": 9}
                    ],
                    "active": True
                },
                {
                    "tax_code": "GST12",
                    "tax_name": "GST @ 12%",
                    "tax_type": "GST",
                    "rate": 12,
                    "components": [
                        {"name": "CGST", "rate": 6},
                        {"name": "SGST", "rate": 6}
                    ],
                    "active": True
                },
                {
                    "tax_code": "GST5",
                    "tax_name": "GST @ 5%",
                    "tax_type": "GST",
                    "rate": 5,
                    "components": [
                        {"name": "CGST", "rate": 2.5},
                        {"name": "SGST", "rate": 2.5}
                    ],
                    "active": True
                },
                {
                    "tax_code": "TDS10",
                    "tax_name": "TDS @ 10%",
                    "tax_type": "TDS",
                    "rate": 10,
                    "components": [],
                    "active": True
                }
            ]
            self.db.save_json(self.company_name, "tax_config.json", self.tax_configs)

        self.display_configs()

    def display_configs(self):
        """Display tax configurations"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for config in self.tax_configs:
            self.tree.insert("", "end", values=(
                config.get("tax_code", ""),
                config.get("tax_name", ""),
                config.get("tax_type", ""),
                f"{config.get('rate', 0)}%",
                "Active" if config.get("active") else "Inactive"
            ))

    def add_tax_config(self):
        """Add new tax configuration"""
        self.show_tax_form("Add Tax Configuration", None)

    def edit_tax_config(self):
        """Edit selected tax configuration"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a tax configuration.")
            return

        item = self.tree.item(selection[0])
        tax_code = item['values'][0]

        for config in self.tax_configs:
            if config.get("tax_code") == tax_code:
                self.show_tax_form("Edit Tax Configuration", config)
                break

    def show_tax_form(self, title, config_data):
        """Show tax configuration form"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()

        main = ctk.CTkFrame(dialog, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        # Tax Code
        ctk.CTkLabel(main, text="Tax Code:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        tax_code = ctk.CTkEntry(main, width=400)
        tax_code.pack(pady=5)
        if config_data:
            tax_code.insert(0, config_data.get("tax_code", ""))

        # Tax Name
        ctk.CTkLabel(main, text="Tax Name:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        tax_name = ctk.CTkEntry(main, width=400)
        tax_name.pack(pady=5)
        if config_data:
            tax_name.insert(0, config_data.get("tax_name", ""))

        # Tax Type
        ctk.CTkLabel(main, text="Tax Type:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        tax_type_var = ctk.StringVar(value=config_data.get("tax_type", "GST") if config_data else "GST")
        tax_type = ctk.CTkComboBox(main, values=["GST", "TDS", "TCS", "Service Tax"], variable=tax_type_var, width=400)
        tax_type.pack(pady=5)

        # Rate
        ctk.CTkLabel(main, text="Rate (%):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        rate = ctk.CTkEntry(main, width=400)
        rate.pack(pady=5)
        if config_data:
            rate.insert(0, str(config_data.get("rate", 0)))

        # Active status
        active_var = ctk.BooleanVar(value=config_data.get("active", True) if config_data else True)
        ctk.CTkCheckBox(main, text="Active", variable=active_var).pack(anchor="w", pady=10)

        # Save button
        def save_config():
            new_config = {
                "tax_code": tax_code.get(),
                "tax_name": tax_name.get(),
                "tax_type": tax_type_var.get(),
                "rate": float(rate.get() or 0),
                "active": active_var.get(),
                "components": []
            }

            # If GST, add CGST/SGST components
            if new_config["tax_type"] == "GST":
                half_rate = new_config["rate"] / 2
                new_config["components"] = [
                    {"name": "CGST", "rate": half_rate},
                    {"name": "SGST", "rate": half_rate}
                ]

            if config_data:
                # Update existing
                for i, c in enumerate(self.tax_configs):
                    if c.get("tax_code") == config_data.get("tax_code"):
                        self.tax_configs[i] = new_config
                        break
            else:
                # Add new
                self.tax_configs.append(new_config)

            self.db.save_json(self.company_name, "tax_config.json", self.tax_configs)
            messagebox.showinfo("Success", "Tax configuration saved!")
            dialog.destroy()
            self.load_tax_configs()

        ctk.CTkButton(main, text="Save", command=save_config, fg_color="#2e7d32", width=150).pack(pady=20)

    def delete_tax_config(self):
        """Delete selected tax configuration"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a tax configuration.")
            return

        item = self.tree.item(selection[0])
        tax_code = item['values'][0]

        if messagebox.askyesno("Confirm", f"Delete tax configuration {tax_code}?"):
            self.tax_configs = [c for c in self.tax_configs if c.get("tax_code") != tax_code]
            self.db.save_json(self.company_name, "tax_config.json", self.tax_configs)
            self.load_tax_configs()

    def generate_gstr1(self):
        """Generate GSTR-1 report (sales)"""
        from_dt = self.from_date.get()
        to_dt = self.to_date.get()

        # Load invoices
        invoices = self.db.load_json(self.company_name, "invoices.json") or []

        # Filter by date range
        filtered = [
            inv for inv in invoices
            if from_dt <= inv.get("date", "") <= to_dt
        ]

        report = f"GSTR-1 Report\nPeriod: {from_dt} to {to_dt}\n"
        report += f"\nTotal Invoices: {len(filtered)}\n"
        
        # Calculate totals
        total_taxable = 0
        total_tax = 0

        for inv in filtered:
            for item in inv.get("items", []):
                taxable = item.get("line_total", 0)
                tax_rate = item.get("tax_rate", 0)
                tax = Calculator.calculate_tax(taxable, tax_rate)
                total_taxable += taxable
                total_tax += tax

        report += f"Total Taxable Value: {Formatters.format_currency(total_taxable)}\n"
        report += f"Total Tax: {Formatters.format_currency(total_tax)}\n"

        messagebox.showinfo("GSTR-1 Report", report)

    def generate_gstr3b(self):
        """Generate GSTR-3B summary"""
        from_dt = self.from_date.get()
        to_dt = self.to_date.get()

        invoices = self.db.load_json(self.company_name, "invoices.json") or []
        expenses = self.db.load_json(self.company_name, "expenses.json") or []

        # Outward supplies (sales)
        sales_taxable = 0
        sales_tax = 0

        for inv in invoices:
            if from_dt <= inv.get("date", "") <= to_dt:
                for item in inv.get("items", []):
                    taxable = item.get("line_total", 0)
                    tax_rate = item.get("tax_rate", 0)
                    tax = Calculator.calculate_tax(taxable, tax_rate)
                    sales_taxable += taxable
                    sales_tax += tax

        # Inward supplies (purchases with GST)
        purchase_tax = 0

        for exp in expenses:
            if from_dt <= exp.get("date", "") <= to_dt:
                amount = exp.get("amount", 0)
                tax_rate = exp.get("tax_rate", 0)
                if tax_rate > 0:
                    tax = Calculator.calculate_tax(amount, tax_rate)
                    purchase_tax += tax

        # Net GST liability
        net_liability = sales_tax - purchase_tax

        report = f"GSTR-3B Summary\nPeriod: {from_dt} to {to_dt}\n\n"
        report += f"Outward Supplies:\n"
        report += f"  Taxable Value: {Formatters.format_currency(sales_taxable)}\n"
        report += f"  Tax: {Formatters.format_currency(sales_tax)}\n\n"
        report += f"Input Tax Credit:\n"
        report += f"  Tax: {Formatters.format_currency(purchase_tax)}\n\n"
        report += f"Net GST Liability: {Formatters.format_currency(net_liability)}\n"

        messagebox.showinfo("GSTR-3B Summary", report)

    def tax_summary(self):
        """Generate tax summary"""
        from_dt = self.from_date.get()
        to_dt = self.to_date.get()

        invoices = self.db.load_json(self.company_name, "invoices.json") or []

        # Group by tax rate
        tax_summary = {}

        for inv in invoices:
            if from_dt <= inv.get("date", "") <= to_dt:
                for item in inv.get("items", []):
                    tax_rate = item.get("tax_rate", 0)
                    taxable = item.get("line_total", 0)
                    tax = Calculator.calculate_tax(taxable, tax_rate)

                    if tax_rate not in tax_summary:
                        tax_summary[tax_rate] = {"taxable": 0, "tax": 0, "count": 0}

                    tax_summary[tax_rate]["taxable"] += taxable
                    tax_summary[tax_rate]["tax"] += tax
                    tax_summary[tax_rate]["count"] += 1

        report = f"Tax Summary\nPeriod: {from_dt} to {to_dt}\n\n"

        for rate, data in sorted(tax_summary.items()):
            report += f"Tax Rate: {rate}%\n"
            report += f"  Items: {data['count']}\n"
            report += f"  Taxable: {Formatters.format_currency(data['taxable'])}\n"
            report += f"  Tax: {Formatters.format_currency(data['tax'])}\n\n"

        total_tax = sum(d['tax'] for d in tax_summary.values())
        report += f"Total Tax Collected: {Formatters.format_currency(total_tax)}\n"

        messagebox.showinfo("Tax Summary", report)
