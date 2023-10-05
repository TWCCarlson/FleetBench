import tkinter as tk
import logging
from tkinter import ttk
import modules.tk_extensions as tk_e

class simDataView(tk.Frame):
    """
        The containing frame for the simulation data readout view
    """
    def __init__(self, parent):
        logging.debug("Simulation Data View UI Class initializing . . .")
        self.parent = parent

        # Fetch frame style configuration
        self.appearanceValues = self.parent.parent.parent.appearance
        frameHeight = self.appearanceValues.simulationInfoPanelHeight
        frameWidth = self.appearanceValues.simulationInfoPanelWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief
        logging.debug("Fetched styling information.")

        # Declare frame
        tk.Frame.__init__(self, parent,
            height=frameHeight,
            width=frameWidth,
            borderwidth=frameBorderWidth,
            relief=frameRelief)
        logging.debug("Simulation Data View Containing Frame constructed.")

        # Render frame
        self.grid(row=2, column=1, sticky="ew")
        self.columnconfigure(0, weight=1)

        self.createTreeViewNotebook()

    def buildReferences(self):
        # Populate the frame with data
        # self.createTreeViewNotebook()
        self.createAgentTreeView()
        self.createTaskTreeView()

    def createTreeViewNotebook(self):
        """
            Creates a Tkinter notebook containing pages for listing agent and task status/details
        """
        logging.debug("Building notebook of simulation treeView pages . . .")

        # Create the notebook object
        self.simObjectListNotebook = ttk.Notebook(self)
        self.simObjectListNotebook.grid(row=0, column=0, sticky="news")
        logging.debug("Simulation notebook rendered.")

        # Create the "agents" tab with a frame and add its treeview
        self.simAgentListFrame = tk.Frame(self.simObjectListNotebook)
        # self.createAgentTreeView()
        self.simObjectListNotebook.add(self.simAgentListFrame, text="Agents")

        # Create the "tasks" tab with a frame and add its treeview
        self.simTaskListFrame = tk.Frame(self.simObjectListNotebook)
        # self.createTaskTreeView()
        self.simObjectListNotebook.add(self.simTaskListFrame, text="Tasks")

        logging.info("All Simulation treeView pages added to notebook.")

    def createAgentTreeView(self):
        logging.debug("Creating simAgentTreeView page . . .")
        
        # Declare the treeview
        self.agentTreeView = ttk.Treeview(self.simAgentListFrame, selectmode='browse')
        
        # Style the treeView
        self.agentTreeView["height"] = 20
        columnList = {'Name': 60, 'Position': 60, 'Class': 60, 'Task': 60}
        self.agentTreeView["columns"] = list(columnList.keys())
        self.agentTreeView.heading('#0', text='A')
        self.agentTreeView.column('#0', width=35, stretch=0)
        for col in columnList:
            self.agentTreeView.heading(col, text=col)
            self.agentTreeView.column(col, width=columnList[col], stretch=True)
        logging.debug("Constructed all column configurations in Simulation agentTreeView.")

        # Render the treeView
        self.simAgentListFrame.columnconfigure(0, weight=1)
        self.agentTreeView.grid(row=0, column=0, sticky="news")
        logging.debug(f"Rendered Simulation treeView with columns: {columnList}")

        # Event bindings
        self.agentTreeView.bind('<Motion>', 'break')
        self.simAgentListFrame.bind('<Enter>', self.bindAgentClicks)
        self.simAgentListFrame.bind('<Leave>', self.unbindAgentClicks)
        agentSelectVar = self.parent.simMainView.simCanvas.currentClickedAgent
        agentSelectVar.trace_add("write", lambda *args, agentSelected=agentSelectVar: self.selectAgent(agentSelectVar.get()))
        logging.debug("Bound mouse events to Simulation agentTreeView")

        # Initialize scrolling
        self.initAgentTreeScrolling()

        # Build right click context menu
        self.agentMenu = tk_e.agentTreeViewMenu(self)
        self.agentMenu.add_entry(label="Delete (unimplemented)", command=print)

        logging.info("Simulation agentTreeView finished rendering.")

    def updateAgentTreeView(self):
        logging.debug("Received request to refresh the agentTreeView. . .")
        # Clear the treeview then regenerate it
        for row in self.agentTreeView.get_children():
            self.agentTreeView.delete(row)
        logging.debug("Cleared the agentTreeView.")

        # Access the list of all agents and rebuild the treeView based on their states
        simAgentManagerRef = self.parent.parent.simulationProcess.simAgentManager
        for agent in simAgentManagerRef.agentList:
            agentData = simAgentManagerRef.agentList.get(agent)
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

    def initAgentTreeScrolling(self):
        logging.debug("Building scrolling capability in the Simulation agentTreeView.")
        # Create scrollbar components
        self.agentTreeView.ybar = tk.Scrollbar(self.simAgentListFrame, orient="vertical")
        self.agentTreeView.xbar = tk.Scrollbar(self.simAgentListFrame, orient="horizontal")
        logging.debug("Scrollbars instantiated inthe Simulation agentTreeView.")

        # Bind the scrollbars to the canvas
        self.agentTreeView.ybar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.agentTreeView.xbar.grid(row=1, column=0, sticky=tk.E+tk.W)
        logging.debug("Scrollbars rendered into Simulation agentTreeView containing frame.")
        
        # Make canvas update scrollbar position to match its view
        self.agentTreeView["yscrollcommand"] = self.agentTreeView.ybar.set
        self.agentTreeView["xscrollcommand"] = self.agentTreeView.xbar.set
        logging.debug("Bound agentTreeView scroll commands to the scrollbars.")

        # Reset the view
        self.agentTreeView.xview_moveto("0.0")
        self.agentTreeView.yview_moveto("0.0")
        logging.debug("Set default agentTreeView scroll levels.")

        logging.info("Finished building agentTreeView scrolling.")

    def bindAgentClicks(self, *event):
        self.agentClickBindFunc = self.agentTreeView.bind('<Button-1>', self.handleAgentSelect)
        self.agentRClickBindFunc = self.agentTreeView.bind('<Button-3>', self.handleAgentRClick)

    def unbindAgentClicks(self, *event):
        self.agentTreeView.unbind('<Button-1>', self.agentClickBindFunc)
        self.agentTreeView.unbind('<Button-3>', self.agentRClickBindFunc)

    def selectAgent(self, selectedAgentName):
        agentIID = self.agentTreeView.tag_has(selectedAgentName)
        self.agentTreeView.selection_set(agentIID)

    def handleAgentSelect(self, event):
        # Identify the selected row
        selectedRow = self.agentTreeView.identify_row(event.y)
        self.agentTreeView.selection_set(selectedRow)

        if selectedRow in self.agentTreeView.tag_has("agent"):
            rowData = self.agentTreeView.item(selectedRow) 
            # Hightlight the selected agent
            agentID = rowData["tags"][1]
            agentRef = self.parent.parent.simulationProcess.simAgentManager.agentList.get(agentID)
            agentRef.highlightAgent(multi=False)
            if agentRef.currentTask:
                agentRef.currentTask.highlightTask(multi=False)
            else:
                self.parent.simMainView.simCanvas.requestRender("highlight", "delete", {"highlightTag": "pickupHighlight"})
                self.parent.simMainView.simCanvas.requestRender("highlight", "delete", {"highlightTag": "depositHighlight"})
            self.parent.simMainView.simCanvas.handleRenderQueue()
            # Update agentManager's currentAgent prop
            self.parent.parent.simulationProcess.simAgentManager.currentAgent = agentRef
            logging.debug(f"User clicked on agent '{agentID}' in agentTreeView.")

    def handleAgentRClick(self, event):
        # Give focus to the right clicked element
        logging.debug("User right clicked an agent in the agentTreeView.")
        self.handleAgentSelect(event)

        # Create the popup menu
        self.agentMenu.popup(event.x, event.y, event.x_root, event.y_root)

    def createTaskTreeView(self):
        logging.debug("Creating simTaskTreeView page . . .")
        
        # Declare the treeview
        self.taskTreeView = ttk.Treeview(self.simTaskListFrame, selectmode='browse')

        # Style the treeView
        columnList = {'Name': 50, 'Pickup': 25, 'Dropoff': 25, 'Assignee': 40, 'Time Limit': 40}
        self.taskTreeView["height"] = 20
        self.taskTreeView["columns"] = list(columnList.keys())
        self.taskTreeView.heading('#0', text='A')
        self.taskTreeView.column('#0', width=35, stretch=0)
        for col in columnList:
            self.taskTreeView.heading(col, text=col)
            self.taskTreeView.column(col, width=columnList[col], stretch=True)
        logging.debug("Constructed all column configurations in Simulation taskTreeView.")

        # Render the treeView
        self.simTaskListFrame.columnconfigure(0, weight=1)
        self.taskTreeView.grid(row=0, column=0, sticky="news")
        logging.debug(f"Rendered Simulation treeView with columns: {columnList}")

        # Event bindings
        self.taskTreeView.bind('<Motion>', 'break')
        self.taskTreeView.bind('<Enter>', self.bindTaskClicks)
        self.taskTreeView.bind('<Leave>', self.unbindTaskClicks)
        logging.debug("Bound mouse events to Simulation taskTreeView")

        # Initialize scrolling
        self.initTaskTreeScrolling()

        # Build right click context menu
        self.taskMenu = tk_e.taskTreeViewMenu(self)
        # self.taskMenu.add_entry(label="Delete", command=self.parent.parent.simulationProcess.simTaskManager.deleteTask)
        logging.debug("Built right click context-sensitive menu in the Simulation taskTreeView.")

        logging.info("Simulation agentTreeView finished rendering.")

    def initTaskTreeScrolling(self):
        logging.debug("Building scrolling capability in the Simulation taskTreeView.")
        # Create scrollbar components
        self.taskTreeView.ybar = tk.Scrollbar(self.simTaskListFrame, orient="vertical")
        self.taskTreeView.xbar = tk.Scrollbar(self.simTaskListFrame, orient="horizontal")
        logging.debug("Scrollbars instantiated in the Simulation taskTreeView.")

        # Bind the scrollbars to the canvas
        self.taskTreeView.ybar["command"] = self.taskTreeView.yview
        self.taskTreeView.xbar["command"] = self.taskTreeView.xview
        logging.debug("Scrollbars bound to Simulation taskTreeView.")

        # Adjust positioning, size relative to grid
        self.taskTreeView.ybar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.taskTreeView.xbar.grid(row=1, column=0, sticky=tk.E+tk.W)
        logging.debug("Scrollbars rendered into Simulation taskTreeView containing frame.")

        # Make canvas update scrollbar position to match its view
        self.taskTreeView["yscrollcommand"] = self.taskTreeView.ybar.set
        self.taskTreeView["xscrollcommand"] = self.taskTreeView.xbar.set
        logging.debug("Bound Simulation taskTreeView scroll commands to the scrollbars.")

        # Reset the view
        self.taskTreeView.xview_moveto("0.0")
        self.taskTreeView.yview_moveto("0.0")
        logging.debug("Set default Simulation taskTreeView scroll levels.")

        logging.info("Finished building Simulation taskTreeView scrolling.")

    def updateTaskTreeView(self):
        logging.debug("Received request to refresh the taskTreeView . . .")
        # Clear the treeview then regenerate it
        for row in self.taskTreeView.get_children():
            self.taskTreeView.delete(row)
        logging.debug("Cleared the taskTreeView.")

        # Access the list of all tasks and rebuild the treeView based on their states
        for task in self.parent.parent.simulationProcess.simTaskManager.taskList:
            taskData = self.parent.parent.simulationProcess.simTaskManager.taskList.get(task)
            taskNumID = taskData.numID
            taskName = taskData.name
            taskPickupPosition = taskData.pickupNode
            taskDropoffPosition = taskData.dropoffNode
            if taskData.assignee is not None:
                taskAssignee = taskData.assignee.ID
            else:
                taskAssignee = None
            taskTimeLimit = taskData.timeLimit
            self.taskTreeView.insert(parent="",
                index='end',
                iid=taskNumID,
                text=f"{str(taskNumID)}",
                values=[taskName, taskPickupPosition, taskDropoffPosition, taskAssignee, taskTimeLimit],
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
            rowData = self.taskTreeView.item(selectedRow) 
            # Hightlight the selected task
            taskID = rowData["tags"][1]
            taskRef = self.parent.parent.simulationProcess.simTaskManager.taskList.get(taskID)
            taskRef.highlightTask(multi=False)
            if taskRef.assignee is not None:
                taskRef.assignee.highlightAgent(multi=False)
            else:
                self.parent.simMainView.simCanvas.requestRender("highlight", "delete", {"highlightTag": "agentHighlight"})
            self.parent.simMainView.simCanvas.handleRenderQueue()
            # Update taskManager's currenttask prop
            self.parent.parent.simulationProcess.simTaskManager.currenttask = taskRef
            logging.debug(f"User clicked on task '{taskID}' in taskTreeView.")

    def handleTaskRClick(self, event):
        # Give focus to the clicked element
        logging.debug("User right click a task in the Simulation taskTReeView.")
        self.handleTaskSelect(event)

        # Create the popup menu
        self.taskMenu.popup(event.x, event.y, event.x_root, event.y_root)