
import pytest
from unittest.mock import MagicMock, patch
import threading
from modules.journal_entries import JournalEntries

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
    with patch('modules.journal_entries.show_loading_overlay'), \
         patch('modules.journal_entries.hide_loading_overlay'), \
         patch('modules.journal_entries.PerformanceOptimizer') as mock_perf:
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
    with patch('modules.journal_entries.ctk') as mock:
        yield mock

@pytest.fixture(autouse=True)
def mock_ttk():
    """Mock ttk widgets"""
    with patch('modules.journal_entries.ttk') as mock:
        yield mock

@pytest.fixture(autouse=True)
def mock_smart_widgets():
    """Mock smart widgets"""
    with patch('modules.journal_entries.SmartEntry'), \
         patch('modules.journal_entries.SmartNumberEntry'), \
         patch('modules.journal_entries.SmartDatePicker'), \
         patch('modules.journal_entries.SmartComboBox'), \
         patch('modules.journal_entries.EnhancedForm'):
        yield

@pytest.fixture
def journal_module(root_window, sample_company_data, sample_user_data, app_controller, mock_db):
    """Fixture to initialize JournalEntries module with mocks"""
    # Patch DatabaseManager globally since it is imported inside methods
    with patch('modules.database_manager.DatabaseManager', return_value=mock_db):
        module = JournalEntries(root_window, sample_company_data, sample_user_data, app_controller)
        yield module

def test_initialization(journal_module):
    """Test that the module initializes correctly"""
    assert journal_module.company_name == "Test Company"
    assert journal_module.entries == []

def test_load_entries(journal_module, mock_db):
    """Test loading entries from database"""
    mock_entries = [
        {"entry_id": "JV-00001", "date": "2023-01-01", "type": "Journal", "narration": "Test Entry", "lines": []}
    ]
    mock_db.load_json.side_effect = [
        [], # accounts
        mock_entries # entries
    ]
    
    # Trigger load
    journal_module.load_entries()
    
    # Execute callback
    args = journal_module.root.after.call_args
    if args:
        callback = args[0][1]
        callback()
    
    assert len(journal_module.entries) == 1
    assert journal_module.entries[0]["entry_id"] == "JV-00001"

def test_search_entries(journal_module):
    """Test searching entries"""
    journal_module.entries = [
        {"entry_id": "JV-00001", "narration": "Opening Balance"},
        {"entry_id": "JV-00002", "narration": "Rent Payment"}
    ]
    
    # Mock search entry and type filter
    journal_module.search_entry = MagicMock()
    journal_module.search_entry.get.return_value = "Rent"
    journal_module.type_filter = MagicMock()
    journal_module.type_filter.get.return_value = "All Types"
    
    journal_module.search_entries()
    
    assert len(journal_module.filtered_entries) == 1
    assert journal_module.filtered_entries[0]["entry_id"] == "JV-00002"

def test_filter_entries(journal_module):
    """Test filtering by type"""
    journal_module.entries = [
        {"entry_id": "JV-00001", "type": "Journal"},
        {"entry_id": "JV-00002", "type": "Payment"}
    ]
    
    # Mock the type filter widget
    journal_module.type_filter = MagicMock()
    journal_module.type_filter.get.return_value = "Payment"
    journal_module.search_entry = MagicMock()
    journal_module.search_entry.get.return_value = ""
    
    journal_module.filter_entries()
    
    assert len(journal_module.filtered_entries) == 1
    assert journal_module.filtered_entries[0]["type"] == "Payment"

def test_save_entry_new(journal_module, mock_db):
    """Test saving a new entry"""
    values = {
        'entry_no': 'JV-999',
        'date': '2023-10-27',
        'entry_type': 'Journal',
        'narration': 'Test Narration'
    }
    
    # Mock widgets for lines
    line_w = {
        'account': MagicMock(),
        'debit': MagicMock(),
        'credit': MagicMock()
    }
    line_w['account'].get.return_value = "1001 - Cash"
    line_w['debit'].get.return_value = "100"
    line_w['credit'].get.return_value = "0"
    
    line_w2 = {
        'account': MagicMock(),
        'debit': MagicMock(),
        'credit': MagicMock()
    }
    line_w2['account'].get.return_value = "2001 - Sales"
    line_w2['debit'].get.return_value = "0"
    line_w2['credit'].get.return_value = "100"
    
    journal_module._current_form_widgets = {
        'id': MagicMock(),
        'date': MagicMock(),
        'type': MagicMock(),
        'narration': MagicMock(),
        'lines': [line_w, line_w2]
    }
    journal_module._current_form_widgets['id'].get.return_value = 'JV-999'
    
    dialog = MagicMock()
    
    with patch('modules.journal_entries.messagebox') as mock_mb:
        journal_module._save_entry(values, [], None, dialog)
        
        mock_mb.showinfo.assert_called_with("Success", "Entry created")
        assert len(journal_module.entries) == 1
        assert journal_module.entries[0]['entry_id'] == 'JV-999'
        mock_db.save_json.assert_called()
        dialog.destroy.assert_called()

def test_save_entry_unbalanced(journal_module):
    """Test saving unbalanced entry"""
    values = {'entry_no': 'JV-999', 'date': '2023-10-27'}
    
    line_w = {
        'account': MagicMock(),
        'debit': MagicMock(),
        'credit': MagicMock()
    }
    line_w['account'].get.return_value = "1001 - Cash"
    line_w['debit'].get.return_value = "100"
    line_w['credit'].get.return_value = "0"
    
    line_w2 = {
        'account': MagicMock(),
        'debit': MagicMock(),
        'credit': MagicMock()
    }
    line_w2['account'].get.return_value = "2001 - Sales"
    line_w2['debit'].get.return_value = "0"
    line_w2['credit'].get.return_value = "90" # Unbalanced
    
    journal_module._current_form_widgets = {
        'id': MagicMock(),
        'date': MagicMock(),
        'type': MagicMock(),
        'narration': MagicMock(),
        'lines': [line_w, line_w2]
    }
    journal_module._current_form_widgets['id'].get.return_value = 'JV-999'
    
    dialog = MagicMock()
    
    with patch('modules.journal_entries.messagebox') as mock_mb:
        journal_module._save_entry(values, [], None, dialog)
        mock_mb.showerror.assert_called()
        dialog.destroy.assert_not_called()

def test_delete_entry(journal_module, mock_db):
    """Test deleting an entry"""
    entry = {'entry_id': 'JV-001'}
    journal_module.entries = [entry]
    
    # Mock selection
    journal_module.tree = MagicMock()
    journal_module.tree.selection.return_value = ["item1"]
    journal_module.tree.item.return_value = {'values': ["JV-001"]}
    
    with patch('modules.journal_entries.messagebox') as mock_mb:
        mock_mb.askyesno.return_value = True
        journal_module.delete_entry()
        
        assert len(journal_module.entries) == 0
        mock_db.save_json.assert_called()
