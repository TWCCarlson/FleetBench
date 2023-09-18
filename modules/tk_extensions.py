import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
from tkinter import font as tkfont
import pprint
pp = pprint.PrettyPrinter(indent=1)

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

class ConfigOptionSet(tk.Frame):
    """
        UI Element builder
        Always creates a label - element pair
        Currently the elements available are:
            - tk.OptionMenu
            - ttk.Spinbox (numeric, validated)
        Unless a specific row-column tuple is given, tacks the entry onto the next row
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.parent = parent
        self.childElements = {}

        # Place this containing frame
        parentGridSize = parent.grid_size()   # (Column, row) tuple
        if isinstance(parent, ConfigOption):
            self.grid(row=0, column=parentGridSize[0], sticky=tk.W)
        else:
            self.grid(row=parentGridSize[1], column=0, sticky=tk.W)

    def buildOutOptionSetUI(self, uiDefineDict):
        for element in uiDefineDict:
            self.childElements[element["labelText"][:-1]] = ConfigOption(self, element)
        
class ConfigOption(tk.Frame):
    """
        UI Element builder
        Always creates a label - element pair
        Currently the elements available are:
            - tk.OptionMenu
            - ttk.Spinbox (numeric, validated)
        Unless a specific row-column tuple is given, tacks the entry onto the next row
    """
    def __init__(self, parent, elementData, **kwargs):
        super().__init__(parent)
        self.parent = parent

        # Place this containing frame
        parentGridSize = parent.grid_size()   # (Column, row) tuple
        if isinstance(parent, ConfigOptionSet):
            self.grid(row=parentGridSize[1], column=0, sticky=tk.W)
        else:
            self.grid(row=parentGridSize[1], column=0, sticky=tk.W)

        type = elementData["elementType"]
        if type == "optionMenu" or type == "numericSpinbox" or type == "checkButton":
            self._addUIElements(elementData=elementData)
        elif type == "descriptiveTracedText" or type=="descriptiveText":
            self._addCustomText(elementData=elementData)

    def _addCustomText(self, elementData):
        if elementData["elementType"] == "descriptiveTracedText":
            # Create the label to contain text
            self.descriptiveText = tk.Text(self, fg="black", bg="SystemButtonFace", bd=0, font=(tkfont.nametofont("TkDefaultFont")))
            self.descriptiveText.configure(state=tk.DISABLED, height=0)
            self.descriptiveText.grid(row=0, column=0)

            # Trace the target variable
            optionValue = elementData["optionValue"]
            elementData["optionValue"].trace_add("write", lambda *args, currentValue=optionValue, elementData=elementData: self._updateDescriptiveTracedText(elementData, currentValue.get()))

    def _updateDescriptiveTracedText(self, elementData, currentValue):
        # Enable editing the text field
        self.descriptiveText.configure(state=tk.NORMAL)

        # Clear the text
        self.descriptiveText.delete('1.0', tk.END)

        for lineOfText in elementData["elementData"]:
            # Fetch formula and calculate
            calcValue = eval(lineOfText["formula"])
            
            # Insert text to descriptiveText
            self.descriptiveText.insert(tk.END, eval(lineOfText["string"][0]) + "\n")

        self.descriptiveText.configure(state=tk.DISABLED, height=len(elementData["elementData"]))

    def _addUIElements(self, elementData):
        # Always create a label
        labelWidget = self._addLabel(elementData=elementData)

        # Identify the target row/column
        gridLoc = self._findNextWidgetLoc()

        # Render the elements
        labelWidget.grid(row=gridLoc[1], column=0)

        # Check the requested element type
        if elementData["elementType"] == "optionMenu":
            inputWidget = self._addOptionMenu(elementData=elementData)
            inputWidget.grid(row=gridLoc[0], column=1)
            self._traceOptionMenu(elementData=elementData)
            # Set the default value
            elementData["optionValue"].set(list(elementData["elementData"].keys())[0])
        elif elementData["elementType"] == "numericSpinbox":
            inputWidget = self._addNumericSpinbox(elementData=elementData)
            inputWidget.grid(row=gridLoc[0], column=1)
        elif elementData["elementType"] == "checkButton":
            inputWidget = self._addCheckButton(elementData=elementData)
            inputWidget.grid(row=gridLoc[0], column=1)

            # If there are no other element datas provided, stop here
            if elementData["elementData"] == None:
                return

            # Build out suboptions
            for key, newElementData in elementData["elementData"].items():
                tempRef = ConfigOptionSet(self)
                tempRef.buildOutOptionSetUI(newElementData)
                setattr(self, key, tempRef)

            # Build a trace that toggles usability of suboptions
            self._traceCheckButton(elementData=elementData)
            # Set the default value
            elementData["optionValue"].set(elementData["elementDefault"])

    def _addLabel(self, elementData):
        # Build the label
        self.labelWidget = tk.Label(self, text=elementData["labelText"])
        return self.labelWidget

    def _addOptionMenu(self, elementData):
        # Build the menu
        self.menuWidget = tk.OptionMenu(self, elementData["optionValue"], *list(elementData["elementData"].keys()))
        return self.menuWidget

    def _traceOptionMenu(self, elementData):
        # Reference to the optionMenu control variable
        optionValue = elementData["optionValue"]
        optionValue.trace_add("write", lambda *args, menuChoice=optionValue, elementData=elementData: self._createSuboptions(elementData=elementData, menuChoice=menuChoice.get()))

    def _createSuboptions(self, elementData, menuChoice):
        self._clearSubframes()

        if elementData["elementData"][menuChoice] == None:
            return
        
        tempRef = ConfigOptionSet(self)
        tempRef.buildOutOptionSetUI(elementData["elementData"][menuChoice])
        setattr(self, menuChoice, tempRef)
        
    def _clearSubframes(self):
        # Destroy all widgets inside child frames of the passed frames, and the child frames themselves
        # Find all child widgets
        for widget in self.winfo_children():
            # Identify which ones are frames
            if isinstance(widget, tk.Frame):
                # Destroy the frame—all children are also automatically destroyed
                # https://www.tcl.tk/man/tcl8.6/TkCmd/destroy.html
                # "This command deletes the windows given by the window arguments, plus all of their descendants."
                widget.destroy()

    def _addNumericSpinbox(self, elementData):
        # Get spinbox range, increment
        spinboxMin = elementData["elementData"][0]
        spinboxMax = elementData["elementData"][1]
        spinboxInc = elementData["elementData"][2]

        # Create the validating function registry
        self.validateNumericSpinboxFunc = self.register(self._validateNumericSpinbox)

        # Build the spinbox
        self.spinboxWidget = ttk.Spinbox(self,
            width=6, from_=spinboxMin, to=spinboxMax, increment=spinboxInc,
            textvariable=elementData["optionValue"], validate='key',
            validatecommand=(self.validateNumericSpinboxFunc, '%P'))
        
        # Set the default value
        elementData["optionValue"].set("" if elementData["elementDefault"] == None else elementData["elementDefault"])

        return self.spinboxWidget

    def _validateNumericSpinbox(self, inputString):
        if inputString.isnumeric():
            # Only allow numeric characters
            return True
        elif len(inputString) == 0:
            # Or an empty box
            return True
        else:
            return False

    def _addCheckButton(self, elementData):
        # Build the checkbutton widget
        self.checkButtonWidget = tk.Checkbutton(self, variable=elementData["optionValue"])

        # Assign a default value
        elementData["optionValue"].set(elementData["elementDefault"])
        return self.checkButtonWidget
    
    def _traceCheckButton(self, elementData):
        optionValue = elementData["optionValue"]
        optionValue.trace_add("write", lambda *args, checkButtonState=optionValue: self._toggleSuboptionUsability(optionChoice=checkButtonState.get()))

    def _toggleSuboptionUsability(self, optionChoice):
        # Set the activity state of all child widgets
        for child in self.winfo_children():
            if optionChoice == False:
                self.setChildrenStates(child, tk.DISABLED)
            elif optionChoice == True:
                self.setChildrenStates(child, tk.NORMAL)

    def setChildrenStates(self, parent, newState):
        for child in parent.winfo_children():
            # Frame type tk objects lack a state field, exclude them
            wtype = child.winfo_class()
            if wtype not in ("Frame", "Labelframe"):
                child.configure(state=newState)
            else:
                self.setChildrenStates(child, newState)

    def _findNextWidgetLoc(self):
        # Grid lengths are larger than the rendered size by 1, so the "next" row is directly found
        gridLoc = self.grid_size()
        return gridLoc