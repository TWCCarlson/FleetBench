import tkinter as tk

class simulationWindow(tk.Toplevel):
    # Window for displaying the current state of simulation
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.focus()
        self.grab_set()