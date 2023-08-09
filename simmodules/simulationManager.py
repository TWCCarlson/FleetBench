import tkinter as tk
from tkinter import ttk
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
        self.createSimulationUpdateRate()

    def launchSimulation(self):
        simulationSettings = self.packageSimulationConfiguration()
        self.parent.launchSimulator(simulationSettings)

    def packageSimulationConfiguration(self):
        """
            Packages the current simulation configuration for saving
        """
        dataPackage = {}
        dataPackage["algorithmSelection"] = self.algorithmChoiceState
        dataPackage["playbackFrameDelay"] = self.frameDelayValue.get()

        return dataPackage
    
    def createAlgorithmChoices(self):
        # Creates a drop down menu for the user to select the driving algorithm for the simulation

        # Optiontype dict
        optionTypeDict = {
            "Dummy": "mapf",
            "Single-agent A*": "sapf"
        }

        # Keys of the dict are the displayed options
        options = list(optionTypeDict.keys())

        # Set a default selection - maybe skip this to force a choice
        self.algorithmChoiceState = self.simulationConfigurationState.algorithmSelectionStringVar
        self.algorithmChoiceState.set(options[0])

        # Declare the drop down menu
        self.algorithmChoiceMenu = tk.OptionMenu(self, self.algorithmChoiceState, *options)

        # If there is more than one agent in the simulation space, disable single-agent pathfinding algorithm options
        for algorithm, type in optionTypeDict.items():
            if type == "sapf" and len(self.parent.agentManager.agentList) > 1:
                self.algorithmChoiceMenu['menu'].entryconfigure(algorithm, state=tk.DISABLED)

        # Render the menu
        self.algorithmChoiceMenu.grid(row=1, column=0)

    def createSimulationUpdateRate(self):
        self.frameDelayLabel = tk.Label(self, text="frameDelay:")
        self.frameDelayValue = tk.StringVar()
        self.validateFrameDelayEntry = self.register(self.validateNumericSpinbox)
        # self.validateTaskTimeLimit = self.register(self.taskTimeLimitValidation)
        # self.commandTaskTimeLimit = partial(self.taskTimeLimitValidation, 'T')
        self.frameDelayValue.trace_add("write", lambda *args, b=self.frameDelayValue : self.frameDelayValidation(b, *args))
        # Create a spinbox with entry for millisecond time between frame updates of the canvas while the play button is depressed
        self.frameDelayEntry = ttk.Spinbox(self,
            width=6,
            from_=0,
            to=100000,
            increment=50,
            textvariable=self.frameDelayValue,
            # command=self.commandTaskTimeLimit,
            validate='key',
            validatecommand=(self.validateFrameDelayEntry, '%P')
        )
        logging.debug("Simulation playback frame delay spinbox built.")

        # Set a default value
        self.frameDelayValue.set(1000)

        # Render components
        self.frameDelayLabel.grid(row=1, column=1)
        self.frameDelayEntry.grid(row=1, column=2)

    def validateNumericSpinbox(self, inputString):
        logging.debug(f"Validating numeric spinbox entry: {inputString}")
        if inputString.isnumeric():
            # Only allow numeric characters
            logging.debug("Numeric spinbox entry is numeric. Allowed.")
            return True
        elif len(inputString) == 0:
            logging.debug("Numeric spinbox entry is empty. Allowed.")
            # Or an empty box
            return True
        else:
            logging.debug("Numeric spinbox entry is invalid.")
            return False
        
    def frameDelayValidation(self, frameDelay, *args):
        logging.debug(f"Validating custom playback frame delay entry '{frameDelay}'.")
        # Spinbox should only accept numeric entries
        if frameDelay.get().isnumeric():
            # self.validFrameDelayEntry = True
            logging.debug("Playback frame delay entry is numeric. Allowed.")
            return True
        else:
            # self.validFrameDelayEntry = False
            logging.debug("Playback frame delay entry is non-numeric and invalid.")
            return False

class simulationConfigurationState:
    # Holds the current state of the simulation config
    def __init__(self, parent):
        self.parent = parent
        logging.info("Simulation State Default Init")

        # Stringvar to hold the algorithm selection
        self.algorithmSelectionStringVar = tk.StringVar()