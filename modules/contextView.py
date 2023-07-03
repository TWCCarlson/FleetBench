import tkinter as tk
from tkinter import ttk
import pprint
pp = pprint.PrettyPrinter(indent=4)
# import networkx as nx
# import matplotlib.pyplot as plt

class contextView(tk.Frame):
    """
        The containing frame for the right-side panel
        Will include manual agent movement, a list of agents, tasks, and ways to view agent decisionmaking
    """
    def __init__(self, parent):
        # Fetch styling
        self.parent = parent
        self.appearanceValues = self.parent.appearance
        frameHeight = self.appearanceValues.contextViewHeight
        frameWidth = self.appearanceValues.contextViewWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief
        # Declare frame
        tk.Frame.__init__(self, parent, height=frameHeight, 
            width=frameWidth, 
            borderwidth=frameBorderWidth, 
            relief=frameRelief)

        # Render frame
        self.grid_propagate(False)
        self.grid(row=0, column=2, rowspan=2, sticky=tk.N)

        # Create the simulation information and configuration access pane
        self.createSimulationInformationInterface()

        # Create Manual Movement Interface
        self.createMovementInterface()

        # Create treeView
        self.createTreeViewNotebook()
        # self.createTreeView()
        # self.initScrolling()

        # Configure the Context View Frame column and row weights for spacing elements
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Saveable data
        self.contextViewState = contextViewState(self)

    def tempFunc(self):
        pp.pprint(self.parent.mapData.mapGraph.nodes(data=True))
        pp.pprint(self.parent.mapData.mapGraph.edges(data=True))
        pp.pprint(self.parent.agentManager.agentList)
        pp.pprint(self.parent.taskManager.taskList)
        self.parent.mapData.packageMapData()

    def createTreeViewNotebook(self):
        """
            Creates a Tkinter notebook to which treeview tabs will be added
            "Agents" 
            "Tasks" 
            "Statistics"
        """
        # Create the notebook object
        self.objectListNotebook = ttk.Notebook(self)
        self.objectListNotebook.grid(row=2, column=0, sticky=tk.S+tk.W+tk.E)
        self.rowconfigure(2, weight=1)

        # Create the "Agents" tab using a Frame and then generating its treeView
        self.agentListFrame = tk.Frame(self.objectListNotebook)
        self.createAgentTreeView()

        # Create the "Tasks" tab using a Frame and then generating its treeView
        self.taskListFrame = tk.Frame(self.objectListNotebook)
        self.createTaskTreeView()

        self.statsListFrame = tk.Frame(self.objectListNotebook)
        self.objectListNotebook.add(self.agentListFrame, text="Agents", sticky=tk.W+tk.E)
        self.objectListNotebook.add(self.taskListFrame, text="Tasks")
        self.objectListNotebook.add(self.statsListFrame, text="Statistics")

    def createAgentTreeView(self):
        self.columnList = {'Name': 50, 'Position': 50, 'Class': 50, 'Task': 40}
        self.agentTreeView = ttk.Treeview(self.agentListFrame, selectmode='browse')
        self.agentTreeView.grid(row=0, column=0, sticky=tk.S+tk.W+tk.E)
        self.agentTreeView["height"] = 20
        self.agentTreeView["columns"] = list(self.columnList.keys())
        self.agentListFrame.columnconfigure(0, weight=1)

        self.agentTreeView.heading('#0', text='A') # Activity status icon column
        self.agentTreeView.column('#0', width=35, stretch=0)
        for col in self.columnList:
            self.agentTreeView.heading(col, text=col)
            self.agentTreeView.column(col, width=self.columnList[col], stretch=True)

        # Event bindings
        self.agentTreeView.bind('<Motion>', 'break') # Prevents resizing
        self.agentListFrame.bind('<Enter>', self.bindAgentClicks)
        self.agentListFrame.bind('<Leave>', self.unbindAgentClicks)

        # Initialize scrolling
        self.initAgentTreeScrolling()
        
    def initAgentTreeScrolling(self):
        # Create scrollbar components
        self.agentTreeView.ybar = tk.Scrollbar(self.agentListFrame, orient="vertical")
        self.agentTreeView.xbar = tk.Scrollbar(self.agentListFrame, orient="horizontal")

        # Bind the scrollbars to the canvas
        self.agentTreeView.ybar["command"] = self.agentTreeView.yview
        self.agentTreeView.xbar["command"] = self.agentTreeView.xview

        # Adjust positioning, size relative to grid
        self.agentTreeView.ybar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.agentTreeView.xbar.grid(row=1, column=0, sticky=tk.E+tk.W)

        # Make canvas update scrollbar position to match its view
        self.agentTreeView["yscrollcommand"] = self.agentTreeView.ybar.set
        self.agentTreeView["xscrollcommand"] = self.agentTreeView.xbar.set

        # Bind mousewheel to interact with the scrollbars
        # Only do this when the cursor is inside this frame
        self.agentTreeView.bind('<Enter>', self.bindMousewheel)
        self.agentTreeView.bind('<Leave>', self.unbindMousewheel)

        # Reset the view
        self.agentTreeView.xview_moveto("0.0")
        self.agentTreeView.yview_moveto("0.0")
        
    def updateAgentTreeView(self):
        # Clear the treeview then regenerate it
        for row in self.agentTreeView.get_children():
            self.agentTreeView.delete(row)

        # Access the list of all agents and rebuild the treeView based on their states
        for agent in self.parent.agentManager.agentList:
            agentData = self.parent.agentManager.agentList.get(agent)
            agentNumID = agentData.numID
            agentID = agentData.ID
            agentPosition = str(agentData.position)
            agentClass = agentData.className
            self.agentTreeView.insert(parent="",
                index='end',
                iid=agentID,
                text=f"A{str(agentNumID)}",
                values=[agentID, agentPosition, agentClass],
                tags=["agent", agentNumID, agentID]
            )

    def bindAgentClicks(self, *event):
        self.agentClickBindFunc = self.agentTreeView.bind('<<TreeviewSelect>>', self.handleAgentSelect)

    def unbindAgentClicks(self, *event):
        self.agentTreeView.unbind('<<TreeviewSelect>>', self.agentClickBindFunc)

    def handleAgentSelect(self, event):
        # Identify the selected row
        selectedRow = self.agentTreeView.focus()
        if selectedRow in self.agentTreeView.tag_has("agent"):
            # Clear existing highlights
            self.parent.mainView.mainCanvas.clearHighlight()
            rowData = self.agentTreeView.item(selectedRow)
            # Hightlight the selected agent
            agentID = rowData["tags"][1]
            self.parent.agentManager.agentList.get(agentID).highlightAgent(multi=False)
            # Update agentManager's currentAgent prop
            self.parent.agentManager.currentAgent = agentID
            print(self.parent.agentManager.currentAgent)
            # Trigger movement button state validation
            self.validateMovementButtonStates()

    def createTaskTreeView(self):
        self.columnList = {'Name': 50, 'Pickup': 50, 'Dropoff': 50, 'Time Limit': 40}
        self.taskTreeView = ttk.Treeview(self.taskListFrame, selectmode='browse')
        self.taskTreeView.grid(row=0, column=0, sticky=tk.S+tk.W+tk.E)
        self.taskTreeView["height"] = 20
        self.taskTreeView["columns"] = list(self.columnList.keys())
        self.taskListFrame.columnconfigure(0, weight=1)

        self.taskTreeView.heading('#0', text='A')
        self.taskTreeView.column('#0', width=35, stretch=0)
        for col in self.columnList:
            self.taskTreeView.heading(col, text=col)
            self.taskTreeView.column(col, width=self.columnList[col], stretch=True)

        # Event bindings
        self.taskTreeView.bind('<Motion>', 'break') # Prevents resizing
        self.taskTreeView.bind('<Enter>', self.bindTaskClicks)
        self.taskTreeView.bind('<Leave>', self.unbindTaskClicks)

        # Initialize scrolling
        self.initTaskTreeScrolling()

    def initTaskTreeScrolling(self):
        # Create scrollbar components
        self.taskTreeView.ybar = tk.Scrollbar(self.taskListFrame, orient="vertical")
        self.taskTreeView.xbar = tk.Scrollbar(self.taskListFrame, orient="horizontal")

        # Bind the scrollbars to the canvas
        self.taskTreeView.ybar["command"] = self.taskTreeView.yview
        self.taskTreeView.xbar["command"] = self.taskTreeView.xview

        # Adjust positioning, size relative to grid
        self.taskTreeView.ybar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.taskTreeView.xbar.grid(row=1, column=0, sticky=tk.E+tk.W)

        # Make canvas update scrollbar position to match its view
        self.taskTreeView["yscrollcommand"] = self.taskTreeView.ybar.set
        self.taskTreeView["xscrollcommand"] = self.taskTreeView.xbar.set

        # Bind mousewheel to interact with the scrollbars
        # Only do this when the cursor is inside this frame
        self.taskListFrame.bind('<Enter>', self.bindMousewheel)
        self.taskListFrame.bind('<Leave>', self.unbindMousewheel)

        # Reset the view
        self.taskTreeView.xview_moveto("0.0")
        self.taskTreeView.yview_moveto("0.0")

    def updateTaskTreeView(self):
        # Clear the treeview then regenerate it
        for row in self.taskTreeView.get_children():
            self.taskTreeView.delete(row)

        # Access the list of all tasks and rebuild the treeView based on their states
        for task in self.parent.taskManager.taskList:
            taskData = self.parent.taskManager.taskList.get(task)
            taskNumID = taskData.numID
            taskName = taskData.name
            taskPickupPosition = taskData.pickupNode
            taskDropoffPosition = taskData.dropoffNode
            taskTimeLimit = taskData.timeLimit
            self.taskTreeView.insert(parent="",
                index='end',
                iid=taskNumID,
                text=f"T{str(taskNumID)}",
                values=[taskName, taskPickupPosition, taskDropoffPosition, taskTimeLimit],
                tags=["task", taskNumID, taskName]
            )

    def bindTaskClicks(self, *event):
        self.taskClickBindFunc = self.taskTreeView.bind('<<TreeviewSelect>>', self.handleTaskSelect)

    def unbindTaskClicks(self, *event):
        self.taskTreeView.unbind('<<TreeviewSelect>>', self.taskClickBindFunc)

    def handleTaskSelect(self, event):
        # Identify the selected row
        selectedRow = self.taskTreeView.focus()
        if selectedRow in self.taskTreeView.tag_has("task"):
            # Clear existing highlights
            self.parent.mainView.mainCanvas.clearHighlight()
            rowData = self.taskTreeView.item(selectedRow)
            # Hightlight the selected tasks's pickup and dropoff points
            taskID = rowData["tags"][1]
            self.parent.taskManager.taskList.get(taskID).highlightTask(False)
            # Update taskManager's currentTask prop
            self.parent.taskManager.currentTask = taskID
            print(self.parent.taskManager.currentTask)

    def createTreeView(self):
        self.columnList = {'Name': 50, 'Position': 50, 'Class': 50, 'Task': 40}
        # Tree view is a stupid fucking widget
        # https://stackoverflow.com/questions/39609865/how-to-set-width-of-treeview-in-tkinter-of-python
        # Create it once, with a single column of nonzero width but all other columns declared, to set the width ???????
        # Then update the object to lock in the requested space
        # Finally reup with everything actually used
        treeViewWidth = self.appearanceValues.contextViewWidth - self.appearanceValues.frameBorderWidth*2 - 21
        self.objectTreeView = ttk.Treeview(self, selectmode='browse')
        self.objectTreeView.grid(row=2, column=0, sticky=tk.S+tk.W+tk.E)
        self.objectTreeView["height"] = 20
        self.objectTreeView["columns"] = list(self.columnList.keys()) # list() must be used for this widget
        # self.objectTreeView.column('#0', width=int(treeViewWidth))
        # Set other columns to be zero-width for simplicity
        # for col in self.columnList:
        #     self.objectTreeView.column(col, width=0)
        self.objectTreeView.update()

        # Set the real column dimensions
        self.objectTreeView.heading('#0', text='im')
        self.objectTreeView.column('#0', width=62, stretch=0)
        # Stretch=True can be used to fill the available space evenly using every column that can stretch
        for col in self.columnList:
            self.objectTreeView.heading(col, text=col)
            self.objectTreeView.column(col, width=self.columnList[col], stretch=True)

        # Insert parent rows
        self.objectTreeView.insert(parent="",
            index=0,
            iid='agentParentRow',
            open=False,
            tags=['agentParentRow'],
            text="Agents"
        )

        # Prevent column resizing:
        # https://stackoverflow.com/questions/45358408/how-to-disable-manual-resizing-of-tkinters-treeview-column/46120502#46120502
        self.objectTreeView.bind('<Button-1>', self.handleClick)
        self.objectTreeView.bind('<Motion>', self.motionIntercept)
        # This event captures too much
        # self.objectTreeView.bind('<<TreeviewSelect>>', self.handleSelect)

    def initScrolling(self):
        # Create scrollbar components
        self.objectTreeView.ybar = tk.Scrollbar(self, orient="vertical")
        self.objectTreeView.xbar = tk.Scrollbar(self, orient="horizontal")

        # Bind the scrollbars to the canvas
        self.objectTreeView.ybar["command"] = self.objectTreeView.yview
        self.objectTreeView.xbar["command"] = self.objectTreeView.xview

        # Adjust positioning, size relative to grid
        self.objectTreeView.ybar.grid(row=2, column=1, sticky="ns")
        self.objectTreeView.xbar.grid(row=3, column=0, sticky="ew")

        # Make canvas update scrollbar position to match its view
        self.objectTreeView["yscrollcommand"] = self.objectTreeView.ybar.set
        self.objectTreeView["xscrollcommand"] = self.objectTreeView.xbar.set

        # Bind mousewheel to interact with the scrollbars
        # Only do this when the cursor is inside this frame
        self.objectTreeView.bind('<Enter>', self.bindMousewheel)
        self.objectTreeView.bind('<Leave>', self.unbindMousewheel)

        # Reset the view
        self.objectTreeView.xview_moveto("0.0")
        self.objectTreeView.yview_moveto("0.0")

    def bindMousewheel(self, event):
        self.bind_all("<MouseWheel>", self.mousewheelAction)
        self.bind_all("<Shift-MouseWheel>", self.shiftMousewheelAction)

    def unbindMousewheel(self, event):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Shift-MouseWheel>")

    def mousewheelAction(self, event):
        self.objectTreeView.yview_scroll(int(-1*(event.delta/10)), "units")

    def shiftMousewheelAction(self, event):
        self.objectTreeView.xview_scroll(int(-1*(event.delta/10)), "units")

    def motionIntercept(self, event):
        if self.objectTreeView.identify_region(event.x, event.y) == "separator":
            # Prevent click interacting with this region
            return "break"

    def updateTreeView(self):
        # Clear the treeview to regenerate it
        # Only remove children of the parent rows
        parentRows = self.objectTreeView.get_children()
        rows = self.objectTreeView.get_children(parentRows)
        for row in rows:
            self.objectTreeView.delete(row)

        # Grabs the list of all agents from the agent manager and generates treeview entries based on their states
        self.treeViewAgentList = self.parent.agentManager.agentList
        for agent in self.treeViewAgentList:
            # Extract relevant data
            agentData = self.treeViewAgentList.get(agent)
            agentNumID = agentData.numID
            agentID = agentData.ID
            agentPosition = str(agentData.position)
            agentClass = agentData.className
            self.objectTreeView.insert(parent="agentParentRow",
                index='end',
                iid=agentID,
                text='A'+str(agentNumID),
                values=[agentID, agentPosition, agentClass],
                tags=["agent", agentNumID, agentID]
            )

    def handleClick(self, event):
        # Header clicks:
        if self.objectTreeView.identify_region(event.x, event.y) == "separator":
            # Prevent click interacting with this region
            return
        else:
            self.handleSelect(event)

    def handleSelect(self, event):
        # Identify the row clicked on
        selectedRow = self.objectTreeView.focus()
        # If the row describes a category
        if selectedRow in self.objectTreeView.tag_has("agentParentRow"):
            # parentRow = self.objectTreeView.item(selectedRow)
            rowChildren = self.objectTreeView.get_children(selectedRow)
            # Highlight all agents
            for row in rowChildren:
                rowData = self.objectTreeView.item(row)
                # Clear existing highlights
                self.parent.mainView.mainCanvas.clearHighlight()
                # Highlight the selected agent
                agentID = rowData["tags"][1]
                agentRef = self.parent.agentManager.agentList.get(agentID)
                agentRef.highlightAgent(multi=True)
                # Update the selection
                self.parent.agentManager.currentAgent = agentID
                print(self.parent.agentManager.currentAgent)
                # Update movement choices for the selected agent
                self.validateMovementButtonStates()

        # If the row describes an agent
        if selectedRow in self.objectTreeView.tag_has("agent"):
            # Clear existing highlights
            self.parent.mainView.mainCanvas.clearHighlight()
            rowData = self.objectTreeView.item(selectedRow)
            # Highlight the selected agent
            agentID = rowData["tags"][1]
            agentRef = self.parent.agentManager.agentList.get(agentID)
            agentRef.highlightAgent(multi=False)
            # Update the selection
            self.parent.agentManager.currentAgent = agentID
            print(self.parent.agentManager.currentAgent)
            # Update movement choices for the selected agent
            self.validateMovementButtonStates()

    def createMovementInterface(self):
        self.movementFrame = tk.LabelFrame(self, text="Manual Movement")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.movementFrame.grid(row=1, column=0, sticky=tk.E+tk.W, padx=4, columnspan=2)
        self.movementFrame.columnconfigure(0, weight=1)
        # self.movementFrame.columnconfigure(1, weight=1)
        self.movementFrame.columnconfigure(2, weight=1)

        ## Movement buttons
        # These should probably not be hotkeyed — its an extra state to manage without much benefit. 
        # Most movement is algorithmic, not manual, a few clicks won't be a significant problem
        # Cardinal movement
        self.moveUp = tk.Button(self.movementFrame, text="⬆\nN", width=10, height=4, relief=tk.GROOVE, borderwidth=6,
            command=self.moveAgentUp)
        self.moveUp.grid(row=0, column=1, pady=4, padx=4, columnspan=1, sticky=tk.S)
        self.moveLeft = tk.Button(self.movementFrame, text="⬅ W", width=10, height=4, relief=tk.GROOVE, borderwidth=6,
            command=self.moveAgentLeft)
        self.moveLeft.grid(row=1, column=0, pady=4, padx=4, columnspan=1, sticky=tk.E)
        self.moveRight = tk.Button(self.movementFrame, text="E ➡", width=10, height=4, relief=tk.GROOVE, borderwidth=6,
            command=self.moveAgentRight)
        self.moveRight.grid(row=1, column=2, pady=4, padx=4, columnspan=1, sticky=tk.W)
        self.moveDown = tk.Button(self.movementFrame, text="S\n⬇", width=10, height=4, relief=tk.GROOVE, borderwidth=6,
            command=self.moveAgentDown)
        self.moveDown.grid(row=2, column=1, pady=4, padx=4, columnspan=1, sticky=tk.N)
        # Rotational movement
        self.rotateCW = tk.Button(self.movementFrame, text="CW", width=8, height=3, relief=tk.GROOVE, borderwidth=6,
            command=self.rotateAgentCW)
        self.rotateCW.grid(row=0, column=0, pady=4, padx=4, columnspan=1, sticky=tk.SE)
        self.rotateCCW = tk.Button(self.movementFrame, text="CCW", width=8, height=3, relief=tk.GROOVE, borderwidth=6,
            command=self.rotateAgentCCW)
        self.rotateCCW.grid(row=0, column=2, pady=4, padx=4, columnspan=1, sticky=tk.SW)
        # Meta controls
        self.pause = tk.Button(self.movementFrame, text="Pause", width=8, height=3, relief=tk.GROOVE, borderwidth=6,
            command=self.pauseAgent, background='yellow')
        self.pause.grid(row=2, column=0, pady=4, padx=4, columnspan=1, sticky=tk.SW)
        self.delete = tk.Button(self.movementFrame, text="Del", width=8, height=3, relief=tk.GROOVE, borderwidth=6,
            command=self.deleteAgent, background='red')
        self.delete.grid(row=2, column=2, pady=4, padx=4, columnspan=1, sticky=tk.SE)

    def validateMovementButtonStates(self):
        # Retrieve the current agent's object
        agentID = self.parent.agentManager.currentAgent
        agentRef = self.parent.agentManager.agentList.get(agentID)

        # Extract the agent's postion
        agentPosition = agentRef.position

        # Check whether edges exist in the cardinal directions from the agent's current tile to the next
        candidateNodeDict = {
            "N": f"({agentPosition[0]}, {agentPosition[1]-1})",
            "W": f"({agentPosition[0]-1}, {agentPosition[1]})",
            "E": f"({agentPosition[0]+1}, {agentPosition[1]})",
            "S": f"({agentPosition[0]}, {agentPosition[1]+1})" 
        }

        # Check if an edge exists to the north
        if self.parent.mapData.mapGraph.has_edge(str(agentPosition), candidateNodeDict["N"]) and not 'agent' in self.parent.mapData.mapGraph.nodes[candidateNodeDict["N"]]:
            self.moveUp.config(state=tk.NORMAL, background='#4ddb67')
        else:
            self.moveUp.config(state=tk.DISABLED, background='#fc7f03')

        # Check if an edge exists to the south
        if self.parent.mapData.mapGraph.has_edge(str(agentPosition), candidateNodeDict["S"]) and not 'agent' in self.parent.mapData.mapGraph.nodes[candidateNodeDict["S"]]:
            self.moveDown.config(state=tk.NORMAL, background='#4ddb67')
        else:
            self.moveDown.config(state=tk.DISABLED, background='#fc7f03')

        # Check if an edge exists to west
        if self.parent.mapData.mapGraph.has_edge(str(agentPosition), candidateNodeDict["W"]) and not 'agent' in self.parent.mapData.mapGraph.nodes[candidateNodeDict["W"]]:
            self.moveLeft.config(state=tk.NORMAL, background='#4ddb67')
        else:
            self.moveLeft.config(state=tk.DISABLED, background='#fc7f03')

        # Check if an edge exists to the left
        if self.parent.mapData.mapGraph.has_edge(str(agentPosition), candidateNodeDict["E"]) and not 'agent' in self.parent.mapData.mapGraph.nodes[candidateNodeDict["E"]]:
            self.moveRight.config(state=tk.NORMAL, background='#4ddb67')
        else:
            self.moveRight.config(state=tk.DISABLED, background='#fc7f03')

    def moveAgentUp(self):
        # Retrieve the current agent's object
        agentID = self.parent.agentManager.currentAgent
        agentRef = self.parent.agentManager.agentList.get(agentID)
        # Call movement method
        agentRef.moveUp()

    def moveAgentLeft(self):
        # Retrieve the current agent's object
        agentID = self.parent.agentManager.currentAgent
        agentRef = self.parent.agentManager.agentList.get(agentID)
        # Call movement method
        agentRef.moveLeft()

    def moveAgentRight(self):
        # Retrieve the current agent's object
        agentID = self.parent.agentManager.currentAgent
        agentRef = self.parent.agentManager.agentList.get(agentID)
        # Call movement method
        agentRef.moveRight()

    def moveAgentDown(self):
        # Retrieve the current agent's object
        agentID = self.parent.agentManager.currentAgent
        agentRef = self.parent.agentManager.agentList.get(agentID)
        # Call movement method
        agentRef.moveDown()

    def rotateAgentCW(self):
        # Retrieve the current agent's object
        agentID = self.parent.agentManager.currentAgent
        agentRef = self.parent.agentManager.agentList.get(agentID)
        # Call movement method
        agentRef.rotateCW()

    def rotateAgentCCW(self):
        # Retrieve the current agent's object
        agentID = self.parent.agentManager.currentAgent
        agentRef = self.parent.agentManager.agentList.get(agentID)
        # Call movement method
        agentRef.rotateCCW()

    def pauseAgent(self):
        print("Agent paused")

    def deleteAgent(self):
        print("Agent deleted")

    def createSimulationInformationInterface(self):
        self.contextLabelFrame = tk.LabelFrame(self, text="Simulation Information")
        self.contextLabelFrame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W, padx=4, columnspan=2)
        self.configureSimulationButton = tk.Button(self.contextLabelFrame, text="Simulation Details", width=20,  command=self.openSimulationInformationWindow)
        self.contextLabelFrame.columnconfigure(0, weight=1)
        self.configureSimulationButton.grid(row=0, column=0, pady=4, padx=4, columnspan=1)

    def openSimulationInformationWindow(self):
        print("Simulation Info window opened!")

class contextViewState:
    """
        Containing class for state data used by the context view widgets, decoupled for pickling and saving
    """
    def __init__(self, parent):
        pass