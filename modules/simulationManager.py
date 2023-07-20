import tkinter as tk

class simulationConfigManager(tk.Toplevel):
    # Window for managing the state of the simulation configuration
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        print("Simulation Configuration Manager Class gen")
        self.title("Simulation Configuration Window")
        self.focus()     # "Select" the window
        self.grab_set()  # Forcefully keep attention on the window
        self.simulationConfigurationState = simulationConfigurationState(self)
        self.simulationLaunch = tk.Button(self, text="Launch Simulation", command=self.parent.launchSimulator)
        self.simulationLaunch.grid(row=0, column=0)

    def packageSimulationConfiguration(self):
        """
            Packages the current simulation configuration for saving
        """
        dataPackage = {}
        return

class simulationConfigurationState:
    # Holds the current state of the simulation config
    def __init__(self, parent):
        self.parent = parent
        self.testVal = 50
        print("Simulation State Default Init")