import tkinter as tk
from tkinter import ttk
import networkx as nx

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

        # Default status
        self.agentNameValid = False
        self.validAgentCreationNode = False
        
        # Establish buttons and inputs
        self.initUI()

    def buildReferences(self):
        self.mainView = self.parent.mainView
        self.mapData = self.parent.mapData
        self.agentManager = self.parent.agentManager

    def initUI(self):
        print("Create toolbar ui elements")
        # Create a labeled container
        self.agentFrame = tk.LabelFrame(self, text="Agent Generator")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.agentFrame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W, padx=4, columnspan=2)

        self.agentCreationPrompt()

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
            self.createAgentButton.config(state=tk.ACTIVE)

    def enableAgentCreation(self):
        self.createAgentButton.config(state=tk.ACTIVE)

    def agentCreationUI(self):
        # Clear what's already in the frame to make space
        self.clearAgentCreationUI()

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
        self.entryXValue = tk.StringVar()
        self.entryXLabel = tk.Label(self.agentDataFrame, text="X Position: ", width=8)
        self.highlightXPos = self.register(self.highlightTargetXPos) # Function wrapper for callback on entry update
        self.entryX = ttk.Spinbox(self.agentDataFrame, 
            width=6,
            from_=0,
            to=self.mapData.dimensionX,
            increment=1,
            textvariable=self.entryXValue,
            command=self.highlightTargetXPos,
            validate='key',
            validatecommand=(self.highlightXPos, '%P')
            )
        self.entryYValue = tk.StringVar()
        self.entryYLabel = tk.Label(self.agentDataFrame, text="Y Position: ", width=8)
        self.highlightYPos = self.register(self.highlightTargetYPos) # Function wrapper for callback on entry update
        self.entryY = ttk.Spinbox(self.agentDataFrame, 
            width=6,
            from_=0,
            increment=1,
            to=self.mapData.dimensionY,
            textvariable=self.entryYValue,
            command=self.highlightTargetYPos,
            validate='key',
            validatecommand=(self.highlightYPos, '%P')
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
        self.agentOrientationN.select()
        self.agentOrientationW = tk.Radiobutton(self.agentOrientationFrame, text="W", variable=self.agentOrientation, value="W")
        self.agentOrientationS = tk.Radiobutton(self.agentOrientationFrame, text="S", variable=self.agentOrientation, value="S")
        self.agentOrientationE = tk.Radiobutton(self.agentOrientationFrame, text="E", variable=self.agentOrientation, value="E")

        # Render
        self.entryXLabel.grid(row=1, column=0, sticky=tk.E)
        self.entryYLabel.grid(row=2, column=0, sticky=tk.E)
        self.entryX.grid(row=1, column=1)
        self.entryY.grid(row=2, column=1)
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

    def highlightTargetXPos(self, *args):
        if args:
            xPos = args[0]
        else:
            xPos = self.entryX.get()
        # Verify that the input is correct
        if xPos.isnumeric():
            # If the value is a number, then we need to:
            # Highlight the value if the Y value is also a number
            self.highlightTargetTile(xPos, None)
            # Check the node exists on the graph to enable the creation button

            # Check that all other enabling conditions are met
            self.updateAgentCreationButton()

            # Numbers are allowed
            return True
        elif len(xPos) == 0:
            # Allow the box to be empty
            return True
        else:
            # Nothing else is allowed
            return False

    def highlightTargetYPos(self, *args):
        if args:
            yPos = args[0]
        else:
            yPos = self.entryY.get()
        # Verify that the input is correct
        if yPos.isnumeric():
            # If the value is a number, then we need to:
            # Highlight the value if the Y value is also a number
            # And check the node exists on the graph to enable the creation button
            self.highlightTargetTile(None, yPos)
            
            # Check that all other enabling conditions are met
            self.updateAgentCreationButton()

            # Numbers are allowed
            return True
        elif len(yPos) == 0:
            # Emptying the box is allowed
            return True
        else:
            # Anything else is not allowed 
            return False

    def highlightTargetTile(self, xPos, yPos):
        # If an input is Nonetype, fetch it from its entry variable
        if xPos == None:
            xPos = self.entryXValue.get()
        elif yPos == None:
            yPos = self.entryYValue.get()

        # Using guard clauses, check that
        # The x input is numeric
        if not xPos.isnumeric():
            # Else it is invalid
            self.validAgentCreationNode = False
            self.mainView.mainCanvas.clearHighlight()
            return
        # The y input is numeric
        if not yPos.isnumeric():
            # Else it is invalid
            self.validAgentCreationNode = False
            self.mainView.mainCanvas.clearHighlight()
            return
        # Check that it belongs to the graph
        if not self.tileInGraphValidation(xPos, yPos):
            # This can still be highlited as a guide to the user
            self.mainView.mainCanvas.highlightTile(xPos, yPos, 'red', multi=False)
            self.validAgentCreationNode = False
            return
        # And that the tile does not already contain an agent
        # print(self.mapData.mapGraph.nodes.data()[f"({eval(xPos)}, {eval(yPos)})"])
        if 'agent' in self.mapData.mapGraph.nodes.data()[f"({eval(xPos)}, {eval(yPos)})"]:
            # Else it is invalid    
            # print("AGENT EXISTS IN THIS TILE ALREADY")
            self.validAgentCreationNode = False
            return
        # If all guard clauses are passed, highlight the tile
        self.mainView.mainCanvas.highlightTile(xPos, yPos, 'red', multi=False)
        # Enable the button based on graph belongingness
        self.validAgentCreationNode = True

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
            self.confirmCreateAgentButton.config(state=tk.ACTIVE)
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
        xPos = eval(self.entryXValue.get())
        yPos = eval(self.entryYValue.get())
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