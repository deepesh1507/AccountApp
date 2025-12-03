import pytest
from pathlib import Path
import shutil
import json
from modules.database_manager import DatabaseManager

@pytest.fixture
def db_manager(tmp_path):
    """Setup temporary test database"""
    test_data_dir = tmp_path / "test_data"
    test_data_dir.mkdir()
    db = DatabaseManager()
    db.base_dir = test_data_dir
    db.initialize_storage()
    yield db
    shutil.rmtree(test_data_dir)

def test_create_company(db_manager):
    """Test company creation"""
    result = db_manager.create_company_structure({
        "name": "Test Company",
        "display_name": "Test Co."
    })
    assert result is True
    
    companies = db_manager.get_all_companies()
    assert "Test Company" in companies

def test_delete_company(db_manager):
    """Test company deletion"""
    # Create test company
    db_manager.create_company_structure({"name": "Test Company"})
    
    # Delete company
    result = db_manager.delete_company("Test Company")
    assert result is True
    
    # Verify deletion
    companies = db_manager.get_all_companies()
    assert "Test Company" not in companies

def test_load_save_json(db_manager):
    """Test JSON operations"""
    test_data = {"test": "data"}
    
    # Create test company
    db_manager.create_company_structure({"name": "Test Company"})
    
    # Test save and load
    assert db_manager.save_json("Test Company", "test.json", test_data)
    loaded_data = db_manager.load_json("Test Company", "test.json")
    assert loaded_data == test_data
