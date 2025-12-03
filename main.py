"""
Main Entry Point for Accounting App
Features:
- Launch Home Screen
- Navigate between Create Company, Select Company, and Login modules
"""

import sys
from typing import Any
import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox
import logging
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add modules path to system path
sys.path.insert(0, str(Path(__file__).parent))

# Module Imports
from modules.home_screen import HomeScreen
from modules.create_company import CreateCompany
from modules.select_company import SelectCompany
from modules.company_login import CompanyLogin
from modules.dashboard import Dashboard
from modules.chart_of_accounts import ChartOfAccounts
from modules.clients import ClientsManagement
from modules.vendors import VendorsManagement  # NEW: Vendors Management
from modules.invoice import InvoiceManagement
from modules.expenses import ExpensesManagement
from modules.enhanced_expenses import EnhancedExpensesManagement  # NEW: Enhanced UI
from modules.reports import ReportsAnalytics
from modules.settings import SettingsScreen
from modules.edit_company import EditCompany
from modules.journal_entries import JournalEntries
from modules.ledger import Ledger
from modules.gst_tax import GSTTaxManagement
from modules.inventory import InventoryManagement
from modules.payment_tracking import PaymentTracking
from modules.erp.fi.gl import FIGLModule  # ERP FI-GL Module
from modules.erp.fi.ap import FIAPModule  # ERP FI-AP Module
from modules.erp.fi.ar import FIARModule  # ERP FI-AR Module
from modules.erp.fi.aa import FIAAModule  # ERP FI-AA Module
from modules.erp.fi.bl import FIBLModule  # ERP FI-BL Module
from modules.erp.fi.tr import FITRModule  # ERP FI-TR Module
from modules.erp.fi.sl import FISLModule  # ERP FI-SL Module
from modules.erp.fi.cl import FICLModule  # ERP FI-CL Module
from modules.erp.co.om import COOMModule  # ERP CO-OM Module
from modules.erp.co.io import COIOModule  # ERP CO-IO Module
from modules.erp.co.pca import COPCAModule  # ERP CO-PCA Module
from modules.erp.co.pa import COPAModule  # ERP CO-PA Module
from modules.erp.co.pc import COPCModule  # ERP CO-PC Module
from modules.erp.co.ml import COOMLModule  # ERP CO-ML Module
from modules.erp.integration.mm_fi import MMFIModule  # SAP MM-FI Module
from modules.erp.integration.sd_fi import SDFIModule  # SAP SD-FI Module
from modules.erp.integration.pp_co import PPCOModule  # SAP PP-CO Module
from modules.erp.integration.hcm_fi import HCMFIModule  # SAP HCM-FI Module
from modules.reports_erp import ERPReports  # ERP Reporting Module

# UI Configuration
USE_ENHANCED_UI = True  # Enhanced UI with better performance, validation, and keyboard shortcuts


