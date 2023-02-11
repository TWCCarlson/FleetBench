import tkinter as tk
from modules.commandBar import commandBar
from modules.toolBar import toolBar
from modules.mainView import mainView
from modules.contextView import contextView
from modules.mapDataClass import mapDataClass
from modules.infoBox import infoBox
from modules.agentManager import agentManager
from config.appearanceValues import appearanceValues

class App(tk.Tk):
    def __init__(self):
        # Main window config
        tk.Tk.__init__(self)
        self.title("Warehousing Simulator")

        # Map information class
        self.mapData = mapDataClass(self)
        # Agent information manager class
        self.agentManager = agentManager(self)

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
        self.toolBar.buildReferences()
        self.mainView.buildReferences()

        # Render the app
        self.mainloop()

app = App()