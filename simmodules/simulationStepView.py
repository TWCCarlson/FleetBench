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

        self.createLabel()

    def createLabel(self):
        # Header text is static
        self.headerText = tk.Label(self, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"),
            text="Simulation Step")
        self.headerText.grid(row=0, column=0)

        # Descriptive text is dynamic, needs a stringVar
        self.simStepTextValue = tk.StringVar(value="Waiting . . .")
        self.simStepText = tk.Label(self, font=(tkfont.nametofont("TkDefaultFont"), 12, "bold"),
            textvariable=self.simStepTextValue)
        self.simStepText.grid(row=1, column=0)
