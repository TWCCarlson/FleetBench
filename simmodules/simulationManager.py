import tkinter as tk
import logging

class simulationConfigManager(tk.Toplevel):
    # Window for managing the state of the simulation configuration
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        logging.info("Simulation Configuration Manager Class gen")
        self.title("Simulation Configuration Window")
        self.focus()     # "Select" the window
        self.grab_set()  # Forcefully keep attention on the window
        self.simulationConfigurationState = simulationConfigurationState(self)
        self.simulationLaunch = tk.Button(self, text="Launch Simulation", command=self.launchSimulation)
        self.simulationLaunch.grid(row=0, column=0)

        self.createAlgorithmChoices()

    def launchSimulation(self):
        simulationSettings = self.packageSimulationConfiguration()
        self.parent.launchSimulator(simulationSettings)

    def packageSimulationConfiguration(self):
        """
            Packages the current simulation configuration for saving
        """
        dataPackage = {}
        dataPackage["algorithmSelection"] = self.algorithmChoiceState

        return dataPackage
    
    def createAlgorithmChoices(self):
        # Creates a drop down menu for the user to select the driving algorithm for the simulation
        options = [
            "Dummy"
        ]

        # Set a default selection - maybe skip this to force a choice
        self.algorithmChoiceState = self.simulationConfigurationState.algorithmSelectionStringVar
        self.algorithmChoiceState.set(options[0])

        # Declare the drop down menu
        self.algorithmChoiceMenu = tk.OptionMenu(self, self.algorithmChoiceState, *options)

        # Render the menu
        self.algorithmChoiceMenu.grid(row=1, column=0)

class simulationConfigurationState:
    # Holds the current state of the simulation config
    def __init__(self, parent):
        self.parent = parent
        logging.info("Simulation State Default Init")

        # Stringvar to hold the algorithm selection
        self.algorithmSelectionStringVar = tk.StringVar()