import tkinter as tk
from tkinter import ttk
import logging
import pprint
pp = pprint.PrettyPrinter(indent=4)
import numpy as np
import itertools
import modules.tk_extensions as tk_e

from collections import Counter

# For graphs embedded in tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class simulationConfigManager(tk.Toplevel):
    # Window for managing the state of the simulation configuration
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        logging.info("Simulation Configuration Manager Class gen")
        self.title("Simulation Configuration Window")
        self.focus()     # "Select" the window
        self.grab_set()  # Forcefully keep attention on the window

        # Some things need to be precalculated to inform the user while they make decisions regarding simulation setup
        self.precalculateTaskGenerationTabInformation()

        # Building a notebook; each page contains a set of options
        self.configNotebook = ttk.Notebook(self)

        # Each page needs a space to insert widgets
        self.pathfindingAlgorithmFrame = tk.Frame(self.configNotebook)
        self.taskGenerationFrame = tk.Frame(self.configNotebook)
        self.displayOptionsFrame = tk.Frame(self.configNotebook)

        # Tabnames-tabframes,tabbuildfunction dictionary
        noteBookTabs = {
            "Pathfinding Algorithm": (self.pathfindingAlgorithmFrame, self.buildPathfindingAlgorithmPage),
            "Task Generation": (self.taskGenerationFrame, self.buildTaskGenerationPage),
            "Display Options": (self.displayOptionsFrame, self.buildDisplayOptionsPage)
        }

        # Add all pages to the notebook and build their content
        for tabName, (tabFrame, tabBuildFunction) in noteBookTabs.items():
            self.configNotebook.add(tabFrame, text=tabName)
            tabBuildFunction()

        # Render the notebook in the window
        self.configNotebook.grid(row=0, column=0)

        # State holder class
        self.simulationConfigurationState = simulationConfigurationState(self)

        # Simulation start button
        self.simulationLaunch = tk.Button(self, text="Launch Simulation", command=self.launchSimulation)
        self.simulationLaunch.grid(row=1, column=0)

    def precalculateTaskGenerationTabInformation(self):
        # Retrieving information useful to the user about the simulation map
        # First get the list of all optimal paths
        nodeTypeDict = self.parent.mapData.generateNodeListsByType()
        dictOfOptimalTaskPaths = self.parent.mapData.generateAllTaskShortestPaths(nodeTypeDict['pickup'], nodeTypeDict['deposit'])
        optimalTaskPaths = list()
        for pickupNode, dropoffPaths in dictOfOptimalTaskPaths.items():
            for dropoffNode, path in dropoffPaths.items():
                optimalTaskPaths.append(path)
                # print(f"{pickupNode}->{dropoffNode}: {path}")

        # Calculate the lengths of each path
        # Note that this is inclusive, so that amount of steps it takes to actually complete these tasks is len-1
        optimalTaskPathLengths = list()
        for path in optimalTaskPaths:
            optimalTaskPathLengths.append(len(path))

        # Calculating relevant statistics about optimal paths for use in the GUI
        self.taskPathLengthCountDict = Counter(optimalTaskPathLengths)          # Count of the number of tasks (value) with a specific length (key)
        optimalTaskPathLengthsArray = np.asarray(optimalTaskPathLengths)        # Converting to a numpy array to utilise numpy functions
        self.meanOptimalTaskPathLength = np.mean(optimalTaskPathLengthsArray)   # Unweighted average of optimal path lengths
        self.standardDeviationOptimalTaskPathLength = np.std(optimalTaskPathLengthsArray)   # Standard deviation of optimal path lengths
        self.maximumOptimalPathLength = np.max(optimalTaskPathLengthsArray)     # Longest length of an optimal path
        self.minimumOptimalPathLength = np.min(optimalTaskPathLengthsArray)     # Shortest length of an optimal path
        self.medianOptimalTaskPathLength = np.median(optimalTaskPathLengthsArray)   # Median length of optimal paths

        # Maximum optimal traversal distance from anywhere in the warehouse to anywhere in the warehouse
        # Turns out this is NP hard and probably not all that useful anyway

    def buildPathfindingAlgorithmPage(self):
        # Intermediate function grouping together declarations and renders for the algorithm choices page
        self.createAlgorithmOptions()

    def buildTaskGenerationPage(self):
        # Intermediate function grouping together declarations and renders for the task generation page
        self.taskGenerationRateFrame = tk.Frame(self.taskGenerationFrame)
        self.taskGenerationRateFrame.grid(row=0, column=0)
        self.createTaskFrequencyOptions()
        self.taskStatisticsFrame = tk.Frame(self.taskGenerationFrame)
        self.taskStatisticsFrame.grid(row=1, column=0)
        self.createTaskInformationPane()
        self.taskLocationFrame = tk.LabelFrame(self.taskGenerationFrame, text="Node Weights")
        self.taskLocationFrame.grid(row=0, column=1, rowspan=2)
        self.createTaskLocationOptions()

    def buildDisplayOptionsPage(self):
        # Intermediate function grouping together declarations and renders for the display options page
        self.createSimulationUpdateRate()

    def launchSimulation(self):
        simulationSettings = self.packageSimulationConfiguration()
        self.parent.launchSimulator(simulationSettings)

    def packageSimulationConfiguration(self):
        """
            Packages the current simulation configuration for saving
        """
        dataPackage = {}
        dataPackage["algorithmSelection"] = self.algorithmSelectionStringVar.get()
        dataPackage["playbackFrameDelay"] = self.frameDelayValue.get()
        dataPackage["taskGenerationFrequencyMethod"] = self.taskFrequencySelectionStringvar.get()

        return dataPackage
    
    def createAlgorithmOptions(self):
        # Creates a drop down menu for the user to select the driving algorithm for the simulation
        # Using types to separate multi-agent and single-agent pathfinding algorithms
        optionTypeDict = {
            "Dummy": "mapf",
            "Single-agent A*": "sapf"
        }

        # Keys of the dict are the displayed options
        algorithmOptions = list(optionTypeDict.keys())

        # Stringvar to hold the algorithm selection
        self.algorithmSelectionStringVar = tk.StringVar()

        # Set a default selection - maybe skip this to force a choice
        self.algorithmSelectionStringVar.set(algorithmOptions[0])

        # Declare the drop down menu
        self.algorithmChoiceMenu = tk.OptionMenu(self.pathfindingAlgorithmFrame, self.algorithmSelectionStringVar, *algorithmOptions)

        # If there is more than one agent in the simulation space, disable single-agent pathfinding algorithm options
        for algorithm, type in optionTypeDict.items():
            if type == "sapf" and len(self.parent.agentManager.agentList) > 1:
                self.algorithmChoiceMenu['menu'].entryconfigure(algorithm, state=tk.DISABLED)

        # Render the menu
        self.algorithmChoiceMenu.grid(row=1, column=0)

    def createTaskInformationPane(self):
        # Creates a graph and text field that displays statistical information about the possible tasks in the warehouse to the user
        # Separate this area from the option gui area
        ttk.Separator(self.taskStatisticsFrame, orient="horizontal").grid(row=1, column=0, sticky=tk.E+tk.W, pady=4, padx=4)
        ttk.Separator(self.taskStatisticsFrame, orient="horizontal").grid(row=3, column=0, sticky=tk.E+tk.W, pady=4, padx=4)

        # Create the figure that will contain the plot
        self.taskInfoFigure = Figure(figsize=(5,2), dpi=100)
        self.taskInfoPlot = self.taskInfoFigure.add_subplot(111)
        # Set the background color of the figure to match the window; matplotlib wants RGB scaled 0-1, while tkinter provides 16-bit rgb
        systemButtonFaceRGB = np.array(self.winfo_rgb("SystemButtonFace"))
        self.taskInfoFigure.set_facecolor(np.divide(systemButtonFaceRGB, 2**16))

        # Define the plot
        self.taskInfoPlot.bar(self.taskPathLengthCountDict.keys(), self.taskPathLengthCountDict.values())
        self.taskInfoPlot.set_xticks(list(range(0, self.maximumOptimalPathLength+1)))
        self.taskInfoPlot.set_xlabel("Optimal Task Path Lengths (steps)")
        self.taskInfoPlot.set_ylabel("Count")
        self.taskInfoPlot.set_title("All Possible Task Optimal Paths")

        # Create the tkinter object using matplotlib's backend, and render it to the page frame
        self.taskInfoCanvasWidget = FigureCanvasTkAgg(self.taskInfoFigure, self.taskStatisticsFrame)
        self.taskInfoCanvasWidget.draw()
        self.taskInfoCanvasWidget.get_tk_widget().grid(row=2, column=0)

        # Mark the mean value with a line on the plot
        self.taskInfoPlot.axvline(self.meanOptimalTaskPathLength, color='r')

        # Create a containing frame for the text widget, to control its size
        self.taskInfoTextFrame = tk.Frame(self.taskStatisticsFrame, width=self.winfo_width(), height=100)
        self.taskInfoTextFrame.grid(row=4, column=0, sticky="news")
        self.taskInfoTextFrame.grid_propagate(False)

        # Create some text providing statistical information about the optimal task paths
        self.taskInfoText = tk.Text(self.taskInfoTextFrame, fg="black", bg="SystemButtonFace", bd=0, font=("Helvetica", 10, "bold"))
        self.taskInfoText.tag_configure("red", foreground="red")
        self.taskInfoText.insert(tk.END, "Statistical Data for all possible optimal task paths: \n")
        self.taskInfoText.insert(tk.END, f"\tMean optimal path length: {round(self.meanOptimalTaskPathLength, 2)}\n", "red")
        self.taskInfoText.insert(tk.END, f"\tMax optimal path length: {self.maximumOptimalPathLength}\n")
        self.taskInfoText.insert(tk.END, f"\tMin optimal path length: {self.minimumOptimalPathLength}\n")
        self.taskInfoText.insert(tk.END, f"\tMedian optimal path length: {self.medianOptimalTaskPathLength}\n")
        self.taskInfoText.insert(tk.END, f"\tOptimal path length standard deviation: {round(self.standardDeviationOptimalTaskPathLength, 2)}")
        self.taskInfoText.configure(state=tk.DISABLED, height=6)

        # Render the text
        self.taskInfoText.grid(row=0, column=0)

    def createTaskFrequencyOptions(self):
        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskFrequencyChoicesFrame = tk.Frame(self.taskGenerationRateFrame)

        # Creates a drop-down for task frequency type
        # Based on selection, creates options specific to the frequency type
        self.taskFrequencyMethodOptionsLabel = tk.Label(self.taskFrequencyChoicesFrame, text="Task Gen. Freq.:")

        # Dict pairing options and respective ui creation functions
        taskFrequencyMethodOptionsDict = {
            "Fixed Rate": self.buildFixedRateTaskGenerationOptions,
            "As Available": self.buildAsAvailableTaskGenerationOptions
        }

        # Menu options are the text in the dict keys
        taskFrequencyMethodMenuOptions = list(taskFrequencyMethodOptionsDict.keys())

        # Stringvar to hold the option selection
        self.taskFrequencySelectionStringvar = tk.StringVar()

        # Add a trace to the stringvar to call the associated UI function when the user makes a selection from the menu
        self.taskFrequencySelectionStringvar.trace_add("write", lambda *args, selection=self.taskFrequencySelectionStringvar, parentFrame=self.taskFrequencyChoicesFrame: taskFrequencyMethodOptionsDict[selection.get()](self.taskFrequencyChoicesFrame))

        # Declare the dropdown menu, linking it to the stringvar
        self.taskFrequencyMethodMenu = tk.OptionMenu(self.taskFrequencyChoicesFrame, self.taskFrequencySelectionStringvar, *taskFrequencyMethodMenuOptions)
        # Render the menu and its label
        self.taskFrequencyChoicesFrame.grid(row=0, column=0)
        self.taskFrequencyMethodOptionsLabel.grid(row=0, column=0)
        self.taskFrequencyMethodMenu.grid(row=0, column=1)
        
        # Set a default selection - maybe skip this to force a choice
        self.taskFrequencySelectionStringvar.set(taskFrequencyMethodMenuOptions[0])

    def buildFixedRateTaskGenerationOptions(self, parentFrame):
        # Clear the parent frame of any leftovers to make room for this frame and its children
        self.removeSubframes(parentFrame)

        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskFixedRateOptionsFrame = tk.Frame(parentFrame)

        # Creates UI elements relevant to setting options for task generation at fixed rates
        self.taskFixedRateMethodOptionsLabel = tk.Label(self.taskFixedRateOptionsFrame, text="Rate setting:")

        # Dict pairing options and respective ui creation functions
        taskFixedRateMethodOptionsDict = {
            "Custom": self.buildFixedRateTaskCustomRate,
            "Auto: Mean Task Length": self.buildFixedRateTaskMeanRate,
            "Auto: Max Task Length": self.buildFixedRateTaskMaxRate,
            "Auto: Min Task Length": self.buildFixedRateTaskMinRate,
            "Auto: Median Task Length": self.buildFixedRateTaskMedianRate
        }

        # Menu options are the text in the dict keys
        taskFixedRateMethodOptions = list(taskFixedRateMethodOptionsDict.keys())

        # Stringvar to hold the option selection
        self.taskFixedRateSelectionStringvar = tk.StringVar()

        # Add a trace to the stringvar to call the associated UI function when the user makes a selection from the menu
        self.taskFixedRateSelectionStringvar.trace_add("write", lambda *args, selection=self.taskFixedRateSelectionStringvar, parentFrame=self.taskFixedRateOptionsFrame: taskFixedRateMethodOptionsDict[selection.get()](parentFrame))

        # Set a default selection - maybe skip this to force a choice
        self.taskFixedRateSelectionStringvar.set(taskFixedRateMethodOptions[0])

        # Declare the dropdown menu, linking it to the stringvar
        self.taskFixedRateMethodMenu = tk.OptionMenu(self.taskFixedRateOptionsFrame, self.taskFixedRateSelectionStringvar, *taskFixedRateMethodOptions)

        # Render the menu and its label
        self.taskFixedRateOptionsFrame.grid(row=0, column=2)
        self.taskFixedRateMethodOptionsLabel.grid(row=0, column=0)
        self.taskFixedRateMethodMenu.grid(row=0, column=1)
    
    def buildFixedRateTaskCustomRate(self, parentFrame):
        # Clear the parent frame of any leftovers to make room for this frame and its children
        self.removeSubframes(parentFrame)

        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskFixedCustomRateOptionsFrame = tk.Frame(parentFrame)

        # Creates UI elements relevant to setting options for task generation at fixed custom rates
        # Interval label and value
        self.taskFixedRateCustomIntervalLabel = tk.Label(self.taskFixedCustomRateOptionsFrame, text="Interval:")
        self.taskFixedRateCustomIntervalValue = tk.StringVar()

        # Interval validation callback on spinbox entry
        self.validateCustomIntervalValue = self.register(self.validateNumericSpinbox)

        # Custom entry numeric spinbox declaration
        self.taskFixedRateCustomIntervalSpinbox = ttk.Spinbox(self.taskFixedCustomRateOptionsFrame,
            width=6,
            from_=1,
            to=100000,
            increment=1,
            textvariable=self.taskFixedRateCustomIntervalValue,
            validate='key',
            validatecommand=(self.validateCustomIntervalValue, '%P')
        )

        # Render label and spinbox
        self.taskFixedCustomRateOptionsFrame.grid(row=0, column=2)
        self.taskFixedRateCustomIntervalLabel.grid(row=0, column=0)
        self.taskFixedRateCustomIntervalSpinbox.grid(row=0, column=1)

        # Amount of tasks per interval label and value
        self.taskFixedRateCustomTasksPerIntervalLabel = tk.Label(self.taskFixedCustomRateOptionsFrame, text="Tasks per Interval:")
        self.taskFixedRateCustomTasksPerIntervalValue = tk.StringVar()

        # Tasks per interval validation callback on spinbox entry
        self.validateCustomTasksPerIntervalValue = self.register(self.validateNumericSpinbox)

        # Custom entry numeric spinbox declaration
        self.taskFixedRateCustomTasksPerIntervalSpinnbox = ttk.Spinbox(self.taskFixedCustomRateOptionsFrame,
            width=6,
            from_=1,
            to=100000,
            increment=1,
            textvariable=self.taskFixedRateCustomTasksPerIntervalValue,
            validate='key',
            validatecommand=(self.validateCustomTasksPerIntervalValue, '%P')
        )

        # Render label and spinbox
        self.taskFixedRateCustomTasksPerIntervalLabel.grid(row=1, column=0)
        self.taskFixedRateCustomTasksPerIntervalSpinnbox.grid(row=1, column=1)

        # Radiobuttons to select task batching strategy
        self.taskFixedRateCustomTaskBatchingStrategyFrame = tk.Frame(self.taskFixedCustomRateOptionsFrame)
        self.taskFixedRateCustomTaskBatchingStrategyValue = tk.StringVar()
        self.taskFixedRateCustomTaskSingleBatchStrategy = tk.Radiobutton(self.taskFixedRateCustomTaskBatchingStrategyFrame, text="Single Batch", variable=self.taskFixedRateCustomTaskBatchingStrategyValue, value="singlebatch")
        self.taskFixedRateCustomTaskEvenSpreadStrategy = tk.Radiobutton(self.taskFixedRateCustomTaskBatchingStrategyFrame, text="Even Spread", variable=self.taskFixedRateCustomTaskBatchingStrategyValue, value="evenspread")
        self.taskFixedRateCustomTaskSingleBatchStrategy.select()

        # Render radiobuttons and frame
        self.taskFixedRateCustomTaskBatchingStrategyFrame.grid(row=2, column=0, columnspan=3)
        self.taskFixedRateCustomTaskSingleBatchStrategy.grid(row=0, column=0)
        self.taskFixedRateCustomTaskEvenSpreadStrategy.grid(row=0, column=1)
        
    def buildFixedRateTaskMeanRate(self, parentFrame):
        # Clear the parent frame of any leftovers to make room for this frame and its children
        self.removeSubframes(parentFrame)

        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskFixedRateMeanOptionsFrame = tk.Frame(parentFrame)
        self.taskFixedRateMeanOptionsFrame.grid(row=0, column=2)

        # Create descriptive text
        tk.Label(self.taskFixedRateMeanOptionsFrame, text=f"One task will be created per active agent e very {round(self.meanOptimalTaskPathLength)} simulation steps.").grid(row=0, column=0)

    def buildFixedRateTaskMaxRate(self, parentFrame):
        # Clear the parent frame of any leftovers to make room for this frame and its children
        self.removeSubframes(parentFrame)
        
        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskFixedRateMaximumOptionsFrame = tk.Frame(parentFrame)
        self.taskFixedRateMaximumOptionsFrame.grid(row=0, column=2)

        # Create descriptive text
        tk.Label(self.taskFixedRateMaximumOptionsFrame, text=f"One task will be created per active agent every {round(self.maximumOptimalPathLength)} simulation steps.").grid(row=0, column=0)

    def buildFixedRateTaskMinRate(self, parentFrame):
        # Clear the parent frame of any leftovers to make room for this frame and its children
        self.removeSubframes(parentFrame)
        
        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskFixedRateMinimumOptionsFrame = tk.Frame(parentFrame)
        self.taskFixedRateMinimumOptionsFrame.grid(row=0, column=2)

        # Create descriptive text
        tk.Label(self.taskFixedRateMinimumOptionsFrame, text=f"One task will be created per active agent every {round(self.minimumOptimalPathLength)} simulation steps.").grid(row=0, column=0)

    def buildFixedRateTaskMedianRate(self, parentFrame):
        # Clear the parent frame of any leftovers to make room for this frame and its children
        self.removeSubframes(parentFrame)
        
        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskFixedRateMedianOptionsFrame = tk.Frame(parentFrame)
        self.taskFixedRateMedianOptionsFrame.grid(row=0, column=2)

        # Create descriptive text
        tk.Label(self.taskFixedRateMedianOptionsFrame, text=f"One task will be created per active agent every {round(self.medianOptimalTaskPathLength)} simulation steps.").grid(row=0, column=0)

    def buildAsAvailableTaskGenerationOptions(self, parentFrame):
        # Clear the parent frame of any leftovers to make room for this frame and its children
        self.removeSubframes(parentFrame)

        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskAsAvailableOptionsFrame = tk.Frame(parentFrame)

        # Create a delay option, specifying how long after an agent becomes an available a new task will be generated
        # Delay label and value
        self.taskAsAvailableDelayLabel = tk.Label(self.taskAsAvailableOptionsFrame, text="Post-completion delay:")
        self.taskAsAvailableDelayValue = tk.StringVar()

        # Delay validation callback on spinbox entry
        self.validateCustomDelayValue = self.register(self.validateNumericSpinbox)

        # Custom entry numeric spinbox declaration
        self.taskAsAvailableDelaySpinbox = ttk.Spinbox(self.taskAsAvailableOptionsFrame,
            width=6,
            from_=0,
            to=1000,
            increment=1,
            textvariable=self.taskAsAvailableDelayValue,
            validate='key',
            validatecommand=(self.validateCustomDelayValue, '%P')
        )

        # Render label and spinbox
        self.taskAsAvailableOptionsFrame.grid(row=0, column=2)
        self.taskAsAvailableDelayLabel.grid(row=1, column=0)
        self.taskAsAvailableDelaySpinbox.grid(row=1, column=1)

        # Task generation trigger label
        self.taskAsAvailableTriggerLabel = tk.Label(self.taskAsAvailableOptionsFrame, text="Determine agent availability: ")

        # When an agent is 'available' to pick up a new task can be configured
        agentAvailabilityTriggerDict = {
            "On Dropoff": "ondeposit", 
            "On Pickup": "onpickup", 
            "On Assignment": "onassignment", 
            "On Rest": "onrest",
            # "On Recharge": "onrecharge"
        }

        # Menu options are the keys of the dict
        agentAvailabilityTriggerOptions = list(agentAvailabilityTriggerDict.keys())

        # Stringvar holding menu selection
        self.taskAsAvailableTriggerStringvar = tk.StringVar()

        # Set a default value - maybe skip this to force a choice
        self.taskAsAvailableTriggerStringvar.set(agentAvailabilityTriggerOptions[0])

        # Declare the dropdown menu, linking it to the stringvar and using the option list
        self.taskAsAvailableAvailabilityTriggerMenu = tk.OptionMenu(self.taskAsAvailableOptionsFrame, self.taskAsAvailableTriggerStringvar, *agentAvailabilityTriggerOptions)

        # Render the menu and its label
        self.taskAsAvailableTriggerLabel.grid(row=0, column=0)
        self.taskAsAvailableAvailabilityTriggerMenu.grid(row=0, column=1)

    def createTaskLocationOptions(self):
        # Allow the user to assign weights or entirely disable certain pickup and dropoff nodes
        # Containing frames
        self.taskLocationPickupLabelFrame = tk.LabelFrame(self.taskLocationFrame, text="Pickup Nodes")
        self.taskLocationPickupLabelFrame.grid(row=0, column=0)
        # Use custom scrolled frame for long lists
        self.taskLocationPickupScrollFrame = tk_e.VerticalScrolledFrame(self.taskLocationPickupLabelFrame)
        self.taskLocationPickupFrame = self.taskLocationPickupScrollFrame.interior
        self.taskLocationPickupScrollFrame.grid(row=0, column=0)

        self.taskLocationDropoffLabelFrame = tk.LabelFrame(self.taskLocationFrame, text="Dropoff Nodes")
        self.taskLocationDropoffLabelFrame.grid(row=0, column=1)
        # Use custom scrolled frame for long lists
        self.taskLocationDropoffScrollFrame = tk_e.VerticalScrolledFrame(self.taskLocationDropoffLabelFrame)
        self.taskLocationDropoffFrame = self.taskLocationDropoffScrollFrame.interior
        self.taskLocationDropoffFrame.grid(row=0, column=1)

        # Spinboxes should only be numeric, so use the validating function
        self.validateTaskWeightValues = self.register(self.validateNumericSpinbox)

        # Get all pickup and dropoff nodes
        nodeTypeDict = self.parent.mapData.generateNodeListsByType()
        listOfPickupNodes = nodeTypeDict['pickup']
        listOfDropoffNodes = nodeTypeDict['deposit']

        # Build the GUI for setting weights of nodes, by type
        self.buildNodeWeightingOptions(listOfPickupNodes, self.taskLocationPickupFrame)
        self.buildNodeWeightingOptions(listOfDropoffNodes, self.taskLocationDropoffFrame)

    def enterVScrollFrameSpinbox(self, event, bindTarget):
        # Release the mouse from managing the containing canvas before binding it to the spinbox it just entered
        bindTarget.unbind_mwheel()
        event.widget.bind('<MouseWheel>', lambda event: event.widget.invoke('buttonup') if event.delta>0 else event.widget.invoke('buttondown'))

    def leaveVScrollFrameSpinbox(self, event, bindTarget):
        # Release the mouse from managing the spinbox before reattaching it to the canvas containing the spinbox
        event.widget.unbind('<MouseWheel>')
        bindTarget.bind_mwheel()

    def buildNodeWeightingOptions(self, nodeList, targetFrame):
        # Iterate over all pickup nodes
        for index, node in enumerate(nodeList):
            # Each node needs a label, tickbox, and numeric spinbox for weight
            # Create the label, displaying the nodes ID/coordinates
            nodeLabel = tk.Label(targetFrame, text=str(node))
            nodeLabel.grid(row=index, column=0)

            # Create the spinbox, to hold the relative numeric weight entry
            nodeWeightBox = tk.Spinbox(targetFrame,
                width=6,
                from_=0,
                to=1000,
                increment=1,
                validate='key',
                validatecommand=(self.validateTaskWeightValues, '%P')
            )
            nodeWeightBox.insert(0, 100)
            nodeWeightBox.grid(row=index, column=2)
            # Bind controls to the spinbox
            nodeWeightBox.bind('<Enter>', lambda event, bindTarget=targetFrame.master.master: self.enterVScrollFrameSpinbox(event, bindTarget))
            nodeWeightBox.bind('<Leave>', lambda event, bindTarget=targetFrame.master.master: self.leaveVScrollFrameSpinbox(event, bindTarget))

            # Create a toggle button that disables the use of the tile
            stateCycler = itertools.cycle([tk.DISABLED, tk.NORMAL]) # Use this to track the state of the widgets tied to the checkbutton, cycling the value on each callback
            nodeTick = tk.Checkbutton(targetFrame, 
                command = lambda stateCycler=stateCycler, index=index, controlWidgetColumn=1: self.toggleWidgetsInRow(index, stateCycler, controlWidgetColumn))
            nodeTick.grid(row=index, column=1)
            nodeTick.select()   # Default toggled on
            
    def toggleWidgetsInRow(self, index, stateCycler, controlWidgetColumn):
        # Using the index of the grid row the widget callback exists in, toggle every other widget
        # State cycler is an `itertools.cycle` object, and the controlWidgetColumn is skipped in iteration
        widgetlist = self.taskLocationPickupFrame.grid_slaves(row=index)
        nextState = next(stateCycler)   # Get the next state
        for widget in widgetlist:
            # Iterate over every widget, skipping the control column (this should stay tk.normal so that it can be clicked again)
            if not widget.grid_info()["column"]==controlWidgetColumn:
                widget.configure(state=nextState)
        
    def createSimulationUpdateRate(self):
        self.frameDelayLabel = tk.Label(self.displayOptionsFrame, text="frameDelay:")
        self.frameDelayValue = tk.StringVar()
        self.validateFrameDelayEntry = self.register(self.validateNumericSpinbox)
        # Create a spinbox with entry for millisecond time between frame updates of the canvas while the play button is depressed
        self.frameDelayEntry = ttk.Spinbox(self.displayOptionsFrame,
            width=6,
            from_=0,
            to=100000,
            increment=50,
            textvariable=self.frameDelayValue,
            # command=self.commandTaskTimeLimit,
            validate='key',
            validatecommand=(self.validateFrameDelayEntry, '%P')
        )
        logging.debug("Simulation playback frame delay spinbox built.")

        # Set a default value
        self.frameDelayValue.set(1000)

        # Render components
        self.frameDelayLabel.grid(row=1, column=1)
        self.frameDelayEntry.grid(row=1, column=2)

    def validateNumericSpinbox(self, inputString):
        logging.debug(f"Validating numeric spinbox entry: {inputString}")
        if inputString.isnumeric():
            # Only allow numeric characters
            logging.debug("Numeric spinbox entry is numeric. Allowed.")
            return True
        elif len(inputString) == 0:
            logging.debug("Numeric spinbox entry is empty. Allowed.")
            # Or an empty box
            return True
        else:
            logging.debug("Numeric spinbox entry is invalid.")
            return False

    def removeSubframes(self, frame):
        # Destroy all widgets inside child frames of the passed frames, and the child frames themselves
        # Find all child widgets
        for widget in frame.winfo_children():
            # Identify which ones are frames
            if isinstance(widget, tk.Frame):
                # Destroy the frame—all children are also automatically destroyed
                # https://www.tcl.tk/man/tcl8.6/TkCmd/destroy.html
                # "This command deletes the windows given by the window arguments, plus all of their descendants."
                widget.destroy()

class simulationConfigurationState:
    # Holds the current state of the simulation config
    def __init__(self, parent):
        self.parent = parent
        logging.info("Simulation State Default Init")