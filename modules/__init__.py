"""AccountApp Modules"""
import sys
import logging
from pathlib import Path
import customtkinter as ctk

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Initialize customtkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# Core imports
from .database_manager import DatabaseManager
from .base_module import BaseModule
from .home_screen import HomeScreen
from .create_company import CreateCompany
from .select_company import SelectCompany
from .company_login import CompanyLogin
from .dashboard import Dashboard

__all__ = [
    'DatabaseManager',
    'BaseModule',
    'HomeScreen',
    'CreateCompany',
    'SelectCompany',
    'CompanyLogin',
    'Dashboard'
]
