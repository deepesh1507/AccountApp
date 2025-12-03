"""
Reports & Analytics Module
Enhanced reporting with Trial Balance, P&L, Balance Sheet, and more
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import threading
from .base_module import BaseModule
from .utilities import Formatters, Calculator


class ReportsAnalytics(BaseModule):
    def __init__(self, root, company_data, user_data, app_controller):
        self.current_report_data = None
        self.current_report_title = ""
        super().__init__(root, company_data, user_data, app_controller)
        
        self.company_name = self.company_data.get('company_name', '')
        self.root.title(f"Reports - {self.company_name}")
        
        # These are populated by refresh(), which is called by setup_ui()
        # setup_ui() is called by BaseModule.__init__
        self.accounts = []
        self.invoices = []
        self.expenses = []
        self.journal_entries = []
        self.products = []

    def setup_ui(self):
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container - Theme-aware background
        main = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(main, fg_color="#7b1fa2", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="📈 Reports & Analytics",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="white"
        ).pack(side="left", padx=30)

        # Navigation
        nav = ctk.CTkFrame(header, fg_color="transparent")
        nav.pack(side="right", padx=20)
        
        ctk.CTkButton(nav, text="← Back", width=100, fg_color="#0d47a1", command=self.go_back).pack(side="left", padx=5)
        ctk.CTkButton(nav, text="🏠 Home", width=80, fg_color="#0d47a1", command=self.go_home).pack(side="left", padx=5)

        # Content - Theme-aware
        content = ctk.CTkFrame(main, fg_color=("white", "gray17"))
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Date Range Selection
        date_frame = ctk.CTkFrame(content, fg_color=("#e3f2fd", "gray25"), corner_radius=10)
        date_frame.pack(fill="x", padx=10, pady=10)

        date_inner = ctk.CTkFrame(date_frame, fg_color="transparent")
        date_inner.pack(pady=15)

        ctk.CTkLabel(date_inner, text="From:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.period_from = ctk.CTkEntry(date_inner, width=120)
        self.period_from.insert(0, datetime.now().replace(day=1).strftime("%Y-%m-%d"))
        self.period_from.pack(side="left", padx=5)

        ctk.CTkLabel(date_inner, text="To:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        self.period_to = ctk.CTkEntry(date_inner, width=120)
        self.period_to.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.period_to.pack(side="left", padx=5)

        ctk.CTkButton(date_inner, text="🔄 Refresh Data", command=self.refresh, fg_color="#2e7d32", width=130).pack(side="left", padx=10)

        # Report Buttons
        reports_label = ctk.CTkLabel(content, text="📊 Financial Reports", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1565c0")
        reports_label.pack(pady=(20, 10))

        # Report button rows
        row1 = ctk.CTkFrame(content, fg_color="transparent")
        row1.pack(fill="x", padx=20, pady=5)        
        ctk.CTkButton(row1, text="📋 Trial Balance", fg_color="#2e7d32", height=50, font=ctk.CTkFont(size=13, weight="bold"), command=self.trial_balance).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(row1, text="💰 Profit & Loss", fg_color="#1976d2", height=50, font=ctk.CTkFont(size=13, weight="bold"), command=self.profit_and_loss).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(row1, text="⚖️ Balance Sheet", fg_color="#f57c00", height=50, font=ctk.CTkFont(size=13, weight="bold"), command=self.balance_sheet).pack(side="left", padx=5, expand=True, fill="x")

        row2 = ctk.CTkFrame(content, fg_color="transparent")
        row2.pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(row2, text="💸 Cash Flow", fg_color="#7b1fa2", height=50, font=ctk.CTkFont(size=13, weight="bold"), command=self.cash_flow_statement).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(row2, text="📊 Tax Summary", fg_color="#f9a825", height=50, font=ctk.CTkFont(size=13, weight="bold"), command=self.tax_summary_report).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(row2, text="⏰ Aging Analysis", fg_color="#00796b", height=50, font=ctk.CTkFont(size=13, weight="bold"), command=self.aging_analysis).pack(side="left", padx=5, expand=True, fill="x")

        row3 = ctk.CTkFrame(content, fg_color="transparent")
        row3.pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(row3, text="📦 Stock Valuation", fg_color="#5e35b1", height=50, font=ctk.CTkFont(size=13, weight="bold"), command=self.stock_valuation).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(row3, text="📈 Ledger Summary", fg_color="#c62828", height=50, font=ctk.CTkFont(size=13, weight="bold"), command=self.ledger_summary).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(row3, text="📁 Export All (CSV)", fg_color="#455a64", height=50, font=ctk.CTkFont(size=13, weight="bold"), command=self.export_all_reports).pack(side="left", padx=5, expand=True, fill="x")

        # Download Actions
        download_frame = ctk.CTkFrame(content, fg_color="transparent")
        download_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(download_frame, text="Download Current Report:", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkButton(download_frame, text="📄 Download PDF", fg_color="#d32f2f", width=140, command=self.download_pdf).pack(side="left", padx=10)
        ctk.CTkButton(download_frame, text="📊 Download CSV", fg_color="#388e3c", width=140, command=self.download_csv).pack(side="left", padx=10)

        # Output Display
        self.loading_label = ctk.CTkLabel(content, text="Loading data...", text_color="blue")
        self.loading_label.pack(pady=5)
        
        output_label = ctk.CTkLabel(content, text="Report Output", font=ctk.CTkFont(size=14, weight="bold"))
        output_label.pack(pady=(20, 5))

        self.output = ctk.CTkTextbox(content, width=900, height=350, font=ctk.CTkFont(family="Consolas", size=11))
        self.output.pack(padx=10, pady=10, fill="both", expand=True)

        # Load initial data
        self.refresh()

    def refresh(self):
        """Load all data from database in background"""
        self.loading_label.pack(pady=5)
        self.output.delete("1.0", "end")
        self.output.insert("end", "Loading data...")
        threading.Thread(target=self._fetch_data_thread, daemon=True).start()

    def _fetch_data_thread(self):
        try:
            company_name = self.company_data.get('company_name', '')
            data = {
                'accounts': self.db.load_json(company_name, "accounts.json") or [],
                'invoices': self.db.load_json(company_name, "invoices.json") or [],
                'expenses': self.db.load_json(company_name, "expenses.json") or [],
                'journal_entries': self.db.load_json(company_name, "journal_entries.json") or [],
                'products': self.db.load_json(company_name, "products.json") or []
            }
            self.root.after(0, lambda: self._update_ui_after_load(data))
        except Exception as exc:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load data:\n{exc}"))

    def _update_ui_after_load(self, data):
        self.accounts = data['accounts']
        self.invoices = data['invoices']
        self.expenses = data['expenses']
        self.journal_entries = data['journal_entries']
        self.products = data['products']
        
        self.output.delete("1.0", "end")
        self.output.insert("end", "✅ Data Loaded Successfully\n")
        self.output.insert("end", "━"*50 + "\n")
        self.output.insert("end", f"Accounts: {len(self.accounts)}\n")
        self.output.insert("end", f"Invoices: {len(self.invoices)}\n")
        self.output.insert("end", f"Expenses: {len(self.expenses)}\n")
        self.output.insert("end", f"Journal Entries: {len(self.journal_entries)}\n")
        self.output.insert("end", f"Products: {len(self.products)}\n\n")
        self.output.insert("end", "Select a report from above to generate.\n")
        self.loading_label.pack_forget()

    def trial_balance(self):
        """Generate Trial Balance"""
        from_dt = self.period_from.get()
        to_dt = self.period_to.get()
        self.current_report_title = f"Trial Balance ({from_dt} to {to_dt})"

        balances = {}
        for acc in self.accounts:
            acc_code = acc.get('code')
            balances[acc_code] = {
                'name': acc.get('name'),
                'type': acc.get('type', '').capitalize(),
                'debit': 0,
                'credit': 0
            }

        for entry in self.journal_entries:
            if from_dt <= entry.get("date", "") <= to_dt:
                for line in entry.get("lines", []):
                    code = line.get("account_code")
                    if code in balances:
                        balances[code]['debit'] += line.get('debit', 0)
                        balances[code]['credit'] += line.get('credit', 0)

        # Prepare data for export
        self.current_report_data = [['Account Code', 'Account Name', 'Type', 'Debit', 'Credit']]
        
        output = f"TRIAL BALANCE\n"
        output += f"Company: {self.company_name}\nPeriod: {from_dt} to {to_dt}\n"
        output += "="*90 + "\n\n"
        output += f"{'Account Code':<15} {'Account Name':<30} {'Type':<12} {'Debit':>15} {'Credit':>15}\n"
        output += "-"*90 + "\n"

        total_debit = total_credit = 0

        for code, data in sorted(balances.items()):
            if data['debit'] > 0 or data['credit'] > 0:
                output += f"{code:<15} {data['name']:<30} {data['type']:<12} "
                output += f"{Formatters.format_number(data['debit']):>15} {Formatters.format_number(data['credit']):>15}\n"
                
                self.current_report_data.append([
                    code, 
                    data['name'], 
                    data['type'], 
                    f"{data['debit']:.2f}", 
                    f"{data['credit']:.2f}"
                ])
                
                total_debit += data['debit']
                total_credit += data['credit']

        output += "-"*90 + "\n"
        output += f"{'TOTAL':<58} {Formatters.format_number(total_debit):>15} {Formatters.format_number(total_credit):>15}\n"
        output += "="*90 + "\n"
        
        self.current_report_data.append(['TOTAL', '', '', f"{total_debit:.2f}", f"{total_credit:.2f}"])

        if abs(total_debit - total_credit) < 0.01:
            output += "\n✅ Trial Balance is BALANCED\n"
        else:
            output += f"\n❌ OUT OF BALANCE by {Formatters.format_number(abs(total_debit - total_credit))}\n"

        self.output.delete("1.0", "end")
        self.output.insert("end", output)

    def profit_and_loss(self):
        """Generate P&L Statement"""
        from_dt, to_dt = self.period_from.get(), self.period_to.get()
        self.current_report_title = f"Profit & Loss Statement ({from_dt} to {to_dt})"

        income = sum(item.get('line_total', 0) for inv in self.invoices 
                    if from_dt <= inv.get('date', '') <= to_dt 
                    for item in inv.get('items', []))

        expenses_total = sum(float(exp.get('amount', 0)) for exp in self.expenses 
                            if from_dt <= exp.get('date', '') <= to_dt)

        net_profit = income - expenses_total

        # Prepare data for export
        self.current_report_data = [
            ['Item', 'Amount'],
            ['REVENUE', ''],
            ['Sales Revenue', f"{income:.2f}"],
            ['Total Revenue', f"{income:.2f}"],
            ['', ''],
            ['EXPENSES', ''],
            ['Operating Expenses', f"{expenses_total:.2f}"],
            ['Total Expenses', f"{expenses_total:.2f}"],
            ['', ''],
            ['NET PROFIT/(LOSS)', f"{net_profit:.2f}"]
        ]

        output = f"PROFIT & LOSS STATEMENT\nCompany: {self.company_name}\nPeriod: {from_dt} to {to_dt}\n"
        output += "="*80 + "\n\nREVENUE\n" + "-"*80 + "\n"
        output += f"Sales Revenue{Formatters.format_currency(income, self.company_data.get('currency', 'INR')):>60}\n"
        output += "-"*80 + "\n" + f"Total Revenue{Formatters.format_currency(income):>60}\n\n"
        output += "EXPENSES\n" + "-"*80 + "\n"
        output += f"Operating Expenses{Formatters.format_currency(expenses_total):>55}\n"
        output += "-"*80 + "\n" + f"Total Expenses{Formatters.format_currency(expenses_total):>58}\n\n"
        output += "="*80 + "\n"
        output += f"NET PROFIT/(LOSS){Formatters.format_currency(net_profit):>55}\n"
        output += "="*80 + "\n"

        if net_profit > 0:
            output += f"\n✅ Profitable: {Formatters.format_currency(net_profit)}\n"
        else:
            output += f"\n⚠️ Loss: {Formatters.format_currency(abs(net_profit))}\n"

        self.output.delete("1.0", "end")
        self.output.insert("end", output)

    def balance_sheet(self):
        """Generate Balance Sheet"""
        self.current_report_title = f"Balance Sheet (As on {self.period_to.get()})"
        
        assets = sum(acc.get('balance', 0) for acc in self.accounts if acc.get('type', '').lower() == 'asset')
        liabilities = sum(acc.get('balance', 0) for acc in self.accounts if acc.get('type', '').lower() == 'liability')
        equity = sum(acc.get('balance', 0) for acc in self.accounts if acc.get('type', '').lower() == 'equity')
        stock_value = sum(p.get('stock_qty', 0) * p.get('unit_price', 0) for p in self.products)
        total_assets = assets + stock_value
        tot_liab_equity = liabilities + equity

        # Prepare data for export
        self.current_report_data = [
            ['Item', 'Amount'],
            ['ASSETS', ''],
            ['Fixed Assets', f"{assets:.2f}"],
            ['Inventory', f"{stock_value:.2f}"],
            ['Total Assets', f"{total_assets:.2f}"],
            ['', ''],
            ['LIABILITIES & EQUITY', ''],
            ['Liabilities', f"{liabilities:.2f}"],
            ['Equity', f"{equity:.2f}"],
            ['Total Liab + Equity', f"{tot_liab_equity:.2f}"]
        ]

        output = f"BALANCE SHEET\nCompany: {self.company_name}\nAs on: {self.period_to.get()}\n"
        output += "="*80 + "\n\nASSETS\n" + "-"*80 + "\n"
        output += f"Fixed Assets{Formatters.format_currency(assets):>60}\n"
        output += f"Inventory{Formatters.format_currency(stock_value):>63}\n"
        output += "-"*80 + "\n"
        output += f"Total Assets{Formatters.format_currency(total_assets):>60}\n\n"
        output += "LIABILITIES & EQUITY\n" + "-"*80 + "\n"
        output += f"Liabilities{Formatters.format_currency(liabilities):>63}\n"
        output += f"Equity{Formatters.format_currency(equity):>69}\n"
        output += "-"*80 + "\n"
        output += f"Total Liab + Equity{Formatters.format_currency(tot_liab_equity):>55}\n\n"
        output += "="*80 + "\n"
        
        if abs(total_assets - tot_liab_equity) < 0.01:
            output += "✅ Balance Sheet BALANCES\n"
        else:
            output += f"❌ Out of balance by {Formatters.format_currency(abs(total_assets - tot_liab_equity))}\n"

        self.output.delete("1.0", "end")
        self.output.insert("end", output)

    def cash_flow_statement(self):
        """Generate Cash Flow"""
        self.current_report_title = f"Cash Flow Statement ({self.period_from.get()} to {self.period_to.get()})"
        
        cash_from_ops = sum(item.get('line_total', 0) for inv in self.invoices for item in inv.get('items', []))
        cash_for_exp = sum(float(e.get('amount', 0)) for e in self.expenses)
        net_cash = cash_from_ops - cash_for_exp

        # Prepare data for export
        self.current_report_data = [
            ['Activity', 'Amount'],
            ['Operating Activities', ''],
            ['Cash from Sales', f"{cash_from_ops:.2f}"],
            ['Cash for Expenses', f"{cash_for_exp:.2f}"],
            ['Net Cash Flow', f"{net_cash:.2f}"]
        ]

        output = f"CASH FLOW STATEMENT\nPeriod: {self.period_from.get()} to {self.period_to.get()}\n"
        output += "="*60 + "\n\nOperating Activities:\n"
        output += f"  Cash from Sales: {Formatters.format_currency(cash_from_ops)}\n"
        output += f"  Cash for Expenses: {Formatters.format_currency(cash_for_exp)}\n"
        output += f"  Net Cash Flow: {Formatters.format_currency(net_cash)}\n"

        self.output.delete("1.0", "end")
        self.output.insert("end", output)

    def tax_summary_report(self):
        """Generate Tax Summary"""
        from_dt, to_dt = self.period_from.get(), self.period_to.get()
        self.current_report_title = f"Tax Summary Report ({from_dt} to {to_dt})"

        tax_collected = {}
        for inv in self.invoices:
            if from_dt <= inv.get('date', '') <= to_dt:
                for item in inv.get('items', []):
                    tax_rate = item.get('tax_rate', 0)
                    taxable = item.get('line_total', 0)
                    tax = Calculator.calculate_tax(taxable, tax_rate)
                    
                    if tax_rate not in tax_collected:
                        tax_collected[tax_rate] = {'taxable': 0, 'tax': 0}
                    tax_collected[tax_rate]['taxable'] += taxable
                    tax_collected[tax_rate]['tax'] += tax

        # Prepare data for export
        self.current_report_data = [['Tax Rate', 'Taxable Amount', 'Tax Amount']]

        output = f"TAX SUMMARY REPORT\nPeriod: {from_dt} to {to_dt}\n" + "="*60 + "\n\n"

        for rate, data in sorted(tax_collected.items()):
            output += f"Tax @ {rate}%:\n"
            output += f"  Taxable: {Formatters.format_currency(data['taxable'])}\n"
            output += f"  Tax: {Formatters.format_currency(data['tax'])}\n\n"
            
            self.current_report_data.append([
                f"{rate}%", 
                f"{data['taxable']:.2f}", 
                f"{data['tax']:.2f}"
            ])

        total_tax = sum(d['tax'] for d in tax_collected.values())
        output += f"Total Tax: {Formatters.format_currency(total_tax)}\n"
        
        self.current_report_data.append(['TOTAL', '', f"{total_tax:.2f}"])

        self.output.delete("1.0", "end")
        self.output.insert("end", output)

    def aging_analysis(self):
        """Generate Aging Analysis"""
        today = datetime.strptime(self.period_to.get(), "%Y-%m-%d")
        self.current_report_title = f"Aging Analysis - AR (As on {self.period_to.get()})"
        
        aging = {"0-30 days": 0, "31-60 days": 0, "61-90 days": 0, "90+ days": 0}

        for inv in self.invoices:
            inv_date = datetime.strptime(inv.get('date', ''), "%Y-%m-%d")
            total = sum(item.get('line_total', 0) for item in inv.get('items', []))
            bucket = Calculator.calculate_aging_buckets(inv_date, today)
            aging[bucket] += total

        # Prepare data for export
        self.current_report_data = [['Aging Bucket', 'Amount']]

        output = f"AGING ANALYSIS - AR\nAs on: {self.period_to.get()}\n" + "="*60 + "\n\n"
        for bucket, amount in aging.items():
            output += f"{bucket}: {Formatters.format_currency(amount)}\n"
            self.current_report_data.append([bucket, f"{amount:.2f}"])

        total_outstanding = sum(aging.values())
        output += f"\nTotal Outstanding: {Formatters.format_currency(total_outstanding)}\n"
        self.current_report_data.append(['TOTAL', f"{total_outstanding:.2f}"])

        self.output.delete("1.0", "end")
        self.output.insert("end", output)

    def stock_valuation(self):
        """Generate Stock Valuation"""
        self.current_report_title = f"Stock Valuation Report (As on {self.period_to.get()})"
        
        total_qty = sum(p.get('stock_qty', 0) for p in self.products)
        total_value = sum(p.get('stock_qty', 0) * p.get('unit_price', 0) for p in self.products)

        # Prepare data for export
        self.current_report_data = [['Product Code', 'Product Name', 'Quantity', 'Unit Price', 'Total Value']]

        output = f"STOCK VALUATION REPORT\nAs on: {self.period_to.get()}\n" + "="*85 + "\n\n"
        output += f"{'Product Code':<15} {'Product Name':<30} {'Qty':>10} {'Price':>12} {'Value':>15}\n"
        output += "-"*85 + "\n"

        for p in self.products:
            qty, price = p.get('stock_qty', 0), p.get('unit_price', 0)
            value = qty * price
            output += f"{p.get('product_code', ''):<15} {p.get('product_name', '')[:30]:<30} {qty:>10.2f} {price:>12.2f} {value:>15.2f}\n"
            
            self.current_report_data.append([
                p.get('product_code', ''),
                p.get('product_name', ''),
                f"{qty:.2f}",
                f"{price:.2f}",
                f"{value:.2f}"
            ])

        output += "-"*85 + "\n"
        output += f"{'TOTAL':<47} {total_qty:>10.2f} {total_value:>28.2f}\n"
        
        self.current_report_data.append(['TOTAL', '', f"{total_qty:.2f}", '', f"{total_value:.2f}"])

        self.output.delete("1.0", "end")
        self.output.insert("end", output)

    def ledger_summary(self):
        """Generate Ledger Summary"""
        from_dt, to_dt = self.period_from.get(), self.period_to.get()
        self.current_report_title = f"Account Ledger Summary ({from_dt} to {to_dt})"
        
        output = f"ACCOUNT LEDGER SUMMARY\nPeriod: {from_dt} to {to_dt}\n"
        output += "="*90 + "\n\n"
        output += f"{'Account':<40} {'Total Debit':>15} {'Total Credit':>15} {'Balance':>15}\n"
        output += "-"*90 + "\n"

        # Prepare data for export
        self.current_report_data = [['Account Name', 'Total Debit', 'Total Credit', 'Balance']]

        summary = {}
        for entry in self.journal_entries:
            for line in entry.get('lines', []):
                code = line.get('account_code')
                if code not in summary:
                    acc = next((a for a in self.accounts if a.get('code') == code), None)
                    summary[code] = {'name': acc.get('name', code) if acc else code, 'debit': 0, 'credit': 0}
                summary[code]['debit'] += line.get('debit', 0)
                summary[code]['credit'] += line.get('credit', 0)

        for code, data in sorted(summary.items()):
            balance = data['debit'] - data['credit']
            output += f"{data['name']:<40} {data['debit']:>15.2f} {data['credit']:>15.2f} {balance:>15.2f}\n"
            
            self.current_report_data.append([
                data['name'],
                f"{data['debit']:.2f}",
                f"{data['credit']:.2f}",
                f"{balance:.2f}"
            ])

        self.output.delete("1.0", "end")
        self.output.insert("end", output)

    def export_all_reports(self):
        """Export all data to CSV"""
        folder = filedialog.askdirectory(title="Select Export Location")
        if not folder:
            return

        try:
            self.db.export_to_csv(self.company_name, "accounts.json", f"{folder}/accounts.csv")
            self.db.export_to_csv(self.company_name, "invoices.json", f"{folder}/invoices.csv")
            self.db.export_to_csv(self.company_name, "expenses.json", f"{folder}/expenses.csv")
            self.db.export_to_csv(self.company_name, "journal_entries.json", f"{folder}/journal_entries.csv")
            self.db.export_to_csv(self.company_name, "products.json", f"{folder}/products.csv")

            messagebox.showinfo("Success", f"All reports exported to:\n{folder}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")

    def download_pdf(self):
        if not self.current_report_data:
            messagebox.showwarning("No Report", "Please generate a report first.")
            return
            
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if not filename:
            return
            
        try:
            doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            elements.append(Paragraph(self.current_report_title, styles['Title']))
            elements.append(Spacer(1, 20))
            
            # Table
            if self.current_report_data:
                # Convert all data to string for PDF table
                table_data = [[str(cell) for cell in row] for row in self.current_report_data]
                
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table)
            
            doc.build(elements)
            messagebox.showinfo("Success", "PDF downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF:\n{str(e)}")

    def download_csv(self):
        if not self.current_report_data:
            messagebox.showwarning("No Report", "Please generate a report first.")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not filename:
            return
            
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(self.current_report_data)
            messagebox.showinfo("Success", "CSV downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV:\n{str(e)}")

    def go_back(self):
        if self.app:
            self.app.show_dashboard(self.company_data, self.user_data)
