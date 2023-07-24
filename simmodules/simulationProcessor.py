import pprint
pp = pprint.PrettyPrinter(indent=4)

class simProcessor:
    def __init__(self, parent, simulationSettings):
        self.parent = parent
        self.simulationSettings = simulationSettings

        self.simulateStep()

    def simulateStep(self):
        """
            Check for selected algorithm
            Feed algorithm all the simulation state information
            - Iterate over agents, top->bottom? bottom->top? some kind of adaptive technique? short distances to go first? long first?
            Collect algorithm Orders
            Validate any interactions
            - Pickup, dropoff, resting, task completion
            Record the history for replay
            Render the new state
            - Update statistics
        """
        # Check what the currently in use algorithm is
        algorithmSelection = self.simulationSettings["algorithmSelection"].get()