import random

class randomGenerator():
    def __init__(self, parent):
        self.parent = parent

        self.currentSeed = 123456789 # Default value

    def updateCurrentSeed(self, value):
        # Update generator's seed
        random.seed(value)
        self.currentSeed = value