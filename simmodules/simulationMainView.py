import tkinter as tk
import math
import logging
import pprint
pp = pprint.PrettyPrinter(indent=4)

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
        self.grid(row=1, column=1, sticky=tk.N)
        logging.debug("Containing frame rendered.")

        # Build the mainView canvas
        self.simCanvas = simCanvas(self, self.appearanceValues)
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

class simCanvas(tk.Canvas):
    """
        The primary view used within the simulation window to view the activity in he warehouse
    """
    def __init__(self, parent, appearanceValues):
        logging.debug("Building the simulation main canvas . . .")

        tk.Canvas.__init__(self, parent)
        self.parent = parent

        # Style
        self.appearanceValues = appearanceValues
        self["bg"] = self.appearanceValues.simCanvasBackgroundColor
        self["width"] = self.appearanceValues.simCanvasDefaultWidth
        self["height"] = self.appearanceValues.simCanvasDefaultHeight
        self["scrollregion"] = (0, 0, self["width"], self["height"])
        self.canvasTileSize = self.appearanceValues.canvasTileSize
        logging.info("Simulation Main Canvas UI element style settings built.")

        # Render canvas
        # Use config to give it size priority over scrollbars
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.grid(column=0, row=0, sticky=tk.N+tk.S+tk.E+tk.W)
        logging.info("Rendered Simulation Main Canvas in simulation window.")

        # Draw gridlines
        self.drawGridlines()

    def drawGridlines(self):
        # Drawn for every linewidth in appearanceValues
        logging.debug("Rendering Simulation Main Canvas gridlines . . .")
        # Horizontal lines
        for i in range(math.floor(int(self["height"])/self.canvasTileSize)+1):
            self.create_line(0, i*self.canvasTileSize, self["width"], i*self.canvasTileSize, fill=self.appearanceValues.simCanvasGridlineColor)
        # Vertical lines
        for i in range(math.floor(int(self["width"])/self.canvasTileSize)+1):
            self.create_line(i*self.canvasTileSize, 0, i*self.canvasTileSize, self["height"], fill=self.appearanceValues.simCanvasGridlineColor)
        
    def setCanvasDimensions(self, tileWidth, tileHeight):
        # Adjusts the canvas to have passed dimensions (in number of tiles)
        canvasWidth = tileWidth * self.appearanceValues.simCanvasTileSize
        canvasHeight = tileHeight * self.appearanceValues.simCanvasTileSize
        self["width"] = canvasWidth
        self["height"] = canvasHeight
        self["scrollregion"] = (0, 0, canvasWidth, canvasHeight)
        logging.debug(f"Main Canvas dimensions updated: canvasWidth={tileWidth}, canvasHeight={tileHeight}")

    def graphCoordToCanvas(self, coord):
        # Converts the tile number to the canvas pixel number
        # In: integer id of a tile
        # Out: central pixel of the corresponding location in the canvas
        tileSize = self.appearanceValues.simCanvasTileSize
        canvasCoord = coord * tileSize + 0.5 * tileSize
        logging.debug(f"Converted tile coordinate '{coord}' to canvas coordinate '{canvasCoord}'")
        return canvasCoord

    def renderGraphState(self):
        # Reset the canvas to being empty before redrawing
        self.clearMainCanvas()
        logging.info("Cleared simulation main canvas for re-rendering.")

        # Retrieve mainView styling information
        tileSize = self.appearanceValues.simCanvasTileSize
        nodeSizeRatio = self.appearanceValues.simCanvasTileCircleRatio
        edgeWidth = self.appearanceValues.simCanvasEdgeWidth
        logging.info("Fetched style reference values.")

        # Retrieve the graph information
        mapGraph = self.parent.parent.parent.simulationProcess.simGraphData.simMapGraph
        pp.pprint(mapGraph)

        # Render grid lines
        self.drawGridlines()

        # Render the mapGraph nodes
        self.renderNodes(mapGraph, tileSize, nodeSizeRatio)

    def clearMainCanvas(self):
        # Destroys all entities on the canvas
        self.delete("all")
        logging.info("Main simulation canvas cleared.")

    def renderNodes(self, mapGraph, tileSize, nodeSizeRatio):
        # Iterate through the graph and draw nodes onto the simulation main view canvas
        for node in mapGraph.nodes.data():
            logging.debug(f"Simulation attempting to draw node: {node}")

            # Extract data
            nodeData = node[1]
            nodePosX = nodeData["pos"]["X"]
            nodePosY = nodeData["pos"]["Y"]
            nodeType = nodeData["type"]

            # Locate the canvas position of the tile
            nodePosGraphX = self.graphCoordToCanvas(nodePosX)
            nodePosGraphY = self.graphCoordToCanvas(nodePosY)

            # Set the node style
            if nodeType == "edge":
                fillColor = "blue"
                tags = ["node", "openNode"]
            elif nodeType == "charge":
                fillColor = "yellow"
                tags = ["node", "chargeNode"]
            elif nodeType == "deposit":
                fillColor = "light green"
                tags = ["node", "depositNode"]
            elif nodeType == "pickup":
                fillColor = "light blue"
                tags = ["node", "pickupNode"]
            elif nodeType == "rest":
                fillColor = "brown"
                tags = ["node", "restNode"]
            elif nodeType == "void":
                # Do nothing
                logging.debug(f"Simulation node is of type 'void', ignoring . . .")
                continue
            logging.debug(f"Simulation node type '{nodeType}' is assigned tags: {tags}")

            # Draw the node onto the simulation canvas
            self.create_oval(
                nodePosGraphX - nodeSizeRatio * tileSize,
                nodePosGraphY - nodeSizeRatio * tileSize,
                nodePosGraphX + nodeSizeRatio * tileSize,
                nodePosGraphY + nodeSizeRatio * tileSize,
                fill=fillColor,
                tags=tags
            )
            logging.debug("Node drawn on the successfully.")
        logging.info("Rendered all graphData nodes to the simulation canvas.")

