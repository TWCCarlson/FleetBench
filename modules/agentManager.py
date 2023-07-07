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
        self.dictLength = len(self.agentList)
        try:
            ID = kwargs.pop("ID")
        except KeyError:
            ID = str(self.dictLength)
            logging.debug(f"Request does not contain an ID. Agent was automatically assigned ID '{ID}'")
        # Create a new agent and add it to the manager's list
        self.latestAgent = agentClass(self, **kwargs, ID=ID, numID = self.dictLength)
        self.agentList[self.dictLength] = self.latestAgent
        logging.info(f"Agent added to the dict of agents.")
        logging.debug(f"Simulation agent dict now reads:")
        for key in self.agentList:
            logging.debug(f" {vars(self.agentList[key])}")
        self.parent.contextView.updateAgentTreeView()
        self.parent.mapData.updateAgentLocations(self.agentList)

    def deleteAgent(self, agentName=None, agentID=None):
        """
            Irrevocably delete an agent from the list. This results in data loss and should only be used to remove agents that shouldn't have been made in the first place.
        """
        logging.info("Received request to delete agent.")
        # If the internal ID of the agent is supplied, it can be deleted from the dict directly
        if agentID: targetAgent = agentID
        # If the human-readable name of the agent is supplied, the attribute needs to be searched for in the dict
        if agentName: targetAgent = [agentID for agentID in list(self.agentList) if self.agentList[agentID].ID == agentName][0]
        targetAgentName = self.agentList[targetAgent].ID
        logging.debug(f"Agent requested for deletion: '{targetAgentName}:{targetAgent}'")

        # First, verify the user actually wants to do this
        deletionPrompt = tk.messagebox.askokcancel(title="Are you sure?", message=f"You are about to delete agent '{self.agentList[targetAgent].ID}' from the simulation. \n\nAre you sure?")

        if deletionPrompt:
            logging.debug(f"User verified deletion of agent: '{targetAgentName}:{targetAgent}'")
            del self.agentList[targetAgent]
        else:
            logging.info("User cancelled deletion of agent.")
            return
        
        # Redraw the agent treeview and the main canvas
        self.parent.contextView.updateAgentTreeView()
        self.parent.mapData.updateAgentLocations(self.agentList)
        self.parent.mainView.mainCanvas.renderGraphState()
        logging.debug(f"Agent '{targetAgentName}:{targetAgent}' successfully deleted.")

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
        for agent in self.agentList:
            agentData = {
                "ID": self.agentList[agent].ID,
                "position": self.agentList[agent].position,
                "orientation": self.agentList[agent].orientation,
                "className": self.agentList[agent].className 
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
        logging.debug(f"Agent '{self.ID}:{self.numID}' requests highlighting from 'mainCanvas'.")
        self.parent.parent.mainView.mainCanvas.highlightTile(self.position[0], self.position[1], 'green', multi=multi, highlightType='agentHighlight')

    def moveUp(self):
        logging.debug(f"Agent '{self.ID}:{self.numID}' attempting to move upwards.")
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
        logging.debug(f"Agent '{self.ID}:{self.numID}' moved upwards.")
        self.highlightAgent(multi=False)
        
        
    def moveLeft(self):
        logging.debug(f"Agent '{self.ID}:{self.numID}' attempting to move leftwards.")
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
        logging.debug(f"Agent '{self.ID}:{self.numID}' moved leftwards.")
        self.highlightAgent(multi=False)
        

    def moveRight(self):
        logging.debug(f"Agent '{self.ID}:{self.numID}' attempting to move rightwards.")
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
        logging.debug(f"Agent '{self.ID}:{self.numID}' moved rightwards.")
        self.highlightAgent(multi=False)
        

    def moveDown(self):
        logging.debug(f"Agent '{self.ID}:{self.numID}' attempting to move downwards.")
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
        logging.debug(f"Agent '{self.ID}:{self.numID}' moved downwards.")
        self.highlightAgent(multi=False)
        

    def rotateCW(self):
        logging.debug(f"Agent '{self.ID}:{self.numID}' attempting to rotate clockwise.")
        # Fetch current orientation as a number from the direction dictionary
        curOrient = self.dirDict[self.orientation]
        # Decrement for CW, modulo for wrapping
        newOrient = (curOrient-1) % len(self.dirDict)
        # Find the new direction as a char
        self.orientation = list(self.dirDict.keys())[list(self.dirDict.values()).index(newOrient)]
        # Redraw the canvas to reflect the change
        self.parent.parent.mapData.updateAgentLocations(self.parent.agentList)
        self.parent.parent.mainView.mainCanvas.renderGraphState()
        # Maintain the highlighting with the change
        logging.debug(f"Agent '{self.ID}:{self.numID}' rotated clockwise.")
        self.highlightAgent(multi=False)
        

    def rotateCCW(self):
        logging.debug(f"Agent '{self.ID}:{self.numID}' attempting to rotate counterclockwise.")
        # Fetch current orientation as a number from the direction dictionary
        curOrient = self.dirDict[self.orientation]
        # Decrement for CW, modulo for wrapping
        newOrient = (curOrient+1) % len(self.dirDict)
        # Find the new direction as a char
        self.orientation = list(self.dirDict.keys())[list(self.dirDict.values()).index(newOrient)]
        # Redraw the canvas to reflect the change
        self.parent.parent.mapData.updateAgentLocations(self.parent.agentList)
        self.parent.parent.mainView.mainCanvas.renderGraphState()
        # Maintain the highlighting with the change
        logging.debug(f"Agent '{self.ID}:{self.numID}' rotated counterclockwise.")
        self.highlightAgent(multi=False)
        
