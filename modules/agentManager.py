class agentManager:
    def __init__(self, parent):
        self.parent = parent
        print("Agent Manager Class gen")
        # Generate agent class value options
        # Generate agent class definitions
        # Generate the agent class with inputs


        # Create a non-gui interface for generating and accessing all agents in the system
        self.agentList = {}
        print(type(self.agentList))

    def createNewAgent(self, *args):
        # Create a new agent and add it to the manager's list
        print(*args)
        self.latestAgent = agentClass(self)
        # The length of a dict is always 1 higher than the numeric id
        self.dictLength = len(self.agentList)
        self.agentList[self.dictLength] = self.latestAgent

        print(self.agentList)

class agentClass:
    def __init__(self, parent, ):
        self.parent = parent
        print("Create agent")
        
        # Collect specification values for this agent
        # - position, orientation, energy, etc
        # - id
        # - class
        # - task
        # - strength

        # Generate the agent object
        # Insert it to the map graph

        # Methods
        # Move
        # Pick up
        # Drop off
        # pathfind
        # set orientation
