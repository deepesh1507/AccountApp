import unittest
import customtkinter as ctk
from modules.erp.fi.bl import FIBLModule
from modules.erp.fi.tr import FITRModule
from modules.erp.fi.sl import FISLModule
from modules.erp.fi.cl import FICLModule

class TestSAPFIRemainingModules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.company_data = {"company_name": "Test Company", "currency": "USD"}
        cls.user_data = {"username": "admin", "role": "admin"}
        cls.app_controller = None

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_bl_module(self):
        """Test FI-BL Module"""
        module = FIBLModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP FI - Bank Accounting (FI-BL)")
        module.open_house_bank()
        self.assertEqual(module.current_form.title_text, "House Bank Setup (FI12)")

    def test_tr_module(self):
        """Test FI-TR Module"""
        module = FITRModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP FI - Treasury (FI-TR)")
        module.open_cash_mgmt()
        self.assertEqual(module.current_form.title_text, "Cash Management")

    def test_sl_module(self):
        """Test FI-SL Module"""
        module = FISLModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP FI - Special Purpose Ledger (FI-SL)")
        module.open_sl_config()
        self.assertEqual(module.current_form.title_text, "Special Ledger Configuration")

    def test_cl_module(self):
        """Test FI-CL Module"""
        module = FICLModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP FI - Credit Management (FI-CL)")
        module.open_credit_master()
        self.assertEqual(module.current_form.title_text, "Credit Master Data (FD32)")

if __name__ == "__main__":
    unittest.main()
