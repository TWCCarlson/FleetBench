import tkinter as tk
from tkinter import ttk
import pprint
import modules.tk_extensions as tk_e
from sys import getsizeof
pp = pprint.PrettyPrinter(indent=4)
import logging
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
        logging.debug("Fetched styling settings.")
        # Declare frame
        tk.Frame.__init__(self, parent, height=frameHeight, 
            width=frameWidth, 
            borderwidth=frameBorderWidth, 
            relief=frameRelief)
        logging.debug("Containing frame settings built.")

        # Render frame
        self.grid_propagate(False)
        self.grid(row=0, column=2, rowspan=2, sticky=tk.N)
        logging.debug("Containing frame rendered.")

        # Create the simulation information and configuration access pane
        self.createSimulationInformationInterface()

        # Create Manual Movement Interface
        logging.info("Creating movement interface in contextView . . .")
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

        logging.info("Context View UI Class initialized.")

    def createTreeViewNotebook(self):
        """
            Creates a Tkinter notebook to which treeview tabs will be added
            "Agents" 
            "Tasks" 
            "Statistics"
        """
        logging.debug("Building notebook of treeView pages . . .")
        # Create the notebook object
        self.objectListNotebook = ttk.Notebook(self)
        self.objectListNotebook.grid(row=2, column=0, sticky=tk.S+tk.W+tk.E)
        self.rowconfigure(2, weight=1)
        logging.debug("Notebook rendered.")

        # Create the "Agents" tab using a Frame and then generating its treeView
        self.agentListFrame = tk.Frame(self.objectListNotebook)
        self.createAgentTreeView()

        # Create the "Tasks" tab using a Frame and then generating its treeView
        self.taskListFrame = tk.Frame(self.objectListNotebook)
        self.createTaskTreeView()

        self.statsListFrame = tk.Frame(self.objectListNotebook)
        self.objectListNotebook.add(self.agentListFrame, text="Agents")
        self.objectListNotebook.add(self.taskListFrame, text="Tasks")
        self.objectListNotebook.add(self.statsListFrame, text="Statistics")

        logging.info("All treeView pages added to notebook.")

    def createAgentTreeView(self):
        logging.debug("Creating agentTreeView page . . .")
        self.columnList = {'Name': 50, 'Position': 50, 'Class': 50, 'Task': 40}
        self.agentTreeView = ttk.Treeview(self.agentListFrame, selectmode='browse')
        self.agentTreeView.grid(row=0, column=0, sticky=tk.S+tk.W+tk.E)
        self.agentTreeView["height"] = 20
        self.agentTreeView["columns"] = list(self.columnList.keys())
        self.agentListFrame.columnconfigure(0, weight=1)
        logging.debug(f"Rendered treeView with columns: {self.columnList}")

        self.agentTreeView.heading('#0', text='A') # Activity status icon column
        self.agentTreeView.column('#0', width=35, stretch=0)
        for col in self.columnList:
            self.agentTreeView.heading(col, text=col)
            self.agentTreeView.column(col, width=self.columnList[col], stretch=True)
        logging.debug("Constructed all column configurations in agentTreeView.")

        # Event bindings
        self.agentTreeView.bind('<Motion>', 'break') # Prevents resizing
        self.agentListFrame.bind('<Enter>', self.bindAgentClicks)
        self.agentListFrame.bind('<Leave>', self.unbindAgentClicks)
        agentSelectVar = self.parent.mainView.mainCanvas.currentClickedAgent
        agentSelectVar.trace_add("write", lambda *args, agentSelected=agentSelectVar:
                self.selectAgent(agentSelectVar.get()))
        logging.debug("Bound mouse events to agentTreeView")

        # Initialize scrolling
        self.initAgentTreeScrolling()

        # Build right click context menu
        self.agentMenu = tk_e.agentTreeViewMenu(self)
        self.agentMenu.add_entry(label="Delete", command=self.parent.agentManager.deleteAgent)
        logging.debug("Built right click context-sensitive menu in the agentTreeView.")

        logging.info("agentTreeView finished rendering.")
        
    def initAgentTreeScrolling(self):
        logging.debug("Building scrolling capability in the agentTreeView.")
        # Create scrollbar components
        self.agentTreeView.ybar = tk.Scrollbar(self.agentListFrame, orient="vertical")
        self.agentTreeView.xbar = tk.Scrollbar(self.agentListFrame, orient="horizontal")
        logging.debug("Scrollbars instantiated in the agentTreeView.")

        # Bind the scrollbars to the canvas
        self.agentTreeView.ybar["command"] = self.agentTreeView.yview
        self.agentTreeView.xbar["command"] = self.agentTreeView.xview
        logging.debug("Scrollbars bound to agentTreeView.")

        # Adjust positioning, size relative to grid
        self.agentTreeView.ybar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.agentTreeView.xbar.grid(row=1, column=0, sticky=tk.E+tk.W)
        logging.debug("Scrollbars rendered into agentTreeView containing frame.")

        # Make canvas update scrollbar position to match its view
        self.agentTreeView["yscrollcommand"] = self.agentTreeView.ybar.set
        self.agentTreeView["xscrollcommand"] = self.agentTreeView.xbar.set
        logging.debug("Bound agentTreeView scroll commands to the scrollbars.")

        # Bind mousewheel to interact with the scrollbars
        # Only do this when the cursor is inside this frame
        self.agentTreeView.bind('<Enter>', self.bindMousewheel)
        self.agentTreeView.bind('<Leave>', self.unbindMousewheel)
        logging.debug("Bound mouse events to capture scrolling in the agentTreeView.")

        # Reset the view
        self.agentTreeView.xview_moveto("0.0")
        self.agentTreeView.yview_moveto("0.0")
        logging.debug("Set default agentTreeView scroll levels.")

        logging.info("Finished building agentTreeView scrolling.")
        
    def updateAgentTreeView(self):
        logging.debug("Received request to refresh the agentTreeView. . .")
        # Clear the treeview then regenerate it
        for row in self.agentTreeView.get_children():
            self.agentTreeView.delete(row)
        logging.debug("Cleared the agentTreeView.")

        # Access the list of all agents and rebuild the treeView based on their states
        for agent in self.parent.agentManager.agentList:
            agentData = self.parent.agentManager.agentList.get(agent)
            agentNumID = agentData.numID
            agentID = agentData.ID
            agentPosition = str(agentData.position)
            agentClass = agentData.className
            try:
                agentCurrentTask = agentData.currentTask.name
            except AttributeError:
                agentCurrentTask = None
            self.agentTreeView.insert(parent="",
                index='end',
                iid=agentID,
                text=f"A{str(agentNumID)}",
                values=[agentID, agentPosition, agentClass, agentCurrentTask],
                tags=["agent", agentNumID, agentID]
            )
            logging.debug(f"Add to agentTreeView: {self.agentTreeView.item(agentID, 'values')}")
        
        logging.info("Updated agentTreeView with current agentManager state.")

    def bindAgentClicks(self, *event):
        self.agentClickBindFunc = self.agentTreeView.bind('<Button-1>', self.handleAgentSelect)
        self.agentRClickBindFunc = self.agentTreeView.bind('<Button-3>', self.handleAgentRClick)

    def unbindAgentClicks(self, *event):
        self.agentTreeView.unbind('<Button-1>', self.agentClickBindFunc)
        self.agentTreeView.unbind('<Button-3>', self.agentRClickBindFunc)

    def updateCurrentAgent(self):
        agentName = self.parent.mainView.mainCanvas.currentClickedAgent.get()
        if agentName.isnumeric():
            agentName = int(agentName)
        self.currentAgent = self.parent.agentManager.agentDict[agentName]

    def setCurrentAgent(self, agentName):
        self.parent.mainView.mainCanvas.currentClickedAgent.set(agentName)

    def selectAgent(self, selectedAgentName):
        agentIID = self.agentTreeView.tag_has(selectedAgentName)
        self.agentTreeView.selection_set(agentIID)
        self.updateCurrentAgent()

    def handleAgentSelect(self, event):
        # Identify the selected row
        selectedRow = self.agentTreeView.identify_row(event.y)
        self.agentTreeView.selection_set(selectedRow)

        if selectedRow in self.agentTreeView.tag_has("agent"):
            # Clear existing highlights
            # self.parent.mainView.mainCanvas.clearHighlight()
            rowData = self.agentTreeView.item(selectedRow)
            # Hightlight the selected agent
            agentID = rowData["tags"][1]
            agentRef = self.parent.agentManager.agentList.get(agentID)
            agentRef.highlightAgent(multi=False)
            if agentRef.currentTask:
                agentRef.currentTask.highlightTask(multi=False)
            self.parent.mainView.mainCanvas.handleRenderQueue()

            # Update agentManager's currentAgent prop
            self.parent.agentManager.currentAgent = agentRef
            self.parent.toolBar.enableAgentManagement()
            logging.debug(f"User clicked on agent '{agentID}' in agentTreeView.")

            # Trigger movement button state validation
            self.setCurrentAgent(agentRef.ID) # Update context view's tracked agent for movement
            self.validateMovementButtonStates()

    def handleAgentRClick(self, event):
        # Give focus to the right clicked element
        logging.debug("User right clicked an agent in the agentTreeView.")
        self.handleAgentSelect(event)

        # Create the popup menu
        self.agentMenu.popup(event.x, event.y, event.x_root, event.y_root)

    def createTaskTreeView(self):
        logging.debug("Building taskTreeView page . . .")
        self.columnList = {'Name': 50, 'Pickup': 50, 'Dropoff': 50, 'Time Limit': 40}
        self.taskTreeView = ttk.Treeview(self.taskListFrame, selectmode='browse')
        self.taskTreeView.grid(row=0, column=0, sticky=tk.S+tk.W+tk.E)
        self.taskTreeView["height"] = 20
        self.taskTreeView["columns"] = list(self.columnList.keys())
        self.taskListFrame.columnconfigure(0, weight=1)
        logging.debug(f"Rendered treeview with columns: {self.columnList}")

        self.taskTreeView.heading('#0', text='A')
        self.taskTreeView.column('#0', width=35, stretch=0)
        for col in self.columnList:
            self.taskTreeView.heading(col, text=col)
            self.taskTreeView.column(col, width=self.columnList[col], stretch=True)
        logging.debug("Constructed all column configurations in taskTreeView.")

        # Event bindings
        self.taskTreeView.bind('<Motion>', 'break') # Prevents resizing
        self.taskTreeView.bind('<Enter>', self.bindTaskClicks)
        self.taskTreeView.bind('<Leave>', self.unbindTaskClicks)
        logging.debug("Bound mouse events to taskTreeView")

        # Initialize scrolling
        self.initTaskTreeScrolling()

        # Build right click context menu
        self.taskMenu = tk_e.taskTreeViewMenu(self)
        self.taskMenu.add_entry(label="Delete", command=self.parent.taskManager.deleteTask)
        logging.debug("Built right click context-sensitive menu in the taskTreeView.")

        logging.info("taskTreeView finished rendering.")

    def initTaskTreeScrolling(self):
        logging.debug("Building scrolling capability in the taskTreeView.")
        # Create scrollbar components
        self.taskTreeView.ybar = tk.Scrollbar(self.taskListFrame, orient="vertical")
        self.taskTreeView.xbar = tk.Scrollbar(self.taskListFrame, orient="horizontal")
        logging.debug("Scrollbars instantiated in the taskTreeView.")

        # Bind the scrollbars to the canvas
        self.taskTreeView.ybar["command"] = self.taskTreeView.yview
        self.taskTreeView.xbar["command"] = self.taskTreeView.xview
        logging.debug("Scrollbars bound to taskTreeView.")

        # Adjust positioning, size relative to grid
        self.taskTreeView.ybar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.taskTreeView.xbar.grid(row=1, column=0, sticky=tk.E+tk.W)
        logging.debug("Scrollbars rendered into taskTreeView containing frame.")

        # Make canvas update scrollbar position to match its view
        self.taskTreeView["yscrollcommand"] = self.taskTreeView.ybar.set
        self.taskTreeView["xscrollcommand"] = self.taskTreeView.xbar.set
        logging.debug("Bound taskTreeView scroll commands to the scrollbars.")

        # Bind mousewheel to interact with the scrollbars
        # Only do this when the cursor is inside this frame
        self.taskListFrame.bind('<Enter>', self.bindMousewheel)
        self.taskListFrame.bind('<Leave>', self.unbindMousewheel)
        logging.debug("Bound mouse events to capture scrolling in the taskTreeView.")

        # Reset the view
        self.taskTreeView.xview_moveto("0.0")
        self.taskTreeView.yview_moveto("0.0")
        logging.debug("Set default taskTreeView scroll levels.")

        logging.info("Finished building taskTreeView scrolling.")

    def updateTaskTreeView(self):
        logging.debug("Received request to refresh the taskTreeView . . .")
        # Clear the treeview then regenerate it
        for row in self.taskTreeView.get_children():
            self.taskTreeView.delete(row)
        logging.debug("Cleared the taskTreeView.")

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
            logging.debug(f"Add to taskTreeView: {self.taskTreeView.item(taskNumID, 'values')}")

        logging.info("Updated taskTreeView with current taskManager state.")

    def bindTaskClicks(self, *event):
        self.taskClickBindFunc = self.taskTreeView.bind('<Button-1>', self.handleTaskSelect)
        self.taskRClickBindFunc = self.taskTreeView.bind('<Button-3>', self.handleTaskRClick)

    def unbindTaskClicks(self, *event):
        self.taskTreeView.unbind('<Button-1>', self.taskClickBindFunc)
        self.taskTreeView.unbind('<Button-3>', self.taskRClickBindFunc)

    def handleTaskSelect(self, event):
        # Identify the selected row
        selectedRow = self.taskTreeView.identify_row(event.y)
        self.taskTreeView.selection_set(selectedRow)

        if selectedRow in self.taskTreeView.tag_has("task"):
            # Clear existing task highlights
            self.parent.mainView.mainCanvas.requestRender("highlight", "delete", {"highlightTag": "taskHighlight"})

            # Get task data for highlighting
            rowData = self.taskTreeView.item(selectedRow)
            taskID = rowData["tags"][1]
            taskRef = self.parent.taskManager.taskList.get(taskID)
            # Perform highlighting
            taskRef.highlightTask(multi=False)
            if taskRef.assignee:
                taskRef.assignee.highlightAgent(multi=False)
            else:
                self.parent.mainView.mainCanvas.requestRender("highlight", "delete", {"highlightTag": "agentHighlight"})
            self.parent.mainView.mainCanvas.handleRenderQueue()

            # Update taskManager's currentTask prop
            self.parent.taskManager.currentTask = taskRef
            self.parent.toolBar.enableTaskManagement()
            logging.debug(f"User clicked on task '{taskID}' in taskTreeView.")

    def handleTaskRClick(self, event):
        # Give focus to the right clicked element
        logging.debug("User right clicked a task in the taskTreeView.")
        self.handleTaskSelect(event)

        # Create the popup menu
        self.taskMenu.popup(event.x, event.y, event.x_root, event.y_root)

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

    def createMovementInterface(self):
        self.movementFrame = tk.LabelFrame(self, text="Manual Movement")
        logging.debug("Created movement interface containing frame.")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.movementFrame.grid(row=1, column=0, sticky=tk.E+tk.W, padx=4, columnspan=2)
        self.movementFrame.columnconfigure(0, weight=1)
        # self.movementFrame.columnconfigure(1, weight=1)
        self.movementFrame.columnconfigure(2, weight=1)
        logging.debug("Rendered movement interface containing frame.")

        # Event binding to check movement button validity upon agent selection
        agentSelectVar = self.parent.mainView.mainCanvas.currentClickedAgent
        agentSelectVar.trace_add("write", lambda *args: self.validateMovementButtonStates())

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
        self.rotateCW.grid(row=0, column=2, pady=4, padx=4, columnspan=1, sticky=tk.SW)
        self.rotateCCW = tk.Button(self.movementFrame, text="CCW", width=8, height=3, relief=tk.GROOVE, borderwidth=6,
            command=self.rotateAgentCCW)
        self.rotateCCW.grid(row=0, column=0, pady=4, padx=4, columnspan=1, sticky=tk.SE)
        # Meta controls
        self.pause = tk.Button(self.movementFrame, text="Pause", width=8, height=3, relief=tk.GROOVE, borderwidth=6,
            command=self.pauseAgent, background='yellow')
        self.pause.grid(row=2, column=0, pady=4, padx=4, columnspan=1, sticky=tk.SW)
        self.delete = tk.Button(self.movementFrame, text="Del", width=8, height=3, relief=tk.GROOVE, borderwidth=6,
            command=self.deleteAgent, background='red')
        self.delete.grid(row=2, column=2, pady=4, padx=4, columnspan=1, sticky=tk.SE)
        logging.info("Rendered all movement interface action buttons.")

    def validateMovementButtonStates(self):
        # Retrieve the current agent's object
        agentRef = self.currentAgent
        # agentRef = self.parent.agentManager.agentList.get(agentID)
        agentID = agentRef.ID

        # Extract the agent's postion
        agentPosition = agentRef.position
        logging.debug(f"Verify movement interface state for agent '{agentID}' in position {agentPosition}")

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
        logging.info("Validated all movement interface button states.")

    def moveAgentUp(self):
        self.currentAgent.moveUp()

    def moveAgentLeft(self):
        self.currentAgent.moveLeft()

    def moveAgentRight(self):
        self.currentAgent.moveRight()

    def moveAgentDown(self):
        self.currentAgent.moveDown()

    def rotateAgentCW(self):
        self.currentAgent.rotateCW()

    def rotateAgentCCW(self):
        self.currentAgent.rotateCCW()

    def pauseAgent(self):
        logging.info("User paused the agent.")

    def deleteAgent(self):
        logging.info("User deleted the agent.")

    def createSimulationInformationInterface(self):
        self.contextLabelFrame = tk.LabelFrame(self, text="Simulation Configuration")
        self.contextLabelFrame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W, padx=4, columnspan=2)
        self.configureSimulationButton = tk.Button(self.contextLabelFrame, text="Simulation Details", width=20,  command=self.openSimulationInformationWindow, state=tk.DISABLED)
        self.contextLabelFrame.columnconfigure(0, weight=1)
        self.configureSimulationButton.grid(row=0, column=0, pady=4, padx=4, columnspan=1)
        logging.debug("Simulation Configuration interface rendered.")

        if self.parent.mapData.mapLoadedBool == True:
            self.configureSimulationButton.config(state=tk.NORMAL)

    def enableSimulationConfiguration(self):
        self.configureSimulationButton.config(state=tk.NORMAL)
        logging.info("Session map loaded, enabling simulation configuration.")

    def openSimulationInformationWindow(self):
        # print("Simulation Info window opened!")
        self.parent.simulationConfiguration()

class contextViewState:
    """
        Containing class for state data used by the context view widgets, decoupled for pickling and saving
    """
    def __init__(self, parent):
        pass