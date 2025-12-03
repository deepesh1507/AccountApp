import unittest
import customtkinter as ctk
from modules.erp.co.om import COOMModule
from modules.erp.co.io import COIOModule
from modules.erp.co.pca import COPCAModule
from modules.erp.co.pa import COPAModule
from modules.erp.co.pc import COPCModule
from modules.erp.co.ml import COOMLModule

class TestERPCOModules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.company_data = {"company_name": "Test Company", "currency": "USD"}
        cls.user_data = {"username": "admin", "role": "admin"}
        cls.app_controller = None

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_om_module(self):
        """Test CO-OM Module"""
        module = COOMModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP CO - Overhead Management (CO-OM)")
        module.open_cost_center()
        self.assertEqual(module.current_form.title_text, "Cost Center Master Data (KS01)")

    def test_io_module(self):
        """Test CO-IO Module"""
        module = COIOModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP CO - Internal Orders (CO-IO)")
        module.open_order_master()
        self.assertEqual(module.current_form.title_text, "Internal Order Master Data (KO01)")

    def test_pca_module(self):
        """Test CO-PCA Module"""
        module = COPCAModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP CO - Profit Center Accounting (CO-PCA)")
        module.open_pc_master()
        self.assertEqual(module.current_form.title_text, "Profit Center Master Data (KE51)")

    def test_pa_module(self):
        """Test CO-PA Module"""
        module = COPAModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP CO - Profitability Analysis (CO-PA)")
        module.open_operating_concern()
        self.assertEqual(module.current_form.title_text, "Operating Concern (KEA0)")

    def test_pc_module(self):
        """Test CO-PC Module"""
        module = COPCModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP CO - Product Costing (CO-PC)")
        module.open_cost_estimate()
        self.assertEqual(module.current_form.title_text, "Material Cost Estimate (CK11N)")

    def test_ml_module(self):
        """Test CO-ML Module"""
        module = COOMLModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP CO - Material Ledger (CO-ML)")
        module.open_activate()
        self.assertEqual(module.current_form.title_text, "Activate Material Ledger (CKMSTART)")

if __name__ == "__main__":
    unittest.main()
