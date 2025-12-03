"""
Fiscal Year Management Module
Handles fiscal year periods, period locking, and year-end closing.
"""

import logging
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from pathlib import Path
import json

from modules.error_handler import BusinessRuleError, ValidationError

logger = logging.getLogger(__name__)


class FiscalPeriod:
    """Represents a fiscal period (month)"""
    
    def __init__(self, year: int, month: int, is_locked: bool = False):
        self.year = year
        self.month = month
        self.is_locked = is_locked
        self.start_date = date(year, month, 1)
        
        # Calculate end date
        if month == 12:
            self.end_date = date(year, 12, 31)
        else:
            next_month = date(year, month + 1, 1)
            from datetime import timedelta
            self.end_date = next_month - timedelta(days=1)
    
    def contains_date(self, check_date: date) -> bool:
        """Check if a date falls within this period"""
        return self.start_date <= check_date <= self.end_date
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'year': self.year,
            'month': self.month,
            'is_locked': self.is_locked,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FiscalPeriod':
        """Create from dictionary"""
        return cls(data['year'], data['month'], data.get('is_locked', False))


class FiscalYear:
    """Represents a fiscal year with periods"""
    
    def __init__(self, start_date: date, company_name: str):
        self.start_date = start_date
        self.company_name = company_name
        self.periods: List[FiscalPeriod] = []
        self.is_closed = False
        
        # Generate 12 periods
        self._generate_periods()
    
    def _generate_periods(self):
        """Generate 12 monthly periods"""
        current_date = self.start_date
        
        for _ in range(12):
            period = FiscalPeriod(current_date.year, current_date.month)
            self.periods.append(period)
            
            # Move to next month
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
    
    def get_period_for_date(self, check_date: date) -> Optional[FiscalPeriod]:
        """Get the period that contains a specific date"""
        for period in self.periods:
            if period.contains_date(check_date):
                return period
        return None
    
    def is_date_in_locked_period(self, check_date: date) -> bool:
        """Check if a date is in a locked period"""
        period = self.get_period_for_date(check_date)
        return period.is_locked if period else False
    
    def lock_period(self, year: int, month: int):
        """Lock a specific period"""
        for period in self.periods:
            if period.year == year and period.month == month:
                period.is_locked = True
                logger.info(f"Locked period: {year}-{month:02d}")
                return
    
    def unlock_period(self, year: int, month: int):
        """Unlock a specific period"""
        for period in self.periods:
            if period.year == year and period.month == month:
                period.is_locked = False
                logger.info(f"Unlocked period: {year}-{month:02d}")
                return
    
    def close_year(self):
        """Close the fiscal year (locks all periods)"""
        for period in self.periods:
            period.is_locked = True
        self.is_closed = True
        logger.info(f"Fiscal year closed: {self.start_date.year}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'start_date': self.start_date.isoformat(),
            'company_name': self.company_name,
            'is_closed': self.is_closed,
            'periods': [p.to_dict() for p in self.periods]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FiscalYear':
        """Create from dictionary"""
        start_date = date.fromisoformat(data['start_date'])
        fy = cls(start_date, data['company_name'])
        fy.is_closed = data.get('is_closed', False)
        
        # Restore period lock states
        for i, period_data in enumerate(data.get('periods', [])):
            if i < len(fy.periods):
                fy.periods[i].is_locked = period_data.get('is_locked', False)
        
        return fy


class FiscalYearManager:
    """Manages fiscal years for companies"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.fiscal_years: Dict[str, FiscalYear] = {}
        self._load_fiscal_years()
    
    def _get_fiscal_year_file(self, company_name: str) -> Path:
        """Get the fiscal year file path for a company"""
        company_dir = self.data_dir / "companies" / company_name
        company_dir.mkdir(parents=True, exist_ok=True)
        return company_dir / "fiscal_year.json"
    
    def _load_fiscal_years(self):
        """Load fiscal years from disk"""
        companies_dir = self.data_dir / "companies"
        if not companies_dir.exists():
            return
        
        for company_dir in companies_dir.iterdir():
            if company_dir.is_dir():
                fy_file = company_dir / "fiscal_year.json"
                if fy_file.exists():
                    try:
                        with open(fy_file, 'r') as f:
                            data = json.load(f)
                            fy = FiscalYear.from_dict(data)
                            self.fiscal_years[fy.company_name] = fy
                    except Exception as e:
                        logger.error(f"Error loading fiscal year for {company_dir.name}: {e}")
    
    def _save_fiscal_year(self, company_name: str):
        """Save fiscal year to disk"""
        if company_name not in self.fiscal_years:
            return
        
        fy_file = self._get_fiscal_year_file(company_name)
        try:
            with open(fy_file, 'w') as f:
                json.dump(self.fiscal_years[company_name].to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving fiscal year for {company_name}: {e}")
    
    def create_fiscal_year(self, company_name: str, start_date: date) -> FiscalYear:
        """Create a new fiscal year for a company"""
        fy = FiscalYear(start_date, company_name)
        self.fiscal_years[company_name] = fy
        self._save_fiscal_year(company_name)
        logger.info(f"Created fiscal year for {company_name} starting {start_date}")
        return fy
    
    def get_fiscal_year(self, company_name: str) -> Optional[FiscalYear]:
        """Get fiscal year for a company"""
        return self.fiscal_years.get(company_name)
    
    def validate_transaction_date(self, company_name: str, transaction_date: date,
                                  allow_locked: bool = False) -> bool:
        """
        Validate if a transaction can be posted on a specific date
        
        Args:
            company_name: Company name
            transaction_date: Transaction date
            allow_locked: Allow transactions in locked periods (for admin)
        
        Returns:
            True if valid
        
        Raises:
            BusinessRuleError: If date is in locked period
        """
        fy = self.get_fiscal_year(company_name)
        
        if not fy:
            # No fiscal year defined, allow transaction
            return True
        
        if not allow_locked and fy.is_date_in_locked_period(transaction_date):
            period = fy.get_period_for_date(transaction_date)
            raise BusinessRuleError(
                f"Cannot post transaction in locked period: "
                f"{period.year}-{period.month:02d}"
            )
        
        return True
    
    def lock_period(self, company_name: str, year: int, month: int):
        """Lock a fiscal period"""
        fy = self.get_fiscal_year(company_name)
        if fy:
            fy.lock_period(year, month)
            self._save_fiscal_year(company_name)
    
    def unlock_period(self, company_name: str, year: int, month: int):
        """Unlock a fiscal period"""
        fy = self.get_fiscal_year(company_name)
        if fy:
            fy.unlock_period(year, month)
            self._save_fiscal_year(company_name)
    
    def close_fiscal_year(self, company_name: str):
        """Close a fiscal year"""
        fy = self.get_fiscal_year(company_name)
        if fy:
            fy.close_year()
            self._save_fiscal_year(company_name)
    
    def get_period_status(self, company_name: str) -> List[Dict[str, Any]]:
        """Get status of all periods for a company"""
        fy = self.get_fiscal_year(company_name)
        if not fy:
            return []
        
        return [
            {
                'year': p.year,
                'month': p.month,
                'month_name': date(p.year, p.month, 1).strftime('%B'),
                'start_date': p.start_date.isoformat(),
                'end_date': p.end_date.isoformat(),
                'is_locked': p.is_locked
            }
            for p in fy.periods
        ]


# Global instance
_fiscal_year_manager = None


def get_fiscal_year_manager() -> FiscalYearManager:
    """Get global fiscal year manager instance"""
    global _fiscal_year_manager
    if _fiscal_year_manager is None:
        _fiscal_year_manager = FiscalYearManager()
    return _fiscal_year_manager
