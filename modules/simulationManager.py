class simulationManager:
    # Manages the state of the simulation configuration
    def __init__(self, parent):
        self.parent = parent
        print("Simulation Manager Class gen")

        self.simulationConfigurationState = simulationConfigurationState(self)

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
        print("Simulation State Default Init")