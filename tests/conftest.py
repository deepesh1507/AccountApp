
import sys
import os
import pytest
from unittest.mock import MagicMock
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.database_manager import DatabaseManager

@pytest.fixture
def mock_db():
    """Fixture to provide a mocked DatabaseManager"""
    db = MagicMock(spec=DatabaseManager)
    
    # Setup default mock behaviors
    db.load_json.return_value = []
    db.save_json.return_value = True
    
    return db

@pytest.fixture
def sample_company_data():
    """Fixture for sample company data"""
    return {
        "company_name": "Test Company",
        "currency": "USD"
    }

@pytest.fixture
def sample_user_data():
    """Fixture for sample user data"""
    return {
        "username": "testuser",
        "role": "admin"
    }
