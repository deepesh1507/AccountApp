"""
Select Company Module
Features: List all companies, Search, Sort by Name/Date, Double-click actions
Actions: Open Company, Edit Details, Delete Company
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING
"""
Select Company Module
Features: List all companies, Search, Sort by Name/Date, Double-click actions
Actions: Open Company, Edit Details, Delete Company
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING
from .database_manager import DatabaseManager

if TYPE_CHECKING:
    from main import AccountingApp


from PIL import Image, ImageTk
import os
from pathlib import Path

class SelectCompany:
    def __init__(self, root: ctk.CTk, app_controller: "AccountingApp"):
        self.root = root
        self.app = app_controller # Store the main app controller
        self.root.title("Select Company")
        
        self.db = DatabaseManager()
        self.companies = []
        self.filtered_companies = []
        self.selected_company = None
        
        self.setup_ui()
        self.load_companies()
    
    def setup_ui(self):
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
            text="🏢 Select Company",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=30, pady=20)
        
        # Back button
        back_btn = ctk.CTkButton(
            header_frame,
            text="← Back to Home",
            font=ctk.CTkFont(size=14),
            width=150,
            height=40,
            fg_color="#0d47a1",
            hover_color="#01579b",
            command=self.go_back
        )
        back_btn.pack(side="right", padx=30)
        
        # Content frame
        content_frame = ctk.CTkFrame(main_frame, fg_color=("white", "gray20"))
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Search and Filter Section
        search_frame = ctk.CTkFrame(content_frame, fg_color=("#e3f2fd", "gray25"), corner_radius=10)
        search_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        search_label = ctk.CTkLabel(search_frame, text="🔍 Search:", font=ctk.CTkFont(size=14, weight="bold"))
        search_label.pack(side="left", padx=(20, 10), pady=15)
        
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search by company name...", width=300, height=35)
        self.search_entry.pack(side="left", padx=10, pady=15)
        self.search_entry.bind("<KeyRelease>", self.search_companies)
        
        sort_label = ctk.CTkLabel(search_frame, text="Sort By:", font=ctk.CTkFont(size=14, weight="bold"))
        sort_label.pack(side="left", padx=(30, 10), pady=15)
        
        self.sort_option = ctk.CTkComboBox(
            search_frame,
            values=["Name (A-Z)", "Name (Z-A)", "Date (Newest)", "Date (Oldest)"],
            width=150,
            height=35,
            command=self.sort_companies
        )
        self.sort_option.set("Name (A-Z)")
        self.sort_option.pack(side="left", padx=10, pady=15)
        
        refresh_btn = ctk.CTkButton(
            search_frame,
            text="↻ Refresh",
            width=100,
            height=35,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            command=self.load_companies
        )
        refresh_btn.pack(side="left", padx=10, pady=15)
        
        self.count_label = ctk.CTkLabel(search_frame, text="Total: 0 companies", font=ctk.CTkFont(size=13))
        self.count_label.pack(side="right", padx=20, pady=15)
        
        # Company Cards Container (Scrollable)
        self.cards_container = ctk.CTkScrollableFrame(content_frame, fg_color="transparent")
        self.cards_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.no_companies_label = ctk.CTkLabel(
            self.cards_container,
            text="📂 No companies found\n\nGo back and create a new company",
            font=ctk.CTkFont(size=16),
            text_color="#666666"
        )
    
    def load_companies(self):
        """Load all companies from database"""
        try:
            companies = self.db.get_all_companies()
            if isinstance(companies, dict) and companies:
                self.companies = list(companies.values())
            else:
                self.companies = []

            self.filtered_companies = self.companies.copy()
            self.display_companies()
            self.update_count()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load companies:\n{str(e)}")
    
    def display_companies(self):
        """Display companies as cards"""
        # Clear existing cards
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        
        if not self.filtered_companies:
            self.no_companies_label.pack(pady=50)
            return
        else:
            self.no_companies_label.pack_forget()
        
        # Configure grid columns for responsive layout
        self.cards_container.grid_columnconfigure(0, weight=1)
        self.cards_container.grid_columnconfigure(1, weight=1)
        self.cards_container.grid_columnconfigure(2, weight=1)

        row = 0
        col = 0
        for company in self.filtered_companies:
            self.create_company_card(company, row, col)
            col += 1
            if col > 2: # 3 cards per row
                col = 0
                row += 1
    
    def create_company_card(self, company, row, col):
        card = ctk.CTkFrame(self.cards_container, fg_color="white", corner_radius=15, border_width=1, border_color="gray80")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Logo
        logo_frame = ctk.CTkFrame(card, fg_color="transparent", height=80)
        logo_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        logo_img = self.get_company_logo(company)
        if logo_img:
            logo_label = ctk.CTkLabel(logo_frame, text="", image=logo_img)
            logo_label.image = logo_img  # Keep reference
        else:
            # Show placeholder when no logo
            logo_label = ctk.CTkLabel(
                logo_frame, 
                text="🏢", 
                font=ctk.CTkFont(size=40),
                width=50,
                height=50,
                fg_color="gray90",
                corner_radius=10
            )
        logo_label.pack(side="left")
        
        # Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        name_label = ctk.CTkLabel(info_frame, text=company.get('company_name', 'Unknown'), font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        name_label.pack(fill="x")
        
        type_label = ctk.CTkLabel(info_frame, text=company.get('company_type', 'Unknown'), font=ctk.CTkFont(size=12), text_color="gray60", anchor="w")
        type_label.pack(fill="x")
        
        loc_text = f"{company.get('city', '')}, {company.get('state', '')}".strip(", ")
        loc_label = ctk.CTkLabel(info_frame, text=f"📍 {loc_text}", font=ctk.CTkFont(size=12), text_color="gray60", anchor="w")
        loc_label.pack(fill="x", pady=(5, 0))

        # Actions
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=15)
        
        open_btn = ctk.CTkButton(action_frame, text="Open", width=80, height=30, fg_color="#2e7d32", hover_color="#1b5e20", command=lambda c=company: self.open_company_action(c))
        open_btn.pack(side="left", padx=(0, 5))
        
        manage_btn = ctk.CTkButton(action_frame, text="Manage", width=80, height=30, fg_color="#1976d2", hover_color="#0d47a1", command=lambda c=company: self.manage_company_action(c))
        manage_btn.pack(side="left")

    def get_company_logo(self, company):
        """Load company logo or default icon"""
        try:
            logo_path = company.get('logo_path')
            if logo_path:
                full_path = self.db.get_company_path(company.get('company_name')) / logo_path
                if full_path.exists():
                    img = Image.open(full_path)
                    img = img.resize((50, 50), Image.Resampling.LANCZOS)
                    return ctk.CTkImage(light_image=img, dark_image=img, size=(50, 50))
        except Exception as e:
            print(f"Error loading logo: {e}")
        return None

    def search_companies(self, event=None):
        term = self.search_entry.get().lower().strip()
        self.filtered_companies = [
            c for c in self.companies if term in c.get('company_name', '').lower()
        ] if term else self.companies.copy()
        self.sort_companies()
        self.update_count()
    
    def sort_companies(self, event=None):
        sort_by = self.sort_option.get()
        if sort_by == "Name (A-Z)":
            self.filtered_companies.sort(key=lambda x: x.get('company_name', '').lower())
        elif sort_by == "Name (Z-A)":
            self.filtered_companies.sort(key=lambda x: x.get('company_name', '').lower(), reverse=True)
        elif sort_by == "Date (Newest)":
            self.filtered_companies.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif sort_by == "Date (Oldest)":
            self.filtered_companies.sort(key=lambda x: x.get('created_at', ''))
        self.display_companies()
    
    def update_count(self):
        total, filtered = len(self.companies), len(self.filtered_companies)
        text = f"Total: {total} companies" if total == filtered else f"Showing: {filtered} of {total} companies"
        self.count_label.configure(text=text)
    
    def open_company_action(self, company):
        try:
            self.app.show_company_login(company)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open login page:\n{str(e)}")

    def manage_company_action(self, company):
        self.selected_company = company
        self.show_action_dialog()

    def show_action_dialog(self):
        if not self.selected_company:
            return
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Company Actions")
        dialog.geometry("400x350")
        dialog.transient(self.root)
        dialog.grab_set()

        info_frame = ctk.CTkFrame(dialog, fg_color=("#e3f2fd", "gray25"))
        info_frame.pack(fill="x", padx=20, pady=20)

        company_label = ctk.CTkLabel(
            info_frame,
            text=f"📋 {self.selected_company.get('company_name')}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1976d2"
        )
        company_label.pack(pady=15)

        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="both", expand=True, pady=10, padx=20)

        btn_edit = ctk.CTkButton(
            button_frame,
            text="✏️ Edit Details",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            fg_color="#f57c00",
            hover_color="#e65100",
            command=lambda: self.edit_company(dialog)
        )
        btn_edit.pack(pady=8, fill="x")

        btn_delete = ctk.CTkButton(
            button_frame,
            text="🗑️ Delete Company",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            fg_color="#c62828",
            hover_color="#8e0000",
            command=lambda: self.delete_company(dialog)
        )
        btn_delete.pack(pady=8, fill="x")

    def edit_company(self, dialog):
        dialog.destroy()
        if self.selected_company:
            if self.app and hasattr(self.app, 'show_edit_company'):
                self.app.show_edit_company(self.selected_company)
            else:
                messagebox.showinfo("Edit Company", "Edit company feature coming soon.")
    
    def delete_company(self, dialog):
        if not self.selected_company:
            return
        name = self.selected_company.get('company_name')
        if messagebox.askyesno("Delete Company", f"Are you sure you want to delete '{name}'?\nThis cannot be undone."):
            try:
                db = DatabaseManager()
                if db.delete_company(name):
                    messagebox.showinfo("Success", f"Company '{name}' deleted successfully!")
                    dialog.destroy()
                    self.load_companies()
                else:
                    messagebox.showerror("Error", "Failed to delete company")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete company:\n{str(e)}")
    
    def go_back(self):
        """Return to Home Screen using the app controller"""
        self.app.show_home_screen()
    
    def refresh_companies_list(self):
        """Refresh the companies list"""
        self.load_companies()


# For testing
if __name__ == "__main__":
    root = ctk.CTk()
    root.geometry("1200x700")
    class DummyAppController:
        def show_home_screen(self): print("Dummy: Back to home")
        def show_company_login(self, company_data): print(f"Dummy: Showing login for {company_data.get('company_name')}")
        def show_edit_company(self, company_data): print(f"Dummy: Showing edit for {company_data.get('company_name')}")
    app = SelectCompany(root, DummyAppController()) # type: ignore
    root.mainloop()
