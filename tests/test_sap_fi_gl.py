import unittest
import customtkinter as ctk
from modules.erp.fi.gl import FIGLModule

class TestFIGLModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.company_data = {"company_name": "Test Company", "currency": "USD"}
        cls.user_data = {"username": "admin", "role": "admin"}
        cls.app_controller = None  # Mock controller

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_init(self):
        """Test module initialization"""
        module = FIGLModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertIsInstance(module, FIGLModule)
        self.assertEqual(module.get_module_title(), "ERP FI - General Ledger (FI-GL)")

    def test_open_chart_of_accounts(self):
        """Test opening Chart of Accounts form"""
        module = FIGLModule(self.root, self.company_data, self.user_data, self.app_controller)
        # This will create the form widgets
        module.open_chart_of_accounts()
        self.assertIsNotNone(module.current_form)
        self.assertEqual(module.current_form.title_text, "Chart of Accounts")

    def test_open_company_code_config(self):
        """Test opening Company Code Config form"""
        module = FIGLModule(self.root, self.company_data, self.user_data, self.app_controller)
        module.open_company_code_config()
        self.assertIsNotNone(module.current_form)
        self.assertEqual(module.current_form.title_text, "Company Code Configuration")

if __name__ == "__main__":
    unittest.main()
