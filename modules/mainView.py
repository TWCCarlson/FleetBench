import tkinter as tk
import math
import pprint
from functools import partial
from PIL import Image, ImageDraw, ImageTk
pp = pprint.PrettyPrinter(indent=4)
from config.appearanceValues import appearanceValues

class mainView(tk.Frame):
    def __init__(self, parent):
        self.parent = parent

        # Map data reference
        self.mapData = self.parent.mapData.mapGraph

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
        self.grid(row=1, column=1, sticky=tk.N)
        
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

        # Draw gridlines
        self.drawGridlines()

    def drawGridlines(self):
        # Draw them at each tile width
        for i in range(math.floor(int(self["height"])/self.canvasTileSize)+1):
            self.create_line(0, i*self.canvasTileSize, self["width"], i*self.canvasTileSize, fill=self.appearanceValues.canvasGridlineColor)
        for i in range(math.floor(int(self["width"])/self.canvasTileSize)+1):
            self.create_line(i*self.canvasTileSize, 0, i*self.canvasTileSize, self["height"], fill=self.appearanceValues.canvasGridlineColor)

    def graphCoordToCanvas(self, coord):
        tileSize = self.appearanceValues.canvasTileSize
        # In: the tile count value for location of the coord
        # Out: the canvas pixel value for location of the coord
        coord = coord * tileSize + 0.5 * tileSize
        return coord

    def renderGraphState(self, graphData):
        print("render map data")
        # Input: NetworkX graph
        # Output: render the tiles of the map, including
        #   - Node tiles
        #   - Edges
        #   - Colorization by type
        # Style references
        tileSize = self.appearanceValues.canvasTileSize
        nodeSizeRatio = self.appearanceValues.canvasTileCircleRatio
        # Draw nodes, being sure to tag them for ordering and overlaying
        self.renderNodes(graphData, tileSize, nodeSizeRatio)
        self.renderEdges(graphData)
        self.renderDanglingEdges(graphData, tileSize)
        self.generateHoverInfo(graphData, tileSize)
        self.setAllLayersVisible()
        self.sortCanvasLayers()
        
    def renderNodes(self, graphData, tileSize, nodeSizeRatio):
        # Display nodes in graph
        for node in graphData.nodes.data():
            # Break down the data
            nodeData = node[1]
            nodePosX = nodeData["pos"]["X"]
            nodePosY = nodeData["pos"]["Y"]
            nodeType = nodeData["type"]

            # Identify the center of the canvas tile
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

            # Draw the node
            self.create_oval(
                nodePosGraphX - nodeSizeRatio * tileSize,
                nodePosGraphY - nodeSizeRatio * tileSize,
                nodePosGraphX + nodeSizeRatio * tileSize,
                nodePosGraphY + nodeSizeRatio * tileSize,
                fill = fillColor,
                tags=tags
            )

    def renderEdges(self, graphData):
        # Display connected edges
        for edge in graphData.edges():
            # Break the edge into its 2 nodes
            firstPoint = edge[0]
            secondPoint = edge[1]

            # Break the string into a tuple and pull out the coordinates
            firstPosX = eval(firstPoint)[0]
            firstPosY = eval(firstPoint)[1]
            secondPosX = eval(secondPoint)[0]
            secondPosY = eval(secondPoint)[1]

            # Find the center of the relevant tiles on the canvas
            firstPosGraphX = self.graphCoordToCanvas(firstPosX)
            firstPosGraphY = self.graphCoordToCanvas(firstPosY)
            secondPosGraphX = self.graphCoordToCanvas(secondPosX)
            secondPosGraphY = self.graphCoordToCanvas(secondPosY)

            # Draw the edge
            self.create_line(
                firstPosGraphX,
                firstPosGraphY,
                secondPosGraphX,
                secondPosGraphY,
                fill = "blue",
                width = 3,
                tags=["edge"]
            )

    def renderDanglingEdges(self, graphData, tileSize):
        # Display dangling edges
        for node in graphData.nodes.data():
            # Break out the data
            nodeName = node[0]
            nodeData = node[1]
            nodePosX = nodeData["pos"]["X"]
            nodePosY = nodeData["pos"]["Y"]
            nodeEdges = nodeData["edgeDirs"]
            # If the node has an edge in a direction
            if nodeEdges["N"] == 1:
                # Calculate what the node it is trying to connect to should be
                edgeTarget = "(" + str(nodePosX) + ", " + str(nodePosY-1) + ")"
                # Check that node is not connected to target by a real edge
                if graphData.has_edge(nodeName, edgeTarget):
                # if edgeTarget in graphData.neighbors(nodeName):
                    pass
                else:
                     # Draw the line if it dangles and tag it appropriately
                    nodePosGraphX = self.graphCoordToCanvas(nodePosX)
                    nodePosGraphY = self.graphCoordToCanvas(nodePosY)
                    self.create_line(
                        nodePosGraphX,
                        nodePosGraphY,
                        nodePosGraphX,
                        nodePosGraphY - 0.5*tileSize,
                        fill="green",
                        width=3,
                        tags=["danglingEdge"]
                    )
            if nodeEdges["E"] == 1:
                # Calculate what the node it is trying to connect to should be
                edgeTarget = "(" + str(nodePosX+1) + ", " + str(nodePosY) + ")"
                # Check that node is not connected to target by a real edge
                if graphData.has_edge(nodeName, edgeTarget):
                    pass
                else:
                    # Draw the line if it dangles and tag it appropriately
                    nodePosGraphX = self.graphCoordToCanvas(nodePosX)
                    nodePosGraphY = self.graphCoordToCanvas(nodePosY)
                    self.create_line(
                        nodePosGraphX,
                        nodePosGraphY,
                        nodePosGraphX + 0.5*tileSize,
                        nodePosGraphY,
                        fill="green",
                        width=3,
                        tags=["danglingEdge"]
                    )
            if nodeEdges["W"] == 1:
                # Calculate what the node it is trying to connect to should be
                edgeTarget = "(" + str(nodePosX-1) + ", " + str(nodePosY) + ")"
                # Check that node is not connected to target by a real edge
                if edgeTarget in graphData.neighbors(nodeName):
                    pass
                else:
                    # Draw the line if it dangles and tag it appropriately
                    nodePosGraphX = self.graphCoordToCanvas(nodePosX)
                    nodePosGraphY = self.graphCoordToCanvas(nodePosY)
                    self.create_line(
                        nodePosGraphX,
                        nodePosGraphY,
                        nodePosGraphX - 0.5*tileSize,
                        nodePosGraphY,
                        fill="green",
                        width=3,
                        tags=["danglingEdge"]
                    )
            if nodeEdges["S"] == 1:
                # Calculate what the node it is trying to connect to should be
                edgeTarget = "(" + str(nodePosX) + ", " + str(nodePosY+1) + ")"
                # Check that node is not connected to target by a real edge
                if edgeTarget in graphData.neighbors(nodeName):
                    pass
                else:
                    # Draw the line if it dangles and tag it appropriately
                    nodePosGraphX = self.graphCoordToCanvas(nodePosX)
                    nodePosGraphY = self.graphCoordToCanvas(nodePosY)
                    self.create_line(
                        nodePosGraphX,
                        nodePosGraphY,
                        nodePosGraphX,
                        nodePosGraphY + 0.5*tileSize,
                        fill="green",
                        width=3,
                        tags=["danglingEdge"]
                    )

    def generateHoverInfo(self, graphData, tileSize):
        # Use an object in the canvas to capture the mouse cursor, it will need to be updated with the information relevant to the tile
        # Place one in each cell of the grid that contains a node
        for node in graphData.nodes.data():
            # Break down the data
            nodeData = node[1]
            nodePosX = nodeData["pos"]["X"]
            nodePosY = nodeData["pos"]["Y"]
            nodeType = nodeData["type"]
            # Create the transparent object
            # Use PIL workaround to create a transparent image, tk.Canvas does not support alpha channels (????)
            tileImage = Image.new('RGBA', (tileSize, tileSize), (255, 255, 255, 0))
            tileImage = ImageTk.PhotoImage(tileImage)
            tileObject = self.create_image(
                nodePosX * tileSize,
                nodePosY * tileSize,
                image=tileImage,
                anchor=tk.NW,
                tags=["infoTile"]
            )
            # Assign the mouseover event to it
            # Tkinter automatically passes the event object to the handler
            self.tag_bind(tileObject, "<Leave>", partial(self.infoHoverEnter, ". . ."))
            self.tag_bind(tileObject, "<Enter>", partial(self.infoHoverEnter, str(node[0])+": "+nodeType.capitalize()))
            

    def infoHoverEnter(self, nodeName, event):
        self.infoBoxFrame = self.parent.parent.infoBox.infoBoxFrame
        self.infoBoxFrame.hoverInfoText.set(nodeName)

    def sortCanvasLayers(self):
        # Orders the stuff on the canvas to a default order
        # Find all objects with each tag
        # Pull them to the front in the right order
        
        # Node icons on top
        objs = self.find_withtag("node")
        for obj in objs:
            self.lift(obj)
        # Invisible infoTile layer
        objs = self.find_withtag("infoTile")
        for obj in objs:
            self.lift(obj)
        print("sort canvas")
        self.setAllLayersVisible()

    def setAllLayersVisible(self):
        # Mark layer states
        self.danglingEdgeVisibility = True
        self.edgeVisibility = True
        self.nodeVisibility = True

        # Update the checkboxes
        self.infoBoxButtons = self.parent.parent.infoBox.infoBoxFrame
        self.infoBoxButtons.danglingEdgeTick.select()
        self.infoBoxButtons.edgeTick.select()
        self.infoBoxButtons.nodeTick.select()

    def toggleDanglingEdgeVisibility(self):
        # Find all objects tagged as "danglingEdge"
        objs = self.find_withtag("danglingEdge")
        # Invert their state
        if self.danglingEdgeVisibility == True:
            self.danglingEdgeVisibility = False
            for obj in objs:
                self.itemconfigure(obj, state='hidden')
        else:
            self.danglingEdgeVisibility = True
            for obj in objs:
                self.itemconfigure(obj, state='normal')

    def toggleEdgeVisibility(self):
        # # Find all objects tagged as "edge"
        objs = self.find_withtag("edge")
        # # Invert their state
        if self.edgeVisibility == True:
            self.edgeVisibility = False
            for obj in objs:
                self.itemconfigure(obj, state='hidden')
        else:
            self.edgeVisibility = True
            for obj in objs:
                self.itemconfigure(obj, state='normal')

    def toggleNodeVisibility(self):
        # Find all objects tagged as "node"
        objs = self.find_withtag("node")
        # Invert their state
        if self.nodeVisibility == True:
            self.nodeVisibility = False
            for obj in objs:
                self.itemconfigure(obj, state='hidden')
        else:
            self.nodeVisibility = True
            for obj in objs:
                self.itemconfigure(obj, state='normal')