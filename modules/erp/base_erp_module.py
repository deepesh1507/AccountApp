import customtkinter as ctk
from typing import Dict, Any, Optional, List, Callable
from ..base_module import BaseModule
from ..enhanced_form import EnhancedForm
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class ERPBaseModule(BaseModule):
    """
    Base class for all ERP Modules (FI, CO, Integration).
    Provides common layout and helper methods for "List View -> Form" pattern.
    """
    
    def __init__(self, root: ctk.CTk, company_data: Dict[str, Any], user_data: Dict[str, Any], app_controller: Any):
        super().__init__(root, company_data, user_data, app_controller)
        self.current_form = None
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        os.makedirs(self.data_dir, exist_ok=True)

    def setup_ui(self):
        """
        Sets up the main container for the module.
        Subclasses should override create_content() to add specific widgets.
        """
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        self.main_frame = ctk.CTkFrame(self.root, fg_color=("gray95", "gray10"))
        self.main_frame.pack(fill="both", expand=True)

        # Header
        self.create_header()

        # Content Area
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Initial Content
        self.create_content()

    def create_header(self):
        """Creates the standard ERP Module header"""
        header_frame = ctk.CTkFrame(self.main_frame, height=60, fg_color=("#1976d2", "#0d47a1"))
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # Back Button
        back_btn = ctk.CTkButton(
            header_frame, 
            text="← Back", 
            command=self.go_back,
            width=80, 
            height=32,
            fg_color="transparent", 
            border_width=1, 
            border_color="white",
            text_color="white",
            hover_color=("#1565c0", "#0a3d91")
        )
        back_btn.pack(side="left", padx=(20, 10), pady=14)

        # Home Button
        home_btn = ctk.CTkButton(
            header_frame, 
            text="🏠 Home", 
            command=self.go_home,
            width=80, 
            height=32,
            fg_color="transparent", 
            border_width=1, 
            border_color="white",
            text_color="white",
            hover_color=("#1565c0", "#0a3d91")
        )
        home_btn.pack(side="left", padx=(0, 20), pady=14)

        # Title
        title_label = ctk.CTkLabel(
            header_frame, 
            text=self.get_module_title(), 
            font=("Arial", 20, "bold"), 
            text_color="white"
        )
        title_label.pack(side="left", padx=10)

    def get_module_title(self) -> str:
        """Subclasses should return the module title"""
        return "ERP Module"

    def create_content(self):
        """Subclasses should implement this to populate the content_frame"""
        pass

    def show_form(self, title: str, on_save: callable):
        """Helper to show an EnhancedForm in the content area"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.current_form = EnhancedForm(
            self.content_frame,
            title=title,
            on_save=on_save,
            on_cancel=self.reset_to_menu
        )
        self.current_form.pack(fill="both", expand=True)
        return self.current_form
    
    def show_list_view(self, title: str, columns: list, data_loader: callable, 
                      on_new: callable, on_edit: callable = None, on_delete: callable = None):
        """
        Show a list view with data table (like Invoices/Clients modules)
        
        Args:
            title: Title of the list view
            columns: List of column names for the table
            data_loader: Function that returns list of data dictionaries
            on_new: Callback when "New" button is clicked
            on_edit: Callback when "Edit" button is clicked (receives selected item values)
            on_delete: Callback when "Delete" button is clicked (receives selected item values)
        """
        
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Container
        list_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        list_container.pack(fill="both", expand=True)
        
        # Toolbar
        toolbar = ctk.CTkFrame(list_container, fg_color=("#e3f2fd", "gray25"), height=60)
        toolbar.pack(fill="x", padx=10, pady=10)
        toolbar.pack_propagate(False)
        
        # Back to Menu Button (if needed)
        ctk.CTkButton(
            toolbar,
            text="← Menu",
            command=self.reset_to_menu,
            width=80,
            height=32,
            fg_color="transparent",
            text_color=("#1976d2", "white"),
            hover_color=("#bbdefb", "gray35")
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            toolbar,
            text=title,
            font=("Arial", 16, "bold"),
            text_color=("#1976d2", "white")
        ).pack(side="left", padx=5)
        
        # Buttons
        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="+ New",
            command=on_new,
            width=100,
            height=35,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        ).pack(side="left", padx=5)
        
        if on_edit:
            ctk.CTkButton(
                btn_frame,
                text="✏️ Edit",
                command=lambda: self._handle_edit(tree, on_edit),
                width=100,
                height=35,
                fg_color="#f57c00",
                hover_color="#e65100"
            ).pack(side="left", padx=5)
        
        if on_delete:
            ctk.CTkButton(
                btn_frame,
                text="🗑️ Delete",
                command=lambda: self._handle_delete(tree, on_delete),
                width=100,
                height=35,
                fg_color="#c62828",
                hover_color="#8e0000"
            ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="↻ Refresh",
            command=lambda: self._refresh_list(tree, data_loader, columns),
            width=100,
            height=35,
            fg_color="#1976d2",
            hover_color="#0d47a1"
        ).pack(side="left", padx=5)
        
        # Table
        table_frame = ctk.CTkFrame(list_container, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Treeview
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        scrollbar.configure(command=tree.yview)
        
        # Configure columns
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="w")
        
        tree.pack(fill="both", expand=True)
        
        # Double-click to edit
        if on_edit:
            tree.bind("<Double-1>", lambda e: self._handle_edit(tree, on_edit))
        
        # Load data
        self._refresh_list(tree, data_loader, columns)
        
        return tree
    
    def _refresh_list(self, tree, data_loader, columns):
        """Refresh the list view with latest data"""
        # Clear existing
        for item in tree.get_children():
            tree.delete(item)
        
        # Load new data
        try:
            data = data_loader()
            for record in data:
                # Ensure values match column order
                values = []
                for col in columns:
                    val = record.get(col, "")
                    values.append(val)
                tree.insert("", "end", values=values)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n{str(e)}")
    
    def _handle_edit(self, tree, on_edit):
        """Handle edit button click"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit")
            return
        
        item = tree.item(selection[0])
        # Convert values tuple to list for easier handling
        on_edit(list(item['values']))
    
    def _handle_delete(self, tree, on_delete):
        """Handle delete button click"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
            item = tree.item(selection[0])
            on_delete(list(item['values']))
            tree.delete(selection[0])

    def reset_to_menu(self):
        """Resets the view to the main menu of the module"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.create_content()

    # --- Generic Data Helpers ---

    def load_json_data(self, filename: str) -> List[Dict]:
        """Load data from a JSON file"""
        file_path = os.path.join(self.data_dir, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_json_data(self, filename: str, data: List[Dict]):
        """Save data to a JSON file"""
        file_path = os.path.join(self.data_dir, filename)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def generic_save(self, filename: str, new_record: Dict, key_field: str):
        """
        Generic save method for simple entities.
        Updates existing record if key_field matches, otherwise appends.
        """
        data = self.load_json_data(filename)
        
        # Check if updating existing
        updated = False
        for i, record in enumerate(data):
            if record.get(key_field) == new_record.get(key_field):
                data[i] = new_record
                updated = True
                break
        
        if not updated:
            data.append(new_record)
            
        self.save_json_data(filename, data)
        messagebox.showinfo("Success", "Data saved successfully!")
        self.reset_to_menu()

    def generic_delete(self, filename: str, key_value: Any, key_field: str):
        """Generic delete method"""
        data = self.load_json_data(filename)
        data = [d for d in data if str(d.get(key_field)) != str(key_value)]
        self.save_json_data(filename, data)
        messagebox.showinfo("Success", "Item deleted successfully!")
