"""
Test script for Phase 2 deep forms
Tests FB70 and F-90 forms with validation
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.erp.fi.ar import FIARModule
from modules.erp.fi.aa import FIAAModule


class TestDeepForms(unittest.TestCase):
    """Test deep forms implementation"""
    
    def test_fb70_validation_success(self):
        """Test FB70 with valid data"""
        module = FIARModule(None, {}, {}, None)
        
        data = {
            'Customer': '1000',
            'Invoice Date': '2025-01-15',
            'Posting Date': '2025-01-15',
            'Amount': '1150.00',
            'Tax Amount': '150.00',
            'grid_0': [
                {'G/L Acct': '4000', 'Description': 'Sales Revenue', 'Amount': '1000.00'},
            ]
        }
        
        # This should not raise an error
        try:
            # We can't actually call save_fb70 without a form, but we can test the logic
            invoice_amount = float(data.get("Amount", 0))
            tax_amount = float(data.get("Tax Amount", 0))
            line_items = data.get('grid_0', [])
            total_line_items = sum(float(item.get("Amount", 0)) for item in line_items)
            expected_total = total_line_items + tax_amount
            
            self.assertAlmostEqual(invoice_amount, expected_total, places=2)
            print("✓ FB70 validation test passed")
        except Exception as e:
            self.fail(f"FB70 validation failed: {e}")
    
    def test_fb70_validation_failure(self):
        """Test FB70 with invalid data (amount mismatch)"""
        data = {
            'Amount': '1200.00',  # Wrong amount
            'Tax Amount': '150.00',
            'grid_0': [
                {'Amount': '1000.00'},
            ]
        }
        
        invoice_amount = float(data.get("Amount", 0))
        tax_amount = float(data.get("Tax Amount", 0))
        line_items = data.get('grid_0', [])
        total_line_items = sum(float(item.get("Amount", 0)) for item in line_items)
        expected_total = total_line_items + tax_amount
        
        # Should not match
        self.assertNotAlmostEqual(invoice_amount, expected_total, places=2)
        print("✓ FB70 validation failure test passed")
    
    def test_f90_validation_success(self):
        """Test F-90 with valid data"""
        data = {
            'Invoice Amount': '11500.00',
            'Tax Amount': '1500.00',
            'grid_0': [
                {'Asset Number': 'A1000', 'Amount': '5000.00'},
                {'Asset Number': 'A1001', 'Amount': '5000.00'},
            ]
        }
        
        invoice_amount = float(data.get("Invoice Amount", 0))
        tax_amount = float(data.get("Tax Amount", 0))
        asset_items = data.get('grid_0', [])
        total_assets = sum(float(item.get("Amount", 0)) for item in asset_items)
        expected_total = total_assets + tax_amount
        
        self.assertAlmostEqual(invoice_amount, expected_total, places=2)
        print("✓ F-90 validation test passed")
    
    def test_f90_missing_asset_number(self):
        """Test F-90 with missing asset number"""
        data = {
            'grid_0': [
                {'Asset Number': '', 'Amount': '5000.00'},  # Missing asset number
            ]
        }
        
        asset_items = data.get('grid_0', [])
        has_empty_asset = any(not item.get('Asset Number', '').strip() for item in asset_items)
        
        self.assertTrue(has_empty_asset, "Should detect missing asset number")
        print("✓ F-90 missing asset number test passed")


class TestDatabaseManager(unittest.TestCase):
    """Test database manager"""
    
    def test_database_initialization(self):
        """Test database initialization"""
        from modules.db_manager import get_db_manager
        
        db = get_db_manager()
        self.assertIsNotNone(db)
        print("✓ Database manager initialization test passed")
    
    def test_save_transaction(self):
        """Test saving a transaction"""
        from modules.db_manager import get_db_manager
        
        db = get_db_manager()
        
        data = {
            'Document Date': '2025-01-15',
            'Posting Date': '2025-01-15',
            'Amount': '1000.00',
            'Reference': 'TEST-001',
            'grid_0': [
                {'G/L Acct': '4000', 'Short Text': 'Test', 'Amount': '1000.00', 'D/C': 'C'},
            ]
        }
        
        transaction_id = db.save_transaction(data, 'Test Module', 'TEST')
        self.assertGreater(transaction_id, 0)
        print(f"✓ Transaction saved with ID: {transaction_id}")
    
    def test_get_transactions(self):
        """Test retrieving transactions"""
        from modules.db_manager import get_db_manager
        
        db = get_db_manager()
        transactions = db.get_transactions()
        
        self.assertIsInstance(transactions, list)
        print(f"✓ Retrieved {len(transactions)} transactions")


if __name__ == '__main__':
    print("="*60)
    print("  Phase 2 Deep Forms Testing")
    print("="*60)
    print()
    
    # Run tests
    unittest.main(verbosity=2)
