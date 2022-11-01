import tkinter as tk

from config.appearanceValues import appearanceValues

class infoBox(tk.Frame):
    def __init__(self, parent):
        self.parent = parent

        # Fetch style
        appearanceValues = self.parent.appearance
        frameHeight = appearanceValues.infoBoxHeight
        frameWidth = appearanceValues.infoBoxWidth
        frameBorderWidth = appearanceValues.frameBorderWidth
        frameRelief = appearanceValues.frameRelief

        # Declare frame
        tk.Frame.__init__(self, parent,
            height=frameHeight,
            width=frameWidth,
            borderwidth=frameBorderWidth,
            relief=frameRelief
        )

        # Render frame
        self.grid(row=0, column=1, sticky=tk.N)