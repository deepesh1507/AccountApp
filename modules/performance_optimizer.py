"""
Performance Optimization Module
Utilities for improving application speed and smoothness
"""

import threading
import time
from functools import wraps
from typing import Callable, Any
import customtkinter as ctk


class PerformanceOptimizer:
    """
    Performance optimization utilities for CustomTkinter applications
    """
    
    @staticmethod
    def debounce(wait_ms: int = 300):
        """
        Debounce decorator to limit function calls
        Useful for search boxes, filters, etc.
        
        Args:
            wait_ms: Milliseconds to wait before executing
        """
        def decorator(func: Callable) -> Callable:
            timer = None
            
            @wraps(func)
            def debounced(*args, **kwargs):
                nonlocal timer
                
                def call_func():
                    func(*args, **kwargs)
                
                if timer is not None:
                    timer.cancel()
                
                timer = threading.Timer(wait_ms / 1000.0, call_func)
                timer.start()
            
            return debounced
        return decorator
    
    @staticmethod
    def async_task(func: Callable) -> Callable:
        """
        Run function in background thread
        Useful for heavy operations like data loading
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
            thread.start()
            return thread
        return wrapper
    
    @staticmethod
    def show_loading(parent: ctk.CTk, message: str = "Loading..."):
        """
        Show loading overlay
        
        Returns:
            Loading frame to destroy when done
        """
        loading_frame = ctk.CTkFrame(
            parent,
            fg_color=("white", "gray20"),
            corner_radius=10
        )
        loading_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Loading spinner (using text animation)
        loading_label = ctk.CTkLabel(
            loading_frame,
            text=f"⏳ {message}",
            font=("Arial", 16, "bold")
        )
        loading_label.pack(padx=40, pady=30)
        
        # Animate
        def animate(dots=0):
            if loading_frame.winfo_exists():
                loading_label.configure(text=f"⏳ {message}{'.' * (dots % 4)}")
                parent.after(200, lambda: animate(dots + 1))
        
        animate()
        
        return loading_frame
    
    @staticmethod
    def batch_insert(tree, items: list, batch_size: int = 100):
        """
        Insert items into treeview in batches for better performance
        
        Args:
            tree: Treeview widget
            items: List of items to insert
            batch_size: Number of items per batch
        """
        def insert_batch(start_idx: int):
            end_idx = min(start_idx + batch_size, len(items))
            
            for i in range(start_idx, end_idx):
                tree.insert("", "end", values=items[i])
            
            if end_idx < len(items):
                # Schedule next batch
                tree.after(10, lambda: insert_batch(end_idx))
        
        insert_batch(0)
    
    @staticmethod
    def lazy_load_images(image_paths: list, callback: Callable):
        """
        Load images in background
        
        Args:
            image_paths: List of image file paths
            callback: Function to call with loaded images
        """
        @PerformanceOptimizer.async_task
        def load():
            from PIL import Image
            import customtkinter as ctk
            
            images = []
            for path in image_paths:
                try:
                    img = ctk.CTkImage(Image.open(path))
                    images.append(img)
                except Exception:
                    images.append(None)
            
            callback(images)
        
        load()
    
    @staticmethod
    def virtual_scroll(tree, total_items: int, fetch_func: Callable):
        """
        Implement virtual scrolling for large datasets
        Only loads visible items
        
        Args:
            tree: Treeview widget
            total_items: Total number of items
            fetch_func: Function to fetch items (offset, limit) -> items
        """
        visible_items = 50
        current_offset = 0
        
        def load_visible():
            nonlocal current_offset
            items = fetch_func(current_offset, visible_items)
            
            # Clear and insert
            for item in tree.get_children():
                tree.delete(item)
            
            for item in items:
                tree.insert("", "end", values=item)
        
        def on_scroll(*args):
            # Load more when scrolling near bottom
            pass
        
        load_visible()
        tree.bind("<MouseWheel>", on_scroll)


class UIOptimizer:
    """
    UI optimization utilities
    """
    
    @staticmethod
    def optimize_treeview(tree):
        """
        Optimize treeview performance
        """
        # Disable updates during bulk operations
        tree.configure(selectmode="browse")
        
        # Use fixed column widths
        for col in tree["columns"]:
            tree.column(col, stretch=False)
    
    @staticmethod
    def reduce_redraws(widget: ctk.CTkBaseClass):
        """
        Reduce widget redraws
        """
        widget.update_idletasks()
    
    @staticmethod
    def cache_widgets(parent: ctk.CTkFrame):
        """
        Cache frequently used widgets
        """
        if not hasattr(parent, '_widget_cache'):
            parent._widget_cache = {}
        return parent._widget_cache
    
    @staticmethod
    def smooth_scroll(scrollable_frame: ctk.CTkScrollableFrame):
        """
        Enable smooth scrolling
        """
        # CustomTkinter already has smooth scrolling
        # This is a placeholder for future enhancements
        pass


class DataOptimizer:
    """
    Data handling optimization utilities
    """
    
    @staticmethod
    def paginate(data: list, page: int = 1, page_size: int = 100):
        """
        Paginate data
        
        Returns:
            (page_data, total_pages, total_items)
        """
        total_items = len(data)
        total_pages = (total_items + page_size - 1) // page_size
        
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_items)
        
        page_data = data[start_idx:end_idx]
        
        return page_data, total_pages, total_items
    
    @staticmethod
    def filter_data(data: list, filters: dict):
        """
        Filter data efficiently
        """
        filtered = data
        
        for key, value in filters.items():
            if value:
                filtered = [
                    item for item in filtered
                    if str(value).lower() in str(item.get(key, '')).lower()
                ]
        
        return filtered
    
    @staticmethod
    def sort_data(data: list, key: str, reverse: bool = False):
        """
        Sort data efficiently
        """
        return sorted(data, key=lambda x: x.get(key, ''), reverse=reverse)
    
    @staticmethod
    def cache_data(cache_key: str, ttl: int = 300):
        """
        Decorator for caching data
        
        Args:
            cache_key: Cache key
            ttl: Time to live in seconds
        """
        cache = {}
        
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                now = time.time()
                
                # Check cache
                if cache_key in cache:
                    data, timestamp = cache[cache_key]
                    if now - timestamp < ttl:
                        return data
                
                # Fetch fresh data
                data = func(*args, **kwargs)
                cache[cache_key] = (data, now)
                
                return data
            
            return wrapper
        return decorator


# Convenience functions

def run_async(func: Callable, *args, **kwargs):
    """Run function asynchronously"""
    thread = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    thread.start()
    return thread


def debounce_search(wait_ms: int = 300):
    """Debounce decorator for search functions"""
    return PerformanceOptimizer.debounce(wait_ms)


def show_loading_overlay(parent: ctk.CTk, message: str = "Loading..."):
    """Show loading overlay"""
    return PerformanceOptimizer.show_loading(parent, message)


def hide_loading_overlay(loading_frame):
    """Hide loading overlay"""
    if loading_frame and loading_frame.winfo_exists():
        loading_frame.destroy()


# Example usage:
"""
from modules.performance_optimizer import debounce_search, run_async, show_loading_overlay

class MyModule:
    @debounce_search(300)
    def search(self, query):
        # This will only run 300ms after user stops typing
        self.filter_data(query)
    
    def load_data(self):
        loading = show_loading_overlay(self.root, "Loading data...")
        
        def fetch():
            data = self.db.load_data()
            self.root.after(0, lambda: self.display_data(data))
            self.root.after(0, lambda: hide_loading_overlay(loading))
        
        run_async(fetch)
"""
