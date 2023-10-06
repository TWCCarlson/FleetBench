import tkinter as tk
import logging

class simInfoBox(tk.Frame):
    """
        Bar resting above the main canvas
        Contains layer toggles
        Contains text responsive to highlights in the canvas
    """
    def __init__(self, parent, targetFrame):
        logging.debug("Simulation Info Box UI Class initializing . . .")
        self.parent = parent
        self.targetFrame = targetFrame

        # Fetch frame style configuration
        self.appearanceValues = self.parent.parent.parent.appearance
        frameHeight = self.appearanceValues.simulationInfoBoxHeight
        frameWidth = self.appearanceValues.simulationInfoBoxWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief
        logging.debug("Fetched styling information.")

        # Declare frame
        tk.Frame.__init__(self, targetFrame,
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

    def buildReferences(self):
        self.simMainView = self.parent.parent.simMainView.simCanvas

    def buildInfoBox(self):
        # Create checkboxes for each canvas layer
        self.danglingEdgeTick = tk.Checkbutton(self.parent, text='Dangling Edges', 
                variable=self.simMainView.danglingEdgeVisibility, onvalue=True, offvalue=False)
        self.edgeTick = tk.Checkbutton(self.parent, text='Edges', 
                variable=self.simMainView.edgeVisibility, onvalue=True, offvalue=False)
        self.nodeTick = tk.Checkbutton(self.parent, text='Nodes', 
                variable=self.simMainView.nodeVisibility, onvalue=True, offvalue=False)
        self.agentTick = tk.Checkbutton(self.parent, text='Agents',
                variable=self.simMainView.agentVisibility, onvalue=True, offvalue=False)
        self.agentOrientationTick = tk.Checkbutton(self.parent, text='Agent Orientation',
                variable=self.simMainView.agentOrientationVisibility, onvalue=True, offvalue=False)
        logging.debug("Created canvas layer visibility toggles.`")

        # Trigger info tile generation in the associated canvas
        self.hoverInfoText = self.simMainView.hoverText

        # Create the hover info text
        # self.hoverInfoText = tk.StringVar()
        self.hoverInfoText.set(". . . ?") # default value
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