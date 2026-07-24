"""Open the operating system's folder selection dialog."""

import tkinter as tk
from tkinter import filedialog


def select_folder():
    """Open a folder picker and return the selected path.

    Returns an empty string when the user cancels the dialog.
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        return filedialog.askdirectory(
            title="Select an image library",
            parent=root,
        )
    finally:
        root.destroy()