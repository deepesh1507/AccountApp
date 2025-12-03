import customtkinter as ctk
from modules.enhanced_form import EnhancedForm
from modules.smart_widgets import SmartEntry, SmartDateEntry, SmartComboBox, SmartNumberEntry
import traceback

def test_form():
    root = ctk.CTk()
    root.geometry("800x600")
    
    def on_save(values):
        print("Saved:", values)
        
    def on_cancel():
        print("Cancelled")
        root.destroy()
        
    try:
        dialog = ctk.CTkToplevel(root)
        dialog.title("Test Form")
        dialog.geometry("800x600")
        
        form = EnhancedForm(
            dialog,
            title="Test Entry",
            on_save=on_save,
            on_cancel=on_cancel
        )
        form.pack(fill="both", expand=True)
        
        # Demonstrate proper EnhancedForm usage
        form.add_section("Header Information")
        
        # Add fields using EnhancedForm's built-in methods
        id_entry = SmartEntry(form.current_section)
        form.add_field("Entry ID:", id_entry)
        
        date_entry = SmartDateEntry(form.current_section)
        form.add_field("Date:", date_entry)
        
        # Test field pairs (two columns)
        name_entry = SmartEntry(form.current_section)
        type_combo = SmartComboBox(form.current_section, values=["Type A", "Type B", "Type C"])
        form.add_field_pair("Name:", name_entry, "Type:", type_combo)
        
        # Add another section
        form.add_section("Details")
        
        amount_entry = SmartNumberEntry(form.current_section, decimals=2)
        form.add_field("Amount:", amount_entry, colspan=2)
        
        description_entry = SmartEntry(form.current_section)
        form.add_field("Description:", description_entry, colspan=2, help_text="Enter a detailed description")
        
        print("Form created successfully")
        
        # Keep window open for a bit to verify visibility
        root.after(2000, lambda: print("Form visible"))
        root.after(3000, root.destroy)
        
        root.mainloop()
        
    except Exception as e:
        print("Error creating form:")
        traceback.print_exc()

if __name__ == "__main__":
    test_form()
