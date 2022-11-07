import tkinter as tk
from tkinter import ttk

class contextView(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        # Fetch styling
        self.appearanceValues = self.parent.appearance
        frameHeight = self.appearanceValues.contextViewHeight
        frameWidth = self.appearanceValues.contextViewWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief
        # Declare frame
        tk.Frame.__init__(self, parent, height=frameHeight, 
            width=frameWidth, 
            borderwidth=frameBorderWidth, 
            relief=frameRelief)
        # Render frame
        self.grid_propagate(False)
        self.grid(row=0, column=2, rowspan=2, sticky=tk.N)

        self.contextLabelFrame = tk.LabelFrame(self, text="Agent Generator")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.contextLabelFrame.grid(row=0, column=0, sticky=tk.N+tk.E+tk.W, padx=4, columnspan=2)
        self.createAgentButton = tk.Button(self.contextLabelFrame, text="Create Agent. . .", width=15)
        self.contextLabelFrame.columnconfigure(0, weight=1)
        self.createAgentButton.grid(row=0, column=0, pady=4, padx=4, columnspan=1)

        # Create treeView
        self.createTreeView()
        # Initialize scrolling
        self.initScrolling()

    def createTreeView(self):
        self.columnList = {'Name': 50, 'Position': 50, 'Task': 50}
        # Tree view is a stupid fucking widget
        # https://stackoverflow.com/questions/39609865/how-to-set-width-of-treeview-in-tkinter-of-python
        # Create it once, with a single column of nonzero width but all other columns declared, to set the width ???????
        # Then update the object to lock in the requested space
        # Finally reup with everything actually used
        treeViewWidth = self.appearanceValues.contextViewWidth - self.appearanceValues.frameBorderWidth*2 - 21
        self.objectTreeView = ttk.Treeview(self, selectmode='browse')
        self.objectTreeView.grid(row=1, column=0, sticky=tk.S)
        self.objectTreeView["height"] = 20
        self.objectTreeView["columns"] = list(self.columnList.keys()) # list() must be used for this widget
        self.objectTreeView.column('#0', width=int(treeViewWidth))
        # Set other columns to be zero-width for simplicity
        for col in self.columnList:
            print(type(col))
            self.objectTreeView.column(col, width=0)
        self.objectTreeView.update()

        # Set the real column dimensions
        self.objectTreeView.heading('#0', text='im')
        self.objectTreeView.column('#0', width=50, stretch=0)
        # Stretch=True can be used to fill the available space evenly using every column that can stretch
        for col in self.columnList:
            self.objectTreeView.heading(col, text=col)
            self.objectTreeView.column(col, width=self.columnList[col], stretch=True)

        # Prevent column resizing:
        # https://stackoverflow.com/questions/45358408/how-to-disable-manual-resizing-of-tkinters-treeview-column/46120502#46120502
        self.objectTreeView.bind('<Button-1>', self.clickIntercept)
        self.objectTreeView.bind('<Motion>', self.motionIntercept)

    def initScrolling(self):
        # Create scrollbar components
        self.objectTreeView.ybar = tk.Scrollbar(self, orient="vertical")
        self.objectTreeView.xbar = tk.Scrollbar(self, orient="horizontal")

        # Bind the scrollbars to the canvas
        self.objectTreeView.ybar["command"] = self.objectTreeView.yview
        self.objectTreeView.xbar["command"] = self.objectTreeView.xview

        # Adjust positioning, size relative to grid
        self.objectTreeView.ybar.grid(row=1, column=1, sticky="ns")
        self.objectTreeView.xbar.grid(row=2, column=0, sticky="ew")

        # Make canvas update scrollbar position to match its view
        self.objectTreeView["yscrollcommand"] = self.objectTreeView.ybar.set
        self.objectTreeView["xscrollcommand"] = self.objectTreeView.xbar.set

        # Bind mousewheel to interact with the scrollbars
        # Only do this when the cursor is inside this frame
        self.objectTreeView.bind('<Enter>', self.bindMousewheel)
        self.objectTreeView.bind('<Leave>', self.unbindMousewheel)

        # Reset the view
        self.objectTreeView.xview_moveto("0.0")
        self.objectTreeView.yview_moveto("0.0")

    def bindMousewheel(self, event):
        self.bind_all("<MouseWheel>", self.mousewheelAction)
        self.bind_all("<Shift-MouseWheel>", self.shiftMousewheelAction)

    def unbindMousewheel(self, event):
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Shift-MouseWheel>")

    def mousewheelAction(self, event):
        self.objectTreeView.yview_scroll(int(-1*(event.delta/10)), "units")

    def shiftMousewheelAction(self, event):
        self.objectTreeView.xview_scroll(int(-1*(event.delta/10)), "units")

    def clickIntercept(self, event):
        if self.objectTreeView.identify_region(event.x, event.y) == "separator":
            # Prevent click interacting with this region
            return "break"

    def motionIntercept(self, event):
        if self.objectTreeView.identify_region(event.x, event.y) == "separator":
            # Prevent click interacting with this region
            return "break"