import pprint
import tkinter as tk
import logging
import json
pp = pprint.PrettyPrinter(indent=4)

class agentManager:
    """
        Class which manages the information pertaining to agent existence and activity
    """
    def __init__(self, parent):
        self.parent = parent
        # Generate agent class value options
        # Generate agent class definitions
        # Generate the agent class with inputs
        self.agentList = {}
        self.agentDict = {}
        self.agentPositionList = {}
        self.currentAgent = []
        logging.debug("Class 'agentManager' initialized.")

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
        logging.info(f"Received request for new agent.")
        logging.debug(f"Requested agent settings: {kwargs}")
        # The length of a dict is always 1 higher than the numeric id
        dictLength = len(self.agentList)
        ID = kwargs.pop("ID")
        
        print(f"{ID}: {type(ID)}")
        # If the request includes a special request for an autogenerated name
        if ID == "ag":
            ID = str(dictLength)
            logging.debug(f"Request does not contain an ID. Agent was automatically assigned ID '{ID}'")
        print(f"{ID}: {type(ID)}")
        # Create a new agent and add it to the manager's list
        self.latestAgent = agentClass(self, **kwargs, ID=ID, numID = dictLength)
        self.agentList[dictLength] = self.latestAgent
        self.agentDict[ID] = self.latestAgent
        logging.info(f"Agent added to the dict of agents.")
        logging.debug(f"Simulation agent dict now reads:")
        for key in self.agentList:
            logging.debug(f" {vars(self.agentList[key])}")
        self.parent.contextView.updateAgentTreeView()
        self.parent.mapData.updateAgentLocations(self.agentList)
        return dictLength

    def deleteAgent(self, agentID):
        """
            Irrevocably delete an agent from the list. This results in data loss and should only be used to remove agents that shouldn't have been made in the first place.
        """
        logging.info("Received request to delete agent.")
        # If the internal ID of the agent is supplied, it can be deleted from the dict directly
        targetAgent = eval(agentID)
        targetAgentName = self.agentList[targetAgent].ID
        # If the human-readable name of the agent is supplied, the attribute needs to be searched for in the dict
        logging.debug(f"Agent requested for deletion: '{targetAgentName}:{targetAgent}'")

        # First, verify the user actually wants to do this
        deletionPrompt = tk.messagebox.askokcancel(title="Are you sure?", message=f"You are about to delete agent '{self.agentList[targetAgent].ID}' from the simulation. \n\nAre you sure?")

        if deletionPrompt:
            logging.debug(f"User verified deletion of agent: '{targetAgentName}:{targetAgent}'")
            del self.agentList[targetAgent]
            print(len(self.agentList))
        else:
            logging.info("User cancelled deletion of agent.")
            return
        
        # Redraw the agent treeview and the main canvas
        self.parent.contextView.updateAgentTreeView()
        self.parent.mapData.updateAgentLocations(self.agentList)
        self.parent.mainView.mainCanvas.requestRender("agent", "delete", {"agentNumID": targetAgent})
        self.parent.mainView.mainCanvas.requestRender("highlight", "clear", {})
        self.parent.mainView.mainCanvas.handleRenderQueue()
        logging.debug(f"Agent '{targetAgentName}:{targetAgent}' successfully deleted.")

    def assignTaskToAgent(self, taskRef, agentRef):
        # Assign the task to the agent
        agentRef.currentTask = taskRef
        agentRef.taskStatus = "retrieving"

        # Update the agent treeView to reflect the changes
        self.parent.contextView.updateAgentTreeView()

    def unassignAgent(self, agentRef):
        if agentRef.currentTask is not None and agentRef.currentTask.assignee is not None:
            agentRef.currentTask.assignee = None
            agentRef.taskStatus = None

    def fixAssignments(self):
        # Iterate through the list of all agents, fixing currentTask to refer to objects instead of IDs
        for agent in self.agentList:
            if not self.agentList[agent].currentTask == None:
                self.agentList[agent].currentTask = self.parent.taskManager.taskList[self.agentList[agent].currentTask]

        # Update the agent treeView to reflect the changes
        self.parent.contextView.updateAgentTreeView()

    def pushDataToCanvas(self):
        self.parent.mainView.mainCanvas.ingestAgentData(self)

    def packageAgentData(self):
        """
            Package reconstruction data for replicating the current state of the agent manager
            This means the data needed to create each agent needs to be available to each call to createNewAgent
                - Agent Name
                - Agent position
                - Agent orientation
                - Agent Class
        """
        logging.info("Received request to package 'agentManager' data.")
        dataPackage = {}
        # Pull assigned object data
        for agent in self.agentList:
            # Pull task info for reconstruction
            if self.agentList[agent].currentTask:
                currentTask = self.agentList[agent].currentTask.numID
            else:
                currentTask = None

            agentData = {
                "ID": self.agentList[agent].ID,
                "position": self.agentList[agent].position,
                "orientation": self.agentList[agent].orientation,
                "className": self.agentList[agent].className,
                "currentTask": currentTask,
                "taskStatus": self.agentList[agent].taskStatus
            }
            dataPackage[self.agentList[agent].numID] = agentData
            logging.debug(f"Packaged agentData: {agentData}")
        logging.info("Packaged all 'agentManager' data.")
        return dataPackage

