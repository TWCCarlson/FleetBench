import tkinter as tk
from tkinter import ttk
from tkinter.constants import *

class agentTreeViewMenu(tk.Menu):
    """
        Contextual pop-up menu for use in the agent treeViews in the context view.
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
        self.tk_popup(eventX_Root, eventY_Root)

class taskTreeViewMenu(tk.Menu):
    """
        Contextual pop-up menu for use in the task treeViews in the context view.
        Needed in order to pass the row data to the functions needed to execute certain 
    """
    def __init__(self, parent):
        super().__init__(parent, tearoff=0)
        self.parent = parent
        self.eventX = None
        self.eventY = None
        self.targetTask = None

    def add_entry(self, label, command):
        self.add_command(label=label, command=lambda: command(self.targetTask))
    
    def popup(self, eventX, eventY, eventX_Root, eventY_Root):
        self.eventX = eventX
        self.eventY = eventY
        self.targetTask = self.parent.taskTreeView.identify_row(self.eventY)
        self.tk_popup(eventX_Root, eventY_Root)

class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    * Stolen from: https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame
    * Adapted to automatically bind mousewheel actions to scroll the canvas
    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        self.canvas = canvas
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        self.canvas.bind('<Enter>', self.bind_mwheel)
        self.canvas.bind('<Leave>', self.unbind_mwheel)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

    def bind_mwheel(self, *event):
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def unbind_mwheel(self, *event):
        self.canvas.unbind_all("<MouseWheel>")

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")