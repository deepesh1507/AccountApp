import unittest
import customtkinter as ctk
from modules.erp.fi.gl import FIGLModule
from modules.erp.fi.ap import FIAPModule

class TestDeepForms(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.company_data = {"company_name": "Test Company", "currency": "USD"}
        cls.user_data = {"username": "admin", "role": "admin"}
        cls.app_controller = None

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def test_fb50_structure(self):
        """Test FB50 Form Structure"""
        module = FIGLModule(self.root, self.company_data, self.user_data, self.app_controller)
        module.open_fb50()
        
        # Check title
        self.assertEqual(module.current_form.title_text, "Enter G/L Account Document (FB50)")
        
        # Check for grid
        has_grid = False
        for widget in module.current_form.scrollable_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                # Check if it looks like a grid container (has "Line Items" label)
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel) and child.cget("text") == "Line Items":
                        has_grid = True
                        break
        self.assertTrue(has_grid, "FB50 should have a Line Items grid")

    def test_fb60_structure(self):
        """Test FB60 Form Structure"""
        module = FIAPModule(self.root, self.company_data, self.user_data, self.app_controller)
        module.open_fb60()
        
        # Check title
        self.assertEqual(module.current_form.title_text, "Vendor Invoice (FB60)")
        
        # Check for grid
        has_grid = False
        for widget in module.current_form.scrollable_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel) and child.cget("text") == "G/L Account Items":
                        has_grid = True
                        break
        self.assertTrue(has_grid, "FB60 should have a G/L Account Items grid")

if __name__ == "__main__":
    unittest.main()
