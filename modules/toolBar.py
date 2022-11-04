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
        self.createAgentButton = tk.Button(self.agentFrame, command=self.agentCreationUI, text="Create Agent. . .", width=15)
        self.agentFrame.columnconfigure(0, weight=1)
        self.createAgentButton.grid(row=0, column=0, pady=4, padx=4, columnspan=2)

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
        self.entryX = tk.Entry(self.agentDataFrame, 
            width=10, 
            textvariable=self.entryXValue,
            validate='key',
            validatecommand=(self.highlightXPos, '%P')
            )
        self.entryYValue = tk.StringVar()
        self.entryYLabel = tk.Label(self.agentDataFrame, text="Y Position: ", width=8)
        self.highlightYPos = self.register(self.highlightTargetYPos) # Function wrapper for callback on entry update
        self.entryY = tk.Entry(self.agentDataFrame, 
            width=10, 
            textvariable=self.entryYValue,
            validate='key',
            validatecommand=(self.highlightYPos, '%P')
            )
        # Render
        self.entryXLabel.grid(row=1, column=0, sticky=tk.E)
        self.entryYLabel.grid(row=2, column=0, sticky=tk.E)
        self.entryX.grid(row=1, column=1)
        self.entryY.grid(row=2, column=1)

        # Separator
        self.sep1 = ttk.Separator(self.agentDataFrame, orient='vertical')
        self.sep1.grid(row=0, column=2, rowspan=3, sticky=tk.N+tk.S+tk.W, pady=4, padx=4)

        # Save and edit buttons
        self.editAgentClassButton = tk.Button(self.agentFrame, 
            command=self.placeholder, 
            text="Edit Information",
            width=15,
            )
        self.placeAgentButton = tk.Button(self.agentFrame, 
            command = self.createAgent, 
            text="Create Agent",
            width=15,
            )
        self.editAgentClassButton.grid(row=2, column=0, sticky=tk.E, pady=4)
        self.placeAgentButton.grid(row=2, column=1, sticky=tk.W, pady=4)

    def clearAgentCreationUI(self):
        for widget in self.agentFrame.winfo_children():
            widget.destroy()
        for row in range(self.agentFrame.grid_size()[0]):
            self.agentFrame.rowconfigure(row, weight=0)
        for col in range(self.agentFrame.grid_size()[1]):
            self.agentFrame.columnconfigure(col, weight=0)

    def highlightTargetXPos(self, xPos):
        # If input is a number, pass it to the highlight draw function
        if xPos.isnumeric():
            self.highlightTargetTile(xPos, None)
            return True
        elif len(xPos) == 0:
            # Allow the box to be empty
            return True
        else:
            return False

    def highlightTargetYPos(self, yPos):
        # If input is a number, pass it to the highlight draw function
        if yPos.isnumeric():
            self.highlightTargetTile(None, yPos)
            return True
        elif len(yPos) == 0:
            # Allow the box to be empty
            return True
        else:
            return False

    def highlightTargetTile(self, xPos, yPos):
        # If an input is Nonetype, fetch it from its entry variable
        if xPos == None:
            xPos = self.entryXValue.get()
        elif yPos == None:
            yPos = self.entryYValue.get()
        # If both inputs are numeric, try to render the cell highlight
        if xPos.isnumeric() and yPos.isnumeric():
            self.mainView.mainCanvas.highlightTile(xPos, yPos)
        else:
            self.mainView.mainCanvas.clearHighlight()

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
        agentOrientation = "N"
        self.agentManager.createNewAgent(
            position=targetNode, 
            orientation=agentOrientation, 
            className=self.agentClass.get()
            )
        # Re-render the map state
        self.mainView.mainCanvas.renderGraphState()
        # Close agent generator
        self.agentCreationPrompt()