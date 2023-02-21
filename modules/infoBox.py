import tkinter as tk

class infoBox(tk.Frame):
    """
        Bar resting above the main canvas
        Contains toggles for showing things like agents, nodes, edges, dangling edges, tasks
        Also contains text responsive to where the cursor hovers in the main canvas
    """
    def __init__(self, parent):
        self.parent = parent

        # Fetch style
        self.appearanceValues = self.parent.appearance
        frameHeight = self.appearanceValues.infoBoxHeight
        frameWidth = self.appearanceValues.infoBoxWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief

        # Declare frame
        tk.Frame.__init__(self, parent,
            height=frameHeight,
            width=frameWidth,
            borderwidth=frameBorderWidth,
            relief=frameRelief
        )

        self.infoBoxState = infoBoxState(self)

    def buildReferences(self):
        self.mainView = self.parent.mainView
        self.reInit()

    def reInit(self):
        self.infoBoxFrame = infoBoxFrame(self)

        # Render frame
        self.grid_propagate(False)
        self.grid(row=0, column=1, sticky=tk.N)

class infoBoxFrame(tk.Frame):
    """
        Bar resting above the main canvas
        Contains toggles for showing things like agents, nodes, edges, dangling edges, tasks
        Also contains text responsive to where the cursor hovers in the main canvas
    """
    def __init__(self, parent):
        self.parent = parent

        self.danglingEdgeVisibility = tk.IntVar()
        self.edgeVisibility = tk.IntVar()
        self.nodeVisibility = tk.IntVar()
        self.agentVisibility = tk.IntVar()
        # Create checkboxes for each canvas layer
        self.danglingEdgeTick = tk.Checkbutton(self.parent, text='Dangling Edges', 
                variable=self.danglingEdgeVisibility, onvalue=1, offvalue=0,
                command=self.setDanglingEdgeVisibility)
        self.edgeTick = tk.Checkbutton(self.parent, text='Edges', 
                variable=self.edgeVisibility, onvalue=1, offvalue=0,
                command=self.setEdgeVisibility)
        self.nodeTick = tk.Checkbutton(self.parent, text='Nodes', 
                variable=self.nodeVisibility, onvalue=1, offvalue=0,
                command=self.setNodeVisibility)
        self.agentTick = tk.Checkbutton(self.parent, text='Agents',
                variable=self.agentVisibility, onvalue=1, offvalue=0,
                command=self.setAgentVisibility)

        # Create the hover info text
        self.hoverInfoText = tk.StringVar()
        self.hoverInfoText.set(". . .") # default value
        font = self.parent.appearanceValues.infoBoxFont
        self.hoverInfo = tk.Label(self.parent, textvariable=self.hoverInfoText, font=font)

        # Render checkboxes
        self.danglingEdgeTick.grid(row=0, column=0)
        self.edgeTick.grid(row=0, column=1)
        self.nodeTick.grid(row=0, column=2)
        self.agentTick.grid(row=0, column=3)
        

        # Render the hovertext
        # Right justify
        self.parent.columnconfigure(4, weight=1)
        self.hoverInfo.grid(row=0, column=4, sticky=tk.E)

    def setDanglingEdgeVisibility(self):
        # Call the canvas function for toggling the state of the layer
        self.parent.mainView.mainCanvas.toggleDanglingEdgeVisibility()

    def setEdgeVisibility(self):
        # Call the canvas function for toggling the state of the layer
        self.parent.mainView.mainCanvas.toggleEdgeVisibility()

    def setNodeVisibility(self):
        # Call the canvas function for toggling the state of the layer
        self.parent.mainView.mainCanvas.toggleNodeVisibility()

    def setAgentVisibility(self):
        # Call the canvas function for toggling the state of the layer
        self.parent.mainView.mainCanvas.toggleAgentVisibility()

class infoBoxState:
    """
        Containing class for state data used by the info box widget, decoupled for pickling and saving
    """
    def __init__(self, parent):
        pass