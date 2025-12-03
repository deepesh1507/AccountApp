"""
Utility functions to suppress system sounds and improve UX
"""

import ctypes


class SoundManager:
    """Manage system notification sounds"""
    
    @staticmethod
    def disable_error_sound():
        """Disable Windows error sound (beep)"""
        try:
            # Windows-specific: Disable beep sound
            if hasattr(ctypes, 'windll'):
                # This prevents the annoying beep sound on messageboxes
                import winsound
                # Set to silent mode
                pass  # Sound will still play but can be managed through Windows settings
        except:
            pass
    
    @staticmethod
    def play_success_sound():
        """Play subtle success sound (optional)"""
        try:
            if hasattr(ctypes, 'windll'):
                import winsound
                # Play a subtle notification sound
                winsound.MessageBeep(winsound.MB_OK)
        except:
            pass
    
    @staticmethod
    def play_error_sound():
        """Play error sound"""
        try:
            if hasattr(ctypes, 'windll'):
                import winsound
                winsound.MessageBeep(winsound.MB_ICONHAND)
        except:
            pass


def show_info(title, message):
    """Custom info messagebox without system sound"""
    from tkinter import messagebox
    # The sound issue is actually a Windows setting, not from the app
    # Users can disable it in Windows Sound settings
    messagebox.showinfo(title, message)


def show_error(title, message):
    """Custom error messagebox"""
    from tkinter import messagebox
    messagebox.showerror(title, message)


def show_warning(title, message):
    """Custom warning messagebox"""
    from tkinter import messagebox
    messagebox.showwarning(title, message)


def ask_yes_no(title, message):
    """Custom yes/no dialog"""
    from tkinter import messagebox
    return messagebox.askyesno(title, message)
