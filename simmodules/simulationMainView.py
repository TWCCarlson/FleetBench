import tkinter as tk
import math
import logging
import pprint
pp = pprint.PrettyPrinter(indent=4)
from functools import partial
from PIL import Image, ImageDraw, ImageTk

from modules.mainCanvas import mainCanvas

class simMainView(tk.Frame):
    """
        The primary viewfield of the warehouse
        Drawn using tk.Canvas to display robot, task, and map information
    """
    def __init__(self, parent):
        logging.debug("Simulation Main View UI Element initializing . . .")
        self.parent = parent

        # Fetch styling configuration
        self.appearanceValues = self.parent.parent.parent.appearance
        frameHeight = self.appearanceValues.simulationMainViewHeight
        frameWidth = self.appearanceValues.simulationMainViewWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief
        logging.debug("Style information retrieved.")

        # Declare the mainView frame
        tk.Frame.__init__(self, parent,
            height=frameHeight,
            width=frameWidth,
            borderwidth=frameBorderWidth,
            relief=frameRelief)
        logging.debug("Containing frame settings built.")

        # Render the frame
        self.grid_propagate(False)
        self.grid(row=1, column=0, sticky=tk.N, rowspan=2)
        logging.debug("Containing frame rendered.")

        # Build the mainView canvas
        self.simCanvas = mainCanvas(self, self.appearanceValues, "simCanvas", gridLoc=(0, 0))
        logging.debug("Simulation canvas rendered.")

        # Create scrollbars
        self.initScrolling()
        logging.info("Simulation Main Canvas UI elements finished building.")

    def initScrolling(self):
        # Create scrollbar components
        self.xbar = tk.Scrollbar(self, orient="horizontal")
        self.ybar = tk.Scrollbar(self, orient="vertical")
        logging.debug("Scrollbar component classes built.")

        # Bind scrollbar state to canvas view window state
        self.xbar["command"] = self.simCanvas.xview
        self.ybar["command"] = self.simCanvas.yview
        logging.debug("Bound scrollbars to simulation canvas view window.")

        # Adjust positioning, size relative to grid
        self.xbar.grid(column=0, row=1, sticky="ew")
        self.ybar.grid(column=1, row=0, sticky="ns")
        logging.debug("Rendered canvas scrollbars")

        # Make canvas update scrollbar position to match the view window state
        self.simCanvas["xscrollcommand"] = self.xbar.set
        self.simCanvas["yscrollcommand"] = self.ybar.set
        logging.debug("Mains canvas scroll commands bound to scrollbar states.")

        # Bind mousewheel to interact with the scrollbars
        # Only bound while cursor is inside the frame
        self.bind('<Enter>', self.bindMousewheel)
        self.bind('<Leave>', self.unbindMousewheel)

        # Reset the view
        self.simCanvas.xview_moveto("0.0")
        self.simCanvas.yview_moveto("0.0")
        logging.debug("Simulation scrollbars and canvas default view window set.")

    def bindMousewheel(self, event):
        self.bind_all("<MouseWheel>", self.mousewheelAction)
        self.bind_all("<Shift-MouseWheel>", self.shiftMousewheelAction)
        logging.debug("Bound mousewheel inputs to simulation main canvas scrollbars.")

    def unbindMousewheel(self, event):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Shift-MouseWheel>")
        logging.debug("Released mousewheel inputs to simulation main canvas scrollbars.")

    def mousewheelAction(self, event):
        self.simCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def shiftMousewheelAction(self, event):
        self.simCanvas.xview_scroll(int(-1*(event.delta/120)), "units")