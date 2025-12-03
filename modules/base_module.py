import customtkinter as ctk
from typing import Dict, Any, Optional


class BaseModule:
    """Base class for application modules.

    Provides small helpers that other modules can use. Subclasses must
    implement `setup_ui`.
    """

    def __init__(
        self,
        root: ctk.CTk,
        company_data: Optional[Dict[str, Any]] = None,
        user_data: Optional[Dict[str, Any]] = None,
        app_controller: Optional[Any] = None,
    ) -> None:
        self.root = root
        self.company_data = company_data or {}
        self.user_data = user_data or {}
        # Optional controller attributes that concrete modules may set.
        # Declaring them here avoids static-analysis errors in callers.
        self.app: Optional[Any] = app_controller
        self.dashboard: Any = None
        # Create DatabaseManager instance for modules to use.
        from .database_manager import DatabaseManager  # local import

        self.db = DatabaseManager()

        # call subclass UI setup
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the UI components. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement setup_ui")

    def destroy(self) -> None:
        """Destroy all widgets in the root window (safe cleanup)."""
        try:
            for widget in list(self.root.winfo_children()):
                widget.destroy()
        except Exception:
            # best-effort cleanup; don't raise during teardown
            pass

    def go_back(self) -> None:
        """Attempt to return to a previous/dashboard screen.
        
        This method uses the main application controller to show the dashboard.
        """
        try:
            if self.app and hasattr(self.app, 'show_dashboard'):
                # The controller needs company and user data to show the dashboard
                self.app.show_dashboard(self.company_data, self.user_data)
            else:
                # Fallback if the controller is missing
                from tkinter import messagebox
                messagebox.showerror("Navigation Error", "Application controller is not available to go back.")
                self.go_home() # Go to home screen as a last resort
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Navigation Error", f"Failed to return to dashboard: {e}")

    def go_home(self) -> None:
        """Return to the application's home screen."""
        try:
            if self.app and hasattr(self.app, 'show_home_screen'):
                self.app.show_home_screen()
            else:
                # Fallback for older modules that don't pass the app controller
                from .home_screen import HomeScreen
                self.destroy()
                HomeScreen(self.root, None) # type: ignore # No controller available
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Navigation Error", f"Failed to go home: {e}")
