"""Open the operating system's folder selection dialog."""

import tkinter as tk
from tkinter import filedialog


def select_folder(title=None):
    """Open a folder picker and return the selected path.

    Returns an empty string when the user cancels the dialog.
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    
    if title is None:
        title = "Select an image library"

    try:
        return filedialog.askdirectory(
            title=title,
            parent=root,
        )
    finally:
        root.destroy()


