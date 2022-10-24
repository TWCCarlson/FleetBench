import tkinter as tk
from modules import commandBar
from modules import toolBar
from config import appearanceValues
from modules import mainView
from modules import contextView

class App(tk.Tk):
    def __init__(self):
        # Main window config
        tk.Tk.__init__(self)
        self.title("Warehousing Simulator")

        # Window components
        # Appearance
        self.appearance = appearanceValues(self)
        # Command bar: load, save, options
        self.commandBar = commandBar(self)
        # Left pane contains choices and buttons
        self.toolBar = toolBar(self)
        # Central pane contains the graph display
        self.mainView = mainView(self)
        # Right pane contains contextual information pane
        self.contextView = contextView(self)

        # Render the app
        self.mainloop()

app = App()