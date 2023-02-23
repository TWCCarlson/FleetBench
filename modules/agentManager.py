import pprint
pp = pprint.PrettyPrinter(indent=4)

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
        self.agentList = {}
        self.agentPositionList = {}
        self.currentAgent = []

    def createNewAgent(self, **kwargs):
        """
            Create a new instance of the Agent class, using collected properties from the generation UI
            Also used when loading in saved data
            Inputs:
                - ID: Human-readable name
                - position: Node within the graph
                - orientation: Direction the agent is facing
                - className: The type of agent to be loaded
                    Each class may carry certain other properties
        """
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
        self.parent.mapData.updateAgentLocations(self.agentList)

    def packageAgentData(self):
        """
            Package reconstruction data for replicating the current state of the agent manager
            This means the data needed to create each agent needs to be available to each call to createNewAgent
                - Agent Name
                - Agent position
                - Agent orientation
                - Agent Class
        """
        dataPackage = {}
        for agent in self.agentList:
            pp.pprint(self.agentList[agent])
            agentData = {
                "ID": self.agentList[agent].ID,
                "position": self.agentList[agent].position,
                "orientation": self.agentList[agent].orientation,
                "className": self.agentList[agent].className 
            }
            dataPackage[self.agentList[agent].numID] = agentData
        pp.pprint(dataPackage)
        return dataPackage

class agentClass:
    """
        Agent class, contains descriptive information and methods for navigating the warehouse
    """
    def __init__(self, parent, **kwargs):
        self.parent = parent
        print("Create agent")
        self.numID = kwargs.pop("numID")# numeric ID, computer use only
        self.ID = kwargs.pop("ID")      # "human-readable" ID, name
        self.position = kwargs.pop("position")
        self.orientation = kwargs.pop("orientation")
        self.className = kwargs.pop("className")

        # Add the agent to the position list for reference in tileHover
        self.parent.agentPositionList[str(self.position)] = [self.ID, self.numID]
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
        self.parent.parent.mapData.updateAgentLocations(self.parent.agentList)
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
        self.parent.parent.mapData.updateAgentLocations(self.parent.agentList)
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
        self.parent.parent.mapData.updateAgentLocations(self.parent.agentList)
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
        self.parent.parent.mapData.updateAgentLocations(self.parent.agentList)
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
        self.parent.parent.mapData.updateAgentLocations(self.parent.agentList)
        self.parent.parent.mainView.mainCanvas.renderGraphState()

    def rotateCCW(self):
        # Fetch current orientation as a number from the direction dictionary
        curOrient = self.dirDict[self.orientation]
        # Decrement for CW, modulo for wrapping
        newOrient = (curOrient+1) % len(self.dirDict)
        # Find the new direction as a char
        self.orientation = list(self.dirDict.keys())[list(self.dirDict.values()).index(newOrient)]
        # Redraw the canvas to reflect the change
        self.parent.parent.mapData.updateAgentLocations(self.parent.agentList)
        self.parent.parent.mainView.mainCanvas.renderGraphState()
