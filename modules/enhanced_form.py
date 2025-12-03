from typing import Dict, List, Callable, Optional, Any
import json
from pathlib import Path
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox


class EnhancedForm(ctk.CTkFrame):
    """
    Professional form with:
    - Two-column grid layout
    - Keyboard shortcuts (F2=Save, ESC=Cancel, F1=Help)
    - Auto-save drafts
    - Field validation
    - Section grouping
    """
    
    def __init__(self, master, title: str, on_save: Callable,
                 on_cancel: Callable, auto_save: bool = True, **kwargs):
        super().__init__(master, **kwargs)
        
        self.title_text = title
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.auto_save_enabled = auto_save
        
        self.fields: Dict[str, Any] = {}
        self.sections: List[ctk.CTkFrame] = []
        self.current_row = 0
        self.current_section = None
        
        # Auto-save timer
        self.auto_save_timer = None
        self.draft_file = None
        
        self._setup_ui()
        self._bind_shortcuts()
    
    def _setup_ui(self):
        """Setup the form UI"""
        # Title bar
        title_frame = ctk.CTkFrame(self, fg_color=("#1976d2", "#0d47a1"), height=60)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            title_frame,
            text=self.title_text,
            font=("Arial", 20, "bold"),
            text_color="white"
        ).pack(side="left", padx=20, pady=15)
        
        # Help hint
        ctk.CTkLabel(
            title_frame,
            text="F1=Help | F2=Save | ESC=Cancel",
            font=("Arial", 10),
            text_color="white"
        ).pack(side="right", padx=20)
        
        # Scrollable content area
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=("gray95", "gray15")
        )
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Button bar
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent", height=70)
        self.button_frame.pack(fill="x", padx=20, pady=10)
        self.button_frame.pack_propagate(False)
        
        # Save button
        self.save_btn = ctk.CTkButton(
            self.button_frame,
            text="💾 Save (F2)",
            command=self._handle_save,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            height=45,
            width=150,
            font=("Arial", 14, "bold")
        )
        self.save_btn.pack(side="left", padx=5)
        
        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            self.button_frame,
            text="❌ Cancel (ESC)",
            command=self._handle_cancel,
            fg_color="#c62828",
            hover_color="#b71c1c",
            height=45,
            width=150,
            font=("Arial", 14, "bold")
        )
        self.cancel_btn.pack(side="left", padx=5)
        
        # Help button
        self.help_btn = ctk.CTkButton(
            self.button_frame,
            text="❓ Help (F1)",
            command=self._show_help,
            fg_color="#455a64",
            hover_color="#263238",
            height=45,
            width=130
        )
        self.help_btn.pack(side="right", padx=5)
    
    def _bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        try:
            # Use winfo_toplevel() to get the root window and bind events there
            root = self.winfo_toplevel()
            root.bind("<F2>", lambda e: self._handle_save())
            root.bind("<Escape>", lambda e: self._handle_cancel())
            root.bind("<F1>", lambda e: self._show_help())
        except Exception as e:
            print(f"Warning: Could not bind shortcuts: {e}")
    
    def add_section(self, title: str) -> ctk.CTkFrame:
        """Add a new section to the form"""
        # Calculate row index based on existing sections
        # Each section takes 2 rows (header + content)
        start_row = len(self.sections) * 2
        
        # Section header
        header = ctk.CTkLabel(
            self.content_frame,
            text=title,
            font=("Arial", 16, "bold"),
            text_color="#1976d2",
            anchor="w"
        )
        header.grid(row=start_row, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # Section frame
        section = ctk.CTkFrame(
            self.content_frame,
            fg_color=("white", "gray20"),
            corner_radius=10
        )
        section.grid(row=start_row + 1, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Configure column weight for content_frame to ensure full width
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        return widget
    
    def add_field_pair(self, label1: str, widget1: Any, label2: str, widget2: Any,
                      help_text1: str = "", help_text2: str = ""):
        """Add two fields side by side"""
        self.add_field(label1, widget1, column=0, help_text=help_text1)
        self.add_field(label2, widget2, column=1, help_text=help_text2)
    
    def get_field(self, field_id: str) -> Optional[Any]:
        """Get a field widget by ID"""
        return self.fields.get(field_id)
    
    def get_all_values(self) -> Dict[str, Any]:
        """Get all field values"""
        values = {}
        for field_id, widget in self.fields.items():
            if hasattr(widget, 'get_value'):
                values[field_id] = widget.get_value()
            elif hasattr(widget, 'get'):
                values[field_id] = widget.get()
            else:
                values[field_id] = None
        return values
    
    def add_line_item_grid(self, title: str, columns: List[str]):
        """
        Add a line item grid for SAP-style multi-line entry
        Used for FB50, FB60, FB70 transactions
        """
        if not self.current_section:
            self.current_section = self.content_frame
        
        # Create a container frame that will be grid-managed
        # This prevents conflicts with other grid-managed fields in the section
        container = ctk.CTkFrame(self.current_section, fg_color="transparent")
        
        # Always use grid for consistency
        # Calculate row index if adding to content_frame
        if self.current_section == self.content_frame:
            # Assuming sections take 2 rows each, find the next available row
            # This is a bit hacky but consistent with add_section
            start_row = len(self.sections) * 2
            container.grid(row=start_row, column=0, sticky="ew", padx=15, pady=8)
            # Increment section count to reserve space (even though it's not a section)
            # A better way would be to track total rows in content_frame
        else:
            container.grid(row=self.current_row, column=0, columnspan=2, 
                          sticky="ew", padx=15, pady=8)
            self.current_row += 1
        
        # Configure grid weights
        self.current_section.grid_columnconfigure(0, weight=1)
        self.current_section.grid_columnconfigure(1, weight=1)
        
        # Section header
        header_frame = ctk.CTkFrame(
            container,
            fg_color=("#e3f2fd", "gray25"),
            corner_radius=5
        )
        header_frame.pack(fill="x", pady=(15, 10), padx=10)
        
        ctk.CTkLabel(
            header_frame,
            text=title,
            font=("Arial", 14, "bold"),
            text_color=("#1976d2", "white")
        ).pack(pady=8, padx=10, anchor="w")
        
        # Grid container
        grid_frame = ctk.CTkFrame(container, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Column headers
        headers_frame = ctk.CTkFrame(grid_frame, fg_color=("#1976d2", "#0d47a1"))
        headers_frame.pack(fill="x", pady=(0, 5))
        
        for i, col in enumerate(columns):
            ctk.CTkLabel(
                headers_frame,
                text=col,
                font=("Arial", 11, "bold"),
                text_color="white",
                width=120
            ).grid(row=0, column=i, padx=2, pady=5, sticky="ew")
        
        # Scrollable grid area
        grid_scroll = ctk.CTkScrollableFrame(grid_frame, height=200)
        grid_scroll.pack(fill="both", expand=True)
        
        # Store grid data
        grid_id = f"grid_{title.lower().replace(' ', '_')}"
        grid_rows = []
        
        def add_row():
            """Add a new row to the grid"""
            row_num = len(grid_rows)
            row_frame = ctk.CTkFrame(grid_scroll, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            row_widgets = {}
            for i, col in enumerate(columns):
                entry = ctk.CTkEntry(row_frame, width=120, height=30)
                entry.grid(row=0, column=i, padx=2, sticky="ew")
                row_widgets[col] = entry
            
            # Delete button
            del_btn = ctk.CTkButton(
                row_frame,
                text="✕",
                width=30,
                height=30,
                fg_color="#c62828",
                hover_color="#8e0000",
                command=lambda: remove_row(row_frame, row_widgets)
            )
            del_btn.grid(row=0, column=len(columns), padx=5)
            
            grid_rows.append(row_widgets)
        
        def remove_row(frame, widgets):
            """Remove a row from the grid"""
            if widgets in grid_rows:
                grid_rows.remove(widgets)
            frame.destroy()
        
        # Add initial rows
        for _ in range(3):
            add_row()
        
        # Add row button
        btn_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="+ Add Line",
            command=add_row,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            width=120,
            height=35
        ).pack(side="left", padx=5)
        
        # Store grid reference for data extraction
        self.fields[grid_id] = grid_rows
        
        return grid_rows
    
    def _handle_save(self):
        """Handle save action"""
        # Extract grid data
        values = {}
        for field_id, widget in self.fields.items():
            if field_id.startswith("grid_"):
                # Extract grid rows
                grid_data = []
                for row_widgets in widget:
                    row_data = {}
                    for col_name, entry_widget in row_widgets.items():
                        row_data[col_name] = entry_widget.get()
                    grid_data.append(row_data)
                values[field_id] = grid_data
            elif hasattr(widget, 'get_value'):
                values[field_id] = widget.get_value()
            elif hasattr(widget, 'get'):
                values[field_id] = widget.get()
            else:
                values[field_id] = None
        
        # Call the save callback
        self.on_save(values)
    
    def _handle_cancel(self):
        """Handle cancel action"""
        if messagebox.askyesno("Cancel", "Discard changes?"):
            self.on_cancel()
    
    def _show_help(self):
        """Show help dialog"""
        help_text = """
        Keyboard Shortcuts:
        
        F1  - Show this help
        F2  - Save form
        ESC - Cancel and close
        F4  - Open calendar (on date fields)
        Tab - Next field
        Shift+Tab - Previous field
        
        Field Shortcuts:
        T - Today (in date fields)
        Y - Yesterday (in date fields)
        
        Tips:
        - Required fields are marked with *
        - Red border indicates validation error
        - Green border indicates valid input
        """
        messagebox.showinfo("Form Help", help_text)
    
    def enable_auto_save(self, draft_file: str):
        """Enable auto-save to draft file"""
        self.draft_file = Path(draft_file)
        self._schedule_auto_save()
    
    def _schedule_auto_save(self):
        """Schedule auto-save"""
        if self.auto_save_enabled and self.draft_file:
            self._save_draft()
            # Schedule next auto-save in 30 seconds
            self.auto_save_timer = self.after(30000, self._schedule_auto_save)
    
    def _save_draft(self):
        """Save current form state as draft"""
        if not self.draft_file:
            return
        
        try:
            values = self.get_all_values()
            draft_data = {
                'timestamp': datetime.now().isoformat(),
                'values': values
            }
            
            self.draft_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.draft_file, 'w') as f:
                json.dump(draft_data, f, indent=2)
        except Exception as e:
            print(f"Auto-save failed: {e}")
    
    def load_draft(self) -> bool:
        """Load draft if available"""
        if not self.draft_file or not self.draft_file.exists():
            return False
        
        try:
            with open(self.draft_file, 'r') as f:
                draft_data = json.load(f)
            
            timestamp = draft_data.get('timestamp', '')
            if messagebox.askyesno(
                "Draft Found",
                f"A draft was saved at {timestamp}.\nDo you want to restore it?"
            ):
                self.set_values(draft_data.get('values', {}))
                return True
        except Exception as e:
            print(f"Failed to load draft: {e}")
        
        return False
    
    def clear_draft(self):
        """Clear the draft file"""
        if self.draft_file and self.draft_file.exists():
            try:
                self.draft_file.unlink()
            except Exception as e:
                print(f"Failed to clear draft: {e}")
    
    def destroy(self):
        """Clean up when destroying the form"""
        if self.auto_save_timer:
            self.after_cancel(self.auto_save_timer)
        super().destroy()
    
    @staticmethod
    def ensure_dialog_visible(dialog: ctk.CTkToplevel, parent: Optional[ctk.CTk] = None):
        """
        Ensure a dialog window is properly visible and focused.
        Call this after creating and configuring a CTkToplevel dialog.
        
        Args:
            dialog: The CTkToplevel dialog window
            parent: Optional parent window for centering
        """
        try:
            # Force window to update its geometry
            dialog.update_idletasks()
            
            # Lift the dialog to the top of the window stack
            dialog.lift()
            dialog.focus_force()
            
            # Set transient if parent is provided
            if parent:
                dialog.transient(parent)
            
            # Make sure grab is set (make it modal)
            dialog.grab_set()
            
            # Center the dialog if parent is available
            if parent:
                EnhancedForm.center_dialog(dialog, parent)
            
            # Ensure dialog is in a normal state
            try:
                dialog.state('normal')
            except:
                pass  # Some platforms may not support this
                
        except Exception as e:
            print(f"Warning: Could not fully ensure dialog visibility: {e}")
    
    @staticmethod
    def center_dialog(dialog: ctk.CTkToplevel, parent: ctk.CTk):
        """
        Center a dialog on its parent window.
        
        Args:
            dialog: The dialog to center
            parent: The parent window
        """
        try:
            # Update geometry to get accurate sizes
            dialog.update_idletasks()
            parent.update_idletasks()
            
            # Get parent window position and size
            parent_x = parent.winfo_x()
            parent_y = parent.winfo_y()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            
            # Get dialog size
            dialog_width = dialog.winfo_width()
            dialog_height = dialog.winfo_height()
            
            # Calculate centered position
            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
            
            # Ensure dialog is on screen
            x = max(0, x)
            y = max(0, y)
            
            # Set the position
            dialog.geometry(f"+{x}+{y}")
        except Exception as e:
            print(f"Warning: Could not center dialog: {e}")
    
    @staticmethod
    def create_dialog_safely(parent: ctk.CTk, title: str, geometry: str = "800x600", 
                            on_error: Optional[Callable] = None) -> Optional[ctk.CTkToplevel]:
        """
        Safely create a dialog with error handling.
        
        Args:
            parent: Parent window
            title: Dialog title
            geometry: Dialog geometry (e.g., "800x600")
            on_error: Optional callback for error handling
            
        Returns:
            CTkToplevel dialog or None if creation failed
        """
        try:
            dialog = ctk.CTkToplevel(parent)
            dialog.title(title)
            dialog.geometry(geometry)
            
            # Ensure it's visible
            EnhancedForm.ensure_dialog_visible(dialog, parent)
            
            return dialog
        except Exception as e:
            error_msg = f"Failed to create dialog '{title}': {e}"
            print(error_msg)
            if on_error:
                on_error(error_msg)
            else:
                messagebox.showerror("Dialog Error", error_msg)
            return None



class FormValidator:
    """
    Form validation helper with common validation rules
    """
    
    @staticmethod
    def validate_form_data(data: Dict[str, Any], rules: Dict[str, List[Callable]]) -> tuple:
        """
        Validate form data against rules
        
        Args:
            data: Form data dictionary
            rules: Dictionary of field_id -> list of validation functions
        
        Returns:
            (is_valid, errors) tuple
        """
        errors = {}
        
        for field_id, validators in rules.items():
            value = data.get(field_id, '')
            
            for validator in validators:
                is_valid, error_msg = validator(value)
                if not is_valid:
                    errors[field_id] = error_msg
                    break  # Stop at first error for this field
        
        return len(errors) == 0, errors
    
    @staticmethod
    def create_required_validator(field_name: str) -> Callable:
        """Create a required field validator"""
        def validator(value: Any) -> tuple:
            if not value or (isinstance(value, str) and not value.strip()):
                return False, f"{field_name} is required"
            return True, ""
        return validator
    
    @staticmethod
    def create_range_validator(min_val: float, max_val: float, field_name: str) -> Callable:
        """Create a range validator"""
        def validator(value: Any) -> tuple:
            try:
                num = float(value)
                if num < min_val or num > max_val:
                    return False, f"{field_name} must be between {min_val} and {max_val}"
                return True, ""
            except (ValueError, TypeError):
                return False, f"{field_name} must be a number"
        return validator
    
    @staticmethod
    def create_length_validator(min_len: int, max_len: int, field_name: str) -> Callable:
        """Create a length validator"""
        def validator(value: Any) -> tuple:
            length = len(str(value))
            if length < min_len:
                return False, f"{field_name} must be at least {min_len} characters"
            if length > max_len:
                return False, f"{field_name} must be at most {max_len} characters"
            return True, ""
        return validator
    
    @staticmethod
    def ensure_dialog_visible(dialog: ctk.CTkToplevel, root: ctk.CTk):
        """Ensure dialog is visible and centered"""
        try:
            dialog.update_idletasks()
            
            # Get dimensions
            width = dialog.winfo_width()
            height = dialog.winfo_height()
            
            # Center on root
            x = root.winfo_x() + (root.winfo_width() // 2) - (width // 2)
            y = root.winfo_y() + (root.winfo_height() // 2) - (height // 2)
            
            dialog.geometry(f"{width}x{height}+{x}+{y}")
            dialog.deiconify()
            dialog.lift()
            dialog.focus_force()
        except Exception as e:
            print(f"Error ensuring dialog visibility: {e}")
