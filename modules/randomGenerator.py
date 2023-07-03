import random

class randomGenerator:
    """
        Class which stores and uses a seeded RNG system to enable repeatable decisionmaking by agents
    """
    def __init__(self, parent):
        self.parent = parent
        self.randomGeneratorState = randomGeneratorState(self)
        random.seed(self.randomGeneratorState.currentSeed)

    def randomChoice(self, sequence):
        # Make a choice out of a sequence at random using the seeded generator
        # Be aware that when selecting a random node from a nodeView, the returned value is a string of the node name, not a tuple
        choice = random.choice(sequence)
        return choice

    def updateCurrentSeed(self, value):
        # Update generator's seed
        random.seed(value)
        self.randomGeneratorState.currentSeed = value

    def packageRandomGeneratorData(self):
        """
            Package data for replicating the current session
                - currentSeed
        """
        dataPackage = {}
        dataPackage["currentSeed"] = self.randomGeneratorState.currentSeed
        return dataPackage

class randomGeneratorState:
    def __init__(self, parent):
        self.currentSeed = 123456789 # Default value