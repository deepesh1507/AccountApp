import unittest
import customtkinter as ctk
from modules.erp.fi.ap import FIAPModule
from modules.erp.fi.ar import FIARModule
from modules.erp.fi.aa import FIAAModule

class TestSAPFIModules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.company_data = {"company_name": "Test Company", "currency": "USD"}
        cls.user_data = {"username": "admin", "role": "admin"}
        cls.app_controller = None

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_ap_module(self):
        """Test FI-AP Module"""
        module = FIAPModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP FI - Accounts Payable (FI-AP)")
        module.open_vendor_master()
        self.assertEqual(module.current_form.title_text, "Vendor Master Data")

    def test_ar_module(self):
        """Test FI-AR Module"""
        module = FIARModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP FI - Accounts Receivable (FI-AR)")
        module.open_customer_master()
        self.assertEqual(module.current_form.title_text, "Customer Master Data")

    def test_aa_module(self):
        """Test FI-AA Module"""
        module = FIAAModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP FI - Asset Accounting (FI-AA)")
        module.open_asset_master()
        self.assertEqual(module.current_form.title_text, "Asset Master Creation (AS01)")

if __name__ == "__main__":
    unittest.main()
