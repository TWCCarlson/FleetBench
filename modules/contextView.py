import tkinter as tk

class contextView(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        # Fetch styling
        appearanceValues = self.parent.appearance
        frameHeight = appearanceValues.contextViewHeight
        frameWidth = appearanceValues.contextViewWidth
        frameBorderWidth = appearanceValues.frameBorderWidth
        frameRelief = appearanceValues.frameRelief
        # Declare frame
        tk.Frame.__init__(self, parent, height=frameHeight, 
            width=frameWidth, 
            borderwidth=frameBorderWidth, 
            relief=frameRelief)
        # Render frame
        self.grid(row=0, column=2, rowspan=2, sticky=tk.N)