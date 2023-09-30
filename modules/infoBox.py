import tkinter as tk
import logging

class infoBox(tk.Frame):
    """
        Bar resting above the main canvas
        Contains toggles for showing things like agents, nodes, edges, dangling edges, tasks
        Also contains text responsive to where the cursor hovers in the main canvas
    """
    def __init__(self, parent):
        logging.debug("Info Box UI Class initializing . . .")
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
        logging.debug("Info Box Containing Frame constructed.")

        self.mainView = self.parent.mainView
        logging.debug("Refences built.")

        self.infoBoxState = infoBoxState(self)
        logging.debug("Info Box state class instantiated.")
        self.infoBoxFrame = infoBoxFrame(self)
        logging.debug("Info Box UI element class instantiated.")

        # Render frame
        self.grid_propagate(False)
        self.grid(row=0, column=1, sticky=tk.N)
        logging.info("Info Box UI elements rendered into main app.")
        
class infoBoxFrame(tk.Frame):
    """
        Bar resting above the main canvas
        Contains toggles for showing things like agents, nodes, edges, dangling edges, tasks
        Also contains text responsive to where the cursor hovers in the main canvas
    """
    def __init__(self, parent):
        self.parent = parent
        self.mainCanvas = self.parent.mainView.mainCanvas

        # Create checkboxes for each canvas layer
        self.danglingEdgeTick = tk.Checkbutton(self.parent, text='Dangling Edges', 
                variable=self.mainCanvas.danglingEdgeVisibility, onvalue=True, offvalue=False)
        self.edgeTick = tk.Checkbutton(self.parent, text='Edges', 
                variable=self.mainCanvas.edgeVisibility, onvalue=True, offvalue=False)
        self.nodeTick = tk.Checkbutton(self.parent, text='Nodes', 
                variable=self.mainCanvas.nodeVisibility, onvalue=True, offvalue=False)
        self.agentTick = tk.Checkbutton(self.parent, text='Agents',
                variable=self.mainCanvas.agentVisibility, onvalue=True, offvalue=False)
        self.agentOrientationTick = tk.Checkbutton(self.parent, text='Agent Orientation',
                variable=self.mainCanvas.agentOrientationVisibility, onvalue=True, offvalue=False)
        logging.debug("Created canvas layer visibility toggles.`")

        # Render checkboxes
        self.danglingEdgeTick.grid(row=0, column=0)
        self.edgeTick.grid(row=0, column=1)
        self.nodeTick.grid(row=0, column=2)
        self.agentTick.grid(row=0, column=3)
        self.agentOrientationTick.grid(row=0, column=4)
        logging.debug("Rendered canvas layer toggle buttons.")

        # Create the hover info text
        self.hoverInfoText = self.mainCanvas.hoverText
        self.hoverInfoText.set(". . .") # default value
        font = self.parent.appearanceValues.infoBoxFont
        self.hoverInfo = tk.Label(self.parent, textvariable=self.hoverInfoText, font=font)
        logging.debug("Created canvas layer hover info display.")
        
        # Render the hovertext
        # Right justify
        self.parent.columnconfigure(5, weight=1)
        self.hoverInfo.grid(row=0, column=5, sticky=tk.E)
        logging.debug("Rendered canvas layer hover info display.")

class infoBoxState:
    """
        Containing class for state data used by the info box widget, decoupled for pickling and saving
    """
    def __init__(self, parent):
        logging.debug("Initialized Info Box UI element state data class.")
        pass