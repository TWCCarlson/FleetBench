import random
import logging

class randomGenerator:
    """
        Class which stores and uses a seeded RNG system to enable repeatable decisionmaking by agents
    """
    def __init__(self, parent):
        self.parent = parent
        self.randomGeneratorState = randomGeneratorState(self)
        random.seed(self.randomGeneratorState.currentSeed)
        logging.debug(f"Random generator engine seeded with {self.randomGeneratorState.currentSeed}.")
        logging.info("Class 'randomGenerator' initialized.")

    def randomChoice(self, sequence):
        # Make a choice out of a sequence at random using the seeded generator
        # Be aware that when selecting a random node from a nodeView, the returned value is a string of the node name, not a tuple
        logging.debug(f"Request for choice from: {sequence}")
        choice = random.choice(sequence)
        logging.info("Random selection made.")
        logging.debug(f"Result: {choice}")
        return choice

    def updateCurrentSeed(self, value):
        # Update generator's seed
        logging.debug(f"Request received to update the seed value for 'randomGenerator' to: {value}")
        random.seed(value)
        self.randomGeneratorState.currentSeed = value
        logging.info("'randomGenerator' seed value updated.")
        logging.debug(f"New value: {self.randomGeneratorState.currentSeed}")

    def packageRandomGeneratorData(self):
        """
            Package data for replicating the current session
                - currentSeed
        """
        logging.info("Received request to package 'randomGenerator' data.")
        dataPackage = {}
        dataPackage["currentSeed"] = self.randomGeneratorState.currentSeed
        logging.debug(f"Packaged agentData: {dataPackage}")
        logging.info("Packaged all 'randomGenerator' data")
        return dataPackage

class randomGeneratorState:
    def __init__(self, parent):
        self.currentSeed = 123456789 # Default value
        logging.info(f"Class 'randomGeneratorState' initialized, with default seed {self.currentSeed}.")