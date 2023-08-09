import tkinter as tk
from tkinter import ttk
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
        frameHeight = self.appearanceValues.simulationControlBoxHeight
        frameWidth = self.appearanceValues.simulationControlBoxWidth
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
        logging.debug("Simulation Control Panel UI elements building . . .")
        # Declare rapid continuous playback button
        self.revertRapidlyButton = tk.Button(self, text="⏪")

        # Declare step backward until event occurred button
        self.revertToLastEventButton = tk.Button(self, text="⏮")

        # Declare step backward once button
        self.revertOneStepButton = tk.Button(self, text="⭰")

        # Declare slow continuous playback/pause button
        self.toggleSimulationRunButton = tk.Button(self, text="⏯", background="yellow", command=self.simulationPlayPauseToggle)

        # Declare step forward once button
        self.simOneStepButton = tk.Button(self, text="⭲", command=self.simulationProcess.simProcessor.simulateStep)

        # Declare playback until event occurs button
        self.simUntilEventButton = tk.Button(self, text="⏭")

        # Declare rapid continous playforward button
        self.simRapidlyButton = tk.Button(self, text="⏩")

        # Declare simulation edit button
        self.editSimulationStateButton = tk.Button(self, text="⏏", background="yellow")

        # Declare simulation stop button
        self.stopSimulationButton = tk.Button(self, text="◼", background="orange")

        # Use column weights to distribute button widths evenly
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=3)
        self.columnconfigure(3, weight=3)
        self.columnconfigure(4, weight=3)
        self.columnconfigure(5, weight=3)
        self.columnconfigure(6, weight=3)
        self.columnconfigure(7, weight=1)
        self.columnconfigure(8, weight=3)
        self.columnconfigure(9, weight=1)
        self.columnconfigure(10, weight=3)
        
        # Render Buttons
        self.revertRapidlyButton.grid(row=0, column=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.revertToLastEventButton.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W)
        self.revertOneStepButton.grid(row=0, column=2, sticky=tk.N+tk.S+tk.E+tk.W)
        self.toggleSimulationRunButton.grid(row=0, column=3, sticky=tk.N+tk.S+tk.E+tk.W)
        self.simOneStepButton.grid(row=0, column=4, sticky=tk.N+tk.S+tk.E+tk.W)
        self.simUntilEventButton.grid(row=0, column=5, sticky=tk.N+tk.S+tk.E+tk.W)
        self.simRapidlyButton.grid(row=0, column=6, sticky=tk.N+tk.S+tk.E+tk.W)
        self.editSimulationStateButton.grid(row=0, column=8, sticky=tk.N+tk.S+tk.E+tk.W)
        self.stopSimulationButton.grid(row=0, column=10, sticky=tk.N+tk.S+tk.E+tk.W)

    def simulationPlayPauseToggle(self):
        logging.debug("User toggled the play state of the simulation.")
        if self.toggleSimulationRunButton['relief'] == tk.RAISED:
            logging.debug("Playback started at standard speed.")
            # Set the button to have the appearance of having been pressed
            self.toggleSimulationRunButton.config(relief=tk.SUNKEN, background="lawn green")
            # Disable the other buttons
            self.disableOtherPlaybackControls(self.toggleSimulationRunButton)
            # Start the updating ticking process
            self.simulationProcess.simProcessor.simulationUpdateTick()
        elif self.toggleSimulationRunButton['relief'] == tk.SUNKEN:
            logging.debug("Play button released. Pausing playback.")
            # Set the button to have the appearance of being released
            self.toggleSimulationRunButton.config(relief=tk.RAISED, background="yellow")
            # Re-enable the other buttons
            self.enableOtherPlaybackControls(self.toggleSimulationRunButton)
            # Stop the update ticking process
            self.simulationProcess.simProcessor.simulationStopTicking()

    def disableOtherPlaybackControls(self, buttonInUse):
        # Iterate over all buttons in the frame, disabling those that are not the one being used
        for widget in self.winfo_children():
            if widget.winfo_class() == "Button" and not widget == buttonInUse:
                widget.config(state=tk.DISABLED)
            

    def enableOtherPlaybackControls(self, buttonReleased):
        # Iterate over all buttons in the frame, enabling those that are not the one being used
        for widget in self.winfo_children():
            if widget.winfo_class() == "Button" and not widget == buttonReleased:
                widget.config(state=tk.NORMAL)