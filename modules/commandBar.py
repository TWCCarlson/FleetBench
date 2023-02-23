import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import pickle
import pprint
pp = pprint.PrettyPrinter(indent=4)

class commandBar(tk.Menu):
    """
        Containing class for the command bar and options. Includes options like:
            - File: New Session, Save Session, Load Session, Quit Session

        commandBar will be the actual Tk widget
        commandBarState will be the decoupled state data of the element
    """
    def __init__(self, parent):
        self.parent = parent
        tk.Menu.__init__(self, parent)

        self.parent.config(menu=self)
        self.fileCommand = FileCommands(self)

        self.commandBarState = commandBarState(self)

class commandBarState:
    """
        Containing class for state data used by the command bar widget, decoupled for pickling and saving
    """
    def __init__(self, parent):
        pass

class FileCommands(tk.Menu):
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

        # Render the menu
        self.parent.add_cascade(label="File", menu=self)

    def newSession(self):
        # Prompt save
        self.promptSave()
        # Create a new session
        self.promptLoadMap()
        print("New Session")

    def promptLoadMap(self):
        messageBox = tk.messagebox.askquestion(title = "New Session",
            message="Load a map? This will close the current session.")
        if messageBox=="yes":
            print("Load new map")
            self.refMapData.ingestMapFromJSON()

    def openSession(self):
        # Open a saved session
        self.promptSave()
        print("Open Session")
        
        # Prompt for which saved file to load
        fid = tk.filedialog.askopenfilename()
        # print(fid)
        # Read the data using pickle
        with open(fid, 'rb') as inp:
            data = pickle.load(inp)
        # pp.pprint(data)

        # Insert the data into the relevant locations
        # self.parent.parent.mapData.mapGraph = data["mapDataClass"]
        # self.parent.parent.agentManager = data["agentManager"]
        # self.parent.parent.taskManager = data["taskManager"]
        # self.parent.parent.randomGenerator.randomGeneratorState = data["randomGenerator"]
        
        # Reconstruct the map from the data
        graphData = data["mapDataClass"]
        self.parent.parent.mapData.loadMapToNetworkX(graphData)

        # Reconstruct the agents from the data
        for agent in data["agentManager"]:
            ID = data["agentManager"][agent]["ID"]
            position = data["agentManager"][agent]["position"]
            orientation = data["agentManager"][agent]["orientation"]
            className = data["agentManager"][agent]["className"]
            self.parent.parent.agentManager.createNewAgent(
                ID=ID, 
                position=position, 
                orientation=orientation, 
                className=className
                )

        # Reconstruct the tasks from the data
        for task in data["taskManager"]:
            taskName = data["taskManager"][task]["name"]
            pickupPosition = data["taskManager"][task]["pickupPosition"]
            dropoffPosition = data["taskManager"][task]["dropoffPosition"]
            timeLimit = data["taskManager"][task]["timeLimit"]
            self.parent.parent.taskManager.createNewTask(
                taskName=taskName,
                pickupPosition=pickupPosition,
                dropoffPosition=dropoffPosition,
                timeLimit=timeLimit
                )
        
        # Reconstruct the current Random Generator data
        self.parent.parent.randomGenerator.randomGeneratorState.currentSeed = data["randomGenerator"]["currentSeed"]

        # Rerender the main canvas
        self.parent.parent.mainView.mainCanvas.renderGraphState()

    def promptSave(self):
        # Create a message box asking to save the current session
        print("Save?")
        messageBox = tk.messagebox.askquestion(title = "Save work?",
            message="Save current session?")
        if messageBox=="yes":
            self.saveSession()

    def saveSession(self):
        # Save a session
        print("Save Session")
        # self.parent = parent causes classes to become unpickleable, but the structure needs to exist
        # Therefore rely on subclasses containing the data
        itemsToSave = {
            "mapDataClass": self.parent.parent.mapData.packageMapData(),
            "agentManager": self.parent.parent.agentManager.packageAgentData(),
            "taskManager": self.parent.parent.taskManager.packageTaskData(),
            "randomGenerator" : self.parent.parent.randomGenerator.packageRandomGeneratorData(),
        }
        fid = tk.filedialog.asksaveasfilename(initialfile = 'Untitled', filetypes=[("All Files", "*.*")])
        print(fid)
        with open(fid, 'wb') as out:
            pickle.dump(itemsToSave, out, pickle.HIGHEST_PROTOCOL)

    def quitSession(self):
        # Close the current session
        print("Quit Session")