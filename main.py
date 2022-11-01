import tkinter as tk
from modules import commandBar
from modules import toolBar
from config import appearanceValues
from modules import mainView
from modules import contextView
from modules import mapDataClass
from modules import infoBox

class App(tk.Tk):
    def __init__(self):
        # Main window config
        tk.Tk.__init__(self)
        self.title("Warehousing Simulator")

        # Map information class
        self.mapData = mapDataClass(self)

        # Window components
        # Appearance
        self.appearance = appearanceValues(self)
        # Command bar: load, save, options
        self.commandBar = commandBar(self)
        # Left pane contains choices and buttons
        self.toolBar = toolBar(self)
        # Central pane info box
        self.infoBox = infoBox(self)
        # Central pane contains the graph display
        self.mainView = mainView(self)
        # Right pane contains contextual information pane
        self.contextView = contextView(self)

        # Build cross-class references
        self.mapData.buildReferences()
        self.infoBox.buildReferences()

        # Render the app
        self.mainloop()

app = App()