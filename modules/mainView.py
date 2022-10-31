import tkinter as tk
import math
import pprint
import json
pp = pprint.PrettyPrinter(indent=4)
from config.appearanceValues import appearanceValues

class mainView(tk.Frame):
    def __init__(self, parent):
        self.parent = parent

        # Fetch styling
        self.appearanceValues = self.parent.appearance
        frameHeight = self.appearanceValues.mainViewHeight
        frameWidth = self.appearanceValues.mainViewWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief

        # Declare frame
        tk.Frame.__init__(self, parent, 
            height=frameHeight, 
            width=frameWidth, 
            borderwidth=frameBorderWidth, 
            relief=frameRelief)

        # Render frame within the app window context
        self.grid_propagate(False)
        self.grid(row=0, column=1)
        
        # Build the canvas containing the display information
        self.mainCanvas = mainCanvas(self, self.appearanceValues)

        # Initialize scrolling behavior
        self.initScrolling()

    def initScrolling(self):
        # Create scrollbar components
        self.ybar = tk.Scrollbar(self, orient="vertical")
        self.xbar = tk.Scrollbar(self, orient="horizontal")

        # Bind the scrollbars to the canvas
        self.ybar["command"] = self.mainCanvas.yview
        self.xbar["command"] = self.mainCanvas.xview

        # Adjust positioning, size relative to grid
        self.ybar.grid(column=1, row=0, sticky="ns")
        self.xbar.grid(column=0, row=1, sticky="ew")

        # Make canvas update scrollbar position to match its view
        self.mainCanvas["yscrollcommand"] = self.ybar.set
        self.mainCanvas["xscrollcommand"] = self.xbar.set

        # Bind mousewheel to interact with the scrollbars
        # Only do this when the cursor is inside this frame
        self.bind('<Enter>', self.bindMousewheel)
        self.bind('<Leave>', self.unbindMousewheel)

        # Reset the view
        self.mainCanvas.xview_moveto("0.0")
        self.mainCanvas.yview_moveto("0.0")

    def bindMousewheel(self, event):
        self.bind_all("<MouseWheel>", self.mousewheelAction)
        self.bind_all("<Shift-MouseWheel>", self.shiftMousewheelAction)

    def unbindMousewheel(self, event):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Shift-MouseWheel>")

    def mousewheelAction(self, event):
        self.mainCanvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def shiftMousewheelAction(self, event):
        self.mainCanvas.xview_scroll(int(-1*(event.delta/120)), "units")

class mainCanvas(tk.Canvas):
    def __init__(self, parent, appearanceValues):
        tk.Canvas.__init__(self, parent)
        self.parent = parent
        self.appearanceValues = appearanceValues
        self["bg"] = self.appearanceValues.canvasBackgroundColor
        self["width"] = self.appearanceValues.canvasDefaultWidth
        self["height"] = self.appearanceValues.canvasDefaultHeight
        self["scrollregion"] = (0,0,self["width"], self["height"])
        self.canvasTileSize = self.appearanceValues.canvasTileSize

        # Render canvas within the mainView frame context
        # Give it size priority to fill the whole frame
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.grid(column=0, row=0, sticky=tk.N+tk.S+tk.E+tk.W)

        # Draw gridlines, mostly for debug
        self.drawGridlines()

    def drawGridlines(self):
        # Draw them at each tile width
        for i in range(math.floor(int(self["height"])/self.canvasTileSize)+1):
            self.create_line(0, i*self.canvasTileSize, self["width"], i*self.canvasTileSize, fill=self.appearanceValues.canvasGridlineColor)
        for i in range(math.floor(int(self["width"])/self.canvasTileSize)+1):
            self.create_line(i*self.canvasTileSize, 0, i*self.canvasTileSize, self["height"], fill=self.appearanceValues.canvasGridlineColor)

    def renderGraphState(self, graphData):
        print("render map data")
        # Input: NetworkX graph
        # Output: render the tiles of the map, including
        #   - Node tiles
        #   - Edges
        #   - Colorization by type

        # Draw nodes, being sure to tag them for ordering and overlaying
        # pp.pprint(graphData)
        # pp.pprint(graphData.nodes.data())
        for node in graphData.nodes.data():
            tileSize = self.appearanceValues.canvasTileSize
            nodeSizeRatio = self.appearanceValues.canvasTileCircleRatio
            pp.pprint(node)
            nodeData = node[1]
            nodePosX = nodeData["pos"]["X"]
            nodePosY = nodeData["pos"]["Y"]
            nodeType = nodeData["type"]
            nodePosGraphX = nodePosX * tileSize + 0.5 * tileSize
            nodePosGraphY = nodePosY * tileSize + 0.5 * tileSize
            self.create_line(0,0,nodePosGraphX, nodePosGraphY, fill="red")

            if nodeType == "edge":
                self.create_oval(
                    nodePosGraphX - nodeSizeRatio * tileSize,
                    nodePosGraphY - nodeSizeRatio * tileSize,
                    nodePosGraphX + nodeSizeRatio * tileSize,
                    nodePosGraphY + nodeSizeRatio * tileSize,
                    fill = "light blue",
                    tags=["nodes", "openNode"]
                )
            print(nodeData["pos"])