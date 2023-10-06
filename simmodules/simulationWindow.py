import tkinter as tk
import logging
from simmodules.simulationMainView import simMainView
from simmodules.simulationInfoBox import simInfoBox
from simmodules.simulationControlPanel import simControlPanel
from simmodules.simulationDataView import simDataView
from simmodules.simulationStepView import simStepView

class simulationWindow(tk.Toplevel):
    # Window for displaying the current state of simulation
    def __init__(self, parent):
        super().__init__(parent.parent)
        self.parent = parent
        # Arrest the focus of the user away from the rest of the app
        self.focus()
        self.state('zoomed')
        self.grab_set()

        self.leftPanel = tk.Frame(self)
        self.rightPanel = tk.Frame(self)
        self.leftPanel.grid(row=0, column=0, sticky="news")
        self.rightPanel.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
        self.columnconfigure(1, weight=1)
        self.rightPanel.rowconfigure(3, weight=1)
        self.rightPanel.columnconfigure(0, weight=1)
        
        # Window components
        # Infobox
        self.simInfoBox = simInfoBox(self, self.leftPanel)
        logging.info("Simulation component class 'simInfoBox' instantiated successfully.")

        # Main view frame and canvas
        self.simMainView = simMainView(self, self.leftPanel)
        logging.info("Simulation Component class 'simMainView' instantiated successfully.")

        # Simulation control bar
        self.simControlPanel = simControlPanel(self, self.rightPanel)
        logging.info("Simulation Component class 'simControlPanel' instantiated successfully.")

        # Simulation current process display
        self.simStepView = simStepView(self, self.rightPanel)
        logging.info("Simulation Component class 'simStepView' instantiated successfully.")

        # Simulation Agent and Task display
        self.simDataView = simDataView(self, self.rightPanel)
        logging.info("Simulation Component class 'simDataView' instantiated successfully.")