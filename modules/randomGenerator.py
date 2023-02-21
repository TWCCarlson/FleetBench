import random

class randomGenerator:
    """
        Class which stores and uses a seeded RNG system to enable repeatable decisionmaking by agents
    """
    def __init__(self, parent):
        self.parent = parent

        self.randomGeneratorState = randomGeneratorState(self)

    def updateCurrentSeed(self, value):
        # Update generator's seed
        random.seed(value)
        self.randomGeneratorState.currentSeed = value

class randomGeneratorState:
    def __init__(self, parent):
        self.currentSeed = 123456789 # Default value