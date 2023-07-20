import tkinter as tk
import logging

class simInfoBox(tk.Frame):
    """
        Bar resting above the main canvas
        Contains layer toggles
        Contains text responsive to highlights in the canvas
    """
    def __init__(self, parent):
        logging.debug("Simulation Info Box UI Class initializing . . .")
        self.parent = parent

        # Fetch frame style configuration
        self.appearanceValues = self.parent.parent.appearance
        frameHeight = self.appearanceValues.simulationInfoBoxHeight
        frameWidth = self.appearanceValues.simulationInfoBoxWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief
        logging.debug("Fetched styling information.")

        # Declare frame
        tk.Frame.__init__(self, parent,
            height=frameHeight,
            width=frameWidth,
            borderwidth=frameBorderWidth,
            relief=frameRelief)
        logging.debug("Simulation Info Box Containing Frame constructed.")

        # Render the frame
        self.grid(row=0, column=1, sticky=tk.N)
        logging.info("Info Box UI elements rendered into simulation window.")
