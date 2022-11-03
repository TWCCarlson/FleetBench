import tkinter as tk
from tkinter import ttk

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
        self.entryYValue = tk.StringVar()
        self.entryXLabel = tk.Label(self.agentDataFrame, text="X Position: ", width=8)
        self.entryX = tk.Entry(self.agentDataFrame, width=10, textvariable=self.entryXValue)
        self.entryYLabel = tk.Label(self.agentDataFrame, text="Y Position: ", width=8)
        self.entryY = tk.Entry(self.agentDataFrame, width=10, textvariable=self.entryYValue)
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
            command = self.placeholder, 
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

    def placeholder(self):
        print(self.entryXValue.get() + ", " + self.entryYValue.get())
        self.agentCreationPrompt()

    def createAgent(self):
        print("Create agent")