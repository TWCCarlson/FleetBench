class agentManager:
    """
        Class which manages the information pertaining to agent existence and activity
    """
    def __init__(self, parent):
        self.parent = parent
        print("Agent Manager Class gen")
        # Generate agent class value options
        # Generate agent class definitions
        # Generate the agent class with inputs

        # Create a non-gui interface for generating and accessing all agents in the system
        self.agentManagerState = agentManagerState(self)

    def createNewAgent(self, **kwargs):
        # The length of a dict is always 1 higher than the numeric id
        self.dictLength = len(self.agentManagerState.agentList)
        try:
            ID = kwargs.pop("ID")
        except KeyError:
            ID = self.dictLength
        # Create a new agent and add it to the manager's list
        self.agentManagerState.latestAgent = agentClass(self, **kwargs, ID=ID, numID = self.dictLength)
        self.agentManagerState.agentList[self.dictLength] = self.agentManagerState.latestAgent
        self.parent.contextView.updateTreeView()
        self.parent.mapData.updateAgentLocations(self.agentManagerState.agentList)

class agentManagerState:
    def __init__(self, parent):
        self.agentList = {}
        self.agentPositionList = {}
        self.currentAgent = []

class agentClass:
    """
        Agent class, contains descriptive information and methods for navigating the warehosue
    """
    def __init__(self, parent, **kwargs):
        self.parent = parent
        print("Create agent")
        self.numID = kwargs.pop("numID")
        self.ID = kwargs.pop("ID")
        self.position = kwargs.pop("position")
        self.orientation = kwargs.pop("orientation")
        self.className = kwargs.pop("className")

        # Add the agent to the position list for reference in tileHover
        self.parent.agentManagerState.agentPositionList[str(self.position)] = [self.ID, self.numID]
        # Push some data into the map graph attributes for fast referencing elsewhere

        # Dict of directions and numerical values used for calculating rotation
        # Incrementing results in CCW, decerementing in CW
        self.dirDict = {
            "N" : 0,
            "W" : 1,
            "S" : 2,
            "E" : 3
        }
        
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
        self.parent.parent.mainView.mainCanvas.highlightTile(self.position[0], self.position[1], 'green', multi=multi, highlightType='agentHightlight')

    def moveUp(self):
        print("Move agent up")
        # Set the target node to be north
        targetNode = (self.position[0], self.position[1]-1)
        self.position = targetNode
        # Change orientation to represent turning to move north
        self.orientation = "N"
        # Update the canvas with the change
        self.parent.parent.mainView.mainCanvas.renderGraphState()
        # Update the movement buttons with the change
        self.parent.parent.contextView.validateMovementButtonStates()
        # Shift the highlighting with the change
        self.highlightAgent(multi=False)
        
    def moveLeft(self):
        print("Move agent left")
        # Set the target node to be west
        targetNode = (self.position[0]-1, self.position[1])
        self.position = targetNode
        # Change orientation to represent turning to move north
        self.orientation = "W"
        # Update the canvas with the change
        self.parent.parent.mainView.mainCanvas.renderGraphState()
        # Update the movement buttons with the change
        self.parent.parent.contextView.validateMovementButtonStates()
        # Shift the highlighting with the change
        self.highlightAgent(multi=False)

    def moveRight(self):
        print("Move agent right")
        # Set the target node to be east
        targetNode = (self.position[0]+1, self.position[1])
        self.position = targetNode
        # Change orientation to represent turning to move north
        self.orientation = "E"
        # Update the canvas with the change
        self.parent.parent.mainView.mainCanvas.renderGraphState()
        # Update the movement buttons with the change
        self.parent.parent.contextView.validateMovementButtonStates()
        # Shift the highlighting with the change
        self.highlightAgent(multi=False)

    def moveDown(self):
        print("Move agent down")
        # Set the target node to be south
        targetNode =  (self.position[0], self.position[1]+1)
        self.position = targetNode
        # Change orientation to represent turning to move north
        self.orientation = "S"
        # Update the canvas with the change
        self.parent.parent.mainView.mainCanvas.renderGraphState()
        # Update the movement buttons with the change
        self.parent.parent.contextView.validateMovementButtonStates()
        # Shift the highlighting with the change
        self.highlightAgent(multi=False)

    def rotateCW(self):
        # Fetch current orientation as a number from the direction dictionary
        curOrient = self.dirDict[self.orientation]
        # Decrement for CW, modulo for wrapping
        newOrient = (curOrient-1) % len(self.dirDict)
        # Find the new direction as a char
        self.orientation = list(self.dirDict.keys())[list(self.dirDict.values()).index(newOrient)]
        # Redraw the canvas to reflect the change
        self.parent.parent.mainView.mainCanvas.renderGraphState()

    def rotateCCW(self):
        # Fetch current orientation as a number from the direction dictionary
        curOrient = self.dirDict[self.orientation]
        # Decrement for CW, modulo for wrapping
        newOrient = (curOrient+1) % len(self.dirDict)
        # Find the new direction as a char
        self.orientation = list(self.dirDict.keys())[list(self.dirDict.values()).index(newOrient)]
        # Redraw the canvas to reflect the change
        self.parent.parent.mainView.mainCanvas.renderGraphState()
