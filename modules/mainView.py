import tkinter as tk
import math
import pprint
from functools import partial
from PIL import Image, ImageDraw, ImageTk
pp = pprint.PrettyPrinter(indent=4)
import networkx as nx
import logging
from modules.mainCanvas import mainCanvas as newCanvas

class mainView(tk.Frame):
    """
        The primary view of the warehouse, drawn with tk.Canvas layers and organized into a reliable stack
    """
    def __init__(self, parent):
        logging.debug("Main View Canvas UI initializing . . .")
        self.parent = parent

        # Map data reference
        self.mapData = self.parent.mapData.mapGraph
        logging.debug("Map data reference built.")

        # Fetch styling
        self.appearanceValues = self.parent.appearance
        frameHeight = self.appearanceValues.mainViewHeight
        frameWidth = self.appearanceValues.mainViewWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief
        logging.debug("Style information retrieved.")

        # Declare frame
        tk.Frame.__init__(self, parent, 
            height=frameHeight, 
            width=frameWidth, 
            borderwidth=frameBorderWidth, 
            relief=frameRelief)
        logging.debug("Containing frame settings constructed.")

        # Render frame within the app window context
        self.grid_propagate(False)
        self.grid(row=1, column=1, sticky=tk.N)
        logging.debug("Containing frame rendered.")
        
        # Build the canvas containing the display information
        logging.debug("Building the canvas . . .")
        self.mainCanvas = newCanvas(self, self.appearanceValues, "editCanvas", gridLoc=(0,0))

        # Initialize scrolling behavior
        self.initScrolling()
        logging.debug("Main Canvas UI element finished building.")

    def buildReferences(self):
        # Build references to classes declared after this one
        self.contextView = self.parent.contextView
        self.agentManager = self.parent.agentManager
        logging.debug("References built.")

    def initScrolling(self):
        # Create scrollbar components
        self.ybar = tk.Scrollbar(self, orient="vertical")
        self.xbar = tk.Scrollbar(self, orient="horizontal")
        logging.debug("Scrollbar component classes built.")

        # Bind the scrollbars to the canvas
        self.ybar["command"] = self.mainCanvas.yview
        self.xbar["command"] = self.mainCanvas.xview
        logging.debug("Bound scrollbars to canvas viewspace.")

        # Adjust positioning, size relative to grid
        self.ybar.grid(column=1, row=0, sticky="ns")
        self.xbar.grid(column=0, row=1, sticky="ew")
        logging.debug("Rendered canvas scrollbars.")

        # Make canvas update scrollbar position to match its view
        self.mainCanvas["yscrollcommand"] = self.ybar.set
        self.mainCanvas["xscrollcommand"] = self.xbar.set
        logging.debug("Main canvas scroll commands bound to scrollbars.")

        # Bind mousewheel to interact with the scrollbars
        # Only do this when the cursor is inside this frame
        self.bind('<Enter>', self.bindMousewheel)
        self.bind('<Leave>', self.unbindMousewheel)
        logging.debug("Mouse input capture bounds established for Main Canvas.")

        # Reset the view
        self.mainCanvas.xview_moveto("0.0")
        self.mainCanvas.yview_moveto("0.0")
        logging.debug("Scrollbar, Canvas position default set.")

    def bindMousewheel(self, event):
        self.bind_all("<MouseWheel>", self.mousewheelAction)
        self.bind_all("<Shift-MouseWheel>", self.shiftMousewheelAction)
        logging.debug("Bound mousewheel inputs to scrollbar.")

    def unbindMousewheel(self, event):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Shift-MouseWheel>")
        logging.debug("Released mousewheel input bindings due to cursor leaving the canvas.")

    def mousewheelAction(self, event):
        self.mainCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def shiftMousewheelAction(self, event):
        self.mainCanvas.xview_scroll(int(-1*(event.delta/120)), "units")