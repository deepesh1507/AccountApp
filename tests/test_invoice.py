
import pytest
from unittest.mock import MagicMock, patch
import threading
from modules.invoice import InvoiceManagement

@pytest.fixture(autouse=True)
def mock_threading():
    """Mock threading to run tasks immediately"""
    with patch('threading.Timer') as mock_timer, \
         patch('threading.Thread') as mock_thread:
        
        def timer_side_effect(interval, function, args=None, kwargs=None):
            # Run immediately
            function(*args if args else [], **kwargs if kwargs else {})
            return MagicMock()
        mock_timer.side_effect = timer_side_effect
        
        def thread_side_effect(target=None, args=(), kwargs={}, daemon=None):
            # Run immediately
            if target:
                target(*args, **kwargs)
            return MagicMock()
        mock_thread.side_effect = thread_side_effect
        yield

@pytest.fixture(autouse=True)
def mock_performance_utils():
    """Mock performance optimizer utilities"""
    with patch('modules.invoice.show_loading_overlay'), \
         patch('modules.invoice.hide_loading_overlay'), \
         patch('modules.invoice.PerformanceOptimizer') as mock_perf:
        # Mock batch_insert to just insert immediately
        def batch_insert(tree, items):
            for item in items:
                tree.insert("", "end", values=item)
        mock_perf.batch_insert.side_effect = batch_insert
        yield

@pytest.fixture
def app_controller():
    return MagicMock()

@pytest.fixture
def root_window():
    root = MagicMock()
    return root

@pytest.fixture(autouse=True)
def mock_ctk():
    """Mock customtkinter widgets"""
    with patch('modules.invoice.ctk') as mock:
        yield mock

@pytest.fixture(autouse=True)
def mock_ttk():
    """Mock ttk widgets"""
    with patch('modules.invoice.ttk') as mock:
        yield mock

@pytest.fixture(autouse=True)
def mock_smart_widgets():
    """Mock smart widgets"""
    with patch('modules.invoice.SmartEntry'), \
         patch('modules.invoice.SmartNumberEntry'), \
         patch('modules.invoice.SmartDatePicker'), \
         patch('modules.invoice.SmartComboBox'), \
         patch('modules.invoice.EnhancedForm'):
        yield

@pytest.fixture
def invoice_module(root_window, sample_company_data, sample_user_data, app_controller, mock_db):
    """Fixture to initialize InvoiceManagement module with mocks"""
    # Patch DatabaseManager globally since it is imported inside methods
    with patch('modules.database_manager.DatabaseManager', return_value=mock_db):
        module = InvoiceManagement(root_window, sample_company_data, sample_user_data, app_controller)
        yield module

def test_initialization(invoice_module):
    """Test that the module initializes correctly"""
    assert invoice_module.company_name == "Test Company"
    assert invoice_module.invoices == []

def test_load_invoices(invoice_module, mock_db):
    """Test loading invoices from database"""
    mock_invoices = [
        {"invoice_id": "INV00001", "client_name": "Client A", "date": "2023-01-01", "items": [], "status": "Unpaid"}
    ]
    mock_db.load_json.return_value = mock_invoices
    
    # Trigger load
    invoice_module.load_invoices()
    
    # Since we mocked threading, run_async runs immediately.
    # But _fetch_data calls root.after(0, callback).
    # We need to execute the callback.
    args = invoice_module.root.after.call_args
    if args:
        callback = args[0][1]
        callback()
    
    assert len(invoice_module.invoices) == 1
    assert invoice_module.invoices[0]["invoice_id"] == "INV00001"
    mock_db.load_json.assert_called_with("Test Company", "invoices.json")

def test_search_invoices(invoice_module):
    """Test searching invoices"""
    invoice_module.invoices = [
        {"invoice_id": "INV001", "client_name": "Alpha"},
        {"invoice_id": "INV002", "client_name": "Beta"}
    ]
    
    # Mock search entry
    invoice_module.search_entry = MagicMock()
    invoice_module.search_entry.get.return_value = "alpha"
    
    # Calling search_invoices triggers debounce decorator
    # Which calls threading.Timer
    # Which we mocked to call function immediately
    invoice_module.search_invoices()
    
    assert len(invoice_module.filtered_invoices) == 1
    assert invoice_module.filtered_invoices[0]["invoice_id"] == "INV001"

def test_save_invoice_new(invoice_module, mock_db):
    """Test saving a new invoice"""
    values = {
        'invoice_id': 'INV999',
        'client': 'New Client',
        'date': '2023-10-27',
        'status': 'Draft'
    }
    items = [{'description': 'Test Item', 'qty': 1, 'rate': 100, 'line_total': 100}]
    dialog = MagicMock()
    
    with patch('modules.invoice.messagebox') as mock_mb:
        invoice_module._save_invoice(values, items, None, dialog)
        
        mock_mb.showinfo.assert_called_with("Success", "Invoice INV999 created")
        assert len(invoice_module.invoices) == 1
        assert invoice_module.invoices[0]['invoice_id'] == 'INV999'
        mock_db.save_json.assert_called()
        dialog.destroy.assert_called()

def test_save_invoice_update(invoice_module, mock_db):
    """Test updating an existing invoice"""
    existing = {'invoice_id': 'INV001', 'client_name': 'Old Client'}
    invoice_module.invoices = [existing]
    
    values = {
        'invoice_id': 'INV001',
        'client': 'Updated Client',
        'date': '2023-10-27',
        'status': 'Unpaid'
    }
    items = [{'description': 'Item 1', 'qty': 1, 'rate': 100, 'line_total': 100}]
    dialog = MagicMock()
    
    with patch('modules.invoice.messagebox') as mock_mb:
        invoice_module._save_invoice(values, items, existing, dialog)
        
        mock_mb.showinfo.assert_called_with("Success", "Invoice INV001 updated")
        assert invoice_module.invoices[0]['client_name'] == 'Updated Client'
        mock_db.save_json.assert_called()

def test_delete_invoice(invoice_module, mock_db):
    """Test deleting an invoice"""
    inv = {'invoice_id': 'INV001'}
    invoice_module.invoices = [inv]
    
    # Mock selection
    invoice_module.tree = MagicMock()
    invoice_module.tree.selection.return_value = ["item1"]
    invoice_module.tree.item.return_value = {'values': ["INV001"]}
    
    with patch('modules.invoice.messagebox') as mock_mb:
        mock_mb.askyesno.return_value = True
        invoice_module.delete_invoice()
        
        assert len(invoice_module.invoices) == 0
        mock_db.save_json.assert_called()

def test_validation_error(invoice_module):
    """Test validation during save"""
    values = {'invoice_id': '', 'client': ''} # Missing required fields
    items = []
    dialog = MagicMock()
    
    with patch('modules.invoice.messagebox') as mock_mb:
        invoice_module._save_invoice(values, items, None, dialog)
        mock_mb.showerror.assert_called()
        dialog.destroy.assert_not_called()
