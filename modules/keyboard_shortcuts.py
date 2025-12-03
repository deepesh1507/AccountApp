"""
Keyboard Shortcuts Handler
Provides Tally-style keyboard shortcuts across the application
Features: Alt+key navigation, F-key shortcuts, quick actions
"""

class KeyboardShortcuts:
    """Handle keyboard shortcuts for the application"""
    
    # Shortcut mappings (Tally-style)
    SHORTCUTS = {
        # F-keys
        "F1": "help",
        "F2": "change_period",
        "F3": "create_company",
        "F4": "close_window",
        "F5": "refresh",
        "F6": "go_back",
        "F9": "accept_form",
        "F12": "configure",
        
        # Alt+key combinations
        "Alt+C": "chart_of_accounts",
        "Alt+I": "invoice",
        "Alt+E": "expenses",
        "Alt+R": "reports",
        "Alt+J": "journal",
        "Alt+L": "ledger",
        "Alt+G": "gst",
        "Alt+P": "inventory",
        "Alt+S": "settings",
        "Alt+Q": "quit",
        
        # Ctrl+key combinations
        "Ctrl+N": "new",
        "Ctrl+S": "save",
        "Ctrl+F": "find",
        "Ctrl+P": "print",
        "Ctrl+E": "export",
        "Ctrl+Q": "quit",
    }
    
    @staticmethod
    def bind_shortcuts(root, handlers):
        """
        Bind keyboard shortcuts to the root window
        
        Args:
            root: The Tk root window
            handlers: Dictionary mapping actions to handler functions
        """
        # F-key bindings
        for i in range(1, 13):
            root.bind(f"<F{i}>", lambda e, key=f"F{i}": KeyboardShortcuts._handle_shortcut(key, handlers))
        
        #Alt+key bindings
        for letter in "CEIRJLGPSQ":
            root.bind(f"<Alt-{letter.lower()}>", lambda e, key=f"Alt+{letter}": KeyboardShortcuts._handle_shortcut(key, handlers))
        
        # Ctrl+key bindings
        for letter in "NSFPEQ":
            root.bind(f"<Control-{letter.lower()}>", lambda e, key=f"Ctrl+{letter}": KeyboardShortcuts._handle_shortcut(key, handlers))
    
    @staticmethod
    def _handle_shortcut(key, handlers):
        """Handle a shortcut keypress"""
        action = KeyboardShortcuts.SHORTCUTS.get(key)
        if action and action in handlers:
            try:
                handlers[action]()
            except Exception as e:
                print(f"Error executing shortcut {key} -> {action}: {e}")
    
    @staticmethod
    def get_shortcut_help():
        """Get formatted help text for shortcuts"""
        help_text = "KEYBOARD SHORTCUTS\n"
        help_text += "="*50 + "\n\n"
        
        help_text += "F-KEYS:\n"
        help_text += "  F1  - Show Help\n"
        help_text += "  F2  - Change Period\n"
        help_text += "  F3  - Create Company\n"
        help_text += "  F4  - Close Window\n"
        help_text += "  F5  - Refresh\n"
        help_text += "  F6  - Go Back\n"
        help_text += "  F9  - Accept/Save Form\n"
        help_text += "  F12 - Configure Settings\n\n"
        
        help_text += "ALT+KEY (Module Navigation):\n"
        help_text += "  Alt+C - Chart of Accounts\n"
        help_text += "  Alt+I - Invoices\n"
        help_text += "  Alt+E - Expenses\n"
        help_text += "  Alt+R - Reports\n"
        help_text += "  Alt+J - Journal Entries\n"
        help_text += "  Alt+L - Ledger\n"
        help_text += "  Alt+G - GST/Tax\n"
        help_text += "  Alt+P - Inventory'\n"
        help_text += "  Alt+S - Settings\n"
        help_text += "  Alt+Q - Quit\n\n"
        
        help_text += "CTRL+KEY (Actions):\n"
        help_text += "  Ctrl+N - New Entry\n"
        help_text += "  Ctrl+S - Save\n"
        help_text += "  Ctrl+F - Find/Search\n"
        help_text += "  Ctrl+P - Print\n"
        help_text += "  Ctrl+E - Export\n"
        help_text += "  Ctrl+Q - Quit\n"
        
        return help_text
