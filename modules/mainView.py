import tkinter as tk
import math
import pprint
from functools import partial
from PIL import Image, ImageDraw, ImageTk
pp = pprint.PrettyPrinter(indent=4)
import networkx as nx

class mainView(tk.Frame):
    """
        The primary view of the warehouse, drawn with tk.Canvas layers and organized into a reliable stack
    """
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

    def buildReferences(self):
        # Build references to classes declared after this one
        self.contextView = self.parent.contextView
        self.agentManager = self.parent.agentManager

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
    """
        The primary view of the warehouse, drawn with tk.Canvas layers and organized into a reliable stack
        Probably needs organizational refactor
    """
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

        # Container for highlighted tiles
        self.images = {}

        # Draw gridlines
        self.drawGridlines()

    def drawGridlines(self):
        # Draw them at each tile width
        # self.create_rectangle(0, 0, self["height"], self["width"], fill="red")
        # +1 for the extra line, +1 for making range inclusive
        # Horizontal Lines
        for i in range(math.floor(int(self["height"])/self.canvasTileSize)+1):
            self.create_line(0, i*self.canvasTileSize, self["width"], i*self.canvasTileSize, fill=self.appearanceValues.canvasGridlineColor)
        # Vertical lines
        for i in range(math.floor(int(self["width"])/self.canvasTileSize)+1):
            self.create_line(i*self.canvasTileSize, 0, i*self.canvasTileSize, self["height"], fill=self.appearanceValues.canvasGridlineColor)

    def graphCoordToCanvas(self, coord):
        tileSize = self.appearanceValues.canvasTileSize
        # In: the tile count value for location of the coord
        # Out: the canvas pixel value for location of the coord
        coord = coord * tileSize + 0.5 * tileSize
        return coord

    def renderGraphState(self):
        print("render map data")
        graphData = self.parent.mapData
        # Input: NetworkX graph
        # Output: render the tiles of the map, including
        #   - Node tiles
        #   - Edges
        #   - Colorization by type
        #   - Agents
        #   - Context tiles
        # Style references
        tileSize = self.appearanceValues.canvasTileSize
        nodeSizeRatio = self.appearanceValues.canvasTileCircleRatio
        edgeWidth = self.appearanceValues.canvasEdgeWidth
        # Clear current canvas 
        self.clearMainCanvas()
        # Draw tiles, being sure to tag them for ordering and overlaying
        self.drawGridlines()
        self.renderNodes(graphData, tileSize, nodeSizeRatio)
        self.renderEdges(graphData, edgeWidth)
        self.renderDanglingEdges(graphData, tileSize, edgeWidth)
        self.renderAgents(graphData, tileSize)
        self.generateHoverInfo(graphData, tileSize)
        self.sortCanvasLayers()
        self.checkLayerVisibility()
        
    def renderNodes(self, graphData, tileSize, nodeSizeRatio):
        # Display nodes in graph
        for node in graphData.nodes.data():
            # print(nx.get_node_attributes(graphData, node))
            # print(node)
            # Break down the data
            nodeData = node[1]
            nodePosX = nodeData["pos"]["X"]
            nodePosY = nodeData["pos"]["Y"]
            nodeType = nodeData["type"]

            # print("=========")
            # print(node[1])
            # nx.set_node_attributes(graphData, ' ', node[0])
            # attr = {node[0]: {'agent': 'exists'}}
            # node[1]['agent'] = 'exists'
            # nx.set_node_attributes(graphData, attr)
            # pp.pprint(graphData.nodes.data())
            # del graphData.nodes[node[0]]['agent']
            # pp.pprint(graphData.nodes.data())

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

    def renderEdges(self, graphData, edgeWidth):
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
                width = edgeWidth,
                tags=["edge"]
            )

    def renderDanglingEdges(self, graphData, tileSize, edgeWidth):
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
                        width=edgeWidth,
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
                        width=edgeWidth,
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
                        width=edgeWidth,
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
                        width=edgeWidth,
                        tags=["danglingEdge"]
                    )

    def renderAgents(self, graphData, tileSize):
        # Renders agent positions and orientations
        print("render agents")

        # Render the agent position direct from the graph object
        # pp.pprint(graphData.nodes(data=True))
        for node in graphData.nodes(data=True):
            if 'agent' in graphData.nodes.data()[node[0]]:
                # Extract the reference to the agent object with a shallow copy
                agentRef = graphData.nodes.data()[node[0]]['agent']
                # Extract position data, convert to canvas coordinates and centralize
                nodePosX = agentRef.position[0]
                centerPosX = nodePosX * tileSize + 0.5 * tileSize
                nodePosY = agentRef.position[1]
                centerPosY = nodePosY * tileSize + 0.5 * tileSize
                # Extract the agent orientation
                agentOrientation = agentRef.orientation
                # Tag the agent for layer sorting
                tag = ["agent" + str(agentRef.ID), "agent"]
                # Dictionary of points for the polygon
                dirDict = {
                    "N": (centerPosX, centerPosY - 0.4 * tileSize),
                    "W": (centerPosX - 0.4 * tileSize, centerPosY),
                    "S": (centerPosX, centerPosY + 0.4 * tileSize),
                    "E": (centerPosX + 0.4 * tileSize, centerPosY)
                }
                # Draw the polygon representing the agent
                self.create_polygon(
                    dirDict["N"][0],
                    dirDict["N"][1],
                    dirDict["W"][0],
                    dirDict["W"][1],
                    dirDict["S"][0],
                    dirDict["S"][1],
                    dirDict["E"][0],
                    dirDict["E"][1],
                    outline='black',
                    width = 2,
                    fill='orange',
                    tags=tag
                )

                # Arrow tags should include a sorting tag
                tag.append("agentOrientation")

                # Draw the orientation arrow
                self.create_line(
                    dirDict[agentOrientation][0],
                    dirDict[agentOrientation][1],
                    centerPosX,
                    centerPosY,
                    arrow = tk.FIRST,
                    tags=tag,
                    fill='white',
                    width=4
                )
                # print(f"{node} contains agent")
            else:
                # print(f"{node} does not contain an agent")
                pass

    def agentClickHighlighter(self, agentName, agentID, event):
        # Remove previous highlighting
        self.clearHighlight()

        print(f"agentName: {agentName}, agentID: {agentID}")

        # Find iid for specified agent in the treeview
        agentIID = self.parent.contextView.agentTreeView.tag_has(agentName)

        # Set the selection to include the agent
        # self.parent.contextView.objectTreeView.see(agentIID)
        self.parent.contextView.agentTreeView.selection_set(agentIID)

        # Highlight the agent
        agentRef = self.parent.agentManager.agentList.get(agentID)
        print(agentRef)
        agentRef.highlightAgent(multi=False)

        # Update the selection tracker
        self.parent.parent.agentManager.currentAgent = agentID
        print(self.parent.parent.agentManager.currentAgent)
        
        # Update movement choices for the selected agent
        self.parent.parent.contextView.validateMovementButtonStates()

    def generateHoverInfo(self, graphData, tileSize):
        # Use an object in the canvas to capture the mouse cursor, it will need to be updated with the information relevant to the tile
        # Place one in each cell of the grid that contains a node
        for node in graphData.nodes.data():
            # pp.pprint(node)
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
            # If there is an agent in the node, include it in the hoverinfo text
            if 'agent' in nodeData:
                nodeAgentName = nodeData['agent'].ID
                nodeAgentID = nodeData['agent'].numID
                hoverString = f"{str(node[0])}: {nodeType.capitalize()}, Agent Name: {nodeAgentName}"

                # Further, make clicks on this hovertile select the agent
                self.tag_bind(tileObject, "<Button-1>", partial(self.agentClickHighlighter, nodeAgentName, nodeAgentID))
            else:
                hoverString = f"{str(node[0])}: {nodeType.capitalize()}"

            # Assign the mouseover event to it
            # Tkinter automatically passes the event object to the handler
            self.tag_bind(tileObject, "<Leave>", partial(self.infoHoverEnter, ". . ."))
            self.tag_bind(tileObject, "<Enter>", partial(self.infoHoverEnter, hoverString))
            
    def infoHoverEnter(self, hoverString, event):
        self.infoBoxFrame = self.parent.parent.infoBox.infoBoxFrame
        self.infoBoxFrame.hoverInfoText.set(hoverString)

    def sortCanvasLayers(self):
        # Orders the stuff on the canvas to a default order
        # Find all objects with each tag
        # Pull them to the front in the right order
        
        # Node icons
        objs = self.find_withtag("node")
        for obj in objs:
            self.lift(obj)
        # Agent icons
        objs = self.find_withtag("agent")
        for obj in objs:
            self.lift(obj)
        # Agent orientation indicators
        objs = self.find_withtag("agentOrientation")
        for obj in objs:
            self.lift(obj)
        # Invisible infoTile layer
        objs = self.find_withtag("infoTile")
        for obj in objs:
            self.lift(obj)
        print("sort canvas")
        # self.setAllLayersVisible()

    def setAllLayersVisible(self):
        # Mark layer states
        self.danglingEdgeVisibility = True
        self.edgeVisibility = True
        self.nodeVisibility = True
        self.agentVisibility = True
        self.agentOrientationVisibility = True

        # Update the checkboxes
        self.infoBoxButtons = self.parent.parent.infoBox.infoBoxFrame
        self.infoBoxButtons.danglingEdgeTick.select()
        self.infoBoxButtons.edgeTick.select()
        self.infoBoxButtons.nodeTick.select()
        self.infoBoxButtons.agentTick.select()
        self.infoBoxButtons.agentOrientationTick.select()

    def checkLayerVisibility(self):
        layerStates = {
            "danglingEdge": self.danglingEdgeVisibility,
            "edge": self.edgeVisibility,
            "node": self.nodeVisibility,
            "agent": self.agentVisibility,
            "agentOrientation": self.agentOrientationVisibility
        }
        for layer in layerStates:
            self.setLayerVisibility(layer, layerStates[layer])

    def clearMainCanvas(self):
        print("wipe canvas")
        self.delete("all")

    def setLayerVisibility(self, layerTag, desiredState):
        # print(f"Layer '{layerTag}' set to '{desiredState}'")
        objs = self.find_withtag(layerTag)
        if desiredState == True:
            for obj in objs:
                self.itemconfigure(obj, state='normal')
        elif desiredState == False:
            for obj in objs:
                self.itemconfigure(obj, state='hidden')

    def toggleLayerVisibility(self, layerTag, state):
        # Find all the objects with the matching tag
        objs = self.find_withtag(layerTag)
        # Toggle their state and visibility
        if state == True:
            state = False
            for obj in objs:
                self.itemconfigure(obj, state='hidden')
        else:
            state = True
            for obj in objs:
                self.itemconfigure(obj, state='normal')
        return state

    def toggleDanglingEdgeVisibility(self):
        self.danglingEdgeVisibility = self.toggleLayerVisibility("danglingEdge", self.danglingEdgeVisibility)

    def toggleEdgeVisibility(self):
        self.edgeVisibility = self.toggleLayerVisibility("edge", self.edgeVisibility)

    def toggleNodeVisibility(self):
        self.nodeVisibility = self.toggleLayerVisibility("node", self.nodeVisibility)

    def toggleAgentVisibility(self):
        self.agentVisibility = self.toggleLayerVisibility("agent", self.agentVisibility)

    def toggleAgentOrientationVisibility(self):
        self.agentOrientationVisibility = self.toggleLayerVisibility("agentOrientation", self.agentOrientationVisibility)

    def highlightTile(self, tileIDX, tileIDY, color, multi, highlightType):
        # print("highlight: (" + str(tileIDX) + ", " + str(tileIDY) + ")")
        # print(f"With: {color}, multi={multi}, and type {highlightType}")
        # Clear the old highlights before drawing this singular highlight
        if multi == False:
            self.clearHighlight(highlightType)
            # print(f"cleared old highlight of type {highlightType}")
        # Draw a translucent highlight over the indicated cell for user guidance
        # tileSize = self.appearanceValues.canvasTileSize
        if isinstance(tileIDX, str):
            tileSize = self.appearanceValues.canvasTileSize
            self.create_rect(
                eval(tileIDX) * tileSize,
                eval(tileIDY) * tileSize,
                eval(tileIDX) * tileSize + tileSize,
                eval(tileIDY) * tileSize + tileSize,
                anchor=tk.NW,
                fill=color,
                alpha=0.3,
                tags=["highlight", highlightType]
            )
        else:
            tileSize = self.appearanceValues.canvasTileSize
            self.create_rect(
                tileIDX * tileSize,
                tileIDY * tileSize,
                tileIDX * tileSize + tileSize,
                tileIDY * tileSize + tileSize,
                anchor=tk.NW,
                fill=color,
                alpha=0.3,
                tags=["highlight", highlightType]
            )
        # Re-sort the layers so the infolayer is not hidden by the highlight
        self.sortCanvasLayers()

    def clearHighlight(self, highlightType=None):
        # Unsafe function, doesn't check that the kind of removal requested actually exists, fails silently too
        # Remove all objects tagged "highlight" if a type isn't specified
        if highlightType == None:
            self.images = {}
            objs = self.find_withtag("highlight")
            for obj in objs:
                self.delete(obj)
        # If a type is specified, only delete highlights of that type
        else:
            objs = self.find_withtag(highlightType)
            for obj in objs:
                self.delete(obj)
            for image in list(self.images.keys()):
                if highlightType in self.images[image]:
                    del self.images[image]

    def create_rect(self, x1, y1, x2, y2, **kwargs):
        # https://stackoverflow.com/questions/54637795/how-to-make-a-tkinter-canvas-rectangle-transparent
        # Modified for passing 'anchor' and 'tags' as kwargs
        if 'alpha' in kwargs:
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            anchor = kwargs.pop('anchor')
            tags = kwargs.pop('tags')
            fill = self.parent.parent.winfo_rgb(fill) + (alpha,)
            image = Image.new('RGBA', (x2-x1, y2-y1), fill)
            tkImage = ImageTk.PhotoImage(image)
            self.images[tkImage] = tags
            self.create_image(x1, y1, image=tkImage, anchor=anchor, tags=tags)
