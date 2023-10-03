import tkinter as tk
import logging
from tkinter import font as tkfont

class simStepView(tk.Frame):
    """
        Displays the current step in the simulation process, some data
    """
    def __init__(self, parent):
        logging.debug("Simulation step display view UI element initializing . . .")
        self.parent = parent

        # Fetch frame style configuration
        self.appearanceValues = self.parent.parent.parent.appearance
        self.frameWidth = self.appearanceValues.simulationControlBoxWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief
        logging.debug("Fetched styling information.")

        # Declare frame
        tk.Frame.__init__(self, parent,
            width=self.frameWidth,
            borderwidth=frameBorderWidth,
            relief=frameRelief)
        logging.debug("Simulation Data View Containing Frame constructed.")

        self.grid(row=1, column=1, sticky=tk.N+tk.W+tk.E)
        self.columnconfigure(0, weight=1)

        self.createStatusLabel()
        self.createStepCountLabel()

    def createStatusLabel(self):
        # Header text is static
        self.statusHeaderText = tk.Label(self, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"),
            text="Simulation Step")
        self.statusHeaderText.grid(row=0, column=0, sticky=tk.W)

        # Descriptive text is dynamic, needs a stringVar
        self.simStatusTextValue = tk.StringVar(value="Waiting . . .")
        self.simStatusText = tk.Label(self, font=(tkfont.nametofont("TkDefaultFont"), 12, "bold"),
            textvariable=self.simStatusTextValue)
        self.simStatusText.grid(row=1, column=0, sticky=tk.W)

    def createStepCountLabel(self):
        # Header text is static
        self.stepCountHeaderText = tk.Label(self, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"),
            text="Step #")
        self.stepCountHeaderText.grid(row=0, column=1, sticky=tk.E)

        # Descriptive text is dynamic, needs a stringvar
        self.simStepCountTextValue = tk.IntVar(value=0)
        self.simStepCountText = tk.Label(self, font=(tkfont.nametofont("TkDefaultFont"), 12, "bold"), textvariable=self.simStepCountTextValue)
        self.simStepCountText.grid(row=1, column=1, sticky=tk.E)
