import tkinter as tk
import logging
from simmodules.simulationMainView import simMainView
from simmodules.simulationInfoBox import simInfoBox

class simulationWindow(tk.Toplevel):
    # Window for displaying the current state of simulation
    def __init__(self, parent):
        super().__init__(parent.parent)
        self.parent = parent
        # Arrest the focus of the user away from the rest of the app
        self.focus()
        self.state('zoomed')
        self.grab_set()
        
        # Window components
        # Infobox
        self.simInfoBox = simInfoBox(self)
        # Main view frame and canvas
        self.simMainView = simMainView(self)
        logging.debug("Simulation Component class 'simMainView' instantiated successfully.")