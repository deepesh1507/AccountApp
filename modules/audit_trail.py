"""
Audit Trail Module
Tracks all data changes for compliance and security.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class AuditEntry:
    """Represents a single audit trail entry"""
    
    def __init__(self, company_name: str, user_name: str, action: str,
                 entity_type: str, entity_id: str, old_values: Optional[Dict] = None,
                 new_values: Optional[Dict] = None, ip_address: Optional[str] = None):
        self.timestamp = datetime.now()
        self.company_name = company_name
        self.user_name = user_name
        self.action = action  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT, EXPORT, etc.
        self.entity_type = entity_type  # journal_entry, invoice, client, etc.
        self.entity_id = entity_id
        self.old_values = old_values or {}
        self.new_values = new_values or {}
        self.ip_address = ip_address
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'company_name': self.company_name,
            'user_name': self.user_name,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEntry':
        """Create from dictionary"""
        entry = cls(
            company_name=data['company_name'],
            user_name=data['user_name'],
            action=data['action'],
            entity_type=data['entity_type'],
            entity_id=data['entity_id'],
            old_values=data.get('old_values'),
            new_values=data.get('new_values'),
            ip_address=data.get('ip_address')
        )
        entry.timestamp = datetime.fromisoformat(data['timestamp'])
        return entry
    
    def get_changes_summary(self) -> str:
        """Get a human-readable summary of changes"""
        if self.action == 'CREATE':
            return f"Created {self.entity_type} {self.entity_id}"
        elif self.action == 'DELETE':
            return f"Deleted {self.entity_type} {self.entity_id}"
        elif self.action == 'UPDATE':
            changes = []
            for key in self.new_values:
                if key in self.old_values and self.old_values[key] != self.new_values[key]:
                    changes.append(f"{key}: {self.old_values[key]} → {self.new_values[key]}")
            return f"Updated {self.entity_type} {self.entity_id}: " + ", ".join(changes)
        else:
            return f"{self.action} on {self.entity_type} {self.entity_id}"


class AuditTrail:
    """Manages audit trail for a company"""
    
    def __init__(self, company_name: str, data_dir: str = "data"):
        self.company_name = company_name
        self.data_dir = Path(data_dir)
        self.entries: List[AuditEntry] = []
        self._load_entries()
    
    def _get_audit_file(self) -> Path:
        """Get audit trail file path"""
        company_dir = self.data_dir / "companies" / self.company_name
        company_dir.mkdir(parents=True, exist_ok=True)
        return company_dir / "audit_trail.json"
    
    def _load_entries(self):
        """Load audit entries from disk"""
        audit_file = self._get_audit_file()
        if audit_file.exists():
            try:
                with open(audit_file, 'r') as f:
                    data = json.load(f)
                    self.entries = [AuditEntry.from_dict(e) for e in data]
                logger.debug(f"Loaded {len(self.entries)} audit entries for {self.company_name}")
            except Exception as e:
                logger.error(f"Error loading audit trail: {e}")
                self.entries = []
    
    def _save_entries(self):
        """Save audit entries to disk"""
        audit_file = self._get_audit_file()
        try:
            # Keep only last 10000 entries to prevent file from growing too large
            entries_to_save = self.entries[-10000:]
            
            with open(audit_file, 'w') as f:
                json.dump([e.to_dict() for e in entries_to_save], f, indent=2)
        except Exception as e:
            logger.error(f"Error saving audit trail: {e}")
    
    def log(self, user_name: str, action: str, entity_type: str, entity_id: str,
            old_values: Optional[Dict] = None, new_values: Optional[Dict] = None,
            ip_address: Optional[str] = None):
        """
        Log an audit entry
        
        Args:
            user_name: Username performing the action
            action: Action type (CREATE, UPDATE, DELETE, etc.)
            entity_type: Type of entity (journal_entry, invoice, etc.)
            entity_id: ID of the entity
            old_values: Previous values (for UPDATE)
            new_values: New values (for CREATE/UPDATE)
            ip_address: IP address of the user
        """
        entry = AuditEntry(
            company_name=self.company_name,
            user_name=user_name,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
        
        self.entries.append(entry)
        self._save_entries()
        
        logger.info(f"Audit: {user_name} - {entry.get_changes_summary()}")
    
    def get_entries(self, entity_type: Optional[str] = None,
                   entity_id: Optional[str] = None,
                   user_name: Optional[str] = None,
                   action: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   limit: int = 100) -> List[AuditEntry]:
        """
        Get audit entries with filters
        
        Args:
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            user_name: Filter by user
            action: Filter by action
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of entries to return
        
        Returns:
            List of audit entries
        """
        filtered = self.entries
        
        if entity_type:
            filtered = [e for e in filtered if e.entity_type == entity_type]
        
        if entity_id:
            filtered = [e for e in filtered if e.entity_id == entity_id]
        
        if user_name:
            filtered = [e for e in filtered if e.user_name == user_name]
        
        if action:
            filtered = [e for e in filtered if e.action == action]
        
        if start_date:
            filtered = [e for e in filtered if e.timestamp >= start_date]
        
        if end_date:
            filtered = [e for e in filtered if e.timestamp <= end_date]
        
        # Return most recent first
        filtered.reverse()
        
        return filtered[:limit]
    
    def get_entity_history(self, entity_type: str, entity_id: str) -> List[AuditEntry]:
        """Get complete history of an entity"""
        return self.get_entries(entity_type=entity_type, entity_id=entity_id, limit=1000)
    
    def get_user_activity(self, user_name: str, days: int = 30) -> List[AuditEntry]:
        """Get recent activity for a user"""
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        return self.get_entries(user_name=user_name, start_date=start_date, limit=1000)


class AuditTrailManager:
    """Manages audit trails for all companies"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.audit_trails: Dict[str, AuditTrail] = {}
    
    def get_audit_trail(self, company_name: str) -> AuditTrail:
        """Get or create audit trail for a company"""
        if company_name not in self.audit_trails:
            self.audit_trails[company_name] = AuditTrail(company_name, self.data_dir)
        return self.audit_trails[company_name]
    
    def log(self, company_name: str, user_name: str, action: str,
            entity_type: str, entity_id: str, old_values: Optional[Dict] = None,
            new_values: Optional[Dict] = None, ip_address: Optional[str] = None):
        """Log an audit entry for a company"""
        audit_trail = self.get_audit_trail(company_name)
        audit_trail.log(user_name, action, entity_type, entity_id,
                       old_values, new_values, ip_address)
    
    def log_create(self, company_name: str, user_name: str,
                   entity_type: str, entity_id: str, values: Dict):
        """Log entity creation"""
        self.log(company_name, user_name, 'CREATE', entity_type, entity_id,
                new_values=values)
    
    def log_update(self, company_name: str, user_name: str,
                   entity_type: str, entity_id: str,
                   old_values: Dict, new_values: Dict):
        """Log entity update"""
        self.log(company_name, user_name, 'UPDATE', entity_type, entity_id,
                old_values, new_values)
    
    def log_delete(self, company_name: str, user_name: str,
                   entity_type: str, entity_id: str, values: Dict):
        """Log entity deletion"""
        self.log(company_name, user_name, 'DELETE', entity_type, entity_id,
                old_values=values)
    
    def log_login(self, company_name: str, user_name: str, success: bool,
                  ip_address: Optional[str] = None):
        """Log login attempt"""
        action = 'LOGIN_SUCCESS' if success else 'LOGIN_FAILED'
        self.log(company_name, user_name, action, 'authentication', user_name,
                ip_address=ip_address)
    
    def log_logout(self, company_name: str, user_name: str):
        """Log logout"""
        self.log(company_name, user_name, 'LOGOUT', 'authentication', user_name)
    
    def log_export(self, company_name: str, user_name: str,
                   export_type: str, record_count: int):
        """Log data export"""
        self.log(company_name, user_name, 'EXPORT', export_type, f"{record_count}_records",
                new_values={'record_count': record_count})


# Global instance
_audit_trail_manager = None


def get_audit_trail_manager() -> AuditTrailManager:
    """Get global audit trail manager instance"""
    global _audit_trail_manager
    if _audit_trail_manager is None:
        _audit_trail_manager = AuditTrailManager()
    return _audit_trail_manager
