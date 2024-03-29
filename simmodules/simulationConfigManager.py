import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import messagebox
from tkinter import filedialog
import logging
import pprint
pp = pprint.PrettyPrinter(indent=4)
import numpy as np
import itertools
import modules.tk_extensions as tk_e
import csv
import random

from collections import Counter

# For graphs embedded in tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from pathlib import Path
import os

class simulationConfigManager(tk.Toplevel):
    # Window for managing the state of the simulation configuration
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        logging.info("Simulation Configuration Manager Class gen")
        self.title("Simulation Configuration Window")
        self.focus()     # "Select" the window
        self.grab_set()  # Forcefully keep attention on the window

        # Building a notebook; each page contains a set of options
        self.configNotebook = ttk.Notebook(self)

        # Each page needs a space to insert widgets
        self.pathfindingAlgorithmFrame = tk.Frame(self.configNotebook)
        self.agentConfigurationFrame = tk.Frame(self.configNotebook)
        self.taskGenerationFrame = tk.Frame(self.configNotebook)
        self.displayOptionsFrame = tk.Frame(self.configNotebook)
        self.simulationEndFrame = tk.Frame(self.configNotebook)

        # Tabnames-tabframes,tabbuildfunction dictionary
        noteBookTabs = {
            "Pathfinding Algorithm": (self.pathfindingAlgorithmFrame, self.buildPathfindingAlgorithmPage),
            "Agent Configuration": (self.agentConfigurationFrame, self.buildAgentConfigurationPage),
            "Task Generation": (self.taskGenerationFrame, self.buildTaskGenerationPage),
            "Display Options": (self.displayOptionsFrame, self.buildDisplayOptionsPage),
            "End Sim Conditions": (self.simulationEndFrame, self.buildSimulationEndPage)
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

        # Trim the dict of possible nodes according to use selection
        for pickupNode in self.nodeAvailableVarDict['pickup']:
            if not self.nodeAvailableVarDict["pickup"][pickupNode].get():
                nodeTypeDict['pickup'].remove(pickupNode)
        for dropoffNode in self.nodeAvailableVarDict['dropoff']:
            if not self.nodeAvailableVarDict["dropoff"][dropoffNode].get():
                nodeTypeDict['deposit'].remove(dropoffNode)

        if len(nodeTypeDict['pickup'])>0 and len(nodeTypeDict['deposit'])>0:
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

    def buildPathfindingAlgorithmPage(self):
        # Using types to separate multi-agent and single-agent pathfinding algorithms
        self.algorithmOptionTypeDict = {
            "Single-agent A*": "sapf",
            "Multi-Agent A* (LRA*)": "mapf",
            "Multi-Agent Cooperative A* (CA*)": "mapf",
            "Hierarchical A* with RRA* (HCA*)": "mapf",
            "Windowed HCA* (WHCA*)": "mapf",
            "Token Passing with A* (TP)": "mapf",
            "TP with Task Swaps (TPTS)": "mapf"
        }

        ### Algorithm Selection
        self.algorithmChoice = tk.StringVar()

        ### A* SAPF Suboptions
        self.SAPFAstarHeuristic = tk.StringVar()
        self.SAPFAstarHeuristicCoefficient = tk.IntVar()

        ### LRA* MAPF Suboptions
        self.MAPFLRAstarHeuristic = tk.StringVar()
        self.MAPFLRAstarHeuristicCoefficient = tk.IntVar()

        ### CA* MAPF Suboptions
        self.MAPFCAstarHeuristic = tk.StringVar()
        self.MAPFCAstarHeuristicCoefficient = tk.IntVar()

        ### HCA* MAPF Suboptions
        self.MAPFHCAstarHeuristic = tk.StringVar()
        self.MAPFHCAstarHeuristicCoefficient = tk.IntVar()

        ### WHCA* MAPF Suboptions
        self.MAPFWHCAstarHeuristic = tk.StringVar()
        self.MAPFWHCAstarHeuristicCoefficient = tk.IntVar()
        self.MAPFWHCAstarWindowSize = tk.IntVar()

        ### TP MAPD Suboptions
        self.MAPFTPHeuristic = tk.StringVar()
        self.MAPFTPHeuristicCoefficient = tk.IntVar()

        ### TPTS MAPD Suboptions
        self.MAPDTPTSHeuristic = tk.StringVar()
        self.MAPDTPTSHeuristicCoefficient = tk.IntVar()

        # UI Definition Dict
        # Sorcery
        cwd = os.path.dirname(__file__)
        filePath = os.path.abspath(os.path.join(cwd, 'simalgorithmmenuconfig.txt'))
        self.algorithmOptionSet = eval(open(filePath, "r").read())

        # Build option menu from config file
        self.algorithmChoiceOptionSetUI = tk_e.ConfigOptionSet(self.pathfindingAlgorithmFrame)
        self.algorithmChoiceOptionSetUI.buildOutOptionSetUI(self.algorithmOptionSet)

        # Intermediate function grouping together declarations and renders for the algorithm choices page
        # self.createAlgorithmOptions()

    # def createAlgorithmOptions(self):
    #     # Creates a drop down menu for the user to select the driving algorithm for the simulation
    #     # Keys of the dict are the displayed options
    #     algorithmOptions = list(self.algorithmOptionTypeDict.keys())

    #     # Stringvar to hold the algorithm selection
    #     self.algorithmSelectionStringVar = tk.StringVar()

    #     # Set a default selection - maybe skip this to force a choice
    #     self.algorithmSelectionStringVar.set(algorithmOptions[0])

    #     # Declare the drop down menu
    #     self.algorithmChoiceMenu = tk.OptionMenu(self.pathfindingAlgorithmFrame, self.algorithmSelectionStringVar, *algorithmOptions)

    #     # If there is more than one agent in the simulation space, disable single-agent pathfinding algorithm options
    #     for algorithm, type in self.algorithmOptionTypeDict.items():
    #         if type == "sapf" and len(self.parent.agentManager.agentList) > 1:
    #             self.algorithmChoiceMenu['menu'].entryconfigure(algorithm, state=tk.DISABLED)

    #     # Render the menu
    #     self.algorithmChoiceMenu.grid(row=1, column=0, sticky=tk.W)

    def buildAgentConfigurationPage(self):
        SPINBOX_DEFAULT_RANGE = (1, 100000, 1)
        # Use a factory to produce ui elements from inputs, maintaining relational lists
        # In: label text, ui element (numspinbox, entry, optionmenu)

        # Control variables, saved here for custom naming and reference ease

        ### Agent collisions
        self.agentCollisionsValue = tk.StringVar()

        ### Limited Charge
        self.agentChargeLimitationValue = tk.StringVar()
        self.agentLimitedChargeCostStyleValue = tk.StringVar()
        self.agentLimitedChargeCapacityValue = tk.StringVar()
        self.agentLimitedChargeStepCostValue = tk.StringVar()
        self.agentLimitedChargeActionCostValue = tk.StringVar()
        self.agentLimitedChargeMovementCostValue = tk.StringVar()
        self.agentLimitedChargePickupCostValue = tk.StringVar()
        self.agentLimitedChargeDropoffCostValue = tk.StringVar()

        ### Breakdowns
        self.agentBreakdownOptionValue = tk.StringVar()
        self.agentBreakdownFixedRateValue = tk.StringVar()
        self.agentBreakdownChancePerStepValue = tk.StringVar()

        ### Start position
        self.agentStartPosStyleValue = tk.StringVar()

        ### Movement Costs
        self.agentMiscOptionRotateCostValue = tk.StringVar()

        ### Interaction Costs
        self.agentMiscOptionTaskInteractCostValue = tk.StringVar()
        
        # UI Definition Dict
        # Sorcery
        cwd = Path(__file__).parent
        filePath = (cwd / 'simagentmenuconfig.txt').resolve()
        self.agentOptionSet = eval(open(filePath, "r").read())

        # Build option menu from config file
        self.agentChargeOptionSetUI = tk_e.ConfigOptionSet(self.agentConfigurationFrame)
        self.agentChargeOptionSetUI.buildOutOptionSetUI(self.agentOptionSet)

    def buildSimulationEndPage(self):
        # Defines the simulation end condition(s)

        # A number of tasks have been completed
        self.endSimOnTaskCount = tk.BooleanVar()
        self.endSimOnTaskCount.set(False)
        self.endSimTaskCount = tk.IntVar()
        self.endSimTaskCount.set(1)
        self.triggerSimEndOnTaskCountCheckbutton = tk.Checkbutton(self.simulationEndFrame, 
            text="Simulation ends after number of task completions", variable=self.endSimOnTaskCount, 
            onvalue=True, offvalue=False)
        self.triggerSimEndOnTaskCountCheckbutton.grid(row=0, column=0)
        # Custom entry numeric spinbox declaration
        self.endSimTaskCountValidator = self.register(self.validateNumericSpinbox)
        self.endSimTaskCountSelector = ttk.Spinbox(self.simulationEndFrame,
            width=6,
            from_=1,
            to=1000,
            increment=1,
            textvariable=self.endSimTaskCount,
            validate='key',
            validatecommand=(self.endSimTaskCountValidator, '%P')
        )
        self.endSimTaskCountSelector.grid(row=0, column=1, sticky=tk.W)

        # A number of timesteps have passed
        self.endSimOnStepCount = tk.BooleanVar()
        self.endSimOnStepCount.set(False)
        self.endSimStepCount = tk.IntVar()
        self.endSimStepCount.set(1)
        self.triggerSimEndOnStepCountCheckbutton = tk.Checkbutton(self.simulationEndFrame,
            text="Simulation ends after number of steps completed", variable=self.endSimOnStepCount,
            onvalue=True, offvalue=False)
        self.triggerSimEndOnStepCountCheckbutton.grid(row=1, column=0)
        # Custom entry numeric spinbox declaration
        self.endSimStepCountValidator = self.register(self.validateNumericSpinbox)
        self.endSimStepCountSelector = ttk.Spinbox(self.simulationEndFrame,
            width=6,
            from_=1,
            to=1000,
            increment=1,
            textvariable=self.endSimStepCount,
            validate='key',
            validatecommand=(self.endSimStepCountValidator, '%P')
        )
        self.endSimStepCountSelector.grid(row=1, column=1, sticky=tk.W)

        # All scheduled tasks have been completed
        self.endSimOnScheduleEnd = tk.BooleanVar()
        self.endSimOnScheduleEnd.set(False)
        self.triggerSimEndOnScheduleEnd = tk.Checkbutton(self.simulationEndFrame,
            text="Simulation ends after task schedule completed", variable=self.endSimOnScheduleEnd,
            onvalue=True, offvalue=False)
        self.triggerSimEndOnScheduleEnd.grid(row=2, column=0)

    def buildTaskGenerationPage(self):
        self.tasksAreScheduled = False
        self.taskSchedule = None
        # Remove all child widgets
        for child in self.taskGenerationFrame.winfo_children():
            child.destroy()

        # StringVars declared here for reference
        self.taskFrequencySelectionStringvar = tk.StringVar()
        self.taskFixedRateSelectionStringvar = tk.StringVar()
        self.taskFixedRateCustomIntervalValue = tk.StringVar()
        self.taskFixedRateCustomTasksPerIntervalValue = tk.StringVar()
        self.taskFixedRateCustomTaskBatchingStrategyValue = tk.StringVar()
        self.taskAsAvailableDelayValue = tk.StringVar()
        self.taskAsAvailableTriggerStringvar = tk.StringVar()

        # Load a .csv with a task schedule instead
        self.loadTaskScheduleButton = tk.Button(self.taskGenerationFrame,
            command=self.loadTaskSchedule, text="Load a Task Schedule (.csv)")
        self.loadTaskScheduleButton.grid(row=3, column=0)

        # Generate a .csv with a task schedule
        self.generateTaskScheduleButton = tk.Button(self.taskGenerationFrame,
            command=self.generateTaskScheduleOptions, text="Create a Task Schedule")
        self.generateTaskScheduleButton.grid(row=3, column=1)

        # Intermediate function grouping together declarations and renders for the task generation page
        self.taskGenerationRateFrame = tk.Frame(self.taskGenerationFrame)
        self.taskGenerationRateFrame.grid(row=0, column=0)
        self.createTaskFrequencyOptions()
        self.taskLocationFrame = tk.LabelFrame(self.taskGenerationFrame, text="Node Weights")
        self.taskLocationFrame.grid(row=0, column=1, rowspan=2)
        self.nodeWeightVarDict = {
            "pickup": {},
            "dropoff": {}
        }
        self.nodeAvailableVarDict = {
            "pickup": {},
            "dropoff": {}
        }
        self.createTaskLocationOptions()
        self.taskStatisticsFrame = tk.Frame(self.taskGenerationFrame)
        self.taskStatisticsFrame.grid(row=1, column=0)
        self.createTaskInformationPane()

    def loadTaskSchedule(self):
        # Ask for a .csv
        fid = tk.filedialog.askopenfilename(filetypes=[("Comma-separated values","*.*"),])
        with open(fid, 'r') as inp:
            # Extract all the data
            reader = csv.reader(inp)
            data = list(reader)
        
        # Row one should contain specific headers if it is a valid file
        columnNames = ["PickupNode", "DropoffNode", "TimeLimit", "ReleaseTime", "Name"]
        if data[0] != columnNames:
            print("Data does not match the timeplate")
            # Invalid
            return

        # Remove all child widgets
        for child in self.taskGenerationFrame.winfo_children():
            child.destroy()

        # Having pressed this button indicates a schedule should be used
        self.tasksAreScheduled = True
        self.taskSchedule = fid

        # Display the loaded schedule (with scrollbar)
        self.buildTaskSchedulePage(data)

    def buildTaskSchedulePage(self, csvData):
        # Build a display frame for the schedule
        # self.taskScheduleDisplayFrame = tk.Frame(self.taskGenerationFrame)
        self.taskScheduleDisplayHeaderFrame = tk.LabelFrame(self.taskGenerationFrame, text="First 100 tasks")
        self.taskScheduleDisplayHeaderFrame.grid(row=1, column=0, sticky="ew")
        self.taskScheduleDisplayScrollFrame = tk_e.VerticalScrolledFrame(self.taskGenerationFrame)
        self.taskScheduleDisplayFrame = self.taskScheduleDisplayScrollFrame.interior
        self.taskGenerationFrame.columnconfigure(0, weight=1)
        self.taskGenerationFrame.rowconfigure(0, weight=1)
        self.taskScheduleDisplayScrollFrame.grid(row=2, column=0, sticky="news")

        graph = self.parent.mapData.mapGraph
        # print("Displaying task schedule")
        # pp.pprint(csvData[0])
        # Column headers
        for i, col in enumerate(csvData[0]):
            # print(col)
            tk.Label(self.taskScheduleDisplayHeaderFrame, text=col).grid(row=0, column=i, sticky=tk.W+tk.E)
            self.taskScheduleDisplayHeaderFrame.columnconfigure(i, weight=1)
            self.taskScheduleDisplayFrame.columnconfigure(i, weight=1)
        # Data
        for i, row in enumerate(csvData, start=1):
            if row[0] not in graph.nodes(data=False):
                # First column must be a node in the graph (pickupNode)
                continue
            if row[1] not in graph.nodes(data=False):
                # Second column must be a node in the graph (dropoffNode)
                continue
            if not isinstance(row[2], int):
                row[2] = int(row[2])
                # Third column must be an integer (timeLimit)
            if not isinstance(row[3], int):
                row[3] = int(row[3])
                # Fourth column must be an integer (releaseTime)
            if not isinstance(row[4], str):
                # Fifth column must be a string (name)
                row[4] = str(row[4])
            tk.Label(self.taskScheduleDisplayFrame, text=row[0]).grid(row=i, column=0, sticky=tk.W+tk.E)
            tk.Label(self.taskScheduleDisplayFrame, text=row[1]).grid(row=i, column=1, sticky=tk.W+tk.E)
            tk.Label(self.taskScheduleDisplayFrame, text=row[2]).grid(row=i, column=2, sticky=tk.W+tk.E)
            tk.Label(self.taskScheduleDisplayFrame, text=row[3]).grid(row=i, column=3, sticky=tk.W+tk.E)
            tk.Label(self.taskScheduleDisplayFrame, text=row[4]).grid(row=i, column=4, sticky=tk.W+tk.E)
            if i > 100:
                # There is a size limitation of the canvas (xd)
                break

        # Build a button to return to the generator configuration page
        self.taskGenerationReturnButton = tk.Button(self.taskGenerationFrame,
            command=self.buildTaskGenerationPage, text="Use Live Task Generation")
        self.taskGenerationReturnButton.grid(row=3, column=0)

    def generateTaskScheduleOptions(self):
        # Remove all child widgets
        for child in self.taskStatisticsFrame.winfo_children():
            child.destroy()
        for child in self.taskGenerationRateFrame.winfo_children():
            child.destroy()
        self.generateTaskScheduleButton.destroy()

        # N tasks should be generated
        agentCount = len(self.parent.agentManager.agentList)
        self.taskScheduleTasksPerGenerate = tk.Label(self.taskStatisticsFrame, text="Tasks per batch:")
        self.tasksPerGenerate = tk.IntVar(value=agentCount)
        # Interval validation callback on spinbox entry
        self.validateTasksPerGenerate = self.register(self.validateNumericSpinbox)
        # Custom entry numeric spinbox declaration
        self.tasksPerGenerateSpinbox = ttk.Spinbox(self.taskStatisticsFrame,
            width=6,
            from_=1,
            to=100000,
            increment=1,
            textvariable=self.tasksPerGenerate,
            validate='key',
            validatecommand=(self.validateTasksPerGenerate, '%P')
        )
        # Render label and spinbox
        self.taskScheduleTasksPerGenerate.grid(row=0, column=0)
        self.tasksPerGenerateSpinbox.grid(row=0, column=1)

        # Every M steps
        self.taskScheduleTaskGenerateFreq = tk.Label(self.taskStatisticsFrame, text="Batch every:")
        self.taskGenerateEvery = tk.IntVar(value= int(self.meanOptimalTaskPathLength))
        # Interval validation callback on spinbox entry
        self.validateGenerateFreq = self.register(self.validateNumericSpinbox)
        # Custom entry numeric spinbox declaration
        self.taskGenerateFreqSpinbox = ttk.Spinbox(self.taskStatisticsFrame,
            width=6,
            from_=1,
            to=100000,
            increment=1,
            textvariable=self.taskGenerateEvery,
            validate='key',
            validatecommand=(self.validateGenerateFreq, '%P')
        )
        # Render label and spinbox
        self.taskScheduleTaskGenerateFreq.grid(row=1, column=0)
        self.taskGenerateFreqSpinbox.grid(row=1, column=1)

        # Out to P steps in total
        self.taskScheduleLengthLabel = tk.Label(self.taskStatisticsFrame, text="Timesteps in Schedule:")
        self.taskScheduleLength = tk.IntVar(value=2000)
        # Interval validation callback on spinbox entry
        self.validateScheduleLength = self.register(self.validateNumericSpinbox)
        # Custom entry numeric spinbox declaration
        self.taskScheduleLengthSpinbox = ttk.Spinbox(self.taskStatisticsFrame,
            width=6,
            from_=1,
            to=100000,
            increment=1,
            textvariable=self.taskScheduleLength,
            validate='key',
            validatecommand=(self.validateScheduleLength, '%P')
        )
        # Render label and spinbox
        self.taskScheduleLengthLabel.grid(row=2, column=0)
        self.taskScheduleLengthSpinbox.grid(row=2, column=1)

        # Generate button
        self.triggerScheduleGeneration = tk.Button(self.taskStatisticsFrame,
            command=self.generateTaskSchedule, text="Generate the schedule")
        self.triggerScheduleGeneration.grid(row=3, column=1)
        # Build a button to return to the generator configuration page
        self.taskGenerationReturnButton = tk.Button(self.taskGenerationFrame,
            command=self.buildTaskGenerationPage, text="Use Live Task Generation")
        self.taskGenerationReturnButton.grid(row=3, column=1)
        
    def generateTaskSchedule(self):
        fid = filedialog.asksaveasfilename(initialfile="Untitled.csv", filetypes=[("CSV", "*.csv"), ("Any", "*.*")])
        batchCount = itertools.count()
        taskCount = itertools.count()
        currentStep = next(batchCount)
        tasksGenEvery = self.taskGenerateEvery.get()
        tasksPerBatch = self.tasksPerGenerate.get()
        scheduleLength = self.taskScheduleLength.get()
        with open(fid, 'w', newline="") as csvfile:
            # Write the header row
            taskScheduler = csv.writer(csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            taskScheduler.writerow(["PickupNode", "DropoffNode", "TimeLimit", "ReleaseTime", "Name"])
            nodeAvailability = [[node for node, value in nodeDict.items() if value.get() == 1] for key, nodeDict in self.nodeAvailableVarDict.items()]
            nodeWeights = [[eval(value.get()) for node, value in nodeDict.items() if node in nodeAvailability[0] or node in nodeAvailability[1]] for key, nodeDict in self.nodeWeightVarDict.items()]
            # pp.pprint(nodeAvailability)
            # pp.pprint(nodeWeights)
            while currentStep*tasksGenEvery < scheduleLength:
                # Generate another batch of tasks
                for i in range(1, tasksPerBatch+1):
                    taskPickupNode = random.choices(population=nodeAvailability[0], weights=nodeWeights[0], k=1)[0]
                    taskDropoffNode = random.choices(population=nodeAvailability[1], weights=nodeWeights[1], k=1)[0]
                    taskTimeLimit = 0
                    taskReleaseTime = currentStep*tasksGenEvery
                    taskName = next(taskCount)
                    taskScheduler.writerow([taskPickupNode, taskDropoffNode, taskTimeLimit, taskReleaseTime, taskName])
                currentStep = next(batchCount)

    def createTaskInformationPane(self):
        # Some things need to be precalculated to inform the user while they make decisions regarding simulation setup
        self.precalculateTaskGenerationTabInformation()

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

        # Create the tkinter object using matplotlib's backend, and render it to the page frame
        self.taskInfoCanvasWidget = FigureCanvasTkAgg(self.taskInfoFigure, self.taskStatisticsFrame)
        self.taskInfoCanvasWidget.draw()
        self.taskInfoCanvasWidget.get_tk_widget().grid(row=2, column=0, sticky=tk.W)

        # Draw the plot
        self.updateTaskInfoPlot()

        # Create a containing frame for the text widget, to control its size
        self.taskInfoTextFrame = tk.Frame(self.taskStatisticsFrame, width=self.winfo_width(), height=100)
        self.taskInfoTextFrame.grid(row=4, column=0, sticky="news")
        self.taskInfoTextFrame.grid_propagate(False)

        # Generate statistical text
        self.taskInfoText = tk.Text(self.taskInfoTextFrame, fg="black", bg="SystemButtonFace", bd=0, font=("Helvetica", 10, "bold"))
        self.taskInfoText.tag_configure("red", foreground="red")
        self.updateTaskStatsText()

    def updateTaskInfoPlot(self):
        if hasattr(self, "taskInfoPlot") and hasattr(self, "taskInfoCanvasWidget"):
            # Clear the plot
            self.taskInfoPlot.cla()

            # Re-draw the data
            self.taskInfoPlot.bar(self.taskPathLengthCountDict.keys(), self.taskPathLengthCountDict.values())
            self.taskInfoPlot.set_xticks(list(range(0, self.maximumOptimalPathLength+1)))
            self.taskInfoPlot.set_xlabel("Optimal Task Path Lengths (steps)")
            self.taskInfoPlot.set_ylabel("Count")
            self.taskInfoPlot.set_title("All Possible Task Optimal Paths")

            # Mark the mean value with a line on the plot
            self.taskInfoPlot.axvline(self.meanOptimalTaskPathLength, color='r')

            # Re-render the graph
            self.taskInfoCanvasWidget.draw()

    def updateTaskStatsText(self):
        if hasattr(self, "taskInfoText"):
            # Enable changes
            self.taskInfoText.configure(state=tk.NORMAL)

            # Clear existing text
            self.taskInfoText.delete('1.0', tk.END)

            # Create some text providing statistical information about the optimal task paths
            self.taskInfoText.insert(tk.END, "Statistical Data for all possible optimal task paths: \n")
            self.taskInfoText.insert(tk.END, f"\tMean optimal path length: {round(self.meanOptimalTaskPathLength, 2)}\n", "red")
            self.taskInfoText.insert(tk.END, f"\tMax optimal path length: {self.maximumOptimalPathLength}\n")
            self.taskInfoText.insert(tk.END, f"\tMin optimal path length: {self.minimumOptimalPathLength}\n")
            self.taskInfoText.insert(tk.END, f"\tMedian optimal path length: {self.medianOptimalTaskPathLength}\n")
            self.taskInfoText.insert(tk.END, f"\tOptimal path length standard deviation: {round(self.standardDeviationOptimalTaskPathLength, 2)}")

            # Prevent interaction
            self.taskInfoText.configure(state=tk.DISABLED, height=6)
            
            # Render the text
            self.taskInfoText.grid(row=0, column=0)

    def createTaskFrequencyOptions(self):
        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskFrequencyChoicesFrame = tk.Frame(self.taskGenerationRateFrame)

        # Creates a drop-down for task frequency type
        # Based on selection, creates options specific to the frequency type
        self.taskFrequencyMethodOptionsLabel = tk.Label(self.taskFrequencyChoicesFrame, text="As Available:")

        # Dict pairing options and respective ui creation functions
        taskFrequencyMethodOptionsDict = {
            # "Fixed Rate": self.buildFixedRateTaskGenerationOptions,
            "As Available": self.buildAsAvailableTaskGenerationOptions
        }

        # Menu options are the text in the dict keys
        taskFrequencyMethodMenuOptions = list(taskFrequencyMethodOptionsDict.keys())

        # Add a trace to the stringvar to call the associated UI function when the user makes a selection from the menu
        self.taskFrequencySelectionStringvar.trace_add("write", lambda *args, selection=self.taskFrequencySelectionStringvar, parentFrame=self.taskFrequencyChoicesFrame: taskFrequencyMethodOptionsDict[selection.get()](parentFrame))

        # Declare the dropdown menu, linking it to the stringvar
        self.taskFrequencyMethodMenu = tk.OptionMenu(self.taskFrequencyChoicesFrame, self.taskFrequencySelectionStringvar, *taskFrequencyMethodMenuOptions)
        # Render the menu and its label
        self.taskFrequencyChoicesFrame.grid(row=0, column=0, sticky=tk.W)
        self.taskFrequencyMethodOptionsLabel.grid(row=0, column=0, sticky=tk.W)
        self.taskFrequencyMethodMenu.grid(row=0, column=1, sticky=tk.W)
        
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

        # Add a trace to the stringvar to call the associated UI function when the user makes a selection from the menu
        self.taskFixedRateSelectionStringvar.trace_add("write", lambda *args, selection=self.taskFixedRateSelectionStringvar, parentFrame=self.taskFixedRateOptionsFrame: taskFixedRateMethodOptionsDict[selection.get()](parentFrame))

        # Set a default selection - maybe skip this to force a choice
        self.taskFixedRateSelectionStringvar.set(taskFixedRateMethodOptions[0])

        # Declare the dropdown menu, linking it to the stringvar
        self.taskFixedRateMethodMenu = tk.OptionMenu(self.taskFixedRateOptionsFrame, self.taskFixedRateSelectionStringvar, *taskFixedRateMethodOptions)

        # Render the menu and its label
        self.taskFixedRateOptionsFrame.grid(row=0, column=2, sticky=tk.W)
        self.taskFixedRateMethodOptionsLabel.grid(row=0, column=0, sticky=tk.W)
        self.taskFixedRateMethodMenu.grid(row=0, column=1, sticky=tk.W)
    
    def buildFixedRateTaskCustomRate(self, parentFrame):
        # Clear the parent frame of any leftovers to make room for this frame and its children
        self.removeSubframes(parentFrame)

        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskFixedCustomRateOptionsFrame = tk.Frame(parentFrame)

        # Creates UI elements relevant to setting options for task generation at fixed custom rates
        # Interval label and value
        self.taskFixedRateCustomIntervalLabel = tk.Label(self.taskFixedCustomRateOptionsFrame, text="Interval:")

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
        self.taskFixedCustomRateOptionsFrame.grid(row=0, column=2, sticky=tk.W)
        self.taskFixedRateCustomIntervalLabel.grid(row=0, column=0, sticky=tk.W)
        self.taskFixedRateCustomIntervalSpinbox.grid(row=0, column=1, sticky=tk.W)

        # Amount of tasks per interval label and value
        self.taskFixedRateCustomTasksPerIntervalLabel = tk.Label(self.taskFixedCustomRateOptionsFrame, text="Tasks per Interval:")

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
        self.taskFixedRateCustomTasksPerIntervalLabel.grid(row=1, column=0, sticky=tk.W)
        self.taskFixedRateCustomTasksPerIntervalSpinnbox.grid(row=1, column=1, sticky=tk.W)

        # Radiobuttons to select task batching strategy
        self.taskFixedRateCustomTaskBatchingStrategyFrame = tk.Frame(self.taskFixedCustomRateOptionsFrame)
        self.taskFixedRateCustomTaskSingleBatchStrategy = tk.Radiobutton(self.taskFixedRateCustomTaskBatchingStrategyFrame, text="Single Batch", variable=self.taskFixedRateCustomTaskBatchingStrategyValue, value="singlebatch")
        self.taskFixedRateCustomTaskEvenSpreadStrategy = tk.Radiobutton(self.taskFixedRateCustomTaskBatchingStrategyFrame, text="Even Spread", variable=self.taskFixedRateCustomTaskBatchingStrategyValue, value="evenspread")
        self.taskFixedRateCustomTaskSingleBatchStrategy.select()

        # Render radiobuttons and frame
        self.taskFixedRateCustomTaskBatchingStrategyFrame.grid(row=2, column=0, columnspan=3, sticky=tk.W)
        self.taskFixedRateCustomTaskSingleBatchStrategy.grid(row=0, column=0, sticky=tk.W)
        self.taskFixedRateCustomTaskEvenSpreadStrategy.grid(row=0, column=1, sticky=tk.W)
        
    def buildFixedRateTaskMeanRate(self, parentFrame):
        # Clear the parent frame of any leftovers to make room for this frame and its children
        self.removeSubframes(parentFrame)

        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskFixedRateMeanOptionsFrame = tk.Frame(parentFrame)
        self.taskFixedRateMeanOptionsFrame.grid(row=0, column=2, sticky=tk.W)

        # Create descriptive text
        tk.Label(self.taskFixedRateMeanOptionsFrame, text=f"One task will be created per active agent every {round(self.meanOptimalTaskPathLength)} simulation steps.").grid(row=0, column=0)

    def buildFixedRateTaskMaxRate(self, parentFrame):
        # Clear the parent frame of any leftovers to make room for this frame and its children
        self.removeSubframes(parentFrame)
        
        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskFixedRateMaximumOptionsFrame = tk.Frame(parentFrame)
        self.taskFixedRateMaximumOptionsFrame.grid(row=0, column=2, sticky=tk.W)

        # Create descriptive text
        tk.Label(self.taskFixedRateMaximumOptionsFrame, text=f"One task will be created per active agent every {round(self.maximumOptimalPathLength)} simulation steps.").grid(row=0, column=0)

    def buildFixedRateTaskMinRate(self, parentFrame):
        # Clear the parent frame of any leftovers to make room for this frame and its children
        self.removeSubframes(parentFrame)
        
        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskFixedRateMinimumOptionsFrame = tk.Frame(parentFrame)
        self.taskFixedRateMinimumOptionsFrame.grid(row=0, column=2, sticky=tk.W)

        # Create descriptive text
        tk.Label(self.taskFixedRateMinimumOptionsFrame, text=f"One task will be created per active agent every {round(self.minimumOptimalPathLength)} simulation steps.").grid(row=0, column=0)

    def buildFixedRateTaskMedianRate(self, parentFrame):
        # Clear the parent frame of any leftovers to make room for this frame and its children
        self.removeSubframes(parentFrame)
        
        # Create a containing frame for this section
        # Useful for deleting all containing widgets later
        self.taskFixedRateMedianOptionsFrame = tk.Frame(parentFrame)
        self.taskFixedRateMedianOptionsFrame.grid(row=0, column=2, sticky=tk.W)

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
        self.taskAsAvailableOptionsFrame.grid(row=0, column=2, sticky=tk.W)
        self.taskAsAvailableDelayLabel.grid(row=1, column=0, sticky=tk.W)
        self.taskAsAvailableDelaySpinbox.grid(row=1, column=1, sticky=tk.W)

        # Task generation trigger label
        self.taskAsAvailableTriggerLabel = tk.Label(self.taskAsAvailableOptionsFrame, text="Determine agent availability: ")

        # When an agent is 'available' to pick up a new task can be configured
        self.agentAvailabilityTriggerDict = {
            "On Dropoff": "completed",
            "On Demand": "ondemand",
            "On Pickup": "onpickup", 
            "On Assignment": "onassignment", 
            "On Rest": "onrest",
            # "On Recharge": "onrecharge"
        }

        # Menu options are the keys of the dict
        agentAvailabilityTriggerOptions = list(self.agentAvailabilityTriggerDict.keys())

        # Set a default value - maybe skip this to force a choice
        self.taskAsAvailableTriggerStringvar.set(agentAvailabilityTriggerOptions[0])

        # Declare the dropdown menu, linking it to the stringvar and using the option list
        self.taskAsAvailableAvailabilityTriggerMenu = tk.OptionMenu(self.taskAsAvailableOptionsFrame, self.taskAsAvailableTriggerStringvar, *agentAvailabilityTriggerOptions)

        # Render the menu and its label
        self.taskAsAvailableTriggerLabel.grid(row=0, column=0, sticky=tk.W)
        self.taskAsAvailableAvailabilityTriggerMenu.grid(row=0, column=1, sticky=tk.W)

    def createTaskLocationOptions(self):
        # Allow the user to assign weights or entirely disable certain pickup and dropoff nodes
        # Containing frames
        self.taskLocationPickupLabelFrame = tk.LabelFrame(self.taskLocationFrame, text="Pickup Nodes")
        self.taskLocationPickupLabelFrame.grid(row=3, column=0)
        # Use custom scrolled frame for long lists
        self.taskLocationPickupScrollFrame = tk_e.VerticalScrolledFrame(self.taskLocationPickupLabelFrame)
        self.taskLocationPickupFrame = self.taskLocationPickupScrollFrame.interior
        self.taskLocationPickupScrollFrame.grid(row=0, column=0)

        self.taskLocationDropoffLabelFrame = tk.LabelFrame(self.taskLocationFrame, text="Dropoff Nodes")
        self.taskLocationDropoffLabelFrame.grid(row=3, column=1)
        # Use custom scrolled frame for long lists
        self.taskLocationDropoffScrollFrame = tk_e.VerticalScrolledFrame(self.taskLocationDropoffLabelFrame)
        self.taskLocationDropoffFrame = self.taskLocationDropoffScrollFrame.interior
        self.taskLocationDropoffScrollFrame.grid(row=0, column=0)

        # Spinboxes should only be numeric, so use the validating function
        self.validateTaskWeightValues = self.register(self.validateNumericSpinbox)

        # Get all pickup and dropoff nodes
        nodeTypeDict = self.parent.mapData.generateNodeListsByType()
        listOfPickupNodes = nodeTypeDict['pickup']
        listOfDropoffNodes = nodeTypeDict['deposit']

        # Build the GUI for setting weights of nodes, by type
        self.buildNodeWeightingOptions(listOfPickupNodes, self.taskLocationPickupFrame, self.nodeWeightVarDict["pickup"], self.nodeAvailableVarDict["pickup"])
        self.buildNodeWeightingOptions(listOfDropoffNodes, self.taskLocationDropoffFrame, self.nodeWeightVarDict["dropoff"], self.nodeAvailableVarDict["dropoff"])

        # Descriptive text
        tk.Label(self.taskLocationFrame, text="Set the relative weight of each node being selected when a task is generated.").grid(row=0, column=0, columnspan=2)
        tk.Label(self.taskLocationFrame, text="Each task generated randomly selects a pickup node and a dropoff node.").grid(row=1, column=0, columnspan=2)
        tk.Label(self.taskLocationFrame, text="Untick a node to ban it from being selected.").grid(row=2, column=0, columnspan=2)

    def enterVScrollFrameSpinbox(self, event, bindTarget):
        # Release the mouse from managing the containing canvas before binding it to the spinbox it just entered
        bindTarget.unbind_mwheel()
        event.widget.bind('<MouseWheel>', lambda event: event.widget.invoke('buttonup') if event.delta>0 else event.widget.invoke('buttondown'))

    def leaveVScrollFrameSpinbox(self, event, bindTarget):
        # Release the mouse from managing the spinbox before reattaching it to the canvas containing the spinbox
        event.widget.unbind('<MouseWheel>')
        bindTarget.bind_mwheel()

    def buildNodeWeightingOptions(self, nodeList, targetFrame, targetWeightDict, targetAvailableDict):
        # Iterate over all nodes in the given list
        for index, node in enumerate(nodeList):
            # Each node needs a label, tickbox, and numeric spinbox for weight
            # Create the label, displaying the nodes ID/coordinates
            nodeLabel = tk.Label(targetFrame, text=str(node))
            nodeLabel.grid(row=index, column=0, sticky=tk.W)

            # Create the spinbox, to hold the relative numeric weight entry
            # Use the textvariable option to enable trace callbacks on changed values
            nodeWeightValue = tk.StringVar()
            targetWeightDict[str(node)] = nodeWeightValue # Tkinter garbage collects local variables, including their traces, so save them to a dict
            nodeWeightBox = tk.Spinbox(targetFrame,
                width=6,
                from_=0,
                to=1000,
                increment=1,
                validate='key',
                validatecommand=(self.validateTaskWeightValues, '%P'),
                textvariable=nodeWeightValue
            )
            nodeWeightBox.insert(0, 1)
            nodeWeightBox.grid(row=index, column=2, sticky=tk.W)
            # .trace_add() supplies lambda the variable ID (PY_VARXX) and the event ("write")
            nodeWeightValue.trace_add("write", lambda *args, targetDict=targetWeightDict, targetFrame=targetFrame, targetColumn=3, targetNode=node : self.calculateLocationSelectionOdds(targetDict, targetFrame, targetColumn, targetNode))
            # Bind controls to the spinbox
            nodeWeightBox.bind('<Enter>', lambda event, bindTarget=targetFrame.master.master: self.enterVScrollFrameSpinbox(event, bindTarget))
            nodeWeightBox.bind('<Leave>', lambda event, bindTarget=targetFrame.master.master: self.leaveVScrollFrameSpinbox(event, bindTarget))

            # Create a label display the calculated % chance this node gets used per task generation
            nodeChanceLabel = tk.Label(targetFrame, text="0%")
            nodeChanceLabel.grid(row=index, column=3, sticky=tk.W)
            self.calculateLocationSelectionOdds(targetWeightDict, targetFrame, targetColumn=3, targetNode=node) # Trigger initial calulcation

            # Create a toggle button that disables the use of the tile
            stateCycler = itertools.cycle([tk.DISABLED, tk.NORMAL]) # Use this to track the state of the widgets tied to the checkbutton, cycling the value on each callback
            nodeTickVar = tk.IntVar()
            targetAvailableDict[str(node)] = nodeTickVar # Tkinter garbage collects local variables, including their traces, so save them to a dict
            nodeTickVar.set(1)
            nodeTick = tk.Checkbutton(targetFrame, variable=nodeTickVar,
                command = lambda stateCycler=stateCycler, index=index, targetFrame=targetFrame, controlWidgetColumn=1, rowName=str(node): 
                                self.toggleWidgetsInRow(index, stateCycler, targetFrame, controlWidgetColumn))
            nodeTick.grid(row=index, column=1, sticky=tk.W)

    def buildDisplayOptionsPage(self):
        SPINBOX_DEFAULT_RANGE = (1, 100000, 50)

        # Headless mode checkbutton
        self.renderPlaybackValue = tk.BooleanVar()
        
        # Render duration vars instantiated here for organization and reference
        self.renderNewSimStep = tk.BooleanVar()
        self.renderNewSimStepTime = tk.IntVar()
        self.renderAgentSelect = tk.BooleanVar()
        self.renderAgentSelectTime = tk.IntVar()
        self.renderTaskAssignment = tk.BooleanVar()
        self.renderTaskAssignmentTime = tk.IntVar()
        self.renderAgentActionSelection = tk.BooleanVar()
        self.renderAgentActionSelectionTime = tk.IntVar()
        self.renderTaskInteraction = tk.BooleanVar()
        self.renderTaskInteractionTime = tk.IntVar()
        self.renderAgentPlanMove = tk.BooleanVar()
        self.renderAgentPlanMoveTime = tk.IntVar()
        self.renderAgentMovement = tk.BooleanVar()
        self.renderAgentMovementTime = tk.IntVar()
        self.renderAgentPathfind = tk.BooleanVar()
        self.renderAgentPathfindTime = tk.IntVar()
        self.renderCheckAgentQueue = tk.BooleanVar()
        self.renderCheckAgentQueueTime = tk.IntVar()
        self.renderEndSimStep = tk.BooleanVar()
        self.renderEndSimStepTime = tk.IntVar()

        # UI Definition Dict
        # Sorcery
        cwd = Path(__file__).parent
        filePath = (cwd / 'simdisplaymenuconfig.txt').resolve()
        self.displayOptionSet = eval(open(filePath, "r").read())

        self.frameDelayOptionSetFrame = tk.LabelFrame(self.displayOptionsFrame, text="Frame Display Time Configuration")
        self.frameDelayOptionSetFrame.grid(row=1, column=0)
        self.frameDelayOptionSetUI = tk_e.ConfigOptionSet(self.frameDelayOptionSetFrame)
        self.frameDelayOptionSetUI.buildOutOptionSetUI(self.displayOptionSet)

    def toggleWidgetsInRow(self, index, stateCycler, targetFrame, controlWidgetColumn):
        # Using the index of the grid row the widget callback exists in, toggle every other widget
        # State cycler is an `itertools.cycle` object, and the controlWidgetColumn is skipped in iteration
        widgetlist = targetFrame.grid_slaves(row=index)
        nextState = next(stateCycler)   # Get the next state
        for widget in widgetlist:
            # Iterate over every widget, skipping the control column (this should stay tk.normal so that it can be clicked again)
            if not widget.grid_info()["column"]==controlWidgetColumn:
                widget.configure(state=nextState)

        # Piggyback to recalculate and re-render the graph
        self.precalculateTaskGenerationTabInformation()

    def calculateLocationSelectionOdds(self, targetDict, targetFrame, targetColumn, targetNode):
        # Calculates the % chance that a node is selected when a random selection is made for task gen
        # (nodeweight) / (total weight of all nodes) * 100
        # Calculate the total weight
        totalWeight = 0
        for nodeName in targetDict:
            nodeWeight = float(targetDict[nodeName].get())
            totalWeight = totalWeight + nodeWeight
        
        # Calculate each node's share of the total weight
        for index, nodeName in enumerate(targetDict):
            nodeWeight = float(targetDict[nodeName].get())
            nodeChance = nodeWeight / totalWeight
            # Update the label in the same row with the value, converted to % for readability
            targetFrame.grid_slaves(row=index, column=targetColumn)[0].configure(text=f"{nodeChance*100:2.2f}%")

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

    def updateTargetOptionMenuChoices(self, targetMenu, menuStringvar, newOptionsList):
        menu = targetMenu["menu"]
        menu.delete(0, tk.END)
        for option in newOptionsList:
            menu.add_command(label=option,
                command=lambda value=option: menuStringvar.set(value))
            
    def packageSimulationConfiguration(self):
        """
            Packages the current simulation configuration for saving
        """
        dataPackage = {}
        # Needs work for handling branched options (nested)
        ### Algorithm Options
        dataPackage["algorithmSelection"] = self.algorithmChoice.get()
        dataPackage["algorithmType"] = self.algorithmOptionTypeDict[self.algorithmChoice.get()]
        # A*
        dataPackage["aStarPathfinderConfig"] = {}
        dataPackage["aStarPathfinderConfig"]["algorithmSAPFAStarHeuristic"] = self.SAPFAstarHeuristic.get()
        dataPackage["aStarPathfinderConfig"]["algorithmSAPFAStarHeuristicCoefficient"] = self.SAPFAstarHeuristicCoefficient.get()
        # LRA*
        dataPackage["LRAstarPathfinderConfig"] = {}
        dataPackage["LRAstarPathfinderConfig"]["algorithmMAPFLRAstarHeuristic"] = self.MAPFLRAstarHeuristic.get()
        dataPackage["LRAstarPathfinderConfig"]["algorithmMAPFLRAstarHeuristicCoefficient"] = self.MAPFLRAstarHeuristicCoefficient.get()
        # CA*
        dataPackage["CAstarPathfinderConfig"] = {}
        dataPackage["CAstarPathfinderConfig"]["algorithmMAPFCAstarHeuristic"] = self.MAPFCAstarHeuristic.get()
        dataPackage["CAstarPathfinderConfig"]["algorithmMAPFCAstarHeuristicCoefficient"] = self.MAPFCAstarHeuristicCoefficient.get()
        # HCA*
        dataPackage["HCAstarPathfinderConfig"] = {}
        dataPackage["HCAstarPathfinderConfig"]["algorithmMAPFHCAstarHeuristic"] = self.MAPFHCAstarHeuristic.get()
        dataPackage["HCAstarPathfinderConfig"]["algorithmMAPFHCAstarHeuristicCoefficient"] = self.MAPFHCAstarHeuristicCoefficient.get()
        # WHCA*
        dataPackage["WHCAstarPathfinderConfig"] = {}
        dataPackage["WHCAstarPathfinderConfig"]["algorithmMAPFWHCAstarHeuristic"] = self.MAPFWHCAstarHeuristic.get()
        dataPackage["WHCAstarPathfinderConfig"]["algorithmMAPFWHCAstarHeuristicCoefficient"] = self.MAPFWHCAstarHeuristicCoefficient.get()
        dataPackage["WHCAstarPathfinderConfig"]["algorithmMAPFWHCAstarWindowSize"] = self.MAPFWHCAstarWindowSize.get()
        # TP
        dataPackage["TPPathfinderConfig"] = {}
        dataPackage["TPPathfinderConfig"]["algorithmMAPFTPHeuristic"] = self.MAPFTPHeuristic.get()
        dataPackage["TPPathfinderConfig"]["algorithmMAPFTPHeuristicCoefficient"] = self.MAPFTPHeuristicCoefficient.get()
        # TPTS
        dataPackage["TPTSPathfinderConfig"] = {}
        dataPackage["TPTSPathfinderConfig"]["algorithmMAPDTPHeuristic"] = self.MAPDTPTSHeuristic.get()
        dataPackage["TPTSPathfinderConfig"]["algorithmMAPDTPHeuristicCoefficient"] = self.MAPDTPTSHeuristicCoefficient.get()


        # Agent Configuration Options
        ### Collisions
        dataPackage["agentCollisionsValue"] = self.agentCollisionsValue.get()

        ### Limited Charge
        dataPackage["agentChargeLimitationValue"] = self.agentChargeLimitationValue.get()
        dataPackage["agentLimitedChargeCostStyleValue"] = self.agentLimitedChargeCostStyleValue.get()
        dataPackage["agentLimitedChargeCapacityValue"] = self.agentLimitedChargeCapacityValue.get()
        dataPackage["agentLimitedChargeStepCostValue"] = self.agentLimitedChargeStepCostValue.get()
        dataPackage["agentLimitedChargeActionCostValue"] = self.agentLimitedChargeActionCostValue.get()
        dataPackage["agentLimitedChargeMovementCostValue"] = self.agentLimitedChargeMovementCostValue.get()
        dataPackage["agentLimitedChargePickupCostValue"] = self.agentLimitedChargePickupCostValue.get()
        dataPackage["agentLimitedChargeDropoffCostValue"] = self.agentLimitedChargeDropoffCostValue.get()

        ### Breakdowns
        dataPackage["agentBreakdownOptionValue"] = self.agentBreakdownOptionValue.get()
        dataPackage["agentBreakdownFixedRateValue"] = self.agentBreakdownFixedRateValue.get()
        dataPackage["agentBreakdownChancePerStepValue"] = self.agentBreakdownChancePerStepValue.get()

        ### Start position
        dataPackage["agentStartPosStyleValue"] = self.agentStartPosStyleValue.get()

        ### Movement Costs
        dataPackage["agentMiscOptionRotateCostValu"] = self.agentMiscOptionRotateCostValue.get()

        ### Interaction Costs
        dataPackage["agentMiscOptionTaskInteractCostValue"] = self.agentMiscOptionTaskInteractCostValue.get()

        # Task Generation Options
        ### Frequency Options
        dataPackage["taskGenerationFrequencyMethod"] = self.taskFrequencySelectionStringvar.get()
        dataPackage["taskGenerationFixedRateMethod"] = self.taskFixedRateSelectionStringvar.get()
        dataPackage["taskGenerationFixedRateCustomInterval"] = self.taskFixedRateCustomIntervalValue.get()
        dataPackage["taskGenerationFixedRateCustomTasksPerInterval"] = self.taskFixedRateCustomTasksPerIntervalValue.get()
        dataPackage["taskGenerationFixedRateCustomTaskDistribution"] = self.taskFixedRateCustomTaskBatchingStrategyValue.get()
        dataPackage["taskGenerationFixedRateMeanTasksPerAgent"] = round(self.meanOptimalTaskPathLength)
        dataPackage["taskGenerationFixedRateMaxTasksPerAgent"] = self.maximumOptimalPathLength
        dataPackage["taskGenerationFixedRateMinTasksPerAgent"] = self.minimumOptimalPathLength
        dataPackage["taskGenerationFixedRateMedianTasksPerAgent"] = self.medianOptimalTaskPathLength
        dataPackage["taskGenerationAsAvailableDelayTime"] = self.taskAsAvailableDelayValue.get()
        dataPackage["taskGenerationAsAvailableTrigger"] = self.agentAvailabilityTriggerDict[self.taskAsAvailableTriggerStringvar.get()]
        dataPackage["tasksAreScheduled"] = self.tasksAreScheduled
        dataPackage["taskScheduleFile"] = self.taskSchedule

        ### Node selection options
        dataPackage["taskNodeWeightDict"] = self.nodeWeightVarDict
        dataPackage["taskNodeAvailableDict"] = self.nodeAvailableVarDict

        ### Display Options
        # Headless mode checkbutton
        dataPackage["renderSimulationPlayback"] = self.renderPlaybackValue.get()
        
        # Render duration vars instantiated here for organization and reference
        dataPackage["renderNewSimStep"] = self.renderNewSimStep.get()
        dataPackage["renderNewSimStepTime"] = self.renderNewSimStepTime.get()
        dataPackage["renderAgentSelect"] = self.renderAgentSelect.get()
        dataPackage["renderAgentSelectTime"] = self.renderAgentSelectTime.get()
        dataPackage["renderTaskAssignment"] = self.renderTaskAssignment.get()
        dataPackage["renderTaskAssignmentTime"] = self.renderTaskAssignmentTime.get()
        dataPackage["renderAgentActionSelection"] = self.renderAgentActionSelection.get()
        dataPackage["renderAgentActionSelectionTime"] = self.renderAgentActionSelectionTime.get()
        dataPackage["renderTaskInteraction"] = self.renderTaskInteraction.get()
        dataPackage["renderTaskInteractionTime"] = self.renderTaskInteractionTime.get()
        dataPackage["renderAgentPlanMove"] = self.renderAgentPlanMove.get()
        dataPackage["renderAgentPlanMoveTime"] = self.renderAgentPlanMoveTime.get()
        dataPackage["renderAgentMovement"] = self.renderAgentMovement.get()
        dataPackage["renderAgentMovementTime"] = self.renderAgentMovementTime.get()
        dataPackage["renderAgentPathfind"] = self.renderAgentPathfind.get()
        dataPackage["renderAgentPathfindTime"] = self.renderAgentPathfindTime.get()
        dataPackage["renderCheckAgentQueue"] = self.renderCheckAgentQueue.get()
        dataPackage["renderCheckAgentQueueTime"] = self.renderCheckAgentQueueTime.get()
        dataPackage["renderEndSimStep"] = self.renderEndSimStep.get()
        dataPackage["renderEndSimStepTime"] = self.renderEndSimStepTime.get()

        ### Simulation end statements
        dataPackage["simulationEndConditions"] = {}
        dataPackage["simulationEndConditions"]["simulationEndOnTaskCount"] = self.endSimOnTaskCount.get()
        dataPackage["simulationEndConditions"]["simulationEndTaskCount"] = self.endSimTaskCount.get()
        dataPackage["simulationEndConditions"]["simulationEndOnStepCount"] = self.endSimOnStepCount.get()
        dataPackage["simulationEndConditions"]["simulationEndStepCount"] = self.endSimStepCount.get()
        dataPackage["simulationEndConditions"]["simulationEndOnSchedule"] = self.endSimOnScheduleEnd.get()

        return dataPackage
    
    def launchSimulation(self):
        simulationSettings = self.packageSimulationConfiguration()
        self.parent.launchSimulator(simulationSettings)

class simulationConfigurationState:
    # Holds the current state of the simulation config
    def __init__(self, parent):
        self.parent = parent
        logging.info("Simulation State Default Init")