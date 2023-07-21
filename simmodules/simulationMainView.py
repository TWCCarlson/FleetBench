import tkinter as tk
import math
import logging

class simMainView(tk.Frame):
    """
        The primary viewfield of the warehouse
        Drawn using tk.Canvas to display robot, task, and map information
    """
    def __init__(self, parent):
        logging.debug("Simulation Main View UI Element initializing . . .")
        self.parent = parent

        # Fetch styling configuration
        self.appearanceValues = self.parent.parent.appearance
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
        self["scrollregion"] = (0,0, self["width"], self["height"])
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
        
        # Re-render the map to display the change
        self.renderGraphState()
        logging.debug(f"Main Canvas dimensions updated: canvasWidth={tileWidth}, canvasHeight={tileHeight}")

    def renderGraphState(self):
        # Reset the canvas to being empty before redrawing
        self.clearMainCanvas()
        # Render grid lines
        self.drawGridlines()
        pass

    def clearMainCanvas(self):
        # Destroys all entities on the canvas
        self.delete("all")
        logging.info("Main simulation canvas cleared.")
