import tkinter as tk
from tkinter import ttk
import networkx as nx
import modules.exceptions as RWSE
from functools import partial
import logging
import pprint
pp = pprint.PrettyPrinter(indent=4)

class toolBar(tk.Frame):
    """
        The containing frame for the left-side panel
        Will include agent generation, task generation, rng seed control
        Probably needs to be refactored into more manageable chunks
    """
    def __init__(self, parent):
        logging.debug("Tool Bar UI Class initializing . . .")
        self.parent = parent

        # Fetch styling
        appearanceValues = self.parent.appearance
        frameHeight = appearanceValues.toolBarHeight
        frameWidth = appearanceValues.toolBarWidth
        frameBorderWidth = appearanceValues.frameBorderWidth
        frameRelief = appearanceValues.frameRelief
        logging.debug("Fetched style options.")

        # Declare frame
        tk.Frame.__init__(self, parent, height=frameHeight, 
            width=frameWidth, 
            borderwidth=frameBorderWidth, 
            relief=frameRelief)
        logging.debug("Containing frame settings constructed.")
        
        # Render frame
        self.grid_propagate(False)
        self.grid(row=0, column=0, rowspan=2, sticky=tk.N)
        logging.debug("Containing frame rendered into main app.")

    def buildReferences(self):
        self.mainView = self.parent.mainView
        self.mapData = self.parent.mapData
        self.agentManager = self.parent.agentManager
        self.taskManager = self.parent.taskManager
        logging.debug("Quick structure references built.")

        # Establish buttons and inputs
        self.initUI()

    def initUI(self):
        logging.debug("Creating tool bar ui elements . . .")
        self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)

        # Create a labeled container for the agent generator
        self.agentFrame = tk.LabelFrame(self, text="Agent Generator")
        self.agentFrame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W, padx=4, columnspan=2)
        self.agentCreationPrompt()
        logging.info("Agent generator UI created successfully.")

        # Create a labeled container for manual agent manipulation
        self.agentManageFrame = tk.LabelFrame(self, text="Agent Manager")
        self.agentManageFrame.grid(row=1, column=0, sticky=tk.N+tk.E+tk.W, padx=4, columnspan=2)
        self.agentManagePrompt()
        logging.info("Agent Manager UI created successfully.")

        # Create a labeled container for the task generator
        self.taskFrame = tk.LabelFrame(self, text="Task Generator")
        self.taskFrame.grid(row=2, column=0, sticky=tk.N+tk.E+tk.W, padx=4, columnspan=2)
        self.taskCreationPrompt()
        logging.info("Task generator UI created successfully.")

        # Create a labeled container for the task manager
        self.taskManageFrame = tk.LabelFrame(self, text="Task Manager")
        self.taskManageFrame.grid(row=3, column=0, sticky="new", padx=4, columnspan=2)
        self.taskManagePrompt()
        logging.info("Task manager UI created successfully.")

        # Create a labeled container for the rng system
        self.randomSeedFrame = tk.LabelFrame(self, text="RNG System Seed")
        self.randomSeedFrame.grid(row=4, column=0, sticky=tk.N+tk.E+tk.W, padx=4, columnspan=2)
        self.createRandomSeedPane()
        logging.info("Random generator engine configuration UI created successfully.")

    def agentCreationPrompt(self):
        self.clearAgentCreationUI()
        # Create a button to start UI creation
        self.createAgentButton = tk.Button(self.agentFrame, 
            command=self.agentCreationUI, text="Create Agent. . .", width=15,
            state=tk.DISABLED)
        self.agentFrame.columnconfigure(0, weight=1)
        self.createAgentButton.grid(row=0, column=0, pady=4, padx=4, columnspan=2)
        logging.debug("Agent creation UI reset to initial state.")
        # If a map is loaded when this gui is created, enable the creation button
        if self.parent.mapData.mapLoadedBool == True:
            self.createAgentButton.config(state=tk.NORMAL)
            logging.debug("Map is loaded; agent creation is enabled.")

    def enableAgentCreation(self):
        self.createAgentButton.config(state=tk.NORMAL)
        logging.info("Agent creation UI is enabled.")

    def agentCreationUI(self):
        logging.debug("Opening agent creation menu . . .")
        # Clear what's already in the frame to make space
        self.clearAgentCreationUI()

        # Default button state values
        self.agentNameValid = False
        self.taskNameValid = False
        self.validAgentCreationNode = False

        # Dropdown selector for agent class
        self.classLabel = tk.Label(self.agentFrame, text="Agent class:")
        self.agentClass = tk.StringVar()
        self.agentClass.set("One") # default value
        self.classDropDown = tk.OptionMenu(self.agentFrame, self.agentClass, "One", "Two", "Three")
        self.classLabel.grid(row=0, column=0, sticky=tk.E)
        self.agentFrame.columnconfigure(1, weight=1)
        self.classDropDown.grid(row=0, column=1, sticky=tk.W)
        logging.debug("Built agent type selector UI element.")

        # Create labeled container for agent information
        self.agentDataFrame = tk.LabelFrame(self.agentFrame, text="Agent Specs")
        self.agentDataFrame.grid(row=1, column=0, sticky=tk.N+tk.E+tk.W, padx=4, columnspan=2)
        logging.debug("Built agent creation option containing frame UI element.")

        # Coordinate Entry boxes and labels
        self.agentXPosValue = tk.StringVar()
        self.agentYPosValue = tk.StringVar()
        self.entryXLabel = tk.Label(self.agentDataFrame, text="X Position: ", width=8)
        self.validateAgentPosCoord = self.register(self.validateNumericSpinbox)
        # self.validateAgentXPos = self.register(self.highlightTargetXPos) # Validation
        # self.commandAgentXPos = partial(self.highlightTargetXPos, 'X', 'agentHighlight', self.entryXValue, self.entryYValue)
        self.agentXPosValue.trace_add("write", lambda *args, b=self.agentXPosValue, c=self.agentYPosValue : self.highlightTargetTile('agentHighlight', b, c, *args))
        self.agentXPosEntry = ttk.Spinbox(self.agentDataFrame, 
            width=6,
            from_=0,
            to=self.mapData.dimensionX,
            increment=1,
            textvariable=self.agentXPosValue,
            # command=self.commandAgentXPos,   # Triggered on scrolling/spinbox button press
            validate='key',
            validatecommand=(self.validateAgentPosCoord, '%P')
            # validatecommand=(self.validateAgentXPos, '%P', 'agentHighlight') # Triggered on typing
            )
        self.entryYLabel = tk.Label(self.agentDataFrame, text="Y Position: ", width=8)
        # self.validateAgentYPos = self.register(self.highlightTargetYPos) # Function wrapper for callback on entry update
        # self.commandAgentYPos = partial(self.highlightTargetYPos, 'Y', 'agentHighlight', self.entryXValue, self.entryYValue)
        self.agentYPosValue.trace_add("write", lambda *args, b=self.agentXPosValue, c=self.agentYPosValue : self.highlightTargetTile('agentHighlight', b, c, *args))
        self.agentYPosEntry = ttk.Spinbox(self.agentDataFrame, 
            width=6,
            from_=0,
            increment=1,
            to=self.mapData.dimensionY,
            textvariable=self.agentYPosValue,
            # command=self.commandAgentYPos,   # Triggered on scrolling/spinbox button press
            validate='key',
            validatecommand=(self.validateAgentPosCoord, '%P')
            # validatecommand=(self.validateAgentYPos, '%P', 'agentHighlight')  # Triggered on typing
        )
        logging.debug("Agent placement spinboxes built.")

        # Custom name entrybox
        self.agentNameLabel = tk.Label(self.agentDataFrame, text="Agent Name:", width=16)
        self.agentNameValue = tk.StringVar()
        self.validateAgentName = self.register(self.agentNameValidation)
        self.agentNameEntry = tk.Entry(self.agentDataFrame, 
            textvariable=self.agentNameValue, 
            width=16,
            validate='key',
            validatecommand=(self.validateAgentName, '%P')
            )
        logging.debug("Agent name entry box built.")

        # Separator
        self.sep2 = ttk.Separator(self.agentDataFrame, orient='horizontal')

        # Starting orientation radio buttons
        self.agentOrientationFrame = tk.Frame(self.agentDataFrame)
        self.agentOrientationLabel = tk.Label(self.agentOrientationFrame, text="Orientation:", width=8)
        self.agentOrientation = tk.StringVar()
        self.agentOrientationN = tk.Radiobutton(self.agentOrientationFrame, text="N", variable=self.agentOrientation, value="N")
        self.agentOrientationN.select() # default selection
        self.agentOrientationW = tk.Radiobutton(self.agentOrientationFrame, text="W", variable=self.agentOrientation, value="W")
        self.agentOrientationS = tk.Radiobutton(self.agentOrientationFrame, text="S", variable=self.agentOrientation, value="S")
        self.agentOrientationE = tk.Radiobutton(self.agentOrientationFrame, text="E", variable=self.agentOrientation, value="E")
        logging.debug("Agent starting orientation option buttons built.")

        # Autogenerate name tickbox
        self.autogenerateNameValue = tk.IntVar()
        self.autogenerateNameTickbox = tk.Checkbutton(self.agentDataFrame, text="Autogenerate Name",
            variable=self.autogenerateNameValue, command=self.updateAgentCreationButton)
        logging.debug("Agent automatic name generation tickbox built.")

        # Render
        self.entryXLabel.grid(row=1, column=0, sticky=tk.E)
        self.entryYLabel.grid(row=2, column=0, sticky=tk.E)
        self.agentXPosEntry.grid(row=1, column=1)
        self.agentYPosEntry.grid(row=2, column=1)
        self.agentNameLabel.grid(row=1, column=2, sticky=tk.E)
        self.agentNameEntry.grid(row=1, column=3, sticky=tk.E)
        self.agentOrientationFrame.grid(row=2, column=2, columnspan=2, sticky=tk.E)
        self.agentOrientationLabel.pack(side=tk.LEFT)
        self.agentOrientationN.pack(side=tk.LEFT)
        self.agentOrientationW.pack(side=tk.LEFT)
        self.agentOrientationS.pack(side=tk.LEFT)
        self.agentOrientationE.pack(side=tk.LEFT)
        self.sep2.grid(row=3, columnspan=4)
        self.autogenerateNameTickbox.grid(row=4, columnspan=4)
        logging.info("Agent generation specification UI built and rendered.")

        # Separator
        self.sep1 = ttk.Separator(self.agentDataFrame, orient='vertical')
        self.sep1.grid(row=0, column=2, rowspan=3, sticky=tk.N+tk.S+tk.W, pady=4, padx=4)

        # Save and edit buttons
        self.editAgentClassButton = tk.Button(self.agentFrame, 
            command=self.cancelAgentCreation, 
            text="Cancel",
            width=15,
            )
        logging.debug("Agent creation cancel button built.")
        self.confirmCreateAgentButton = tk.Button(self.agentFrame, 
            command = self.createAgent, 
            text="Create Agent",
            width=15,
            state=tk.DISABLED
            )
        logging.debug("Agent creation action button built.")
        self.editAgentClassButton.grid(row=2, column=0, sticky=tk.E, pady=4)
        self.confirmCreateAgentButton.grid(row=2, column=1, sticky=tk.W, pady=4)
        logging.info("Agent creation specification UI built and rendered successfully.")

    def clearAgentCreationUI(self):
        logging.debug("Received request to clear the agent creation UI.")
        # Destroys all the agent creation ui elements
        for widget in self.agentFrame.winfo_children():
            widget.destroy()
        for row in range(self.agentFrame.grid_size()[0]):
            self.agentFrame.rowconfigure(row, weight=0)
        for col in range(self.agentFrame.grid_size()[1]):
            self.agentFrame.columnconfigure(col, weight=0)

        # Resets the enabled status of the create agent button
        # Should these be here?
        self.validAgentCreationNode = False
        self.agentNameValid = False
        logging.info("Agent creation elements destroyed.")

    def highlightTargetTile(self, highlightType, stringVarX, stringVarY, *args):
        # If an input is Nonetype, fetch it from its entry variable
        # print(stringVarX)
        xPos = stringVarX.get()
        yPos = stringVarY.get()
        logging.debug(f"Received request to highlight tile: '({xPos},{yPos}):{highlightType}'")

        # Using guard clauses, check that
        # The x input is numeric
        if not xPos.isnumeric():
            # Else it is invalid
            self.validAgentCreationNode = False
            self.mainView.mainCanvas.requestRender("highlight", "delete", {"highlightTag": highlightType})
            self.mainView.mainCanvas.handleRenderQueue()
            logging.debug(f"Variable xPos='{xPos}' is not numeric. Highlight impossible.")
            return
        # The y input is numeric
        if not yPos.isnumeric():
            # Else it is invalid
            self.validAgentCreationNode = False
            self.mainView.mainCanvas.requestRender("highlight", "delete", {"highlightTag": highlightType})
            self.mainView.mainCanvas.handleRenderQueue()
            logging.debug(f"Variable yPos='{yPos}' is not numeric. Highlight impossible.")
            return
        # If all guard clauses are passed, highlight the tile
        if highlightType == 'agentHighlight':
            self.mainView.mainCanvas.requestRender(
                "highlight", "new", {"targetNodeID": (xPos, yPos), "highlightType": highlightType, "multi": False, "highlightTags": ["agentPlacement"]})
            # Validate for placing an agent
            self.validateAgentPlacement(xPos, yPos, highlightType)
        elif highlightType == 'pickupHighlight':
            self.mainView.mainCanvas.requestRender(
                "highlight", "new", {"targetNodeID": (xPos, yPos), "highlightType": highlightType, "multi": False, "highlightTags": ["agentPlacement"]})
            # Validate for placing a task
            self.validateTaskPlacement(highlightType)
        elif highlightType == 'depositHighlight':
            self.mainView.mainCanvas.requestRender(
                "highlight", "new", {"targetNodeID": (xPos, yPos), "highlightType": highlightType, "multi": False, "highlightTags": ["agentPlacement"]})
            # Validate
            self.validateTaskPlacement(highlightType)
        self.mainView.mainCanvas.handleRenderQueue()

    def validateAgentPlacement(self, xPos, yPos, highlightType):
        # Using guard clauses, check that
        # The x input is numeric
        if not xPos.isnumeric():
            # Else it is invalid
            self.validAgentCreationNode = False
            logging.debug(f"Target 'xPos={xPos}' is not numeric and cannot be highlighted. Removing highlight.")
            self.updateAgentCreationButton()
            self.mainView.mainCanvas.clearHighlight(highlightType)
            return
        # The y input is numeric
        if not yPos.isnumeric():
            # Else it is invalid
            self.validAgentCreationNode = False
            logging.debug(f"Target 'yPos={yPos}' is not numeric and cannot be highlighted. Removing highlight.")
            self.updateAgentCreationButton()
            self.mainView.mainCanvas.clearHighlight(highlightType)
            return
        # Check that it belongs to the graph
        if not self.tileInGraphValidation(xPos, yPos):
            self.validAgentCreationNode = False
            logging.debug(f"Target combination of coordinates '({xPos},{yPos})' does not exist in session map data.")
            self.updateAgentCreationButton()
            return
        # And that the tile does not already contain an agent
        # print(self.mapData.mapGraph.nodes.data()[f"({eval(xPos)}, {eval(yPos)})"])
        if 'agent' in self.mapData.mapGraph.nodes.data()[f"({eval(xPos)}, {eval(yPos)})"]:
            # Else it is invalid    
            # print("AGENT EXISTS IN THIS TILE ALREADY")
            self.validAgentCreationNode = False
            logging.debug(f"Target node '({xPos},{yPos})' already contains an agent.")
            self.updateAgentCreationButton()
            return
        # Enable the button based on graph belongingness
        self.validAgentCreationNode = True
        logging.debug(f"Target node '({xPos},{yPos})' is a valid location to place a new agent.")
        logging.info("Validated position data for new user-created agent.")

        # Check that all other enabling conditions are met
        self.updateAgentCreationButton()

    def tileInGraphValidation(self, xPos, yPos):
        logging.debug(f"Verifying that requested node '({xPos}, {yPos})' exists in the graph . . .")
        # Check that the node formed by these positions is actually part of the warehouse graph
        graphCandidate = '(' + str(xPos) + ", " + str(yPos) + ')'
        if graphCandidate in self.mapData.mapGraph.nodes:
            # If so, enable the button
            # self.confirmCreateAgentButton.config(state=tk.ACTIVE)
            logging.debug("Node exists.")
            return True
        else:
            # self.confirmCreateAgentButton.config(state=tk.DISABLED)
            logging.debug("Node does not exist")
            return False

    def agentNameValidation(self, agentName):
        logging.debug(f"Validating user-inputted agent name: '{agentName}'")
        # If the agentName box contains a name of less length than 3, it is not valid
        if len(agentName) < 3:
            # Disable the ability to create the agent
            self.agentNameValid = False
            logging.debug(f"User-input agent name '{agentName}' is too short.")

            # Check that all other enabling conditions are met
            self.updateAgentCreationButton()

            # self.confirmCreateAgentButton.config(state=tk.DISABLED)
            # Allow the box to be empty
            return True
        elif any(self.parent.agentManager.agentList[i].ID == agentName for i in self.parent.agentManager.agentList):
            # i for i in self.parent.agentManager.agentList if self.parent.agentManager.agentList[i].ID == agentName
            # Creates an iterator containing all instances where there is a match
            # Next then moves the generator through the container, either yielding a value (True) or reaching the end of the container
            # At the end of the container, raise StopIteration or return the default value False

            # If the agentName is the same as an agent that already exists, disallow creating it
            self.agentNameValid = False
            logging.debug(f"User-input agent name '{agentName}' already exists in the agent list.")

            # Check that all other enabling conditions are met
            self.updateAgentCreationButton()

            # Allow the box to be empty
            return True
        else:
            # Enable the ability to create the agent
            self.agentNameValid = True
            logging.debug(f"User-input agent name '{agentName}' is valid.")

            # Check that all other enabling conditions are met
            self.updateAgentCreationButton()

            # self.confirmCreateAgentButton.config(state=tk.ACTIVE)
            return True

    def updateAgentCreationButton(self):
        # Checks if all preconditions for placing an agent on the graph are met
        # Input box validation is done with callbacks
        logging.debug(f"Node: {self.validAgentCreationNode} Name: {self.agentNameValid}, Auto: {self.autogenerateNameValue.get()}")
        if self.validAgentCreationNode and (self.agentNameValid or self.autogenerateNameValue.get()):
            self.confirmCreateAgentButton.config(state=tk.NORMAL)
            logging.info("User-selected agent settings are all valid. Enabling creation.")
        else:
            self.confirmCreateAgentButton.config(state=tk.DISABLED)
            logging.info("User-selected agent settings are not all valid. Disabling creation.")

    def cancelAgentCreation(self):
        logging.debug("Cancelling agent creation . . .")
        self.mainView.mainCanvas.requestRender("highlight", "delete", {"highlightTag": "agentHighlight"})
        self.mainView.mainCanvas.handleRenderQueue()
        self.agentCreationPrompt()

    def createAgent(self):
        logging.debug("Creating agent using user-input settings.")
        # Create the agent, place it
        # https://networkx.org/documentation/stable/reference/generated/networkx.classes.function.set_node_attributes.html
        # Note that if the dictionary contains nodes that are not in G, the values are silently ignored:
        xPos = eval(self.agentXPosValue.get())
        yPos = eval(self.agentYPosValue.get())
        targetNode = (xPos, yPos)
        agentOrientation = self.agentOrientation.get()
        if len(self.agentNameValue.get()) == 0 and self.autogenerateNameValue:
            ID=len(self.parent.agentManager.agentList) # Let agentManager generate a name, works because minimum manual name length is 3 characters
        else:
            ID=self.agentNameValue.get()
        
        logging.debug(f"New agent settings: '(Name: {ID}, Class: {self.agentClass.get()}, Position: ({xPos}, {yPos}), Orientation: {agentOrientation})'")

        agentNumID = self.agentManager.createNewAgent(
            ID=ID,
            position=targetNode, 
            orientation=agentOrientation, 
            className=self.agentClass.get(),
            )
        # Remove previous highlights
        self.mainView.mainCanvas.requestRender("highlight", "delete", {"highlightTag": "agentHighlight"})
        self.mainView.mainCanvas.requestRender("agent", "new", {"position": targetNode, "agentNumID": agentNumID, "orientation": agentOrientation})
        self.mainView.mainCanvas.handleRenderQueue()
        # Close agent generator
        self.agentCreationPrompt()

    def agentManagePrompt(self):
        logging.debug("Creating agent management prompt UI elements.")
        self.clearAgentManagementUI()
        # Create a button that starts prompting the user
        self.manageAgentButton = tk.Button(self.agentManageFrame,
            command=self.agentManagementUI, text="Manage Agent . . .", width=15,
            state=tk.DISABLED)
        
        # Render the button, centered in the frame
        self.agentManageFrame.columnconfigure(0, weight=1)
        self.manageAgentButton.grid(row=0, column=0, pady=4, padx=4, columnspan=2)
        logging.debug("Agent management UI reset to initial state.")

    def enableAgentManagement(self):
        # Enable the management interface
        self.manageAgentButton.config(state=tk.NORMAL)

    def clearAgentManagementUI(self):
        # Destroys all the task creation ui elements
        for widget in self.agentManageFrame.winfo_children():
            widget.destroy()
        # Reset column/row weights
        for row in range(self.agentManageFrame.grid_size()[0]):
            self.agentManageFrame.rowconfigure(row, weight=0)
        for col in range(self.agentManageFrame.grid_size()[1]):
            self.agentManageFrame.columnconfigure(col, weight=0)
        logging.debug("Removed all UI elements from the task creation frame.")

    def agentManagementUI(self):
        logging.debug("Creating agent management UI elements.")
        self.clearAgentManagementUI()

        # Prevent simultaneous management of tasks and agents
        self.taskManagePrompt()

        # Display the currently managed agent
        agentRef = self.parent.agentManager.currentAgent
        self.managedAgentLabel = tk.Label(self.agentManageFrame, text=f"Managing Agent {agentRef.numID}:{agentRef.ID} at {agentRef.position}")
        self.managedAgentLabel.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        # Create a label for the task assignment drop down
        self.agentTaskAssignmentLabel = tk.Label(self.agentManageFrame, text="Assign task: ")
        self.agentTaskAssignmentLabel.grid(row=1, column=0)

        # Create an action button to assign the task
        self.agentTaskAssignmentButton = tk.Button(self.agentManageFrame,
            command=self.assignSelectedTask, text="Assign Task", width=10,
            state=tk.DISABLED
            )
        self.agentTaskAssignmentButton.grid(row=1, column=2, padx=4, pady=4)

        # Create the drop down menu
        taskList = self.taskManager.taskList
        self.agentManageFrame.columnconfigure(1, weight=1)
        if taskList:
            # There are tasks to choose from
            taskOptions = ()
            for task in taskList:
                taskOptions = (*taskOptions, taskList[task].name)
            self.agentTaskStringVar = tk.StringVar()
            self.agentTaskAssignmentOptionMenu = ttk.Combobox(self.agentManageFrame, width=20, textvariable=self.agentTaskStringVar)
            self.agentTaskAssignmentOptionMenu['values'] = taskOptions

            # Render the menu
            self.agentTaskAssignmentOptionMenu.grid(row=1, column=1)
            self.agentTaskAssignmentOptionMenu.bind("<<ComboboxSelected>>", self.prepSelectedTaskForAssignment)
        else:
            # There are no tasks to choose from
            self.agentNoTasksAvailableLabel = tk.Label(self.agentManageFrame, text="No tasks available to assign!")
            self.agentNoTasksAvailableLabel.grid(row=1, column=1)

    def prepSelectedTaskForAssignment(self, event):
        # Find the task object ID
        selectedTaskOption = self.agentTaskStringVar.get()
        selectedTaskID = next((taskID for taskID, task in self.taskManager.taskList.items() if task.name == selectedTaskOption))
        self.taskManager.taskList[selectedTaskID].highlightTask(multi=False)
        
        # Save the task into an attribute for external access
        self.parent.taskManager.currentTask = self.parent.taskManager.taskList[selectedTaskID]

        # Enable the assignment action button
        self.agentTaskAssignmentButton.configure(state=tk.ACTIVE)

    def assignSelectedTask(self):
        # Execute the task assignment
        self.parent.taskManager.assignAgentToTask()
        self.parent.agentManager.assignTaskToAgent()

        # Reset the UI
        self.agentManagePrompt()

        # Clear highlights on the mainView
        self.parent.mainView.mainCanvas.clearHighlight()

        # Re-render the app state
        self.parent.mainView.mainCanvas.renderGraphState()

    def taskCreationPrompt(self):
        logging.debug("Creating task creation prompt UI elements.")   
        self.clearTaskCreationUI()
        # Default button state values
        self.taskNameValid = False
        self.validTaskLocations = False
        self.validTaskTimeLimit = False
        self.taskGeneratorRespectsNodeTypes = True
        # Create a button to start UI creation
        self.createTaskButton = tk.Button(self.taskFrame, 
            command=self.taskCreationUI, text="Create Task. . .", width=15,
            state=tk.DISABLED)
        self.taskFrame.columnconfigure(0, weight=1)
        self.createTaskButton.grid(row=0, column=0, pady=4, padx=4, columnspan=2)
        logging.debug("Task creation processstart button built.")
        # If a map is loaded when this gui is created, enable the creation button
        if self.parent.mapData.mapLoadedBool == True:
            self.createTaskButton.config(state=tk.NORMAL)
        logging.info("Task creation prompt UI elements built.")

    def enableTaskCreation(self):
        self.createTaskButton.config(state=tk.NORMAL)
        logging.debug("Task creation enabled.")

    def clearTaskCreationUI(self):
        # Destroys all the task creation ui elements
        for widget in self.taskFrame.winfo_children():
            widget.destroy()
        # Reset column/row weights
        for row in range(self.taskFrame.grid_size()[0]):
            self.taskFrame.rowconfigure(row, weight=0)
        for col in range(self.taskFrame.grid_size()[1]):
            self.taskFrame.columnconfigure(col, weight=0)
        logging.debug("Removed all UI elements from the task creation frame.")

    def taskCreationUI(self):
        logging.debug("Building custom task creation UI elements . . .")
        # Clear what's already in the task frame to make space
        self.clearTaskCreationUI()

        # Tasks have
        # Pickup location
        # Dropoff location
        # Name
        # Internal ID
        # Status (unassigned, assigned, in progress, complete, abandoned, cancelled, failed)

        # Containing frame
        self.taskSpecsFrame = tk.LabelFrame(self.taskFrame, text="Task Specs")
        self.taskSpecsFrame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W, padx=4, pady=4)
        logging.debug("Task creation UI label frame built.")

        # Task name entry section
        self.taskNameLabel = tk.Label(self.taskSpecsFrame, text="Task Name: ")
        self.taskNameValue = tk.StringVar()
        self.validateTaskName = self.register(self.taskNameValidation)
        self.taskNameEntry = tk.Entry(self.taskSpecsFrame, 
            textvariable=self.taskNameValue,
            width=16,
            validate='key',
            validatecommand=(self.validateTaskName, '%P')
        )
        logging.debug("Task name input entry box built.")
        
        # Task coordinate entry section
        self.coordinateLabelX = tk.Label(self.taskSpecsFrame, text="X")
        self.coordinateLabelY = tk.Label(self.taskSpecsFrame, text="Y")
        self.pickupPositionLabel = tk.Label(self.taskSpecsFrame, text="Pickup Location:")
        self.dropoffPositionLabel = tk.Label(self.taskSpecsFrame, text="Dropoff Location:")
        self.pickupXPosValue = tk.StringVar()
        self.pickupYPosValue = tk.StringVar()
        self.validateTaskPosCoord = self.register(self.validateNumericSpinbox)
        # self.commandPickupXPos = partial(self.highlightTargetXPos, 'X', 'pickupHighlight', self.pickupXPosValue, self.pickupYPosValue)
        # Use a trace on the stringvars to respond with a single function call any time the stringvar value is updated
        # This decouples validation from highlighting
        self.pickupXPosValue.trace_add("write", lambda *args, b=self.pickupXPosValue, c=self.pickupYPosValue : self.highlightTargetTile('pickupHighlight', b, c, *args))
        self.pickupXPosEntry = ttk.Spinbox(self.taskSpecsFrame,
            width=6,
            from_=0,
            to=self.mapData.dimensionX,
            increment=1,
            textvariable=self.pickupXPosValue,
            # command=self.commandPickupXPos,
            validate='key',
            validatecommand=(self.validateTaskPosCoord, '%P'),
            background='#6fe64e'
        )
        # self.validatePickupYPos = self.register(self.highlightTargetYPos)
        # self.commandPickupYPos = partial(self.highlightTargetYPos, 'Y', 'pickupHighlight', self.pickupXPosValue, self.pickupYPosValue)
        self.pickupYPosValue.trace_add("write", lambda *args, b=self.pickupXPosValue, c=self.pickupYPosValue : self.highlightTargetTile('pickupHighlight', b, c, *args))
        self.pickupYPosEntry = ttk.Spinbox(self.taskSpecsFrame,
            width=6,
            from_=0,
            to=self.mapData.dimensionX,
            increment=1,
            textvariable=self.pickupYPosValue,
            # command=self.commandPickupYPos,
            validate='key',
            validatecommand=(self.validateTaskPosCoord, '%P'),
            # validatecommand=(self.validatePickupYPos, '%P', 'pickupHighlight', self.pickupXPosValue, self.pickupYPosValue),
            background='#6fe64e'
        )
        logging.debug("Custom task pickup location spinboxes built.")

        self.dropoffXPosValue = tk.StringVar()
        self.dropoffYPosValue = tk.StringVar()
        # self.validateDropoffXPos = self.register(self.highlightTargetXPos)
        # self.commandDropoffXPos = partial(self.highlightTargetXPos, 'X', 'dropoffHighlight', self.dropoffXPosValue, self.dropoffYPosValue)
        self.dropoffXPosValue.trace_add("write", lambda *args, b=self.dropoffXPosValue, c=self.dropoffYPosValue : self.highlightTargetTile('depositHighlight', b, c, *args))
        self.dropoffXPosEntry = ttk.Spinbox(self.taskSpecsFrame,
            width=6,
            from_=0,
            to=self.mapData.dimensionX,
            increment=1,
            textvariable=self.dropoffXPosValue,
            # command=self.commandDropoffXPos,
            validate='key',
            validatecommand=(self.validateTaskPosCoord, '%P'),
            # validatecommand=(self.validateDropoffXPos, '%P', 'dropoffHighlight', self.dropoffXPosValue, self.dropoffYPosValue),
            background='cyan'
        )
        # self.validateDropoffYPos = self.register(self.highlightTargetYPos)
        # self.commandDropoffYPos = partial(self.highlightTargetYPos, 'Y', 'dropoffHighlight', self.dropoffXPosValue, self.dropoffYPosValue)
        self.dropoffYPosValue.trace_add("write", lambda *args, b=self.dropoffXPosValue, c=self.dropoffYPosValue : self.highlightTargetTile('depositHighlight', b, c, *args))
        self.dropoffYPosEntry = ttk.Spinbox(self.taskSpecsFrame,
            width=6,
            from_=0,
            to=self.mapData.dimensionX,
            increment=1,
            textvariable=self.dropoffYPosValue,
            # command=self.commandDropoffYPos,
            validate='key',
            validatecommand=(self.validateTaskPosCoord, '%P'),
            # validatecommand=(self.validateDropoffYPos, '%P', 'dropoffHighlight', self.dropoffXPosValue, self.dropoffYPosValue),
            background='cyan'
        )
        logging.debug("Custom task dropoff location spinboxes built.")

        # Task time limitation entry section
        self.timeLimitLabel = tk.Label(self.taskSpecsFrame, text="Time limit (Sim steps)")
        self.timeLimitLabel2 = tk.Label(self.taskSpecsFrame, text="0 means unlimited.")
        self.timeLimitValue = tk.StringVar()
        self.validateTaskTimeLimit = self.register(self.validateNumericSpinbox)
        # self.validateTaskTimeLimit = self.register(self.taskTimeLimitValidation)
        # self.commandTaskTimeLimit = partial(self.taskTimeLimitValidation, 'T')
        self.timeLimitValue.trace_add("write", lambda *args, b=self.timeLimitValue : self.taskTimeLimitValidation(b, *args))
        self.timeLimitEntry = ttk.Spinbox(self.taskSpecsFrame,
            width=6,
            from_=0,
            to=999,
            increment=1,
            textvariable=self.timeLimitValue,
            # command=self.commandTaskTimeLimit,
            validate='key',
            validatecommand=(self.validateTaskTimeLimit, '%P')
        )
        logging.debug("Custom task time limit spinbox built.")

        # Section separators
        self.sep1 = ttk.Separator(self.taskSpecsFrame, orient='horizontal')
        self.sep2 = ttk.Separator(self.taskSpecsFrame, orient='vertical')
        self.sep3 = ttk.Separator(self.taskSpecsFrame, orient='horizontal')

        # Confirm and cancel buttons
        self.createTaskButton = tk.Button(self.taskSpecsFrame,
            command=self.createTask,
            text="Create Task",
            width=15,
            state=tk.DISABLED
            )
        logging.debug("Task creation cancel button built.")
        self.cancelTaskCreationButton = tk.Button(self.taskSpecsFrame,
            command=self.cancelTaskCreation,
            text="Cancel",
            width=15,
            )
        logging.debug("Task creation action button built.")

        self.taskSpecsFrame.columnconfigure(0, weight=1)
        self.taskSpecsFrame.columnconfigure(1, weight=1)
        self.taskSpecsFrame.columnconfigure(2, weight=1)
        self.taskSpecsFrame.columnconfigure(3, weight=1)

        # Autogenerate name tickbox
        self.autogenerateTaskNameValue = tk.IntVar()
        self.autogenerateTaskNameTickbox = tk.Checkbutton(self.taskSpecsFrame, text="Autogen. Name",
            variable=self.autogenerateTaskNameValue, command=self.updateTaskCreationButton)
        logging.debug("Task automatic name generation tickbox built.")

        # Render widgets
        self.taskNameLabel.grid(row=0, column=0)
        self.taskNameEntry.grid(row=0, column=1, sticky=tk.W)
        self.autogenerateTaskNameTickbox.grid(row=0, column=2, columnspan=2)
        self.coordinateLabelX.grid(row=2, column=2)
        self.coordinateLabelY.grid(row=2, column=3)
        self.pickupPositionLabel.grid(row=3, column=1)
        self.dropoffPositionLabel.grid(row=4, column=1)
        self.pickupXPosEntry.grid(row=3, column=2)
        self.pickupYPosEntry.grid(row=3, column=3)
        self.dropoffXPosEntry.grid(row=4, column=2)
        self.dropoffYPosEntry.grid(row=4, column=3)
        self.timeLimitLabel.grid(row=2, column=0)
        self.timeLimitLabel2.grid(row=3, column=0)
        self.timeLimitEntry.grid(row=4, column=0, pady=4)
        self.sep1.grid(row=1, column=0, columnspan=4, sticky=tk.W+tk.E, padx=4, pady=4)
        self.sep2.grid(row=2, column=1, rowspan=3, sticky=tk.N+tk.S+tk.W, pady=4)
        self.sep3.grid(row=5, column=0, columnspan=4, sticky=tk.W+tk.E, padx=4)
        self.cancelTaskCreationButton.grid(row=6, column=0, columnspan=2, pady=4)
        self.createTaskButton.grid(row=6, column=2, columnspan=2, pady=4)
        logging.debug("Custom task creation UI elements rendered.")

        # Containing Frame for random task generation
        self.taskRandomGeneratorFrame = tk.LabelFrame(self.taskFrame, text="Generate Random Task")
        self.taskRandomGeneratorFrame.grid(row=1, column=0, sticky=tk.E+tk.W, padx=4, pady=4)
        logging.debug("Randomized task generation containing frame built.")

        # UI Elements for generating random tasks
        self.taskRandomGeneratorRespectNodeTypeButton = tk.Checkbutton(self.taskRandomGeneratorFrame, 
            text="Respect Node Types",
            onvalue=True,
            offvalue=False,
            command=self.toggleRandomGeneratorRespectsNodeTypeState
        )
        self.taskRandomGeneratorRespectNodeTypeButton.select() # Default state is True, make the visual match
        logging.debug("Randomized task generation node type respect toggle built.")

        # Button to trigger generation
        self.taskRandomGeneratorButton = tk.Button(self.taskRandomGeneratorFrame, 
            text="Gen. Randomized Task", 
            command=lambda : self.parent.taskManager.generateRandomTask(self.taskGeneratorRespectsNodeTypes)
        )
        logging.debug("Randomized task generation action button built.")

        # Render Widgets
        self.taskRandomGeneratorRespectNodeTypeButton.grid(row=0, column=0, pady=4)
        self.taskRandomGeneratorButton.grid(row=0, column=1, pady=4)

    def cancelTaskCreation(self):
        logging.debug("Cancelling task generation . . .")
        self.mainView.mainCanvas.requestRender("highlight", "delete", {"highlightTag": "pickupHighlight"})
        self.mainView.mainCanvas.requestRender("highlight", "delete", {"highlightTag": "depositHighlight"})
        self.mainView.mainCanvas.handleRenderQueue()
        self.taskCreationPrompt()

    def toggleRandomGeneratorRespectsNodeTypeState(self):
        self.taskGeneratorRespectsNodeTypes = not self.taskGeneratorRespectsNodeTypes
        logging.debug(f"Random generator node type respect toggled to '{self.taskGeneratorRespectsNodeTypes}'.")
        # print(self.taskGeneratorRespectsNodeTypes)

    def validateNumericSpinbox(self, inputString):
        logging.debug(f"Validating numeric spinbox entry: {inputString}")
        if inputString.isnumeric():
            # Only allow numeric characters
            logging.debug("Numeric spinbox entry is numeric. Allowed.")
            return True
        elif len(inputString) == 0:
            logging.debug("Numeric spinbox entry is empty. Allowed.")
            # Or an empty box
            return True
        else:
            logging.debug("Numeric spinbox entry is invalid.")
            return False
        
    def taskNameValidation(self, taskName):
        logging.debug(f"Validating user-entered task name '{taskName}'.")
        if len(taskName) < 1:
            # Disable the ability to create the task
            self.taskNameValid = False
            logging.debug("User-entered task name is too short.")

            # Check that all other enabling conditions are met
            self.updateTaskCreationButton()

            # Allow the box to be empty
            return True
        elif any(self.parent.taskManager.taskList[i].name == taskName for i in self.parent.taskManager.taskList):
            # If the taskName is the same as a task that already exists, disallow creating it
            self.taskNameValid = False
            logging.debug(f"User-input task name '{taskName}' already exists in the task list.")

            # Check that all other enabling conditions are met
            self.updateTaskCreationButton()

            # Allow the box to be empty
            return True
        else:
            # Enable the ability to create the task
            self.taskNameValid = True
            logging.debug("User-entered task name is valid.")

            # Check that all tohe renabling conditions are met
            self.updateTaskCreationButton()

            return True

    def taskTimeLimitValidation(self, timeLimit, *args):
        logging.debug(f"Validating custom task time limit entry '{timeLimit}'.")
        # Spinbox should only accept numeric entries
        if timeLimit.get().isnumeric():
            self.validTaskTimeLimit = True
            logging.debug("Task time limit entry is numeric. Allowed.")
            self.updateTaskCreationButton()
            return True
        else:
            self.validTaskTimeLimit = False
            logging.debug("Task  time limit is non-numeric and invalid.")
            self.updateTaskCreationButton()
            return False

    def validateTaskPlacement(self, highlightType):
        # Using guard clauses check that
        # The pickup x position input is numeric
        pickupX = self.pickupXPosValue.get()
        pickupY = self.pickupYPosValue.get()
        dropoffX = self.dropoffXPosValue.get()
        dropoffY = self.dropoffYPosValue.get()
        logging.debug(f"Validating task placement: 'Pickup: ({pickupX}, {pickupY})' and 'Dropoff: ({dropoffX}, {dropoffY})'")
        # print(f"Validate task with: ({pickupX}, {pickupY}) and ({dropoffX}, {dropoffY})")
        if not pickupX.isnumeric():
            # print("PICKUPX IS NOT NUMERIC")
            # Else it is invalid
            self.validTaskLocations = False
            logging.debug(f"Task pickup X coordinate '{pickupX}' is not numeric.")
            self.updateTaskCreationButton()
            return
        # The pickup y position input is numeric
        if not pickupY.isnumeric():
            # print("PICKUPY IS NOT NUMERIC")
            # Else it is invalid
            self.validTaskLocations = False
            logging.debug(f"Task pickup Y coordinate '{pickupY}' is not numeric.")
            self.updateTaskCreationButton()
            return
        # The dropoff x position input is numeric
        if not dropoffX.isnumeric():
            # print("DROPOFFX IS NOT NUMERIC")
            # Else it is invalid
            self.validTaskLocations = False
            logging.debug(f"Task dropoff X coordinate '{dropoffX}' is not numeric.")
            self.updateTaskCreationButton()
            return
        # The dropoff y position input is numeric
        if not dropoffY.isnumeric():
            # print("DROPOFFY IS NOT NUMERIC")
            # Else it is invalid
            self.validTaskLocations = False
            logging.debug(f"Task dropoff Y coordinate '{dropoffY}' is not numeric.")
            self.updateTaskCreationButton()
            return
        # The pickup location must belong to the graph
        if not self.tileInGraphValidation(pickupX, pickupY):
            # print("PICKUP NODE NOT WITHIN GRAPH")
            # Else it is invalid
            self.validTaskLocations = False
            logging.debug(f"Pickup coordinates '({pickupX}, {pickupY})' does not exist in the graph.")
            self.updateTaskCreationButton()
            return
        # The dropoff location must belong to the graph
        if not self.tileInGraphValidation(dropoffX, dropoffY):
            # print("DROPOFF NODE NOT WITHIN GRAPH")
            # Else it is invalid
            self.validTaskLocations = False
            logging.debug(f"Dropoff coordinates '({dropoffX}, {dropoffY})' does not exist in the graph.")
            self.updateTaskCreationButton()
            return
        # Pickups and dropoffs can overlap in this case, awkward to handle though, revisit
        # If all guard clauses are passed, enable the create task button
        self.validTaskLocations = True
        logging.debug(f"Task placement settings are valid.")
        # Check that all other enabling conditions are met
        self.updateTaskCreationButton()

    def updateTaskCreationButton(self):
        # Change the status of the create task button based on entry validity
        # Input validation is already handled at this point
        logging.debug(f"Name: {self.taskNameValid}, Locations: {self.validTaskLocations}, Time limit: {self.validTaskTimeLimit}")
        if self.validTaskTimeLimit and self.validTaskLocations and (self.taskNameValid or self.autogenerateTaskNameValue.get()):
            self.createTaskButton.config(state=tk.NORMAL)
            logging.debug("All task settings are valid. Allowing creation.")
        else:
            self.createTaskButton.config(state=tk.DISABLED)
            logging.debug("Not all task settings are valid. Creation blocked.")

    def createTask(self):
        logging.debug("Attempting to create task . . .")

        # Create the task, place it
        pickupXPos = eval(self.pickupXPosValue.get())
        pickupYPos = eval(self.pickupYPosValue.get())
        pickupNode = (pickupXPos, pickupYPos)
        dropoffXPos = eval(self.dropoffXPosValue.get())
        dropoffYPos = eval(self.dropoffYPosValue.get())
        dropoffNode = (dropoffXPos, dropoffYPos)
        timeLimit = eval(self.timeLimitValue.get())
        if len(self.taskNameValue.get()) == 0 and self.autogenerateTaskNameValue:
            taskName = len(self.parent.taskManager.taskList)
        else:
            taskName = self.taskNameValue.get()

        logging.debug(f"New task settings: '(Name: {taskName}, Pickup: {str(pickupNode)}, Dropoff: {str(dropoffNode)}, TimeLimit: {timeLimit})'")

        # Verify that nodes belong to proper type
        if not self.parent.mapData.mapGraph.nodes()[str(pickupNode)]['type'] == 'pickup' or not self.parent.mapData.mapGraph.nodes()[str(dropoffNode)]['type'] == 'deposit':
            # Both nodes are invalid
            pickupNodeType = self.parent.mapData.mapGraph.nodes()[str(pickupNode)]['type']
            dropoffNodeType = self.parent.mapData.mapGraph.nodes()[str(dropoffNode)]['type']
            response = tk.messagebox.askokcancel(title="One or more node types mismatch", 
                message=f"One or more nodes in this task do not match the standard type. \n\nChosen pickup node {pickupNode} is of type '{pickupNodeType}'\nChosen dropoff node {dropoffNode} is of type '{dropoffNodeType}'\n\nPress OK to initiate the task anyway, or cancel to change nodes.")
            if response == True:
                logging.debug("User chose to ignore the node types when creating task. Continuing . . .")
                pass
            else:
                logging.debug("User was warned that node types are incompatible and cancelled task creation.")
                return
        
        try:
            logging.info("Creating task . . .")
            # Attempt to create the task
            self.taskManager.createNewTask(
                taskName = taskName,
                pickupPosition = pickupNode,
                dropoffPosition = dropoffNode,
                timeLimit = timeLimit
            )
            # Remove previous highlights
            self.mainView.mainCanvas.requestRender("highlight", "delete", {"highlightTag": "pickupHighlight"})
            self.mainView.mainCanvas.requestRender("highlight", "delete", {"highlightTag": "depositHighlight"})
            self.mainView.mainCanvas.handleRenderQueue()
            # Close the task generator
            self.taskCreationPrompt()
        except nx.NetworkXNoPath:
            # If the graph does not contain connections to allow path completion, display a warning
            logging.warning("Task is not completable because there is no path between task nodes!")
            tk.messagebox.showerror(title="Invalid Task Path", message=f"No path between {pickupNode} and {dropoffNode}!")
        except RWSE.RWSTaskTimeLimitImpossible as exc:
            logging.warning("Task is not completable because the time limit is too low for the best path to attain.")
            tk.messagebox.showerror(title="Task time limit too low", message=f"Optimal pathing cannot complete the task in time. \nMinimum complete time: {exc.minTimeToComplete} \nTime limit: {exc.timeLimit}")

    def taskManagePrompt(self):
        logging.debug("Creating task management prompt UI eleemnts . . .")
        self.clearTaskManagementUI()
        # Create a button that starts prompting the user
        self.manageTaskButton = tk.Button(self.taskManageFrame,
            command=self.taskManagementUI, text="Manage Task . . .", width=15,
            state=tk.DISABLED)
        
        # Render the button, centered in the frame
        self.taskManageFrame.columnconfigure(0, weight=1)
        self.manageTaskButton.grid(row=0, column=0, pady=4, padx=4, columnspan=2)
        logging.debug("Task management UI reset to initial state.")

    def enableTaskManagement(self):
        # Enable the management interface
        self.manageTaskButton.config(state=tk.NORMAL)

    def clearTaskManagementUI(self):
        # Destroys all the task creation ui elements
        for widget in self.taskManageFrame.winfo_children():
            widget.destroy()
        # Reset column/row weights
        for row in range(self.taskManageFrame.grid_size()[0]):
            self.taskManageFrame.rowconfigure(row, weight=0)
        for col in range(self.taskManageFrame.grid_size()[1]):
            self.taskManageFrame.columnconfigure(col, weight=0)
        logging.debug("Removed all UI elements from the task creation frame.")

    def taskManagementUI(self):
        logging.debug("Creating task management UI elements.")
        self.clearTaskManagementUI()

        # Prevent simultaneous management of tasks and agents
        self.agentManagePrompt()

        # Display the currently managed task
        taskRef = self.parent.taskManager.currentTask
        self.managedTaskLabel = tk.Label(self.taskManageFrame, text=f"Managing Task {taskRef.numID}:{taskRef.name}. Pickup node is: {taskRef.pickupPosition} Dropoff node is: {taskRef.dropoffPosition}")
        self.managedTaskLabel.grid(row=0, column=0, columnspan=3, sticky=tk.W)

        # Create a label for the agent assignment drop down
        self.taskAgentAssignmentLabel = tk.Label(self.taskManageFrame, text="Assign agent: ")
        self.taskAgentAssignmentLabel.grid(row=1, column=0)

        # Create the drop down menu
        agentList = self.agentManager.agentList
        self.taskManageFrame.columnconfigure(1, weight=1)
        if agentList:
            # There are agents to choose from
            agentOptions = ()
            for agent in agentList:
                agentOptions = (*agentOptions, agentList[agent].ID)
            self.taskAgentStringVar = tk.StringVar()
            self.taskAgentAssignmentOptionMenu = ttk.Combobox(self.taskManageFrame, width=20, textvariable=self.taskAgentStringVar)
            self.taskAgentAssignmentOptionMenu['values'] = agentOptions

            # Render the menu
            self.taskAgentAssignmentOptionMenu.grid(row=1, column=1)
            self.taskAgentAssignmentOptionMenu.bind("<<ComboboxSelected>>", self.prepSelectedAgentForAssignment)
        else:
            # There are no tasks to choose from
            self.taskNoAgentsAvailableLabel = tk.Label(self.taskManageFrame, text="No agents available to assign!")
            self.taskNoAgentsAvailableLabel.grid(row=1, column=1)
        
        # Create an action button to assign the task
        self.taskAgentAssignmentButton = tk.Button(self.taskManageFrame,
            command=self.assignSelectedAgent, text="Assign Agent", width=10,
            state=tk.DISABLED
            )
        self.taskAgentAssignmentButton.grid(row=1, column=2, padx=4, pady=4)

    def prepSelectedAgentForAssignment(self, event):
        # Find the agent object ID
        selectedAgentOption = self.taskAgentStringVar.get()
        selectedAgentID = next((agentID for agentID, agent in self.agentManager.agentList.items() if agent.ID == selectedAgentOption))
        self.agentManager.agentList[selectedAgentID].highlightAgent(multi=False)

        # Save the task into an attribute for external access
        self.parent.agentManager.currentAgent = self.parent.agentManager.agentList[selectedAgentID]

        # Enable the assignment action button
        self.taskAgentAssignmentButton.configure(state=tk.ACTIVE)

    def assignSelectedAgent(self):
        # Execute the task assignment
        self.parent.taskManager.assignAgentToTask()
        self.parent.agentManager.assignTaskToAgent()

        # Reset the UI
        self.taskManagePrompt()

        # Clear the highlights on the mainView
        self.parent.mainView.mainCanvas.clearHighlight()

        # Re-render the app state
        self.parent.mainView.mainCanvas.renderGraphState()

    def createRandomSeedPane(self):
        logging.debug("Creating random generator engine UI panel elements . . .")
        self.randomSeedFrame.columnconfigure(0, weight=1)
        self.randomSeedFrame.columnconfigure(1, weight=1)
        self.randomSeedFrame.columnconfigure(2, weight=1)

        # Label for RNG seed entrybox
        self.randomSeedLabel = tk.Label(self.randomSeedFrame, text="RNG Seed Value:")
        self.randomSeedLabel.grid(row=0, column=0, pady=4, padx=4, sticky=tk.W)

        # Entry box for setting the seed value
        self.randomSeedValue = tk.StringVar()
        self.validateRandomSeed = self.register(self.randomSeedValidation)
        self.randomSeedEntry = tk.Entry(self.randomSeedFrame, 
            textvariable=self.randomSeedValue, 
            width=30,
            validate='key',
            validatecommand=(self.validateRandomSeed, '%P')
            )
        self.randomSeedEntry.grid(row=0, column=1, pady=4, padx=4, sticky=tk.W)
        logging.debug("Random generator seed entry box built.")

        # Button for confirming choice of seed value
        self.randomSeedSetButton = tk.Button(self.randomSeedFrame,
            command = self.copyRandomSeed,
            text="Set",
            width=6,
            state=tk.DISABLED
        )
        self.randomSeedSetButton.grid(row=0, column=2, pady=4, padx=4)
        logging.debug("Random generator seed set action button built.")

        # Text displaying the current seed value
        currentSeed = self.parent.randomGenerator.randomGeneratorState.currentSeed
        self.currentSeedLabel = tk.Label(self.randomSeedFrame, text=f"Current RNG Seed Value: {currentSeed}")
        self.currentSeedLabel.grid(row=1, column=0, columnspan=2)
        logging.debug("Random generator current seed display built.")

    def randomSeedValidation(self, seedString):
        logging.debug(f"Validating new seed input: '{seedString}'")
        # Only accept alphanumeric characters
        if any(not char.isalnum() for char in seedString):
            self.randomSeedSetButton.config(state=tk.DISABLED)
            logging.debug("New seed is not alphanumeric.")
            return False
        # Ensure the new seed differs from the old seed
        if seedString == self.parent.randomGenerator.randomGeneratorState.currentSeed:
            self.randomSeedSetButton.config(state=tk.DISABLED)
            logging.debug("New seed is identical to the current seed.")
            return False
        # Ensure a minimum seed string length
        if len(seedString) < 2:
            self.randomSeedSetButton.config(state=tk.DISABLED)
            logging.debug("New seed is too short.")
            return True
        else:
            logging.debug("Seed is valid, allowing engine to be set.")
            self.randomSeedSetButton.config(state=tk.NORMAL)
        return True

    def copyRandomSeed(self):
        # Pull the RNG seed from the text entry box
        seed = self.randomSeedEntry.get()
        # Update the generator's seed
        self.parent.randomGenerator.updateCurrentSeed(seed)
        logging.debug("Random Generator engine seed updated.")
        # Update the display
        self.updateCurrentSeedDisplay()
        # Disable the set button
        self.randomSeedSetButton.config(state=tk.DISABLED)

    def updateCurrentSeedDisplay(self):
        logging.debug("Updating the current random generator engine seed display value . . .")
        currentSeed = self.parent.randomGenerator.randomGeneratorState.currentSeed
        self.currentSeedLabel.config(text=f"Current RNG Seed Value: {currentSeed}")
