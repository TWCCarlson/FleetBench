class simProcessor:
    def __init__(self, parent):
        self.parent = parent

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
        