class agentClass:
    """
        Agent class, contains descriptive information and methods for navigating the warehouse
    """
    def __init__(self, parent, **kwargs):
        self.parent = parent
        logging.info(f"New 'agentClass' instantiated.")
        logging.debug(f"Agent settings: {kwargs}")
        self.numID = kwargs.get("numID")# numeric ID, computer use only
        self.ID = kwargs.get("ID")      # "human-readable" ID, name
        self.position = kwargs.get("position")
        self.orientation = kwargs.get("orientation")
        self.className = kwargs.get("className")
        self.currentTask = kwargs.get("currentTask")
        self.taskStatus = kwargs.get("taskStatus", "unassigned")


        print(f"{self.ID}: {type(self.ID)}")

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

    def highlightAgent(self, multi=False):
        # Have the agent request highlighting from the main canvas
        logging.debug(f"Agent '{self.ID}:{self.numID}' requests highlighting from 'mainCanvas'.")
        self.parent.parent.mainView.mainCanvas.requestRender(
                "highlight", "new", {"targetNodeID": self.position, "highlightType": "agentHighlight", "multi": multi, "highlightTags": ["agent"+str(self.numID)+"Highlight"]})

    def moveUp(self):
        logging.debug(f"User tried to move agent '{self.ID}:{self.numID}' upwards.")
        # Set the target node to be north
        targetNode = (self.position[0], self.position[1]-1)
        # Change orientation to represent turning to move north
        targetOrientation = "N"
        # Update the canvas with the change
        self.parent.parent.mainView.mainCanvas.requestRender(
                "agent", "move", {"agentNumID": self.numID, "sourceNodeID": self.position, "targetNodeID": targetNode})
        self.parent.parent.mainView.mainCanvas.requestRender(
                "agent", "rotate", {"agentNumID": self.numID, "orientation": targetOrientation, "position": targetNode})
        self.parent.parent.mainView.mainCanvas.requestRender(
                "highlight", "move", {"highlightTag": "agent"+str(self.numID)+"Highlight", "position": targetNode})
        self.parent.parent.mainView.mainCanvas.handleRenderQueue()
        # Update the movement buttons with the change
        self.position = targetNode
        self.orientation = targetOrientation
        self.parent.parent.mapData.updateAgentLocations(self.parent.agentList)
        self.parent.parent.contextView.validateMovementButtonStates()
        logging.debug(f"Agent '{self.ID}:{self.numID}' moved upwards.")
        
    def moveLeft(self):
        logging.debug(f"User tried to move agent '{self.ID}:{self.numID}' leftwards.")
        # Set the target node to be west
        targetNode = (self.position[0]-1, self.position[1])
        # Change orientation to represent turning to move north
        targetOrientation = "W"
        # Update the canvas with the change
        self.parent.parent.mainView.mainCanvas.requestRender(
                "agent", "move", {"agentNumID": self.numID, "sourceNodeID": self.position, "targetNodeID": targetNode})
        self.parent.parent.mainView.mainCanvas.requestRender(
                "agent", "rotate", {"agentNumID": self.numID, "orientation": targetOrientation, "position": targetNode})
        self.parent.parent.mainView.mainCanvas.requestRender(
                "highlight", "move", {"highlightTag": "agent"+str(self.numID)+"Highlight", "position": targetNode})
        self.parent.parent.mainView.mainCanvas.handleRenderQueue()
        # Update the movement buttons with the change
        self.position = targetNode
        self.orientation = targetOrientation
        self.parent.parent.mapData.updateAgentLocations(self.parent.agentList)
        self.parent.parent.contextView.validateMovementButtonStates()
        logging.debug(f"Agent '{self.ID}:{self.numID}' moved leftwards.")

    def moveRight(self):
        logging.debug(f"User tried to move agent '{self.ID}:{self.numID}' rightwards.")
        # Set the target node to be east
        targetNode = (self.position[0]+1, self.position[1])
        # Change orientation to represent turning to move north
        targetOrientation = "E"
        # Update the canvas with the change
        self.parent.parent.mainView.mainCanvas.requestRender(
                "agent", "move", {"agentNumID": self.numID, "sourceNodeID": self.position, "targetNodeID": targetNode})
        self.parent.parent.mainView.mainCanvas.requestRender(
                "agent", "rotate", {"agentNumID": self.numID, "orientation": targetOrientation, "position": targetNode})
        self.parent.parent.mainView.mainCanvas.requestRender(
                "highlight", "move", {"highlightTag": "agent"+str(self.numID)+"Highlight", "position": targetNode})
        self.parent.parent.mainView.mainCanvas.handleRenderQueue()
        # Update the movement buttons with the change
        self.position = targetNode
        self.orientation = targetOrientation
        self.parent.parent.mapData.updateAgentLocations(self.parent.agentList)
        self.parent.parent.contextView.validateMovementButtonStates()
        logging.debug(f"Agent '{self.ID}:{self.numID}' moved rightwards.")
        
    def moveDown(self):
        logging.debug(f"User tried to move agent '{self.ID}:{self.numID}' downwards.")
        # Set the target node to be south
        targetNode =  (self.position[0], self.position[1]+1)
        # Change orientation to represent turning to move north
        targetOrientation = "S"
        # Update the canvas with the change
        self.parent.parent.mainView.mainCanvas.requestRender(
                "agent", "move", {"agentNumID": self.numID, "sourceNodeID": self.position, "targetNodeID": targetNode})
        self.parent.parent.mainView.mainCanvas.requestRender(
                "agent", "rotate", {"agentNumID": self.numID, "orientation": targetOrientation, "position": targetNode})
        self.parent.parent.mainView.mainCanvas.requestRender(
                "highlight", "move", {"highlightTag": "agent"+str(self.numID)+"Highlight", "position": targetNode})
        self.parent.parent.mainView.mainCanvas.handleRenderQueue()
        # Update the movement buttons with the change
        self.position = targetNode
        self.orientation = targetOrientation
        self.parent.parent.mapData.updateAgentLocations(self.parent.agentList)
        self.parent.parent.contextView.validateMovementButtonStates()
        
        logging.debug(f"Agent '{self.ID}:{self.numID}' moved downwards.")
        
    def rotateCW(self):
        logging.debug(f"User tried to rotate agent '{self.ID}:{self.numID}' clockwise.")
        # Fetch current orientation as a number from the direction dictionary
        curOrient = self.dirDict[self.orientation]
        # Decrement for CW, modulo for wrapping
        newOrient = (curOrient-1) % len(self.dirDict)
        # Find the new direction as a char
        self.orientation = list(self.dirDict.keys())[list(self.dirDict.values()).index(newOrient)]
        # Redraw the canvas to reflect the change
        self.parent.parent.mainView.mainCanvas.requestRender(
                "agent", "rotate", {"agentNumID": self.numID, "orientation": self.orientation, "position": self.position})
        self.parent.parent.mainView.mainCanvas.handleRenderQueue()
        # Maintain the highlighting with the change
        logging.debug(f"Agent '{self.ID}:{self.numID}' rotated clockwise.")
        
    def rotateCCW(self):
        logging.debug(f"User tried to rotate agent '{self.ID}:{self.numID}' counter-clockwise.")
        # Fetch current orientation as a number from the direction dictionary
        curOrient = self.dirDict[self.orientation]
        # Decrement for CW, modulo for wrapping
        newOrient = (curOrient+1) % len(self.dirDict)
        # Find the new direction as a char
        self.orientation = list(self.dirDict.keys())[list(self.dirDict.values()).index(newOrient)]
        # Redraw the canvas to reflect the change
        self.parent.parent.mainView.mainCanvas.requestRender(
                "agent", "rotate", {"agentNumID": self.numID, "orientation": self.orientation, "position": self.position})
        self.parent.parent.mainView.mainCanvas.handleRenderQueue()
        # Maintain the highlighting with the change
        logging.debug(f"Agent '{self.ID}:{self.numID}' rotated counterclockwise.")
        
