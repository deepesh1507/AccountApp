"""
Enhanced Dashboard with Professional Navigation
Tally/SAP-style layout with left sidebar navigation and KPI dashboard
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import threading
from PIL import Image, ImageTk
from pathlib import Path


class Dashboard:
    def __init__(self, root, company_data, user_data, app_controller):
        self.root = root
        self.company_data = company_data
        self.user_data = user_data
        self.app = app_controller
        self.company_name = company_data.get("company_name", "Unknown")
        
        from .database_manager import DatabaseManager
        self.db = DatabaseManager()
        
        self.setup_ui()

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        main_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main_frame.pack(fill="both", expand=True)
        
        self.create_top_nav(main_frame)
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        self.create_navigation_sidebar(content_frame)
        self.create_dashboard_content(content_frame)
        self.create_footer(main_frame)

    def create_top_nav(self, parent):
        nav_bar = ctk.CTkFrame(parent, fg_color="#1976d2", height=60)
        nav_bar.pack(fill="x")
        nav_bar.pack_propagate(False)
        
        title_frame = ctk.CTkFrame(nav_bar, fg_color="transparent")
        title_frame.pack(side="left", padx=20)
        
        # Logo in Dashboard
        logo_img = self.get_dashboard_logo()
        if logo_img:
            logo_label = ctk.CTkLabel(title_frame, text="", image=logo_img)
            logo_label.pack(side="left", padx=(0, 10))

        text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        text_frame.pack(side="left")

        ctk.CTkLabel(text_frame, text=f"🏢 {self.company_name}", font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack(anchor="w")
        ctk.CTkLabel(text_frame, text="Professional Accounting System", font=ctk.CTkFont(size=11), text_color="#e3f2fd").pack(anchor="w")
        
        right_frame = ctk.CTkFrame(nav_bar, fg_color="transparent")
        right_frame.pack(side="right", padx=20)
        
        ctk.CTkButton(right_frame, text="⛶ Fullscreen", command=self.toggle_fullscreen, width=100, fg_color="#0d47a1", hover_color="#01579b").pack(side="left", padx=5)
        ctk.CTkButton(right_frame, text="🚪 Logout", command=self.logout, width=100, fg_color="#c62828", hover_color="#8e0000").pack(side="left", padx=5)

    def create_navigation_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, fg_color=("white", "gray20"), width=280)
        sidebar.pack(side="left", fill="y", padx=(20, 10), pady=20)
        sidebar.pack_propagate(False)
        
        user_header = ctk.CTkFrame(sidebar, fg_color=("#1976d2", "#0d47a1"), corner_radius=10)
        user_header.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(user_header, text=f"👤 {self.user_data.get('username', 'User')}", font=ctk.CTkFont(size=14, weight="bold"), text_color="white").pack(pady=8)
        ctk.CTkLabel(user_header, text=self.user_data.get('role', 'Admin').upper(), font=ctk.CTkFont(size=10), text_color="#e3f2fd").pack(pady=(0, 8))
        
        ctk.CTkLabel(sidebar, text="📋 MODULES", font=ctk.CTkFont(size=13, weight="bold"), text_color=("#1976d2", "#64b5f6")).pack(pady=(15, 5), padx=15, anchor="w")
        
        menu_scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        menu_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Standard Modules
        standard_modules = [
            ("📊", "Chart of Accounts", self.open_chart_of_accounts, "#2e7d32"),
            ("📝", "Journal Entries", self.open_journal_entries, "#1976d2"),
            ("📖", "Ledger", self.open_ledger, "#7b1fa2"),
            ("👥", "Clients", self.open_clients, "#00796b"),
            ("🏭", "Vendors", self.open_vendors, "#d32f2f"),
            ("📄", "Invoices", self.open_invoices, "#f57c00"),
            ("💰", "Expenses", self.open_expenses, "#c62828"),
            ("📋", "GST & Tax", self.open_gst_tax, "#f9a825"),
            ("📦", "Inventory", self.open_inventory, "#5e35b1"),
            ("💸", "Payment Tracking", self.open_payment_tracking, "#00796b"),
            ("📈", "Reports", self.open_reports, "#0277bd"),
            ("⚙️", "Settings", self.open_settings, "#455a64"),
        ]
        
        for icon, name, command, color in standard_modules:
            self.create_menu_button(menu_scroll, icon, name, command)

        # ERP Modules (Collapsible)
        self.create_collapsible_menu(menu_scroll, "📘", "ERP FI (Financials)", [
            ("General Ledger (FI-GL)", self.open_erp_fi_gl),
            ("Accounts Payable (FI-AP)", self.open_erp_fi_ap),
            ("Accounts Receivable (FI-AR)", self.open_erp_fi_ar),
            ("Asset Accounting (FI-AA)", self.open_erp_fi_aa),
            ("Bank Accounting (FI-BL)", self.open_erp_fi_bl),
            ("Treasury (FI-TR)", self.open_erp_fi_tr),
            ("Special Purpose Ledger (FI-SL)", self.open_erp_fi_sl),
            ("Credit Management (FI-CL)", self.open_erp_fi_cl),
        ])

        self.create_collapsible_menu(menu_scroll, "📗", "ERP CO (Controlling)", [
            ("Overhead Mgmt (CO-OM)", self.open_erp_co_om),
            ("Internal Orders (CO-IO)", self.open_erp_co_io),
            ("Profit Center (CO-PCA)", self.open_erp_co_pca),
            ("Profitability (CO-PA)", self.open_erp_co_pa),
            ("Product Costing (CO-PC)", self.open_erp_co_pc),
            ("Material Ledger (CO-ML)", self.open_erp_co_ml),
        ])
        
        self.create_collapsible_menu(menu_scroll, "🔄", "ERP Integration", [
            ("MM -> FI (Procurement)", self.open_erp_int_mm_fi),
            ("SD -> FI (Sales)", self.open_erp_int_sd_fi),
            ("PP -> CO (Production)", self.open_erp_int_pp_co),
            ("HCM -> FI (Payroll)", self.open_erp_int_hcm_fi),
        ])
        
        quick_frame = ctk.CTkFrame(sidebar, fg_color=("#e3f2fd", "gray25"), corner_radius=8)
        quick_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(quick_frame, text="⚡ QUICK ACTIONS", font=ctk.CTkFont(size=10, weight="bold")).pack(pady=5)
        ctk.CTkButton(quick_frame, text="+ New Invoice", command=self.open_invoices, height=30, fg_color="#2e7d32", font=ctk.CTkFont(size=11)).pack(fill="x", padx=8, pady=3)
        ctk.CTkButton(quick_frame, text="+ New Journal", command=self.open_journal_entries, height=30, fg_color="#1976d2", font=ctk.CTkFont(size=11)).pack(fill="x", padx=8, pady=3)

    def create_menu_button(self, parent, icon, text, command):
        btn = ctk.CTkButton(
            parent, 
            text=f"{icon}  {text}", 
            command=command, 
            anchor="w", 
            fg_color="transparent", 
            hover_color=("gray85", "gray25"), 
            text_color=("gray10", "gray90"), 
            font=ctk.CTkFont(size=13), 
            height=40, 
            corner_radius=8
        )
        btn.pack(fill="x", padx=5, pady=2)
        return btn

    def create_collapsible_menu(self, parent, icon, title, items):
        """Creates a collapsible menu section"""
        # Header Button
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=0, pady=2)
        
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        
        def toggle():
            if content_frame.winfo_viewable():
                content_frame.pack_forget()
                indicator.configure(text="▶")
            else:
                content_frame.pack(fill="x", padx=10, pady=2)
                indicator.configure(text="▼")
        
        header = ctk.CTkButton(
            frame,
            text=f"{icon}  {title}",
            command=toggle,
            anchor="w",
            fg_color="transparent",
            hover_color=("gray85", "gray25"),
            text_color=("gray10", "gray90"),
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=8
        )
        header.pack(fill="x", padx=5)
        
        # Indicator (arrow)
        indicator = ctk.CTkLabel(header, text="▶", font=("Arial", 10), width=20)
        indicator.place(relx=1.0, rely=0.5, anchor="e", x=-10)

        # Items
        for name, command in items:
            btn = ctk.CTkButton(
                content_frame,
                text=f"• {name}",
                command=command,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                text_color=("gray30", "gray70"),
                font=ctk.CTkFont(size=12),
                height=30,
                corner_radius=8
            )
            btn.pack(fill="x", padx=5, pady=1)

    def open_erp_fi_gl(self):
        try:
            self.app.show_erp_fi_gl(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP FI-GL:\n{str(e)}")

    def open_erp_fi_ap(self):
        try:
            self.app.show_erp_fi_ap(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP FI-AP:\n{str(e)}")

    def open_erp_fi_ar(self):
        try:
            self.app.show_erp_fi_ar(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP FI-AR:\n{str(e)}")

    def open_erp_fi_aa(self):
        try:
            self.app.show_erp_fi_aa(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP FI-AA:\n{str(e)}")

    def open_erp_fi_bl(self):
        try:
            self.app.show_erp_fi_bl(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP FI-BL:\n{str(e)}")

    def open_erp_fi_tr(self):
        try:
            self.app.show_erp_fi_tr(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP FI-TR:\n{str(e)}")

    def open_erp_fi_sl(self):
        try:
            self.app.show_erp_fi_sl(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP FI-SL:\n{str(e)}")

    def open_erp_fi_cl(self):
        try:
            self.app.show_erp_fi_cl(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP FI-CL:\n{str(e)}")

    # --- CO Modules ---

    def open_erp_co_om(self):
        try:
            self.app.show_erp_co_om(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP CO-OM:\n{str(e)}")

    def open_erp_co_io(self):
        try:
            self.app.show_erp_co_io(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP CO-IO:\n{str(e)}")

    def open_erp_co_pca(self):
        try:
            self.app.show_erp_co_pca(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP CO-PCA:\n{str(e)}")

    def open_erp_co_pa(self):
        try:
            self.app.show_erp_co_pa(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP CO-PA:\n{str(e)}")

    def open_erp_co_pc(self):
        try:
            self.app.show_erp_co_pc(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP CO-PC:\n{str(e)}")

    def open_erp_co_ml(self):
        try:
            self.app.show_erp_co_ml(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP CO-ML:\n{str(e)}")

    # --- Integration Modules ---

    def open_erp_int_mm_fi(self):
        try:
            self.app.show_erp_int_mm_fi(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP MM-FI:\n{str(e)}")

    def open_erp_int_sd_fi(self):
        try:
            self.app.show_erp_int_sd_fi(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP SD-FI:\n{str(e)}")

    def open_erp_int_pp_co(self):
        try:
            self.app.show_erp_int_pp_co(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP PP-CO:\n{str(e)}")

    def open_erp_int_hcm_fi(self):
        try:
            self.app.show_erp_int_hcm_fi(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP HCM-FI:\n{str(e)}")

    def create_dashboard_content(self, parent):
        dashboard = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        dashboard.pack(side="left", fill="both", expand=True, padx=(10, 20), pady=20)
        
        welcome_frame = ctk.CTkFrame(dashboard, fg_color=("white", "gray20"), corner_radius=12)
        welcome_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(welcome_frame, text=f"Welcome back, {self.user_data.get('username', 'User')}!", font=ctk.CTkFont(size=22, weight="bold")).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(welcome_frame, text=f"📅 {datetime.now().strftime('%A, %B %d, %Y')}", font=ctk.CTkFont(size=12), text_color=("gray50", "gray60")).pack(anchor="w", padx=20, pady=(0, 15))
        
        # Initialize StringVars for KPIs
        self.kpi_vars = {
            'revenue': ctk.StringVar(value="Loading..."),
            'expenses': ctk.StringVar(value="Loading..."),
            'profit': ctk.StringVar(value="Loading..."),
            'clients': ctk.StringVar(value="Loading..."),
            'invoices': ctk.StringVar(value="Loading..."),
            'stock': ctk.StringVar(value="Loading...")
        }
        
        kpi_row1 = ctk.CTkFrame(dashboard, fg_color="transparent")
        kpi_row1.pack(fill="x", pady=10)
        
        self.create_kpi_card(kpi_row1, "💰 Total Revenue", self.kpi_vars['revenue'], "#2e7d32").pack(side="left", fill="x", expand=True, padx=5)
        self.create_kpi_card(kpi_row1, "📊 Total Expenses", self.kpi_vars['expenses'], "#c62828").pack(side="left", fill="x", expand=True, padx=5)
        self.create_kpi_card(kpi_row1, "📈 Net Profit", self.kpi_vars['profit'], "#1976d2").pack(side="left", fill="x", expand=True, padx=5)
        
        kpi_row2 = ctk.CTkFrame(dashboard, fg_color="transparent")
        kpi_row2.pack(fill="x", pady=10)
        
        self.create_kpi_card(kpi_row2, "👥 Total Clients", self.kpi_vars['clients'], "#00796b").pack(side="left", fill="x", expand=True, padx=5)
        self.create_kpi_card(kpi_row2, "📄 Invoices (Month)", self.kpi_vars['invoices'], "#f57c00").pack(side="left", fill="x", expand=True, padx=5)
        self.create_kpi_card(kpi_row2, "📦 Stock Value", self.kpi_vars['stock'], "#5e35b1").pack(side="left", fill="x", expand=True, padx=5)
        
        # Start background loading
        threading.Thread(target=self.load_data_background, daemon=True).start()
        
        ctk.CTkLabel(dashboard, text="📋 RECENT ACTIVITY", font=ctk.CTkFont(size=16, weight="bold"), text_color=("#1976d2", "#64b5f6")).pack(anchor="w", pady=(25, 10))
        
        activity_frame = ctk.CTkFrame(dashboard, fg_color=("white", "gray20"), corner_radius=12)
        activity_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        ctk.CTkLabel(activity_frame, text="Recent activities will appear here when you create invoices, journal entries, or expenses.", font=ctk.CTkFont(size=12), text_color=("gray50", "gray60")).pack(padx=20, pady=30)
        
        ctk.CTkLabel(dashboard, text="⚡ QUICK REPORTS", font=ctk.CTkFont(size=16, weight="bold"), text_color=("#1976d2", "#64b5f6")).pack(anchor="w", pady=(25, 10))
        
        reports_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        reports_frame.pack(fill="x")
        
        ctk.CTkButton(reports_frame, text="📋 Trial Balance", command=self.open_reports, fg_color="#2e7d32", height=45, font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(reports_frame, text="💰 P&L Statement", command=self.open_reports, fg_color="#1976d2", height=45, font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(reports_frame, text="📊 GST Reports", command=self.open_gst_tax, fg_color="#f9a825", height=45, font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", fill="x", expand=True, padx=5)

    def create_kpi_card(self, parent, title, variable, color):
        card = ctk.CTkFrame(parent, fg_color=("white", "gray20"), corner_radius=12)
        color_bar = ctk.CTkFrame(card, fg_color=color, width=5, corner_radius=12)
        color_bar.pack(side="left", fill="y", padx=(0, 10))
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=15)
        ctk.CTkLabel(content, text=title, font=ctk.CTkFont(size=11), text_color=("gray50", "gray60")).pack(anchor="w")
        ctk.CTkLabel(content, textvariable=variable, font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(5, 0))
        return card

    def load_data_background(self):
        """Fetch statistics in background thread"""
        try:
            stats = self.get_statistics()
            self.root.after(0, lambda: self.update_stats(stats))
        except Exception as e:
            print(f"Error loading stats: {e}")

    def update_stats(self, stats):
        """Update UI with fetched statistics"""
        try:
            self.kpi_vars['revenue'].set(f"₹{stats['total_revenue']:,.2f}")
            self.kpi_vars['expenses'].set(f"₹{stats['total_expenses']:,.2f}")
            self.kpi_vars['profit'].set(f"₹{stats['net_profit']:,.2f}")
            self.kpi_vars['clients'].set(str(stats['total_clients']))
            self.kpi_vars['invoices'].set(str(stats['monthly_invoices']))
            self.kpi_vars['stock'].set(f"₹{stats['stock_value']:,.2f}")
        except Exception as e:
            print(f"Error updating stats UI: {e}")

    def create_footer(self, parent):
        footer_frame = ctk.CTkFrame(parent, fg_color=("gray85", "gray15"), height=35)
        footer_frame.pack(side="bottom", fill="x")
        footer_frame.pack_propagate(False)
        footer_label = ctk.CTkLabel(footer_frame, text=f"© 2025 {self.company_name} | Logged in: {datetime.now().strftime('%d-%m-%Y %H:%M')}", font=ctk.CTkFont(size=10), text_color=("gray40", "gray60"))
        footer_label.pack(pady=8)

    def get_statistics(self):
        try:
            invoices = self.db.load_json(self.company_name, "invoices.json") or []
            expenses = self.db.load_json(self.company_name, "expenses.json") or []
            clients = self.db.load_json(self.company_name, "clients.json") or []
            products = self.db.load_json(self.company_name, "products.json") or []
            
            total_revenue = sum(sum(item.get('line_total', 0) for item in inv.get('items', [])) for inv in invoices)
            total_expenses = sum(float(exp.get('amount', 0)) for exp in expenses)
            net_profit = total_revenue - total_expenses
            
            current_month = datetime.now().strftime("%Y-%m")
            monthly_invoices = len([inv for inv in invoices if inv.get('date', '').startswith(current_month)])
            stock_value = sum(p.get('stock_qty', 0) * p.get('unit_price', 0) for p in products)
            
            return {'total_revenue': total_revenue, 'total_expenses': total_expenses, 'net_profit': net_profit, 'total_clients': len(clients), 'monthly_invoices': monthly_invoices, 'stock_value': stock_value}
        except:
            return {'total_revenue': 0, 'total_expenses': 0, 'net_profit': 0, 'total_clients': 0, 'monthly_invoices': 0, 'stock_value': 0}

    def open_chart_of_accounts(self):
        try:
            self.app.show_chart_of_accounts(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Chart of Accounts:\n{str(e)}")

    def open_clients(self):
        try:
            self.app.show_clients(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Clients:\n{str(e)}")
    
    def open_vendors(self):
        try:
            self.app.show_vendors(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Vendors:\n{str(e)}")

    def open_invoices(self):
        try:
            self.app.show_invoices(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Invoices:\n{str(e)}")

    def open_expenses(self):
        try:
            self.app.show_expenses(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Expenses:\n{str(e)}")

    def open_reports(self):
        try:
            self.app.show_reports(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Reports:\n{str(e)}")

    def open_journal_entries(self):
        try:
            self.app.show_journal_entries(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Journal Entries:\n{str(e)}")

    def open_ledger(self):
        try:
            self.app.show_ledger(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Ledger:\n{str(e)}")

    def open_gst_tax(self):
        try:
            self.app.show_gst_tax(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open GST/Tax:\n{str(e)}")

    def open_inventory(self):
        try:
            self.app.show_inventory(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Inventory:\n{str(e)}")

    def open_payment_tracking(self):
        try:
            self.app.show_payment_tracking(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Payment Tracking:\n{str(e)}")

    def open_settings(self):
        self.app.show_settings()

    def open_erp_fi(self):
        try:
            from .sap.fi.gl import FIGLModule
            # For now, we only have GL implemented, so we open that directly or a menu if we had a main FI menu.
            # But the user asked for "ERP FI" which contains GL, AP, AR etc.
            # Since I only implemented GL so far, I will open GL.
            # Ideally, I should have a main FI menu that links to GL, AP, AR.
            # Let's assume FIGLModule is the entry point for now or create a main FI module later.
            # Actually, the user wants "ERP FI" -> "GL", "AP", etc.
            # So I should probably create a main FI module that lists these.
            # For this step, I'll just open GL as a placeholder for "ERP FI" or create a simple menu.
            # Let's create a simple FI menu in the dashboard or a separate class.
            # To keep it simple and stick to the plan, I will open the GL module for now as it's the only one ready.
            # Wait, the plan said "Create a new sap directory... update dashboard...".
            # I'll implement a temporary open_erp_fi that opens the GL module for demonstration.
            self.app.show_erp_fi_gl(self.company_data, self.user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open ERP FI:\n{str(e)}")

    def open_erp_co(self):
        messagebox.showinfo("ERP CO", "ERP COntrolling module is coming soon!")

    def open_erp_integration(self):
        messagebox.showinfo("SAP Integration", "SAP Integration module is coming soon!")

    def toggle_fullscreen(self):
        current = self.root.attributes('-fullscreen')
        if not current:
            # Entering fullscreen
            # Force maximized state first to avoid partial fullscreen issues on Windows
            try:
                self.root.state('zoomed')
                self.root.update_idletasks()
            except:
                pass
            
            self.root.attributes('-fullscreen', True)
            if hasattr(self.app, 'is_fullscreen'):
                self.app.is_fullscreen = True
        else:
            # Exiting fullscreen
            self.root.attributes('-fullscreen', False)
            if hasattr(self.app, 'is_fullscreen'):
                self.app.is_fullscreen = False

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.app.show_home_screen()

    def get_dashboard_logo(self):
        """Load company logo for dashboard header"""
        try:
            logo_path = self.company_data.get('logo_path')
            if logo_path:
                full_path = self.db.get_company_path(self.company_name) / logo_path
                if full_path.exists():
                    img = Image.open(full_path)
                    img = img.resize((40, 40), Image.Resampling.LANCZOS)
                    return ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))
        except Exception:
            pass
        return None
