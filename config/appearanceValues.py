import tkinter as tk
from tkinter import RIDGE

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
        self.toolBarWidth = 0.15 * screen_width

        # Infobox style
        self.infoBoxHeight = 0.032 * screen_height
        self.infoBoxWidth = 0.7 * screen_width
        self.infoBoxFont = ('Segoe UI', 11, 'bold')

        # Mainview style
        self.mainViewHeight = screen_height - self.infoBoxHeight - window_unusable
        self.mainViewWidth = 0.7 * screen_width
        self.canvasBackgroundColor = "light gray"
        self.canvasDefaultWidth = 2000
        self.canvasDefaultHeight = 2000
        self.canvasTileSize = 48
        self.canvasTileCircleRatio = 0.25
        self.canvasGridlineColor = "black"

        # Contextview style
        self.contextViewHeight = screen_height - window_unusable
        self.contextViewWidth = 0.15 * screen_width

        # Frame style
        self.frameBorderWidth = 5
        self.frameRelief = RIDGE