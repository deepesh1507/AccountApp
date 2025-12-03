"""
Company Login Module
Features: Login and Register options
Each company has separate user management
After login -> Dashboard, Register -> Registration Form -> Login
"""

import customtkinter as ctk
from tkinter import messagebox
import hashlib
from datetime import datetime


class CompanyLogin:
    def __init__(self, root, company_data, app_controller):
        self.root = root
        self.company_data = company_data
        # Use the main app controller for navigation
        self.app = app_controller
        self.company_name = company_data.get('company_name', '')
        
        self.root.title(f"Login - {self.company_name}")
        
        self.setup_login_ui()
    
    def setup_login_ui(self):
        """Setup login screen"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main_frame.pack(fill="both", expand=True)
        
        # Header with company info
        header_frame = ctk.CTkFrame(main_frame, fg_color="#1565c0", height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        company_label = ctk.CTkLabel(
            header_frame,
            text=f"🏢 {self.company_name}",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        company_label.pack(pady=20)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text=f"{self.company_data.get('company_type', '')} | {self.company_data.get('city', '')}",
            font=ctk.CTkFont(size=13),
            text_color="#e3f2fd"
        )
        subtitle_label.pack()
        
        # Back button
        back_btn = ctk.CTkButton(
            header_frame,
            text="← Select Another Company",
            font=ctk.CTkFont(size=12),
            width=180,
            height=35,
            fg_color="#0d47a1",
            hover_color="#01579b",
            command=self.go_back
        )
        back_btn.place(x=20, y=30)
        
        # Center content frame (fill both so inner card isn't clipped)
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Login card
        # Let the card size to its content so buttons are never clipped
        login_card = ctk.CTkFrame(content_frame, fg_color=("white", "gray20"), corner_radius=15, width=450)
        login_card.pack(pady=20)
        login_card.pack_propagate(True)
        
        # Login icon/title
        title_label = ctk.CTkLabel(
            login_card,
            text="🔐 User Login",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#1565c0"
        )
        title_label.pack(pady=(40, 10))
        
        welcome_label = ctk.CTkLabel(
            login_card,
            text="Please enter your credentials",
            font=ctk.CTkFont(size=13),
            text_color="#666666"
        )
        welcome_label.pack(pady=(0, 30))
        
        # Username field
        username_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        username_frame.pack(pady=10)
        
        username_label = ctk.CTkLabel(
            username_frame,
            text="👤 Username",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        username_label.pack(anchor="w", padx=50)
        
        self.username_entry = ctk.CTkEntry(
            username_frame,
            placeholder_text="Enter username",
            width=320,
            height=40
        )
        self.username_entry.pack(pady=5)
        
        # Password field
        password_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        password_frame.pack(pady=10)
        
        password_label = ctk.CTkLabel(
            password_frame,
            text="🔒 Password",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        password_label.pack(anchor="w", padx=50)
        
        self.password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="Enter password",
            width=320,
            height=40,
            show="●"
        )
        self.password_entry.pack(pady=5)
        
        # Show password checkbox
        self.show_password = ctk.CTkCheckBox(
            password_frame,
            text="Show password",
            command=self.toggle_password
        )
        self.show_password.pack(anchor="w", padx=50, pady=5)
        
        # Login button
        login_btn = ctk.CTkButton(
            login_card,
            text="Login",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=320,
            height=45,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            command=self.login_user
        )
        login_btn.pack(pady=20)
        
        # Divider
        divider_frame = ctk.CTkFrame(login_card, fg_color="transparent")
        divider_frame.pack(pady=10)
        
        ctk.CTkLabel(divider_frame, text="──────────  OR  ──────────", 
                    text_color="#999999").pack()
        
        # Register button
        register_btn = ctk.CTkButton(
            login_card,
            text="Register New User",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=320,
            height=40,
            fg_color="#1976d2",
            hover_color="#0d47a1",
            command=self.show_registration
        )
        register_btn.pack(pady=10)
        
        # Bind Enter key
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login_user())
    
    def toggle_password(self):
        """Toggle password visibility"""
        if self.show_password.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="●")
    
    def login_user(self):
        """Handle user login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Warning", "Please enter both username and password")
            return
        
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            users = db.load_json(self.company_name, "users.json") or []
            
            # Check if users exist
            if not users:
                messagebox.showwarning("No Users", "No users registered yet. Please register first.")
                return
            
            # Hash password for comparison
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Find user
            user_found = False
            for user in users:
                if user['username'] == username and user['password'] == password_hash:
                    user_found = True
                    
                    # Update last login
                    user['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    db.save_json(self.company_name, "users.json", users)
                    
                    messagebox.showinfo("Success", f"Welcome back, {user['full_name']}!")
                    
                    # Open dashboard
                    self.open_dashboard(user)
                    break
            
            if not user_found:
                messagebox.showerror("Login Failed", "Invalid username or password")
                self.password_entry.delete(0, 'end')
        
        except Exception as e:
            messagebox.showerror("Error", f"Login error:\n{str(e)}")
    
    def show_registration(self):
        """Show registration form"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="#1976d2", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📝 New User Registration",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=25)
        
        # Back to login button
        back_login_btn = ctk.CTkButton(
            header_frame,
            text="← Back to Login",
            font=ctk.CTkFont(size=12),
            width=140,
            height=35,
            fg_color="#0d47a1",
            hover_color="#01579b",
            command=self.setup_login_ui
        )
        back_login_btn.place(x=20, y=22)
        
        # Scrollable form
        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color=("white", "gray20"))
        scroll_frame.pack(fill="both", expand=True, padx=200, pady=30)
        
        form_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Registration form fields
        fields = [
            ("Full Name *", "full_name"),
            ("Username *", "username"),
            ("Password *", "password"),
            ("Confirm Password *", "confirm_password"),
            ("Email Address *", "email"),
            ("Phone Number", "phone"),
            ("Designation", "designation"),
            ("Department", "department")
        ]
        
        self.reg_entries = {}
        
        for idx, (label_text, field_name) in enumerate(fields):
            label = ctk.CTkLabel(
                form_frame,
                text=label_text,
                font=ctk.CTkFont(size=13, weight="bold")
            )
            label.grid(row=idx, column=0, sticky="w", pady=10, padx=10)
            
            if "password" in field_name.lower():
                entry = ctk.CTkEntry(form_frame, width=350, height=35, show="●")
            else:
                entry = ctk.CTkEntry(form_frame, width=350, height=35)
            
            entry.grid(row=idx, column=1, sticky="w", pady=10, padx=10)
            self.reg_entries[field_name] = entry
        
        # Role selection
        role_label = ctk.CTkLabel(
            form_frame,
            text="User Role *",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        role_label.grid(row=len(fields), column=0, sticky="w", pady=10, padx=10)
        
        self.role_combo = ctk.CTkComboBox(
            form_frame,
            values=["Admin", "Manager", "Accountant", "User"],
            width=350,
            height=35
        )
        self.role_combo.set("User")
        self.role_combo.grid(row=len(fields), column=1, sticky="w", pady=10, padx=10)
        
        # Permissions
        perm_label = ctk.CTkLabel(
            form_frame,
            text="Permissions",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        perm_label.grid(row=len(fields)+1, column=0, sticky="nw", pady=10, padx=10)
        
        perm_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        perm_frame.grid(row=len(fields)+1, column=1, sticky="w", pady=10, padx=10)
        
        self.permissions = {}
        permissions_list = ["View Reports", "Create Invoices", "Manage Clients", "Manage Accounts"]
        
        for perm in permissions_list:
            cb = ctk.CTkCheckBox(perm_frame, text=perm)
            cb.pack(anchor="w", pady=3)
            self.permissions[perm] = cb
        
        # Action buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=len(fields)+2, column=0, columnspan=2, pady=30)
        
        register_btn = ctk.CTkButton(
            button_frame,
            text="✓ Register User",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=200,
            height=50,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            command=self.register_user
        )
        register_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="✕ Cancel",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=150,
            height=50,
            fg_color="#c62828",
            hover_color="#8e0000",
            command=self.setup_login_ui
        )
        cancel_btn.pack(side="left", padx=10)
    
    def register_user(self):
        """Register new user"""
        # Get all field values
        full_name = self.reg_entries['full_name'].get().strip()
        username = self.reg_entries['username'].get().strip()
        password = self.reg_entries['password'].get().strip()
        confirm_password = self.reg_entries['confirm_password'].get().strip()
        email = self.reg_entries['email'].get().strip()
        phone = self.reg_entries['phone'].get().strip()
        designation = self.reg_entries['designation'].get().strip()
        department = self.reg_entries['department'].get().strip()
        role = self.role_combo.get()
        
        # Validation
        if not all([full_name, username, password, confirm_password, email]):
            messagebox.showwarning("Warning", "Please fill all required fields marked with *")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        if len(password) < 6:
            messagebox.showwarning("Warning", "Password must be at least 6 characters long")
            return
        
        try:
            from .database_manager import DatabaseManager
            db = DatabaseManager()
            users = db.load_json(self.company_name, "users.json") or []
            
            # Check if username exists
            for user in users:
                if user.get('username') == username:
                    messagebox.showerror("Error", "Username already exists!")
                    return
            
            # Get selected permissions
            user_permissions = [perm for perm, cb in self.permissions.items() if cb.get()]
            
            # Create user data
            user_data = {
                'user_id': len(users) + 1,
                'full_name': full_name,
                'username': username,
                'password': hashlib.sha256(password.encode()).hexdigest(),
                'email': email,
                'phone': phone,
                'designation': designation,
                'department': department,
                'role': role,
                'permissions': user_permissions,
                'status': 'Active',
                'created_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'last_login': None
            }
            
            # Add user to list
            users.append(user_data)
            
            # Save to database
            db.save_json(self.company_name, "users.json", users)
            
            messagebox.showinfo("Success", f"User '{username}' registered successfully!\n\nYou can now login with your credentials.")
            
            # Redirect to login page
            self.setup_login_ui()
        
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed:\n{str(e)}")
    
    def open_dashboard(self, user_data):
        """Open dashboard after successful login"""
        try:
            # Use the app controller to show the dashboard
            self.app.show_dashboard(self.company_data, user_data)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open dashboard:\n{str(e)}")
    
    def go_back(self):
        """Go back to select company screen"""
        self.app.show_select_company()

# For testing
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1200x700")
    
    class DummySelectCompany:
        def setup_ui(self):
            pass
    
    dummy_company = {
        'company_name': 'Test Company Pvt Ltd',
        'company_type': 'Private Limited',
        'city': 'Mumbai'
    }
    
    app = CompanyLogin(root, dummy_company, DummySelectCompany())
    root.mainloop()
