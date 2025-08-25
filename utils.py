import tkinter as tk
from tkinter import ttk

class ActivityBar:
    """
    A simple, modal activity indicator using an indeterminate progress bar.

    This class creates a floating Toplevel window with a progress bar that
    hovers over the main application, graying out the background and
    preventing user interaction with the main window until the task is complete.
    """
    def __init__(self, master):
        """
        Initializes the ActivityBar.

        Args:
            master (tk.Tk): The parent widget (typically the main Tk window).
        """
        self.master = master
        self.top_level = None
        self.progressbar = None

    def start(self, message="Processing..."):
        """
        Displays the activity bar, making it modal and starting the animation.

        Args:
            message (str): The text message to display.
        """
        # Create a Toplevel window to act as the overlay
        self.top_level = tk.Toplevel(self.master)
        self.top_level.title("")
        self.top_level.config(bg="#f0f0f0", bd=0, relief="flat")

        # Remove the window's title bar and controls
        self.top_level.overrideredirect(True)

        # Center the Toplevel window over the main window
        self.master.update_idletasks()
        main_width = self.master.winfo_width()
        main_height = self.master.winfo_height()
        main_x = self.master.winfo_x()
        main_y = self.master.winfo_y()

        bar_width = 250
        bar_height = 100
        x_pos = main_x + (main_width // 2) - (bar_width // 2)
        y_pos = main_y + (main_height // 2) - (bar_height // 2)
        self.top_level.geometry(f"{bar_width}x{bar_height}+{x_pos}+{y_pos}")

        # Set up a semi-transparent background frame
        bg_frame = tk.Frame(self.top_level, bg="#e0e0e0", relief="raised", bd=2)
        bg_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Use a modern theme for ttk widgets
        style = ttk.Style(self.top_level)
        style.theme_use('clam')
        style.configure('TProgressbar', thickness=15)

        # Add a label and the indeterminate progress bar
        status_label = ttk.Label(bg_frame, text=message, font=("Helvetica", 12))
        status_label.pack(pady=(15, 5))

        self.progressbar = ttk.Progressbar(
            bg_frame,
            orient="horizontal",
            mode="indeterminate"
        )
        self.progressbar.pack(fill="x", padx=10, pady=10)

        # Make the Toplevel modal by grabbing the focus.
        # This prevents interaction with the main window.
        self.top_level.transient(self.master)
        self.top_level.grab_set()

        # Start the progress bar animation
        self.progressbar.start(15)

    def stop(self):
        """
        Stops the animation and hides the activity bar.
        """
        if self.progressbar:
            self.progressbar.stop()
        if self.top_level:
            self.top_level.destroy()
            self.top_level = None
            # Release the focus grab
            self.master.grab_release()


def show_snackbar(root, message, duration = 3000):
    """
    :type root: tk.Tk
    :type message: str
    :type duration: int
    """
    snackbar = tk.Toplevel(root)
    snackbar.overrideredirect(True)  # remove window decorations
    snackbar.configure(bg="#323232")

    # position it at the bottom center of the root window
    root_x = root.winfo_rootx()
    root_y = root.winfo_rooty()
    root_height = root.winfo_height()
    margin = 50
    snackbar.geometry(f"+{root_x + margin}+{root_y + root_height - margin}")

    label = tk.Label(snackbar, text=message, fg="white", bg="#323232", padx=20, pady=10)
    label.pack()

    # destroy after duration ms
    # noinspection PyTypeChecker
    snackbar.after(duration, snackbar.destroy)