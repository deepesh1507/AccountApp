import unittest
import customtkinter as ctk
from modules.erp.integration.mm_fi import MMFIModule
from modules.erp.integration.sd_fi import SDFIModule
from modules.erp.integration.pp_co import PPCOModule
from modules.erp.integration.hcm_fi import HCMFIModule

class TestERPIntegrationModules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.company_data = {"company_name": "Test Company", "currency": "USD"}
        cls.user_data = {"username": "admin", "role": "admin"}
        cls.app_controller = None

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_mm_fi_module(self):
        """Test MM-FI Module"""
        module = MMFIModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP Integration - MM -> FI (Procurement)")
        module.open_obyc()
        self.assertEqual(module.current_form.title_text, "Automatic Account Determination (OBYC)")

    def test_sd_fi_module(self):
        """Test SD-FI Module"""
        module = SDFIModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP Integration - SD -> FI (Sales)")
        module.open_vkoa()
        self.assertEqual(module.current_form.title_text, "Revenue Account Determination (VKOA)")

    def test_pp_co_module(self):
        """Test PP-CO Module"""
        module = PPCOModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP Integration - PP -> CO (Production)")
        module.open_work_center()
        self.assertEqual(module.current_form.title_text, "Work Center Costing")

    def test_hcm_fi_module(self):
        """Test HCM-FI Module"""
        module = HCMFIModule(self.root, self.company_data, self.user_data, self.app_controller)
        self.assertEqual(module.get_module_title(), "ERP Integration - HCM -> FI (Payroll)")
        module.open_wage_type()
        self.assertEqual(module.current_form.title_text, "Wage Type Posting")

if __name__ == "__main__":
    unittest.main()
