import customtkinter as ctk
from modules.enhanced_form import EnhancedForm
from modules.smart_widgets import SmartEntry
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
        
        # Test with just ONE simple field
        form.add_section("Header Information")
        
        id_entry = SmartEntry(form.current_section)
        form.add_field("Entry ID:", id_entry)
        
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
