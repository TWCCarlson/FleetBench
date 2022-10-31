from tkinter import RIDGE

class appearanceValues():
    def __init__(self, parent):
        # Toolbar style
        self.toolBarHeight = 1030
        self.toolBarWidth = 325

        # Mainview style
        self.mainViewHeight = 1030
        self.mainViewWidth = 1250
        self.canvasBackgroundColor = "light gray"
        self.canvasDefaultWidth = 2000
        self.canvasDefaultHeight = 2000
        self.canvasTileSize = 48
        self.canvasTileCircleRatio = 0.25
        self.canvasGridlineColor = "black"

        # Contextview style
        self.contextViewHeight = 1030
        self.contextViewWidth = 335

        # Frame style
        self.frameBorderWidth = 5
        self.frameRelief = RIDGE