import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import pickle
import pprint
import logging
pp = pprint.PrettyPrinter(indent=4)

class commandBar(tk.Menu):
    """
        Containing class for the command bar and options. Includes options like:
            - File: New Session, Save Session, Load Session, Quit Session

        commandBar will be the actual Tk widget
        commandBarState will be the decoupled state data of the element
    """
    def __init__(self, parent):
        logging.debug("Command Bar UI class initializing . . .")
        self.parent = parent
        tk.Menu.__init__(self, parent)

        self.parent.config(menu=self)
        self.fileCommand = fileCommands(self)
        logging.info("Command Bar sub-element 'File Menu' built.")
        self.commandBarState = commandBarState(self)
        logging.info("Command Bar UI built successfully.")

class commandBarState:
    """
        Containing class for state data used by the command bar widget, decoupled for pickling and saving
    """
    def __init__(self, parent):
        pass

class fileCommands(tk.Menu):
    """
        The cascade menu containing commands for new, load, save, and quitting of the simulation sessions
    """
    def __init__(self, parent):
        tk.Menu.__init__(self, parent, tearoff=0)

        # Establish structure
        self.parent = parent
        self.refMapData = parent.parent.mapData

        # Add menu functions
        # Pass the function as a callback instead of calling it
        self.add_command(label="New Session", command=self.newSession)
        self.add_command(label="Open Session", command=self.openSession)
        self.add_command(label="Save Session", command=self.saveSession)
        self.add_command(label="Quit Session", command=self.quitSession)
        logging.debug("File Menu actions built successfully.")

        # Render the menu
        self.parent.add_cascade(label="File", menu=self)
        logging.debug("File Menu rendered successfully.")

    def newSession(self):
        logging.info("User attempting to create new session.")
        # Prompt save
        self.promptSave()
        # Create a new session
        self.promptLoadMap()
        logging.info("User started a new session.")

    def promptLoadMap(self):
        logging.debug("Checking if user will load a new map . . .")
        messageBox = tk.messagebox.askquestion(title = "New Session",
            message="Load a map? This will close the current session.")
        if messageBox=="yes":
            logging.info("User will supply new session map data.")
            self.refMapData.ingestMapFromJSON()

    def openSession(self, **kwargs):  
        # Prompt for which saved file to load
        if "fid" in kwargs:
            logging.info("User launched in debug mode with default session loaded.")
            fid = kwargs.pop("fid")
        else:
            # Open a saved session
            self.promptSave()
            logging.info("User attempting to open a saved session.")
            fid = tk.filedialog.askopenfilename()
        
        logging.debug(f"User wants to open session datafile: {fid}")
        # Read the data using pickle
        with open(fid, 'rb') as inp:
            data = pickle.load(inp)
        # logging.debug(f"{data}")
        # if 
        
        # Reconstruct the map from the data
        graphData = data["mapDataClass"]
        logging.debug("Received graphData:")
        logging.debug(f"{graphData}")
        self.parent.parent.mapData.loadMapToNetworkX(graphData)
        logging.info("Loaded new map data to session map graph.")

        # Reconstruct the agents from the data
        logging.debug("Received new agentData:")
        for agent in data["agentManager"]:
            ID = data["agentManager"][agent]["ID"]
            position = data["agentManager"][agent]["position"]
            orientation = data["agentManager"][agent]["orientation"]
            className = data["agentManager"][agent]["className"]
            taskStatus = data["agentManager"][agent]["taskStatus"]
            try:
                currentTask = data["agentManager"][agent]["currentTask"]
            except KeyError:
                currentTask = None
            self.parent.parent.agentManager.createNewAgent(
                ID=ID, 
                position=position, 
                orientation=orientation, 
                className=className,
                currentTask=currentTask,
                taskStatus=taskStatus
                )
        logging.info("Loaded new agent data to session state.")

        # Reconstruct the tasks from the data
        logging.debug("Received new taskData:")
        for task in data["taskManager"]:
            taskName = data["taskManager"][task]["name"]
            pickupPosition = data["taskManager"][task]["pickupPosition"]
            dropoffPosition = data["taskManager"][task]["dropoffPosition"]
            timeLimit = data["taskManager"][task]["timeLimit"]
            taskStatus = data["taskManager"][task]["taskStatus"]
            try:
                assignee = data["taskManager"][task]["assignee"]
            except KeyError:
                assignee = None
            self.parent.parent.taskManager.createNewTask(
                taskName=taskName,
                pickupPosition=pickupPosition,
                dropoffPosition=dropoffPosition,
                timeLimit=timeLimit,
                assignee=assignee,
                taskStatus=taskStatus,
                loadOp=True
                )
        logging.info("Loaded new task data to session state.")
        
        # Building task/agent interdependencies
        self.parent.parent.agentManager.fixAssignments()
        self.parent.parent.taskManager.fixAssignments()

        # Reconstruct the current Random Generator data
        logging.debug("Received new random generator engine data:")
        self.parent.parent.randomGenerator.randomGeneratorState.currentSeed = data["randomGenerator"]["currentSeed"]
        logging.info("Loaded new random generator engine state.")

        # Render the new data on the canvas graph
        self.parent.parent.agentManager.pushDataToCanvas()
        self.parent.parent.mainView.mainCanvas.delete("all")
        self.parent.parent.mainView.mainCanvas.renderGraphState()

    def promptSave(self):
        # Create a message box asking to save the current session
        logging.info("Checking if user wants to save the current session . . .")
        messageBox = tk.messagebox.askquestion(title = "Save work?",
            message="Save current session?")
        if messageBox=="yes":
            logging.debug("User chose to save the current session.")
            self.saveSession()

    def saveSession(self):
        # Save a session
        logging.info("Attempting to save the current session.")
        # self.parent = parent causes classes to become unpickleable, but the structure needs to exist
        # Therefore rely on subclasses containing the data
        itemsToSave = {
            "mapDataClass": self.parent.parent.mapData.packageMapData(),
            "agentManager": self.parent.parent.agentManager.packageAgentData(),
            "taskManager": self.parent.parent.taskManager.packageTaskData(),
            "randomGenerator" : self.parent.parent.randomGenerator.packageRandomGeneratorData(),
        }
        logging.info("Save data collected.")
        logging.debug(f"{itemsToSave}")
        fid = tk.filedialog.asksaveasfilename(initialfile = 'Untitled', filetypes=[("All Files", "*.*")])
        logging.debug(f"User requested data be saved to: {fid}")
        with open(fid, 'wb') as out:
            pickle.dump(itemsToSave, out, pickle.HIGHEST_PROTOCOL)
        logging.info("Session data saved.")

    def quitSession(self):
        # Close the current session
        logging.info("User attempting to close out the session.")