class AccountingApp:
    """
    Main Application Controller.
    Handles window management and navigation between different screens.
    """

    def __init__(self):
        # Load saved settings BEFORE creating the window
        self.settings = self.load_settings()
        
        # Apply theme and color scheme from settings
        theme = self.settings.get("theme", "system")
        color_scheme = self.settings.get("color_scheme", "blue")
        
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme(color_scheme)
        
        self.root = ctk.CTk()
        self.root.title("AccountApp - Professional Accounting System")
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window to 90% of screen size for better visibility
        window_width = int(screen_width * 0.9)
        window_height = int(screen_height * 0.9)
        
        # Calculate position to center window
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        # Set window size and position (centered on screen)
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        
        # Set minimum size to prevent too small windows
        self.root.minsize(1000, 600)
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Bind ESC key to exit fullscreen
        self.root.bind("<Escape>", self.exit_fullscreen)
        
        # Start maximized for best experience
        try:
            self.root.state('zoomed')  # Windows-specific maximize
        except:
            pass  # Fallback for other OS
        
        logger.info("AccountingApp initialized")

        self.current_screen = None
        self.is_fullscreen = False

        # Set window close behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start with Home Screen
        self.show_home_screen()

    # ---------- Navigation Methods ----------
    def show_home_screen(self):
        """Clears the window and displays the Home Screen."""
        self.clear_window()
        self.current_screen = HomeScreen(self.root, self)

    def show_create_company(self):
        """Clears the window and displays the Create Company Screen."""
        self.clear_window()
        self.current_screen = CreateCompany(self.root, self)

    def show_select_company(self):
        """Clears the window and displays the Select Company Screen."""
        self.clear_window()
        self.current_screen = SelectCompany(self.root, self)

    def show_company_login(self, company_data: dict[str, Any]):
        """Clears the window and displays the Company Login Screen."""
        self.clear_window()
        self.current_screen = CompanyLogin(self.root, company_data, self)

    def show_dashboard(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the main Dashboard."""
        self.clear_window()
        self.current_screen = Dashboard(self.root, company_data, user_data, self)

    def show_chart_of_accounts(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the Chart of Accounts screen."""
        self.clear_window()
        self.current_screen = ChartOfAccounts(self.root, company_data, user_data, self)

    def show_clients(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the Clients Management screen."""
        self.clear_window()
        self.current_screen = ClientsManagement(self.root, company_data, user_data, self)
    
    def show_vendors(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the Vendors Management screen."""
        self.clear_window()
        self.current_screen = VendorsManagement(self.root, company_data, user_data, self)

    def show_invoices(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the Invoice Management screen."""
        self.clear_window()
        self.current_screen = InvoiceManagement(self.root, company_data, user_data, self)

    def show_expenses(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the Expenses Management screen."""
        self.clear_window()
        if USE_ENHANCED_UI:
            self.current_screen = EnhancedExpensesManagement(self.root, company_data, user_data, self)
        else:
            self.current_screen = ExpensesManagement(self.root, company_data, user_data, self)

    def show_reports(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the Reports & Analytics screen."""
        self.clear_window()
        self.current_screen = ReportsAnalytics(self.root, company_data, user_data, self)

    def show_settings(self):
        """Clears the window and displays the Settings Screen."""
        self.clear_window()
        self.current_screen = SettingsScreen(self.root, self)

    def show_edit_company(self, company_data: dict[str, Any]):
        """Clears the window and displays the Edit Company Screen."""
        self.clear_window()
        self.current_screen = EditCompany(self.root, self, company_data)

    def show_journal_entries(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the Journal Entries screen."""
        self.clear_window()
        self.current_screen = JournalEntries(self.root, company_data, user_data, self)

    def show_ledger(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the Ledger screen."""
        self.clear_window()
        self.current_screen = Ledger(self.root, company_data, user_data, self)

    def show_gst_tax(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the GST/Tax Management screen."""
        self.clear_window()
        self.current_screen = GSTTaxManagement(self.root, company_data, user_data, self)

    def show_inventory(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the Inventory Management screen."""
        self.clear_window()
        self.current_screen = InventoryManagement(self.root, company_data, user_data, self)

    def show_payment_tracking(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the Payment Tracking screen."""
        self.clear_window()
        self.current_screen = PaymentTracking(self.root, company_data, user_data, self)

    def show_erp_fi_gl(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP FI-GL module."""
        self.clear_window()
        self.current_screen = FIGLModule(self.root, company_data, user_data, self)

    def show_erp_fi_ap(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP FI-AP module."""
        self.clear_window()
        self.current_screen = FIAPModule(self.root, company_data, user_data, self)

    def show_erp_fi_ar(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP FI-AR module."""
        self.clear_window()
        self.current_screen = FIARModule(self.root, company_data, user_data, self)

    def show_erp_fi_aa(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP FI-AA module."""
        self.clear_window()
        self.current_screen = FIAAModule(self.root, company_data, user_data, self)

    def show_erp_fi_bl(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP FI-BL module."""
        self.clear_window()
        self.current_screen = FIBLModule(self.root, company_data, user_data, self)

    def show_erp_fi_tr(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP FI-TR module."""
        self.clear_window()
        self.current_screen = FITRModule(self.root, company_data, user_data, self)

    def show_erp_fi_sl(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP FI-SL module."""
        self.clear_window()
        self.current_screen = FISLModule(self.root, company_data, user_data, self)

    def show_erp_fi_cl(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP FI-CL module."""
        self.clear_window()
        self.current_screen = FICLModule(self.root, company_data, user_data, self)

    # --- CO Modules ---

    def show_erp_co_om(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP CO-OM module."""
        self.clear_window()
        self.current_screen = COOMModule(self.root, company_data, user_data, self)

    def show_erp_co_io(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP CO-IO module."""
        self.clear_window()
        self.current_screen = COIOModule(self.root, company_data, user_data, self)

    def show_erp_co_pca(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP CO-PCA module."""
        self.clear_window()
        self.current_screen = COPCAModule(self.root, company_data, user_data, self)

    def show_erp_co_pa(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP CO-PA module."""
        self.clear_window()
        self.current_screen = COPAModule(self.root, company_data, user_data, self)

    def show_erp_co_pc(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP CO-PC module."""
        self.clear_window()
        self.current_screen = COPCModule(self.root, company_data, user_data, self)

    def show_erp_co_ml(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP CO-ML module."""
        self.clear_window()
        self.current_screen = COOMLModule(self.root, company_data, user_data, self)

    # --- Integration Modules ---

    def show_erp_int_mm_fi(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP MM-FI module."""
        self.clear_window()
        self.current_screen = MMFIModule(self.root, company_data, user_data, self)

    def show_erp_int_sd_fi(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP SD-FI module."""
        self.clear_window()
        self.current_screen = SDFIModule(self.root, company_data, user_data, self)

    def show_erp_int_pp_co(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP PP-CO module."""
        self.clear_window()
        self.current_screen = PPCOModule(self.root, company_data, user_data, self)

    def show_erp_int_hcm_fi(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP HCM-FI module."""
        self.clear_window()
        self.current_screen = HCMFIModule(self.root, company_data, user_data, self)

    def show_erp_reports(self, company_data: dict[str, Any], user_data: dict[str, Any]):
        """Clears the window and displays the ERP Reports module."""
        self.clear_window()
        self.current_screen = ERPReports(self.root, company_data, user_data, self)

    # ---------- Utility ----------
    def clear_window(self):
        """Destroys all widgets in the root window to prepare for a new screen."""
        for widget in self.root.winfo_children():
            widget.destroy()


    def exit_fullscreen(self, event=None):
        """Exit fullscreen mode when ESC is pressed"""
        if self.root.attributes('-fullscreen'):
            self.root.attributes('-fullscreen', False)
            self.is_fullscreen = False
        return "break"
    
    def load_settings(self):
        """Load application settings from file"""
        settings_file = Path(__file__).parent / "data" / "app_settings.json"
        default_settings = {
            "theme": "system",
            "color_scheme": "blue",
            "font_family": "Segoe UI",
            "font_size": 12
        }
        
        try:
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    loaded = json.load(f)
                    default_settings.update(loaded)
        except Exception as e:
            logger.warning(f"Could not load settings: {e}")
        
        return default_settings

    def on_closing(self):
        """Shows a confirmation dialog when the user tries to close the app."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit the Accounting App?"):
            self.root.destroy()


# ---------- Run Application ----------
if __name__ == "__main__":
    app = AccountingApp()
    app.root.mainloop()
