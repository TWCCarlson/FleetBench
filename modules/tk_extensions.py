import tkinter as tk
from functools import partial

class treeViewMenu(tk.Menu):
    """
        Contextual pop-up menu for use in the treeViews in the context view.
        Needed in order to pass the row data to the functions needed to execute certain 
    """
    def __init__(self, parent):
        super().__init__(parent, tearoff=0)
        self.parent = parent
        self.eventX = None
        self.eventY = None
        self.targetAgent = None

    def add_entry(self, label, command):
        self.add_command(label=label, command=lambda: command(self.targetAgent))
    
    def popup(self, eventX, eventY, eventX_Root, eventY_Root):
        self.eventX = eventX
        self.eventY = eventY
        self.targetAgent = self.parent.agentTreeView.identify_row(self.eventY)
        print("==========")
        print(self.targetAgent)
        self.tk_popup(eventX_Root, eventY_Root)