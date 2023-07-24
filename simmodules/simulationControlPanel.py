import tkinter as tk
import logging

class simControlPanel(tk.Frame):
    """
        Panel housing controls for the simulation play
        - 1 step
        - Play (steps with pauses for display)
        - Advance X steps
        - Advance X task completions
    """
    def __init__(self, parent):
        logging.debug("Simulation Control Panel UI Class initializing . . .")
        self.parent = parent

        # Fetch style
        self.appearanceValues = self.parent.parent.parent.appearance
        frameHeight = self.appearanceValues.simulationInfoBoxHeight
        frameWidth = self.appearanceValues.simulationInfoBoxWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief

        # Declare frame
        tk.Frame.__init__(self, parent,
            height=frameHeight,
            width=frameWidth,
            borderwidth=frameBorderWidth,
            relief=frameRelief                  
        )
        logging.debug("Simulation Control Panel Containing Frame constructed.")

        # Render Frame
        self.grid_propagate(False)
        self.grid(row=0, column=1, sticky=tk.N)

    def buildReferences(self):
        # Build references to other parts of the simulation
        self.simulationProcess = self.parent.parent.simulationProcess

        # Build the rest of the UI with the needed references
        self.buildSimulationControlUI()

    def buildSimulationControlUI(self):
        # Declare step forward once button
        self.simOneStepButton = tk.Button(self, text="⏵", command=self.parent.parent.simulationProcess.simProcessor.simulateStep)
        
        # Render Buttons
        self.simOneStepButton.grid(row=0, column=0)