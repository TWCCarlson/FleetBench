class agentManager:
    def __init__(self, parent):
        self.parent = parent
        print("Agent Manager Class gen")
        # Generate agent class value options
        # Generate agent class definitions
        # Generate the agent class with inputs


        # Create a non-gui interface for generating and accessing all agents in the system
        self.agentList = {}
        self.agentPositionList = {}
        self.currentAgent = []
        print(type(self.agentList))

    def createNewAgent(self, **kwargs):
        # The length of a dict is always 1 higher than the numeric id
        self.dictLength = len(self.agentList)
        try:
            ID = kwargs.pop("ID")
        except KeyError:
            ID = self.dictLength
        # Create a new agent and add it to the manager's list
        self.latestAgent = agentClass(self, **kwargs, ID=ID, numID = self.dictLength)
        self.agentList[self.dictLength] = self.latestAgent

        self.parent.contextView.updateTreeView()

class agentClass:
    def __init__(self, parent, **kwargs):
        self.parent = parent
        print("Create agent")
        self.numID = kwargs.pop("numID")
        self.ID = kwargs.pop("ID")
        self.position = kwargs.pop("position")
        self.orientation = kwargs.pop("orientation")
        self.className = kwargs.pop("className")

        # Add the agent to the position list for reference in tileHover
        self.parent.agentPositionList[str(self.position)] = [self.ID, self.numID]
        # Push some data into the map graph attributes for fast referencing elsewhere

        
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

    def highlightAgent(self, multi):
        # Have the agent request highlighting from the main canvas
        self.parent.parent.mainView.mainCanvas.highlightTile(self.position[0], self.position[1], 'green', multi=multi)

    def moveUp(self):
        print("Move agent up")
        

    def moveLeft(self):
        print("Move agent left")

    def moveRight(self):
        print("Move agent right")

    def moveDown(self):
        print("Move agent down")

    def rotateCW(self):
        print("Rotate CW")

    def rotateCCW(self):
        print("Rotate CCW")
