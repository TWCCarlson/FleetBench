import tkinter as tk
from tkinter import ttk
import networkx as nx
from functools import partial

class toolBar(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        # Fetch styling
        appearanceValues = self.parent.appearance
        frameHeight = appearanceValues.toolBarHeight
        frameWidth = appearanceValues.toolBarWidth
        frameBorderWidth = appearanceValues.frameBorderWidth
        frameRelief = appearanceValues.frameRelief
        # Declare frame
        tk.Frame.__init__(self, parent, height=frameHeight, 
            width=frameWidth, 
            borderwidth=frameBorderWidth, 
            relief=frameRelief)
        # Render frame
        self.grid_propagate(False)
        self.grid(row=0, column=0, rowspan=2, sticky=tk.N)
        
        # Establish buttons and inputs
        self.initUI()

    def buildReferences(self):
        self.mainView = self.parent.mainView
        self.mapData = self.parent.mapData
        self.agentManager = self.parent.agentManager
        self.taskManager = self.parent.taskManager

    def initUI(self):
        print("Create toolbar ui elements")
        self.columnconfigure(0, weight=1)
        # self.rowconfigure(0, weight=1)
        # Create a labeled container for the agent generator
        self.agentFrame = tk.LabelFrame(self, text="Agent Generator")
        self.agentFrame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W, padx=4, columnspan=2)
        self.agentCreationPrompt()

        # Create a labeled container for the task generator
        self.taskFrame = tk.LabelFrame(self, text="Task Generator")
        self.taskFrame.grid(row=1, column=0, sticky=tk.N+tk.E+tk.W, padx=4, columnspan=2)
        self.taskCreationPrompt()

        # Create a labeled container for the rng system
        self.randomSeedFrame = tk.LabelFrame(self, text="RNG System Seed")
        self.randomSeedFrame.grid(row=2, column=0, sticky=tk.N+tk.E+tk.W, padx=4, columnspan=2)
        self.createRandomSeedPane()


    def agentCreationPrompt(self):
        self.clearAgentCreationUI()
        # Create a button to start UI creation
        self.createAgentButton = tk.Button(self.agentFrame, 
            command=self.agentCreationUI, text="Create Agent. . .", width=15,
            state=tk.DISABLED)
        self.agentFrame.columnconfigure(0, weight=1)
        self.createAgentButton.grid(row=0, column=0, pady=4, padx=4, columnspan=2)
        # If a map is loaded when this gui is created, enable the creation button
        if self.parent.mapData.mapLoadedBool == True:
            self.createAgentButton.config(state=tk.NORMAL)

    def enableAgentCreation(self):
        self.createAgentButton.config(state=tk.NORMAL)

    def agentCreationUI(self):
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

        # Create labeled container for agent information
        self.agentDataFrame = tk.LabelFrame(self.agentFrame, text="Agent Specs")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.agentDataFrame.grid(row=1, column=0, sticky=tk.N+tk.E+tk.W, padx=4, columnspan=2)

        # Coordinate Entry boxes and labels
        self.agentXPosValue = tk.StringVar()
        self.agentYPosValue = tk.StringVar()
        self.entryXLabel = tk.Label(self.agentDataFrame, text="X Position: ", width=8)
        validateCommand = self.register(self.validateNumericSpinbox)
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
            validatecommand=validateCommand
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
            validatecommand=validateCommand
            # validatecommand=(self.validateAgentYPos, '%P', 'agentHighlight')  # Triggered on typing
        )

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

        # Separator
        self.sep1 = ttk.Separator(self.agentDataFrame, orient='vertical')
        self.sep1.grid(row=0, column=2, rowspan=3, sticky=tk.N+tk.S+tk.W, pady=4, padx=4)

        # Save and edit buttons
        self.editAgentClassButton = tk.Button(self.agentFrame, 
            command=self.placeholder, 
            text="Edit Information",
            width=15,
            )
        self.confirmCreateAgentButton = tk.Button(self.agentFrame, 
            command = self.createAgent, 
            text="Create Agent",
            width=15,
            state=tk.DISABLED
            )
        self.editAgentClassButton.grid(row=2, column=0, sticky=tk.E, pady=4)
        self.confirmCreateAgentButton.grid(row=2, column=1, sticky=tk.W, pady=4)

    def clearAgentCreationUI(self):
        # Destroys all the agent creation ui elements
        for widget in self.agentFrame.winfo_children():
            widget.destroy()
        for row in range(self.agentFrame.grid_size()[0]):
            self.agentFrame.rowconfigure(row, weight=0)
        for col in range(self.agentFrame.grid_size()[1]):
            self.agentFrame.columnconfigure(col, weight=0)

        # Resets the enabled status of the create agent button
        self.validAgentCreationNode = False
        self.agentNameValid = False

    def highlightTargetTile(self, highlightType, stringVarX, stringVarY, *args):
        # 
        # If an input is Nonetype, fetch it from its entry variable
        # print(stringVarX)
        xPos = stringVarX.get()
        yPos = stringVarY.get()
        # print(f"Called highlightTargetTile with: {xPos}, {yPos}, {highlightType}, {stringVarX.get()}, {stringVarY.get()}")

        # Color selection dictionary
        highlightColors = {
            "agentHighlight": "red",
            "pickupHighlight": "green",
            "dropoffHighlight": "cyan"
        }
        highlightColor = highlightColors[highlightType]

        # Using guard clauses, check that
        # The x input is numeric
        if not xPos.isnumeric():
            # Else it is invalid
            self.validAgentCreationNode = False
            self.mainView.mainCanvas.clearHighlight(highlightType)
            return
        # The y input is numeric
        if not yPos.isnumeric():
            # Else it is invalid
            self.validAgentCreationNode = False
            self.mainView.mainCanvas.clearHighlight(highlightType)
            return
        # If all guard clauses are passed, highlight the tile
        if highlightType == 'agentHighlight':
            self.mainView.mainCanvas.highlightTile(xPos, yPos, highlightColor, multi=False, highlightType=highlightType)
            # Validate for placing an agent
            self.validateAgentPlacement(xPos, yPos, highlightType)
        elif highlightType == 'pickupHighlight' or highlightType == 'dropoffHighlight':
            print(f"highlighting tile of type {highlightType}")
            self.mainView.mainCanvas.highlightTile(xPos, yPos, highlightColor, multi=False, highlightType=highlightType)
            # Validate for placing a task
            self.validateTaskPlacement(highlightType)

    def validateAgentPlacement(self, xPos, yPos, highlightType):
        # Using guard clauses, check that
        # The x input is numeric
        if not xPos.isnumeric():
            # Else it is invalid
            self.validAgentCreationNode = False
            self.updateAgentCreationButton()
            self.mainView.mainCanvas.clearHighlight(highlightType)
            return
        # The y input is numeric
        if not yPos.isnumeric():
            # Else it is invalid
            self.validAgentCreationNode = False
            self.updateAgentCreationButton()
            self.mainView.mainCanvas.clearHighlight(highlightType)
            return
        # Check that it belongs to the graph
        if not self.tileInGraphValidation(xPos, yPos):
            self.validAgentCreationNode = False
            self.updateAgentCreationButton()
            return
        # And that the tile does not already contain an agent
        # print(self.mapData.mapGraph.nodes.data()[f"({eval(xPos)}, {eval(yPos)})"])
        if 'agent' in self.mapData.mapGraph.nodes.data()[f"({eval(xPos)}, {eval(yPos)})"]:
            # Else it is invalid    
            # print("AGENT EXISTS IN THIS TILE ALREADY")
            self.validAgentCreationNode = False
            self.updateAgentCreationButton()
            return
        # Enable the button based on graph belongingness
        self.validAgentCreationNode = True

        # Check that all other enabling conditions are met
        self.updateAgentCreationButton()

    def tileInGraphValidation(self, xPos, yPos):
        # Check that the node formed by these positions is actually part of the warehouse graph
        graphCandidate = '(' + str(xPos) + ", " + str(yPos) + ')'
        if graphCandidate in self.mapData.mapGraph.nodes:
            # If so, enable the button
            # self.confirmCreateAgentButton.config(state=tk.ACTIVE)
            return True
        else:
            # self.confirmCreateAgentButton.config(state=tk.DISABLED)
            return False

    def agentNameValidation(self, agentName):
        # If the agentName box is empty (length = 0), it is not valid
        if len(agentName) < 3:
            # Disable the ability to create the agent
            self.agentNameValid = False

            # Check that all other enabling conditions are met
            self.updateAgentCreationButton()

            # self.confirmCreateAgentButton.config(state=tk.DISABLED)
            # Allow the box to be empty
            return True
        else:
            # Enable the ability to create the agent
            self.agentNameValid = True

            # Check that all other enabling conditions are met
            self.updateAgentCreationButton()

            # self.confirmCreateAgentButton.config(state=tk.ACTIVE)
            return True

    def updateAgentCreationButton(self):
        # Checks if all preconditions for placing an agent on the graph are met
        # Input box validation is done with callbacks
        if self.validAgentCreationNode and self.agentNameValid:
            self.confirmCreateAgentButton.config(state=tk.NORMAL)
        else:
            self.confirmCreateAgentButton.config(state=tk.DISABLED)

    def placeholder(self):
        print(self.entryXValue.get() + ", " + self.entryYValue.get())
        self.agentCreationPrompt()

    def createAgent(self):
        print("Create agent")
        # Remove previous highlight of tile
        self.mainView.mainCanvas.clearHighlight()
        # Create the agent, place it
        # https://networkx.org/documentation/stable/reference/generated/networkx.classes.function.set_node_attributes.html
        # Note that if the dictionary contains nodes that are not in G, the values are silently ignored:
        xPos = eval(self.agentXPosValue.get())
        yPos = eval(self.agentYPosValue.get())
        targetNode = (xPos, yPos)
        agentOrientation = self.agentOrientation.get()
        self.agentManager.createNewAgent(
            ID = self.agentNameValue.get(),
            position=targetNode, 
            orientation=agentOrientation, 
            className=self.agentClass.get(),
            )
        # Re-render the map state
        self.mainView.mainCanvas.renderGraphState()
        # Close agent generator
        self.agentCreationPrompt()

    def createRandomSeedPane(self):
        print("create rng seed panel")
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

        # Button for confirming choice of seed value
        self.randomSeedSetButton = tk.Button(self.randomSeedFrame,
            command = self.copyRandomSeed,
            text="Set",
            width=6,
            state=tk.DISABLED
        )
        self.randomSeedSetButton.grid(row=0, column=2, pady=4, padx=4)

        # Text displaying the current seed value
        currentSeed = self.parent.randomGenerator.currentSeed
        self.currentSeedLabel = tk.Label(self.randomSeedFrame, text=f"Current RNG Seed Value: {currentSeed}")
        self.currentSeedLabel.grid(row=1, column=0, columnspan=2)

    def randomSeedValidation(self, seedString):
        # Only accept alphanumeric characters
        if any(not char.isalnum() for char in seedString):
            self.randomSeedSetButton.config(state=tk.DISABLED)
            return False
        # Ensure the new seed differs from the old seed
        if seedString == self.parent.randomGenerator.currentSeed:
            self.randomSeedSetButton.config(state=tk.DISABLED)
            return False
        # Ensure a minimum seed string length
        if len(seedString) < 2:
            self.randomSeedSetButton.config(state=tk.DISABLED)
            return True
        else:
            self.randomSeedSetButton.config(state=tk.NORMAL)
        return True

    def copyRandomSeed(self):
        # Pull the RNG seed from the text entry box
        seed = self.randomSeedEntry.get()
        # Update the generator's seed
        self.parent.randomGenerator.updateCurrentSeed(seed)
        # Update the display
        self.updateCurrentSeedDisplay()
        # Disable the set button
        self.randomSeedSetButton.config(state=tk.DISABLED)

    def updateCurrentSeedDisplay(self):
        currentSeed = self.parent.randomGenerator.currentSeed
        self.currentSeedLabel.config(text=f"Current RNG Seed Value: {currentSeed}")

    def taskCreationPrompt(self):
        print("Create task generator prompt")
        self.clearTaskCreationUI()
        # Default button state values
        self.taskNameValid = False
        self.validTaskLocations = False
        self.validTaskTimeLimit = False
        # Create a button to start UI creation
        self.createTaskButton = tk.Button(self.taskFrame, 
            command=self.taskCreationUI, text="Create Task. . .", width=15,
            state=tk.DISABLED)
        self.taskFrame.columnconfigure(0, weight=1)
        self.createTaskButton.grid(row=0, column=0, pady=4, padx=4, columnspan=2)
        # If a map is loaded when this gui is created, enable the creation button
        if self.parent.mapData.mapLoadedBool == True:
            self.createTaskButton.config(state=tk.NORMAL)

    def enableTaskCreation(self):
        self.createTaskButton.config(state=tk.NORMAL)

    def clearTaskCreationUI(self):
        # Destroys all the task creation ui elements
        for widget in self.taskFrame.winfo_children():
            widget.destroy()
        # Reset column/row weights
        for row in range(self.taskFrame.grid_size()[0]):
            self.taskFrame.rowconfigure(row, weight=0)
        for col in range(self.taskFrame.grid_size()[1]):
            self.taskFrame.columnconfigure(col, weight=0)

    def taskCreationUI(self):
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
        
        # Task coordinate entry section
        self.coordinateLabelX = tk.Label(self.taskSpecsFrame, text="X")
        self.coordinateLabelY = tk.Label(self.taskSpecsFrame, text="Y")
        self.pickupPositionLabel = tk.Label(self.taskSpecsFrame, text="Pickup Location:")
        self.dropoffPositionLabel = tk.Label(self.taskSpecsFrame, text="Dropoff Location:")

        self.pickupXPosValue = tk.StringVar()
        self.pickupYPosValue = tk.StringVar()
        validateCommand = self.register(self.validateNumericSpinbox)
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
            validatecommand=(validateCommand, '%P'),
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
            validatecommand=(validateCommand, '%P'),
            # validatecommand=(self.validatePickupYPos, '%P', 'pickupHighlight', self.pickupXPosValue, self.pickupYPosValue),
            background='#6fe64e'
        )
        self.dropoffXPosValue = tk.StringVar()
        self.dropoffYPosValue = tk.StringVar()
        # self.validateDropoffXPos = self.register(self.highlightTargetXPos)
        # self.commandDropoffXPos = partial(self.highlightTargetXPos, 'X', 'dropoffHighlight', self.dropoffXPosValue, self.dropoffYPosValue)
        self.dropoffXPosValue.trace_add("write", lambda *args, b=self.dropoffXPosValue, c=self.dropoffYPosValue : self.highlightTargetTile('dropoffHighlight', b, c, *args))
        self.dropoffXPosEntry = ttk.Spinbox(self.taskSpecsFrame,
            width=6,
            from_=0,
            to=self.mapData.dimensionX,
            increment=1,
            textvariable=self.dropoffXPosValue,
            # command=self.commandDropoffXPos,
            validate='key',
            validatecommand=(validateCommand, '%P'),
            # validatecommand=(self.validateDropoffXPos, '%P', 'dropoffHighlight', self.dropoffXPosValue, self.dropoffYPosValue),
            background='cyan'
        )
        # self.validateDropoffYPos = self.register(self.highlightTargetYPos)
        # self.commandDropoffYPos = partial(self.highlightTargetYPos, 'Y', 'dropoffHighlight', self.dropoffXPosValue, self.dropoffYPosValue)
        self.dropoffYPosValue.trace_add("write", lambda *args, b=self.dropoffXPosValue, c=self.dropoffYPosValue : self.highlightTargetTile('dropoffHighlight', b, c, *args))
        self.dropoffYPosEntry = ttk.Spinbox(self.taskSpecsFrame,
            width=6,
            from_=0,
            to=self.mapData.dimensionX,
            increment=1,
            textvariable=self.dropoffYPosValue,
            # command=self.commandDropoffYPos,
            validate='key',
            validatecommand=(validateCommand, '%P'),
            # validatecommand=(self.validateDropoffYPos, '%P', 'dropoffHighlight', self.dropoffXPosValue, self.dropoffYPosValue),
            background='cyan'
        )

        # Task time limitation entry section
        self.timeLimitLabel = tk.Label(self.taskSpecsFrame, text="Time limit (Sim steps)")
        self.timeLimitLabel2 = tk.Label(self.taskSpecsFrame, text="0 means unlimited.")
        self.timeLimitValue = tk.StringVar()
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
            validatecommand=(validateCommand, '%P')
        )

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
        self.cancelTaskCreation = tk.Button(self.taskSpecsFrame,
            command=self.placeholder,
            text="Cancel",
            width=15,
            )

        self.taskSpecsFrame.columnconfigure(0, weight=1)
        self.taskSpecsFrame.columnconfigure(1, weight=1)
        self.taskSpecsFrame.columnconfigure(2, weight=1)
        self.taskSpecsFrame.columnconfigure(3, weight=1)

        # Render widgets
        self.taskNameLabel.grid(row=0, column=0)
        self.taskNameEntry.grid(row=0, column=1, sticky=tk.W)
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
        self.cancelTaskCreation.grid(row=6, column=0, columnspan=2, pady=4)
        self.createTaskButton.grid(row=6, column=2, columnspan=2, pady=4)

    def validateNumericSpinbox(self, inputString):
        if inputString.isnumeric():
            # Only allow numeric characters
            return True
        elif len(inputString) == 0:
            # Or an empty box
            return True
        else:
            return False
        

    def taskNameValidation(self, taskName):
        if len(taskName) < 1:
            # Disable the ability to create the task
            self.taskNameValid = False

            # Check that all other enabling conditions are met
            self.updateTaskCreationButton()

            # Allow the box to be empty
            return True
        else:
            # Enable the ability to create the task
            self.taskNameValid = True

            # Check that all tohe renabling conditions are met
            self.updateTaskCreationButton()

            return True

    def taskTimeLimitValidation(self, timeLimit, *args):
        # Spinbox should only accept numeric entries
        if timeLimit.get().isnumeric():
            self.validTaskTimeLimit = True
            self.updateTaskCreationButton()
            return True
        else:
            self.validTaskTimeLimit = False
            self.updateTaskCreationButton()
            return False

    def validateTaskPlacement(self, highlightType):
        # Using guard clauses check that
        # The pickup x position input is numeric
        pickupX = self.pickupXPosValue.get()
        pickupY = self.pickupYPosValue.get()
        dropoffX = self.dropoffXPosValue.get()
        dropoffY = self.dropoffYPosValue.get()
        # print(f"Validate task with: ({pickupX}, {pickupY}) and ({dropoffX}, {dropoffY})")
        if not pickupX.isnumeric():
            # print("PICKUPX IS NOT NUMERIC")
            # Else it is invalid
            self.validTaskLocations = False
            self.updateTaskCreationButton()
            return
        # The pickup y position input is numeric
        if not pickupY.isnumeric():
            # print("PICKUPY IS NOT NUMERIC")
            # Else it is invalid
            self.validTaskLocations = False
            self.updateTaskCreationButton()
            return
        # The dropoff x position input is numeric
        if not dropoffX.isnumeric():
            # print("DROPOFFX IS NOT NUMERIC")
            # Else it is invalid
            self.validTaskLocations = False
            self.updateTaskCreationButton()
            return
        # The dropoff y position input is numeric
        if not dropoffY.isnumeric():
            # print("DROPOFFY IS NOT NUMERIC")
            # Else it is invalid
            self.validTaskLocations = False
            self.updateTaskCreationButton()
            return
        # The pickup location must belong to the graph
        if not self.tileInGraphValidation(pickupX, pickupY):
            # print("PICKUP NODE NOT WITHIN GRAPH")
            # Else it is invalid
            self.validTaskLocations = False
            self.updateTaskCreationButton()
            return
        # The dropoff location must belong to the graph
        if not self.tileInGraphValidation(dropoffX, dropoffY):
            # print("DROPOFF NODE NOT WITHIN GRAPH")
            # Else it is invalid
            self.validTaskLocations = False
            self.updateTaskCreationButton()
            return
        # Pickups and dropoffs can overlap in this case, awkward to handle though, revisit
        # If all guard clauses are passed, enable the create task button
        self.validTaskLocations = True
        print("valid task location")
        # Check that all other enabling conditions are met
        self.updateTaskCreationButton()

    def updateTaskCreationButton(self):
        # Change the status of the create task button based on entry validity
        # Input validation is already handled at this point
        if self.taskNameValid and self.validTaskLocations and self.validTaskTimeLimit:
            self.createTaskButton.config(state=tk.NORMAL)
        else:
            # print(f"Task Name Valid: {self.taskNameValid}")
            # print(f"Task Location Valid: {self.validTaskLocations}")
            # print(f"Task Time Limit Valid: {self.validTaskTimeLimit}")
            self.createTaskButton.config(state=tk.DISABLED)

    def createTask(self):
        print("Create task")
        # Remove previous highlights
        self.mainView.mainCanvas.clearHighlight()
        # Create the task, place it
        pickupXPos = eval(self.pickupXPosValue.get())
        pickupYPos = eval(self.pickupYPosValue.get())
        pickupNode = (pickupXPos, pickupYPos)
        dropoffXPos = eval(self.dropoffXPosValue.get())
        dropoffYPos = eval(self.dropoffYPosValue.get())
        dropoffNode = (dropoffXPos, dropoffYPos)
        timeLimit = eval(self.timeLimitValue.get())
        taskName = self.taskNameValue.get()
        self.taskManager.createNewTask(
            taskName = taskName,
            pickupPosition = pickupNode,
            dropoffPosition = dropoffNode,
            timeLimit = timeLimit
        )
        # Re-render the map state
        self.mainView.mainCanvas.renderGraphState()
        # Close the task generator
        self.taskCreationPrompt()

