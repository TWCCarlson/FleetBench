import tkinter as tk

class simulationWindow(tk.Toplevel):
    # Window for displaying the current state of simulation
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        # Arrest the focus of the user away from the rest of the app
        self.focus()
        self.state('zoomed')
        self.grab_set()