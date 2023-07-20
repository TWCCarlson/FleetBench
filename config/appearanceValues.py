import tkinter as tk
from tkinter import RIDGE
import logging

class appearanceValues():
    def __init__(self, parent):
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
        self.canvasEdgeWidth = 4

        # Contextview style
        self.contextViewHeight = screen_height - window_unusable
        self.contextViewWidth = 0.2 * screen_width

        # Frame style
        self.frameBorderWidth = 5
        self.frameRelief = RIDGE

        """
            Simulation window values
        """
        # Simulation Main Canvas Style
        self.simulationWindowWidth = 0.75 * screen_width
        self.simulationWindowHeight = screen_height - window_unusable

        # Simulation info box style
        self.simulationInfoBoxWidth = 0.75 * screen_width
        self.simulationInfoBoxHeight = 0.032 * screen_height
        self.simulationInfoBoxFont = ('Segoe UI', 11, 'bold')

        # Simulation control panel style
        self.simulationControlBoxWidth = 0.25 * screen_width
        self.simulationControlBoxHeight = 0.2 * (screen_height - window_unusable)

        # Simulation information panel style
        self.simulationInfoPanelWidth = 0.25 * screen_width
        self.simulationInfoPanelHeight = 0.8 * (screen_height - window_unusable)

        logging.info("Appearance configuration settings loaded.")