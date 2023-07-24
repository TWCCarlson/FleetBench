import tkinter as tk
import logging

class simInfoBox(tk.Frame):
    """
        Bar resting above the main canvas
        Contains layer toggles
        Contains text responsive to highlights in the canvas
    """
    def __init__(self, parent):
        logging.debug("Simulation Info Box UI Class initializing . . .")
        self.parent = parent

        # Fetch frame style configuration
        self.appearanceValues = self.parent.parent.parent.appearance
        frameHeight = self.appearanceValues.simulationInfoBoxHeight
        frameWidth = self.appearanceValues.simulationInfoBoxWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief
        logging.debug("Fetched styling information.")

        # Declare frame
        tk.Frame.__init__(self, parent,
            height=frameHeight,
            width=frameWidth,
            borderwidth=frameBorderWidth,
            relief=frameRelief)
        logging.debug("Simulation Info Box Containing Frame constructed.")

        self.simInfoBoxFrame = infoBoxFrame(self)
        logging.debug("Simulation Info Box UI element class instantiated.")

        # Render the frame
        self.grid_propagate(False)
        self.grid(row=0, column=0, sticky=tk.N)
        logging.info("Info Box UI elements rendered into simulation window.")

class infoBoxFrame(tk.Frame):
    """
        Bar resting above the simulation main canvas
        Contains toggles for showing things like agents, nodes, edges, dangling edges, tasks
        Also contains text responsive to where the cursor hovers in the main canvas
    """
    def __init__(self, parent):
        self.parent = parent

        # Intvars store the state of each checkbox
        self.danglingEdgeVisibility = tk.IntVar()
        self.edgeVisibility = tk.IntVar()
        self.nodeVisibility = tk.IntVar()
        self.agentVisibility = tk.IntVar()
        self.agentOrienationVisibility = tk.IntVar()

        # Create checkboxes for each canvas layer
        self.danglingEdgeTick = tk.Checkbutton(self.parent, text='Dangling Edges', 
                variable=self.danglingEdgeVisibility, onvalue=1, offvalue=0,
                command=self.setDanglingEdgeVisibility
                )
        self.edgeTick = tk.Checkbutton(self.parent, text='Edges', 
                variable=self.edgeVisibility, onvalue=1, offvalue=0,
                command=self.setEdgeVisibility
                )
        self.nodeTick = tk.Checkbutton(self.parent, text='Nodes', 
                variable=self.nodeVisibility, onvalue=1, offvalue=0,
                command=self.setNodeVisibility
                )
        self.agentTick = tk.Checkbutton(self.parent, text='Agents',
                variable=self.agentVisibility, onvalue=1, offvalue=0,
                command=self.setAgentVisibility
                )
        self.agentOrientationTick = tk.Checkbutton(self.parent, text='Agent Orientation',
                variable=self.agentOrienationVisibility, onvalue=1, offvalue=0,
                command=self.setAgentOrientationVisibility
                )
        logging.debug("Created canvas layer visibility toggles.`")

        # Create the hover info text
        self.hoverInfoText = tk.StringVar()
        self.hoverInfoText.set(". . .") # default value
        font = self.parent.appearanceValues.simulationInfoBoxFont
        self.hoverInfo = tk.Label(self.parent, textvariable=self.hoverInfoText, font=font)
        logging.debug("Created canvas layer hover info display.")

        # Render checkboxes
        self.danglingEdgeTick.grid(row=0, column=0)
        self.edgeTick.grid(row=0, column=1)
        self.nodeTick.grid(row=0, column=2)
        self.agentTick.grid(row=0, column=3)
        self.agentOrientationTick.grid(row=0, column=4)
        logging.debug("Rendered canvas layer toggle buttons.")
        
        # Render the hovertext
        # Right justify
        self.parent.columnconfigure(5, weight=1)
        self.hoverInfo.grid(row=0, column=5, sticky=tk.E)
        logging.debug("Rendered canvas layer hover info display.")

    def setDanglingEdgeVisibility(self):
        # Call the canvas function for toggling the state of the layer
        logging.debug("Requesting 'danglingEdge' visibility toggle.")
        self.parent.parent.simMainView.simCanvas.toggleDanglingEdgeVisibility()

    def setEdgeVisibility(self):
        # Call the canvas function for toggling the state of the layer
        logging.debug("Requesting 'edge' visibility toggle.")
        self.parent.parent.simMainView.simCanvas.toggleEdgeVisibility()

    def setNodeVisibility(self):
        # Call the canvas function for toggling the state of the layer
        logging.debug("Requesting 'node' visibility toggle.")
        self.parent.parent.simMainView.simCanvas.toggleNodeVisibility()

    def setAgentVisibility(self):
        # Call the canvas function for toggling the state of the layer
        logging.debug("Requesting 'agent' visibility toggle.")
        self.parent.parent.simMainView.simCanvas.toggleAgentVisibility()

    def setAgentOrientationVisibility(self):
        # Call the canvas function for toggling the state of the layer
        logging.debug("Requesting 'agentOrientation' visibility toggle.")
        self.parent.parent.simMainView.simCanvas.toggleAgentOrientationVisibility()