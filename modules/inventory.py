"""
Inventory Management Module
Features: Product master, stock tracking, purchase orders, stock valuation
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from typing import Dict, List, Optional, Any
from .base_module import BaseModule
from .utilities import Validators, Formatters, IDGenerator
from .smart_widgets import (
    SmartEntry, SmartNumberEntry, SmartComboBox, 
    ValidationLabel, validate_required
)
from .enhanced_form import EnhancedForm
from .performance_optimizer import debounce_search, run_async, show_loading_overlay, hide_loading_overlay, PerformanceOptimizer

class InventoryManagement(BaseModule):
    def __init__(self, root, company_data, user_data, app_controller):
        super().__init__(root, company_data, user_data, app_controller)
        self.company_name = company_data.get("company_name", "")
        self.products = []
        self.filtered_products = []
        self.loading_overlay = None
        self.root.title(f"Inventory - {self.company_name}")
        self.load_products()

    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self.root, fg_color=("gray90", "gray13"))
        main_frame.pack(fill="both", expand=True)

        # --- Header ---
        header = ctk.CTkFrame(main_frame, fg_color="#f57c00", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(
            header, 
            text="📦 Inventory Management", 
            font=ctk.CTkFont(size=24, weight="bold"), 
            text_color="white"
        ).pack(side="left", padx=30, pady=18)

        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.pack(side="right", padx=20)
        
        ctk.CTkButton(
            nav_frame, 
            text="← Back", 
            command=self.go_back, 
            width=120,
            height=35,
            fg_color="#ef6c00",
            hover_color="#e65100"
        ).pack(side="left", padx=5)

        # --- Content ---
        content = ctk.CTkFrame(main_frame, fg_color=("white", "gray20"))
        content.pack(fill="both", expand=True, padx=20, pady=20)

        # Toolbar
        toolbar = ctk.CTkFrame(content, fg_color=("#e3f2fd", "gray25"), corner_radius=8)
        toolbar.pack(fill="x", padx=10, pady=10)

        # Search
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="left", padx=10, pady=8)
        
        ctk.CTkLabel(search_frame, text="🔍", font=("Arial", 16)).pack(side="left", padx=(0, 5))

        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Search products... (F3)", 
            width=300,
            height=35
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", self.search_products)

        # Filter
        self.category_filter = ctk.CTkComboBox(
            toolbar,
            values=["All Categories", "General", "Electronics", "Furniture", "Stationery", "Hardware", "Software"],
            width=150,
            height=35,
            command=self.filter_products
        )
        self.category_filter.set("All Categories")
        self.category_filter.pack(side="left", padx=10)

        refresh_btn = ctk.CTkButton(
            toolbar,
            text="↻ Refresh (F5)",
            width=120,
            height=35,
            fg_color="#1976d2",
            command=self.load_products
        )
        refresh_btn.pack(side="left", padx=10)

        self.count_label = ctk.CTkLabel(
            toolbar, 
            text="Total: 0 products",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.count_label.pack(side="right", padx=20)

        # Table
        table_frame = ctk.CTkFrame(content, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Product Code", "Product Name", "Category", "Stock Qty", "Unit Price", "Stock Value")
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=34, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 12, "bold"))

        scrollbar = ctk.CTkScrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show="headings", 
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        scrollbar.configure(command=self.tree.yview)

        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("Product Code", width=120)
        self.tree.column("Product Name", width=250)
        self.tree.column("Category", width=120)
        self.tree.column("Stock Qty", width=100, anchor="center")
        self.tree.column("Unit Price", width=120, anchor="e")
        self.tree.column("Stock Value", width=120, anchor="e")
        
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda e: self.edit_product())

        # Action Buttons
        action_frame = ctk.CTkFrame(content, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=(5, 10))

        ctk.CTkButton(action_frame, text="+ Add Product (Ctrl+N)", command=self.add_product, fg_color="#2e7d32", width=160, height=35).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="✏️ Edit", command=self.edit_product, fg_color="#f57c00", width=100, height=35).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="🗑️ Delete", command=self.delete_product, fg_color="#c62828", width=100, height=35).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📊 Stock Adjustment", command=self.stock_adjustment, fg_color="#7b1fa2", width=150, height=35).pack(side="left", padx=5)
        ctk.CTkButton(action_frame, text="📈 Stock Report", command=self.stock_report, width=150, height=35).pack(side="left", padx=5)

        # Shortcuts
        self.root.bind("<Control-n>", lambda e: self.add_product())
        self.root.bind("<F3>", lambda e: self.search_entry.focus())
        self.root.bind("<F5>", lambda e: self.load_products())

    def load_products(self):
        """Load products from database"""
        self.loading_overlay = show_loading_overlay(self.root, "Loading inventory...")
        run_async(self._fetch_data)

    def _fetch_data(self):
        try:
            data = self.db.load_json(self.company_name, "products.json")
            products = data if isinstance(data, list) else []
            self.root.after(0, lambda: self._update_ui_after_load(products))
        except Exception as e:
            self.root.after(0, lambda: self._handle_load_error(e))

    def _handle_load_error(self, error):
        hide_loading_overlay(self.loading_overlay)
        messagebox.showerror("Error", f"Failed to load products:\n{error}")

    def _update_ui_after_load(self, products):
        self.products = products
        self.filtered_products = self.products.copy()
        self.display_products()
        hide_loading_overlay(self.loading_overlay)

    def display_products(self):
        """Display products in tree"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        total_value = 0
        items_to_insert = []
        
        for product in self.filtered_products:
            qty = product.get("stock_qty", 0)
            price = product.get("unit_price", 0)
            value = qty * price
            total_value += value

            items_to_insert.append((
                product.get("product_code", ""),
                product.get("product_name", ""),
                product.get("category", ""),
                qty,
                Formatters.format_currency(price),
                Formatters.format_currency(value)
            ))

        PerformanceOptimizer.batch_insert(self.tree, items_to_insert)
        self.count_label.configure(text=f"Total: {len(self.filtered_products)} products | Value: {Formatters.format_currency(total_value)}")

    @debounce_search(300)
    def search_products(self, event=None):
        term = self.search_entry.get().lower().strip()
        self._apply_filters(term)

    def filter_products(self, event=None):
        term = self.search_entry.get().lower().strip()
        self._apply_filters(term)

    def _apply_filters(self, term):
        category = self.category_filter.get()
        
        filtered = self.products
        
        if category != "All Categories":
            filtered = [p for p in filtered if p.get("category") == category]
            
        if term:
            filtered = [
                p for p in filtered
                if term in p.get("product_name", "").lower() or
                   term in p.get("product_code", "").lower()
            ]
            
        self.filtered_products = filtered
        self.display_products()

    def get_selected_product(self) -> Optional[Dict[str, Any]]:
        sel = self.tree.selection()
        if not sel:
            return None
        code = self.tree.item(sel[0])['values'][0]
        return next((p for p in self.products if p.get("product_code") == code), None)

    def add_product(self):
        """Add new product"""
        self.show_product_form(None)

    def edit_product(self):
        """Edit selected product"""
        product = self.get_selected_product()
        if not product:
            messagebox.showwarning("Warning", "Please select a product.")
            return
        self.show_product_form(product)

    def show_product_form(self, product_data: Optional[Dict[str, Any]]):
        """Show product form dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Edit Product" if product_data else "Add New Product")
        dialog.geometry("600x600")
        dialog.transient(self.root)
        dialog.grab_set()

        def on_save(values):
            self._save_product(values, product_data, dialog)

        def on_cancel():
            dialog.destroy()

        form = EnhancedForm(
            dialog,
            title="Edit Product" if product_data else "New Product",
            on_save=on_save,
            on_cancel=on_cancel,
            auto_save=True
        )
        form.pack(fill="both", expand=True)

        # --- Section 1: Product Details ---
        form.add_section("📦 Product Details")

        # Product Code
        code_val = product_data.get("product_code", "") if product_data else IDGenerator.generate_id("PRD-", self.products[-1].get("product_code") if self.products else None)
        code_entry = SmartEntry(form.current_section, required=True)
        code_entry.insert(0, code_val)
        if product_data:
            code_entry.configure(state="disabled")

        # Product Name
        name_entry = SmartEntry(form.current_section, required=True, placeholder_text="Product Name")
        if product_data: name_entry.insert(0, product_data.get("product_name", ""))

        form.add_field_pair(
            "Product Code:", code_entry,
            "Product Name:", name_entry,
            help_text1="Unique Product ID",
            help_text2="Name of the item"
        )

        # Category
        category_combo = SmartComboBox(
            form.current_section,
            values=["General", "Electronics", "Furniture", "Stationery", "Hardware", "Software"],
            allow_custom=True
        )
        category_combo.set(product_data.get("category", "General") if product_data else "General")

        form.add_field_pair("Category:", category_combo, "", None)

        # --- Section 2: Pricing & Stock ---
        form.add_section("💰 Pricing & Stock")

        # Unit Price
        price_entry = SmartNumberEntry(form.current_section, placeholder_text="0.00")
        if product_data: price_entry.insert(0, str(product_data.get("unit_price", 0)))

        # Stock Qty
        qty_entry = SmartNumberEntry(form.current_section, placeholder_text="0")
        if product_data: qty_entry.insert(0, str(product_data.get("stock_qty", 0)))
        else: qty_entry.insert(0, "0")

        form.add_field_pair(
            "Unit Price:", price_entry,
            "Initial Stock:", qty_entry,
            help_text1="Price per unit",
            help_text2="Current quantity on hand"
        )

    def _save_product(self, values, existing_data, dialog):
        # Extract values
        code = values.get("product_code", "").strip()
        name = values.get("product_name", "").strip()
        category = values.get("category", "General")
        
        if not code or not name:
            messagebox.showerror("Error", "Product Code and Name are required")
            return

        try:
            price = float(values.get("unit_price", "0").replace(',', ''))
            qty = float(values.get("initial_stock", "0").replace(',', '')) # label "Initial Stock:" -> "initial_stock"
        except ValueError:
            price = 0.0
            qty = 0.0

        new_product = {
            "product_code": code,
            "product_name": name,
            "category": category,
            "unit_price": price,
            "stock_qty": qty,
            "created_at": existing_data.get("created_at", datetime.now().isoformat()) if existing_data else datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        try:
            if existing_data:
                for i, p in enumerate(self.products):
                    if p.get("product_code") == code:
                        self.products[i] = new_product
                        break
                messagebox.showinfo("Success", "Product updated!")
            else:
                self.products.append(new_product)
                messagebox.showinfo("Success", "Product created!")

            self.db.save_json(self.company_name, "products.json", self.products)
            dialog.destroy()
            self.load_products()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save product:\n{e}")

    def delete_product(self):
        """Delete selected product"""
        product = self.get_selected_product()
        if not product:
            messagebox.showwarning("Warning", "Please select a product.")
            return

        if messagebox.askyesno("Confirm", f"Delete product {product.get('product_code')}?"):
            self.products = [p for p in self.products if p.get("product_code") != product.get("product_code")]
            self.db.save_json(self.company_name, "products.json", self.products)
            self.load_products()

    def stock_adjustment(self):
        """Stock adjustment dialog"""
        product = self.get_selected_product()
        if not product:
            messagebox.showwarning("Warning", "Please select a product.")
            return

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Stock Adjustment")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()

        form = EnhancedForm(
            dialog,
            title="Stock Adjustment",
            on_save=None,
            on_cancel=lambda: dialog.destroy(),
            auto_save=False
        )
        form.pack(fill="both", expand=True)

        form.add_section(f"Adjust Stock: {product.get('product_name')}")

        # Current Stock Display
        curr_stock = product.get('stock_qty', 0)
        lbl = ctk.CTkLabel(form.current_section, text=f"Current Stock: {curr_stock}", font=ctk.CTkFont(size=14, weight="bold"))
        lbl.grid(row=form.current_row, column=0, columnspan=2, pady=10)
        form.current_row += 1

        # Adjustment Type
        type_combo = SmartComboBox(form.current_section, values=["Add Stock", "Remove Stock", "Set Absolute Value"], allow_custom=False)
        type_combo.set("Add Stock")
        
        qty_entry = SmartNumberEntry(form.current_section, placeholder_text="0")

        form.add_field_pair("Adjustment Type:", type_combo, "Quantity:", qty_entry)

        reason_entry = SmartEntry(form.current_section, placeholder_text="Reason for adjustment")
        form.add_field_pair("Reason:", reason_entry, "", None)

        def on_save(values):
            adj_type = type_combo.get()
            try:
                qty = float(qty_entry.get().replace(',', ''))
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity")
                return

            new_qty = curr_stock
            if adj_type == "Add Stock":
                new_qty += qty
            elif adj_type == "Remove Stock":
                new_qty -= qty
            elif adj_type == "Set Absolute Value":
                new_qty = qty

            if new_qty < 0:
                messagebox.showerror("Error", "Stock cannot be negative")
                return

            product["stock_qty"] = new_qty
            self.db.save_json(self.company_name, "products.json", self.products)
            messagebox.showinfo("Success", f"Stock adjusted. New Quantity: {new_qty}")
            dialog.destroy()
            self.load_products()

        form.save_btn.configure(command=lambda: on_save(None))
        form.save_btn.configure(text="Apply Adjustment")

    def stock_report(self):
        """Show stock valuation report"""
        total_qty = sum(p.get("stock_qty", 0) for p in self.products)
        total_value = sum(p.get("stock_qty", 0) * p.get("unit_price", 0) for p in self.products)

        report = f"Stock Valuation Report\n"
        report += f"Total Products: {len(self.products)}\n"
        report += f"Total Stock Quantity: {total_qty}\n"
        report += f"Total Stock Value: {Formatters.format_currency(total_value)}\n\n"

        # Low stock items (qty < 10)
        low_stock = [p for p in self.products if p.get("stock_qty", 0) < 10]
        if low_stock:
            report += f"\nLow Stock Items ({len(low_stock)}):\n"
            for p in low_stock:
                report += f"  - {p.get('product_name')}: {p.get('stock_qty')} units\n"

        messagebox.showinfo("Stock Report", report)
