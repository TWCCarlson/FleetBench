import tkinter as tk
from tkinter import RIDGE
import logging

class appearanceValues():
    def __init__(self, parent):
        """
            Node style values
        """
        self.openNodeColor = "black"
        self.openNodeSizeRatio = 0.1
        self.chargeNodeColor = "sandy brown"
        self.chargeNodeSizeRatio = 0.28
        self.depositNodeColor = "light green"
        self.depositNodeSizeRatio = 0.28
        self.pickupNodeColor = "light blue"
        self.pickupNodeSizeRatio = 0.28
        self.restNodeColor = "brown"
        self.restNodeSizeRatio = 0.28

        """
            Edge style values
        """
        self.edgeColor = "black"
        self.edgeWidth = 5
        self.danglingEdgeColor = "green"
        self.danglingEdgeWidth = 5

        """
            Agent style values
        """
        self.agentSizeRatio = 0.4
        self.agentBorderColor = 'gray50'
        self.agentBorderWidth = 2
        self.agentFillColor = 'orange'
        self.agentPointerWidth = 3
        self.agentWindowRatio = 0.12
        self.agentWindowWidth = 1

        """
            Highlight style values
        """
        self.highlightAlpha = 0.5
        self.depositHighlightColor = "light blue"
        self.pickupHighlightColor = "light green"
        self.agentHighlightColor = "red"
        self.pathfindHighlightColor = "purple4"
        self.highlightTextSize = 8
        self.defaultHighlightColor = "orange red"

        """
            Misc. Canvas item style values
        """
        self.defaultTextColor = "white"
        self.canvasArrowDefaultColor = "white"
        self.canvasArrowDefaultWidth = 3

        """
            Editor window style
        """

        self.parent = parent
        # Get screen dimensions for fractional measurements
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        window_unusable = screen_height * 0.04
        # Set app to maximized
        self.parent.state('zoomed')

        # Toolbar style
        self.toolBarHeight = screen_height - window_unusable
        self.toolBarWidth = 0.2 * screen_width

        # Infobox style
        self.infoBoxHeight = 0.032 * screen_height
        self.infoBoxWidth = 0.60 * screen_width
        self.infoBoxFont = ('Segoe UI', 11, 'bold')

        # Mainview style
        self.mainViewHeight = screen_height - self.infoBoxHeight - window_unusable
        self.mainViewWidth = 0.60 * screen_width
        self.canvasBackgroundColor = "light gray"
        self.canvasDefaultWidth = 2000
        self.canvasDefaultHeight = 2000
        self.canvasTileSize = 48
        self.canvasTileCircleRatio = 0.28
        self.canvasGridlineColor = "black"
        self.canvasEdgeWidth = 6

        # Contextview style
        self.contextViewHeight = screen_height - window_unusable
        self.contextViewWidth = 0.2 * screen_width

        # Frame style
        self.frameBorderWidth = 5
        self.frameRelief = RIDGE

        """
            Simulation window values
        """

        # Simulation info box style
        self.simulationInfoBoxWidth = 0.8 * screen_width
        self.simulationInfoBoxHeight = 0.032 * screen_height
        self.simulationInfoBoxFont = ('Segoe UI', 11, 'bold')

        # Simulation Main Canvas Style
        self.simulationMainViewWidth = 0.8 * screen_width
        self.simulationMainViewHeight = screen_height - self.simulationInfoBoxHeight - window_unusable
        self.simCanvasBackgroundColor = "white"
        self.simCanvasDefaultWidth = 2000
        self.simCanvasDefaultHeight = 2000
        self.simCanvasTileSize = 48
        self.simCanvasTileCircleRatio = 0.28
        self.simCanvasGridlineColor = "light gray"
        self.simCanvasEdgeWidth = 4

        # Simulation control panel style
        self.simulationControlBoxWidth = 0.2 * screen_width
        self.simulationControlBoxHeight = 0.032 * screen_height

        # Simulation information panel style
        self.simulationInfoPanelWidth = 0.2 * screen_width
        self.simulationInfoPanelHeight = screen_height - self.simulationControlBoxHeight - window_unusable

        logging.info("Appearance configuration settings loaded.")