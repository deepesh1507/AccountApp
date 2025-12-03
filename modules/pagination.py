"""
Pagination Utility for AccountApp
Provides reusable pagination widget and logic for list views.
"""

import customtkinter as ctk
from typing import List, Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PaginationWidget(ctk.CTkFrame):
    """
    Reusable pagination widget for CustomTkinter
    
    Features:
    - Page navigation (First, Previous, Next, Last)
    - Page number display
    - Jump to page
    - Configurable page size
    - Total records display
    """
    
    def __init__(self, parent, page_size: int = 100, on_page_change: Optional[Callable] = None):
        """
        Initialize pagination widget
        
        Args:
            parent: Parent widget
            page_size: Number of items per page
            on_page_change: Callback function when page changes (receives page_number)
        """
        super().__init__(parent)
        
        self.page_size = page_size
        self.current_page = 1
        self.total_pages = 1
        self.total_records = 0
        self.on_page_change = on_page_change
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create pagination controls"""
        # Info label (left side)
        self.info_label = ctk.CTkLabel(
            self,
            text="No records",
            font=("Arial", 12)
        )
        self.info_label.pack(side="left", padx=10)
        
        # Navigation buttons (right side)
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(side="right", padx=10)
        
        # First page button
        self.first_btn = ctk.CTkButton(
            nav_frame,
            text="⏮ First",
            width=80,
            command=self._go_to_first_page
        )
        self.first_btn.pack(side="left", padx=2)
        
        # Previous page button
        self.prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀ Prev",
            width=80,
            command=self._go_to_previous_page
        )
        self.prev_btn.pack(side="left", padx=2)
        
        # Page info
        self.page_label = ctk.CTkLabel(
            nav_frame,
            text="Page 1 of 1",
            font=("Arial", 12, "bold")
        )
        self.page_label.pack(side="left", padx=10)
        
        # Next page button
        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="Next ▶",
            width=80,
            command=self._go_to_next_page
        )
        self.next_btn.pack(side="left", padx=2)
        
        # Last page button
        self.last_btn = ctk.CTkButton(
            nav_frame,
            text="Last ⏭",
            width=80,
            command=self._go_to_last_page
        )
        self.last_btn.pack(side="left", padx=2)
        
        # Page size selector
        size_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
        size_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(size_frame, text="Per page:").pack(side="left", padx=2)
        
        self.size_var = ctk.StringVar(value=str(self.page_size))
        self.size_dropdown = ctk.CTkOptionMenu(
            size_frame,
            variable=self.size_var,
            values=["25", "50", "100", "200", "500"],
            width=80,
            command=self._on_page_size_change
        )
        self.size_dropdown.pack(side="left", padx=2)
    
    def update(self, total_records: int, current_page: Optional[int] = None):
        """
        Update pagination state
        
        Args:
            total_records: Total number of records
            current_page: Current page number (optional, keeps current if None)
        """
        self.total_records = total_records
        self.total_pages = max(1, (total_records + self.page_size - 1) // self.page_size)
        
        if current_page is not None:
            self.current_page = max(1, min(current_page, self.total_pages))
        else:
            # Ensure current page is valid
            self.current_page = max(1, min(self.current_page, self.total_pages))
        
        self._update_display()
    
    def _update_display(self):
        """Update the display of pagination controls"""
        # Update info label
        start_record = (self.current_page - 1) * self.page_size + 1
        end_record = min(self.current_page * self.page_size, self.total_records)
        
        if self.total_records == 0:
            self.info_label.configure(text="No records")
        else:
            self.info_label.configure(
                text=f"Showing {start_record}-{end_record} of {self.total_records} records"
            )
        
        # Update page label
        self.page_label.configure(text=f"Page {self.current_page} of {self.total_pages}")
        
        # Enable/disable navigation buttons
        self.first_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < self.total_pages else "disabled")
        self.last_btn.configure(state="normal" if self.current_page < self.total_pages else "disabled")
    
    def _go_to_first_page(self):
        """Navigate to first page"""
        if self.current_page != 1:
            self.current_page = 1
            self._on_page_changed()
    
    def _go_to_previous_page(self):
        """Navigate to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self._on_page_changed()
    
    def _go_to_next_page(self):
        """Navigate to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._on_page_changed()
    
    def _go_to_last_page(self):
        """Navigate to last page"""
        if self.current_page != self.total_pages:
            self.current_page = self.total_pages
            self._on_page_changed()
    
    def _on_page_size_change(self, value: str):
        """Handle page size change"""
        try:
            new_size = int(value)
            if new_size != self.page_size:
                self.page_size = new_size
                # Recalculate pages and adjust current page
                self.update(self.total_records, 1)  # Reset to first page
                self._on_page_changed()
        except ValueError:
            logger.error(f"Invalid page size: {value}")
    
    def _on_page_changed(self):
        """Trigger page change callback"""
        self._update_display()
        if self.on_page_change:
            self.on_page_change(self.current_page)
    
    def get_current_page(self) -> int:
        """Get current page number"""
        return self.current_page
    
    def get_page_size(self) -> int:
        """Get current page size"""
        return self.page_size
    
    def get_offset(self) -> int:
        """Get offset for database queries"""
        return (self.current_page - 1) * self.page_size
    
    def get_limit(self) -> int:
        """Get limit for database queries"""
        return self.page_size


class Paginator:
    """
    Helper class for paginating data
    Useful for in-memory pagination when not using database queries
    """
    
    def __init__(self, data: List[Any], page_size: int = 100):
        """
        Initialize paginator
        
        Args:
            data: List of data to paginate
            page_size: Number of items per page
        """
        self.data = data
        self.page_size = page_size
        self.total_records = len(data)
        self.total_pages = max(1, (self.total_records + page_size - 1) // page_size)
    
    def get_page(self, page_number: int) -> List[Any]:
        """
        Get data for a specific page
        
        Args:
            page_number: Page number (1-indexed)
        
        Returns:
            List of items for the page
        """
        page_number = max(1, min(page_number, self.total_pages))
        start_idx = (page_number - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, self.total_records)
        return self.data[start_idx:end_idx]
    
    def get_page_info(self, page_number: int) -> dict:
        """
        Get pagination information for a page
        
        Args:
            page_number: Page number (1-indexed)
        
        Returns:
            Dictionary with pagination info
        """
        page_number = max(1, min(page_number, self.total_pages))
        start_record = (page_number - 1) * self.page_size + 1
        end_record = min(page_number * self.page_size, self.total_records)
        
        return {
            'page_number': page_number,
            'page_size': self.page_size,
            'total_pages': self.total_pages,
            'total_records': self.total_records,
            'start_record': start_record,
            'end_record': end_record,
            'has_previous': page_number > 1,
            'has_next': page_number < self.total_pages
        }


def paginate_query_results(query_func: Callable, page: int, page_size: int, *args, **kwargs) -> tuple:
    """
    Helper function to paginate database query results
    
    Args:
        query_func: Function that executes the query (should accept offset and limit)
        page: Page number (1-indexed)
        page_size: Number of items per page
        *args: Additional arguments for query_func
        **kwargs: Additional keyword arguments for query_func
    
    Returns:
        Tuple of (results, total_count)
    
    Usage:
        def get_clients(offset, limit):
            return db.select("clients", limit=limit, offset=offset)
        
        results, total = paginate_query_results(get_clients, page=1, page_size=100)
    """
    offset = (page - 1) * page_size
    
    # Execute query with pagination
    results = query_func(*args, offset=offset, limit=page_size, **kwargs)
    
    # Get total count (you may need to modify this based on your query function)
    # This assumes query_func can be called with count=True to get total
    try:
        total_count = query_func(*args, count=True, **kwargs)
    except:
        # Fallback: estimate from results
        total_count = len(results) if len(results) < page_size else len(results) * page
    
    return results, total_count
