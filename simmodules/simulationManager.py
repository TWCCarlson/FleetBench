import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
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

        # Building a notebook; each page contains a set of options
        self.configNotebook = ttk.Notebook(self)

        # Each page needs a space to insert widgets
        self.pathfindingAlgorithmFrame = tk.Frame(self.configNotebook)
        self.agentConfigurationFrame = tk.Frame(self.configNotebook)
        self.taskGenerationFrame = tk.Frame(self.configNotebook)
        self.displayOptionsFrame = tk.Frame(self.configNotebook)

        # Tabnames-tabframes,tabbuildfunction dictionary
        noteBookTabs = {
            "Pathfinding Algorithm": (self.pathfindingAlgorithmFrame, self.buildPathfindingAlgorithmPage),
            "Agent Configuration": (self.agentConfigurationFrame, self.buildAgentConfigurationPage),
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

            # Update relevant text
            self.updateTaskStatsText()

            # Update relevant graph
            self.updateTaskInfoPlot()

            # Maximum optimal traversal distance from anywhere in the warehouse to anywhere in the warehouse
            # Turns out this is NP hard and probably not all that useful anyway

    def buildPathfindingAlgorithmPage(self):
        # Intermediate function grouping together declarations and renders for the algorithm choices page
        self.createAlgorithmOptions()

    def buildAgentConfigurationPage(self):
        # Intermediate function grouping together declarations and renders for the agent configuration page
        self.agentChargeOptionFrame = tk.Frame(self.agentConfigurationFrame)
        self.agentChargeOptionFrame.grid(row=0, column=0, sticky=tk.W)
        self.buildAgentChargeOptions()
        self.populateAgentChargeOptions()
        self.renderAgentChargeOptions()
        # self.agentTypeOptionFrame = tk.Frame(self.agentConfigurationFrame)
        # self.agentTypeOptionFrame.grid(row=0, column=0)
        # self.buildAgentTypeOptions(self.agentTypeOptionFrame)
        self.agentBreakdownOptionFrame = tk.Frame(self.agentConfigurationFrame)
        self.agentBreakdownOptionFrame.grid(row=1, column=0, sticky=tk.W)
        self.buildAgentBreakdownOptions(self.agentBreakdownOptionFrame)
        self.populateAgentBreakdownOptions(self.agentBreakdownOptionFrame)
        self.renderAgentBreakdownOptions()
        self.agentStartPosOptionFrame = tk.Frame(self.agentConfigurationFrame)
        self.agentStartPosOptionFrame.grid(row=2, column=0, sticky=tk.W)
        self.buildAgentStartPosOptions(self.agentStartPosOptionFrame)
        self.populateAgentStartPosOptions(self.agentStartPosOptionFrame)
        self.renderAgentStartPosOptions()
        self.agentMiscOptionsFrame = tk.Frame(self.agentConfigurationFrame)
        self.agentMiscOptionsFrame.grid(row=3, column=0, sticky=tk.W)
        self.buildAgentMiscOptions(self.agentMiscOptionsFrame)
        self.populateAgentMiscOptions(self.agentMiscOptionsFrame)
        self.renderAgentMiscOptions()

    def buildAgentChargeOptions(self):
        # Creates widgets for options related to how the charge level on agents is managed
        # Create a label
        self.agentChargeOptionLabel = tk.Label(self.agentChargeOptionFrame)

        # Create an optionmenu and the variable holding the selection
        self.agentChargeOptionValue = tk.StringVar()
        self.agentChargeOptionMenu = tk.OptionMenu(self.agentChargeOptionFrame, self.agentChargeOptionValue, "temp")

    def populateAgentChargeOptions(self):
        # Inserts data into the agent charge level management options widgets

        # Set label text
        self.agentChargeOptionLabel.configure(text="Agent Charge Limitation:")

        # Build the dict of options and their relevant frames
        agentChargeStyleOptionsDict = {
            "Ignored / Unlimited": self.buildAgentUnlimitedChargeOptions,
            "Limited": self.buildAgentLimitedChargeOptionSet
        }

        # Menu options are the text in the dict keys
        agentChargeStyleMenuOptions = list(agentChargeStyleOptionsDict.keys())

        # Regenerate the menu with options
        self.updateTargetOptionMenuChoices(self.agentChargeOptionMenu, self.agentChargeOptionValue, agentChargeStyleMenuOptions)

        # Add a trace to the menu stringvar to call up the relevant UI when a choice is made
        self.agentChargeOptionValue.trace_add("write", lambda *args, selection=self.agentChargeOptionValue, parentFrame=self.agentChargeOptionFrame: agentChargeStyleOptionsDict[selection.get()](parentFrame))

        # Set a default selection - maybe skip this to force a choice
        self.agentChargeOptionValue.set(agentChargeStyleMenuOptions[0])

    def renderAgentChargeOptions(self):
        # Renders the agent charge level management widgets
        self.agentChargeOptionLabel.grid(row=0, column=0, sticky=tk.W)
        self.agentChargeOptionMenu.grid(row=0, column=1, sticky=tk.W)

    def buildAgentUnlimitedChargeOptions(self, parentFrame):
        # There are no options if the charge is unlimited
        # Therefore just remove any suboption frames
        self.removeSubframes(parentFrame)

    def buildAgentLimitedChargeOptionSet(self, parentFrame):
        # When agent energy is a limited and managed resource, user needs to set agent:
        # Capacity, costs, charge rate, and charge station strategy
        # Clear out any subframes
        self.removeSubframes(parentFrame)

        # Build a new subframe for containing everything
        self.agentLimitedChargeOptionsFrame = tk.Frame(parentFrame)
        self.agentLimitedChargeOptionsFrame.grid(row=0, column=2, sticky=tk.W)

        # Build, then populate, then render the widgets
        self.buildAgentLimitedChargeOptions(self.agentLimitedChargeOptionsFrame)
        self.populateAgentLimitedChargeOptions(self.agentLimitedChargeOptionsFrame)
        self.renderAgentLimitedChargeOptions()

    def buildAgentLimitedChargeOptions(self, parentFrame):
        # Creates widgets relating to the option set when agent charge is limited
        
        ### Capacity widgets
        # Label
        self.agentLimitedChargeCapacityLabel = tk.Label(parentFrame)

        # Numeric spinbox
        self.agentLimitedChargeCapacityValue = tk.StringVar()
        self.validateAgentChargeCapacityValue = self.register(self.validateNumericSpinbox)
        self.agentLimitedChargeCapacitySpinbox = ttk.Spinbox(parentFrame,
            width=6,
            from_=1,
            to=100000,
            increment=1,
            textvariable=self.agentLimitedChargeCapacityValue,
            validate='key',
            validatecommand=(self.validateAgentChargeCapacityValue, '%P')
        )

        ### Costs widgets
        # Label
        self.agentLimitedChargeCostStyleLabel = tk.Label(parentFrame)

        # Optionmenu for cost payment style
        self.agentLimitedChargeCostStyleValue = tk.StringVar()
        self.agentLimitedChargeCostStyleMenu = tk.OptionMenu(parentFrame, self.agentLimitedChargeCostStyleValue, "temp")

    def populateAgentLimitedChargeOptions(self, parentFrame):
        # Attaches information to the widgets for limited agent charge options

        # Set agent capacity label text
        self.agentLimitedChargeCapacityLabel.configure(text="Agent Charge Capacity:")

        # Set agent cost payment style text
        self.agentLimitedChargeCostStyleLabel.configure(text="Cost Determ. Method:")

        # Build the dict of options and their relevant frames
        agentLimitedChargeCostStyleDict = {
            "Fixed per sim. step": self.buildAgentLimitedChargeStepCostSet,
            "Fixed per action taken": self.buildAgentLimitedChargeActionCostSet,
            "Custom": self.buildAgentLimitedChargeCustomCostSet,
        }

        # Menu options are the text in the dict keys
        agentLimitedChargeCostStyleMenuOptions = list(agentLimitedChargeCostStyleDict.keys())

        # Regenerate the menu with options
        self.updateTargetOptionMenuChoices(self.agentLimitedChargeCostStyleMenu, self.agentLimitedChargeCostStyleValue, agentLimitedChargeCostStyleMenuOptions)

        # Add a `z` to the menu stringvar to call up the relevant UI when a choice is made
        self.agentLimitedChargeCostStyleValue.trace_add("write", lambda *args, selection=self.agentLimitedChargeCostStyleValue,
            parentFrame=parentFrame : agentLimitedChargeCostStyleDict[selection.get()](parentFrame))
        
        # Set a default selection - maybe skip this to force a choice
        self.agentLimitedChargeCostStyleValue.set(agentLimitedChargeCostStyleMenuOptions[0])

    def renderAgentLimitedChargeOptions(self):
        # Renders widgets relating to limited agent charge options
        self.agentLimitedChargeCapacityLabel.grid(row=0, column=0, sticky=tk.W)
        self.agentLimitedChargeCapacitySpinbox.grid(row=0, column=1, sticky=tk.W)

        self.agentLimitedChargeCostStyleLabel.grid(row=1, column=0, sticky=tk.W)
        self.agentLimitedChargeCostStyleMenu.grid(row=1, column=1, sticky=tk.W)
        
    def buildAgentLimitedChargeStepCostSet(self, parentFrame):
        # Intermediate function for options about energy cost in simulation
        # Clear out any subframes
        self.removeSubframes(parentFrame)

        # Create new subframe for easier management
        self.agentLimitedChargeStepCostOptionFrame = tk.Frame(parentFrame)
        self.agentLimitedChargeStepCostOptionFrame.grid(row=0, column=2, sticky=tk.W)

        self.buildAgentLimitedChargeStepCostOptions(self.agentLimitedChargeStepCostOptionFrame)
        self.populateAgentLimitedChargeStepCostOptions()
        self.renderAgentLimitedChargeStepCostOptions()

    def buildAgentLimitedChargeStepCostOptions(self, parentFrame):
        # Builds widgets related to setting the cost per step when agent charge is limited
        # Spinbox label
        self.agentLimitedChargeStepCostLabel = tk.Label(parentFrame)
        
        # Numeric Spinbox for entering the cost per simulation step
        self.agentLimitedChargeStepCostValue = tk.StringVar()
        self.validateAgentChargeStepCost = self.register(self.validateNumericSpinbox)
        self.agentLimitedChargeStepCostSpinbox = ttk.Spinbox(parentFrame,
            width=6,
            from_=1,
            to=100000,
            increment=1,
            textvariable=self.agentLimitedChargeStepCostValue,
            validate='key',
            validatecommand=(self.validateAgentChargeStepCost, '%P')
        )

    def populateAgentLimitedChargeStepCostOptions(self):
        # Inserts data into the agent charge cost per simulation step options widgets
        # Set label text
        self.agentLimitedChargeStepCostLabel.configure(text="Cost Per Sim. Step:")

    def renderAgentLimitedChargeStepCostOptions(self):
        # Renders agent charge cost per simulation step options widgets
        self.agentLimitedChargeStepCostLabel.grid(row=0, column=0, sticky=tk.W)
        self.agentLimitedChargeStepCostSpinbox.grid(row=0, column=1, sticky=tk.W)

    def buildAgentLimitedChargeActionCostSet(self,parentFrame):
        # Intermediate function for options about energy cost per action
        # Clear out any subframes
        self.removeSubframes(parentFrame)

        # Create new subframe for easier management
        self.agentLimitedChargeActionCostFrame = tk.Frame(parentFrame)
        self.agentLimitedChargeActionCostFrame.grid(row=0, column=2, sticky=tk.W)

        self.buildAgentLimitedChargeActionCostOptions(self.agentLimitedChargeActionCostFrame)
        self.populateAgentLimitedChargeActionCostOptions()
        self.renderAgentLimitedChargeActionCostOptions()

    def buildAgentLimitedChargeActionCostOptions(self, parentFrame):
        # Builds widgets related to setting the cost per action when the agent charge is limited
        # Spinbox label
        self.agentLimitedChargeActionCostLabel = tk.Label(parentFrame)

        # Numeric spinbox for entering the cost per agent action
        self.agentLimitedChargeActionCostValue = tk.StringVar()
        self.validateAgentChargeActionCost = self.register(self.validateNumericSpinbox)
        self.agentLimitedChargeActionCostSpinbox = ttk.Spinbox(parentFrame,
            width=6,
            from_=1,
            to=100000,
            increment=1,
            textvariable=self.agentLimitedChargeActionCostValue,
            validate='key',
            validatecommand=(self.validateAgentChargeActionCost, '%P')
        )

    def populateAgentLimitedChargeActionCostOptions(self):
        # Inserts data into the agent charge cost per simulation step options widgets
        # Set label text
        self.agentLimitedChargeActionCostLabel.configure(text="Cost Per Action:")

    def renderAgentLimitedChargeActionCostOptions(self):
        # Renders agent charge cost per action options widgets
        self.agentLimitedChargeActionCostLabel.grid(row=0, column=0, sticky=tk.W)
        self.agentLimitedChargeActionCostSpinbox.grid(row=0, column=1, sticky=tk.W)

    def buildAgentLimitedChargeCustomCostSet(self, parentFrame):
        # Intermediate function grouping functions related to setting custom costs
        # X per move, Y per pickup, Z per step
        # Clear out any subframes
        self.removeSubframes(parentFrame)

        # Create new subframe for easier management
        self.agentLimitedChargeCustomCostFrame = tk.Frame(parentFrame)
        self.agentLimitedChargeCustomCostFrame.grid(row=0, column=2, rowspan=2)

        self.buildAgentLimitedChargeCustomCostOptions(self.agentLimitedChargeCustomCostFrame)
        self.populateAgentLimitedChargeCustomCostOptions()
        self.renderAgentLimitedChargeCustomCostOptions()

    def buildAgentLimitedChargeCustomCostOptions(self, parentFrame):
        # Builds widgets related to setting a custom cost value for each type of action an agent can take
        ### Movement cost
        # Spinbox label
        self.agentLimitedChargeMovementCostLabel = tk.Label(parentFrame)

        # Numeric spinbox for entering the cost per agent move
        self.agentLimitedChargeMovementCostValue = tk.StringVar()
        self.validateAgentChargeMovementCost = self.register(self.validateNumericSpinbox)
        self.agentLimitedChargeMovementCostSpinbox = ttk.Spinbox(parentFrame,
            width=6,
            from_=1,
            to=100000,
            increment=1,
            textvariable=self.agentLimitedChargeMovementCostValue,
            validate='key',
            validatecommand=(self.validateAgentChargeMovementCost, '%P')
        )
        
        ### Pickup cost
        # Spinbox label
        self.agentLimitedChargePickupCostLabel = tk.Label(parentFrame)

        # Numeric spinbox for entering the cost per agent pickup action
        self.agentLimitedChargePickupCostValue = tk.StringVar()
        self.validateAgentChargePickupCost = self.register(self.validateNumericSpinbox)
        self.agentLimitedChargePickupCostSpinbox = ttk.Spinbox(parentFrame,
            width=6,
            from_=1,
            to=100000,
            increment=1,
            textvariable=self.agentLimitedChargePickupCostValue,
            validate='key',
            validatecommand=(self.validateAgentChargePickupCost, '%P')
        )

        ### Dropoff cost
        # Spinbox label
        self.agentLimitedChargeDropoffCostLabel = tk.Label(parentFrame)

        # Numeric spinbox for entering the cost per agent action
        self.agentLimitedChargeDropoffCostValue = tk.StringVar()
        self.validateAgentChargeDropoffCost = self.register(self.validateNumericSpinbox)
        self.agentLimitedChargeDropoffCostSpinbox = ttk.Spinbox(parentFrame,
            width=6,
            from_=1,
            to=100000,
            increment=1,
            textvariable=self.agentLimitedChargeDropoffCostValue,
            validate='key',
            validatecommand=(self.validateAgentChargeDropoffCost, '%P')
        )

    def populateAgentLimitedChargeCustomCostOptions(self):
        # Inserts data into the agent charge cost per simulation step options widgets
        # Set label text
        self.agentLimitedChargeMovementCostLabel.configure(text="Cost Per Move:")
        self.agentLimitedChargePickupCostLabel.configure(text="Cost Per Pickup:")
        self.agentLimitedChargeDropoffCostLabel.configure(text="Cost Per Dropoff:")

    def renderAgentLimitedChargeCustomCostOptions(self):
        # Renders agent charge custom cost by action type options widgets
        self.agentLimitedChargeMovementCostLabel.grid(row=0, column=0, sticky=tk.W)
        self.agentLimitedChargeMovementCostSpinbox.grid(row=0, column=1, sticky=tk.W)
        self.agentLimitedChargePickupCostLabel.grid(row=1, column=0, sticky=tk.W)
        self.agentLimitedChargePickupCostSpinbox.grid(row=1, column=1, sticky=tk.W)
        self.agentLimitedChargeDropoffCostLabel.grid(row=2, column=0, sticky=tk.W)
        self.agentLimitedChargeDropoffCostSpinbox.grid(row=2, column=1, sticky=tk.W)

    def buildAgentTypeOptions(self, parentFrame):
        # Not implemented
        pass

    def buildAgentBreakdownOptions(self, parentFrame):
        # Intermediate function grouping together declarations and renders for the agent breakdown options page
        # Breakdown style label
        self.agentBreakdownOptionLabel = tk.Label(parentFrame)

        # Option menu for breakdown behavior style selection
        self.agentBreakdownOptionValue = tk.StringVar()
        self.agentBreakdownOptionMenu = tk.OptionMenu(parentFrame, self.agentBreakdownOptionValue, "temp")

        # Breakdown handling label
        self.agentBreakdownHandlingOptionLabel = tk.Label(parentFrame)

        # Option menu for breakdown handling style selection
        self.agentBreakdownHandlingOptionValue = tk.StringVar()
        self.agentBreakdownhandlingOptionMenu = tk.OptionMenu(parentFrame, self.agentBreakdownHandlingOptionValue, "temp")

    def populateAgentBreakdownOptions(self, parentFrame):
        # Inserts data in to the agent breakdown handling style widgets
        # Set the label text
        self.agentBreakdownOptionLabel.configure(text="Breakdown Style:")

        # Build the dict of options and relevant UI functions
        agentBreakdownOptionsDict = {
            "Problem-free operation": self.buildAgentNoBreakdownOptionSet,
            "Fixed-rate maintenance schedule": self.buildAgentFixedRateBreakdownOptionSet,
            "Fixed chance of failure per sim. step": self.buildAgentChancePerStepOptionSet
        }

        # Menu options consist of a list of the dict keys
        agentBreakdownMenuOptions = list(agentBreakdownOptionsDict.keys())

        # Regenerate the menu with the options
        self.updateTargetOptionMenuChoices(self.agentBreakdownOptionMenu, self.agentBreakdownOptionValue, agentBreakdownMenuOptions)

        # Trace changes to the option menu's stringvar to call the relevant UI functions
        self.agentBreakdownOptionValue.trace_add("write", lambda *args, selection=self.agentBreakdownOptionValue, parentFrame=parentFrame:
            agentBreakdownOptionsDict[selection.get()](parentFrame))
        
        # Set a default selection - maybe skip this to force a choice
        self.agentBreakdownOptionValue.set(agentBreakdownMenuOptions[0])

        # Set label text
        self.agentBreakdownHandlingOptionLabel.configure(text="Breakdown response:")

        # Build the dict of options
        agentBreakdownResponseList = ["Return home", "Nearest Repair Station"]

        # Regenerate the menu with the options
        self.updateTargetOptionMenuChoices(self.agentBreakdownhandlingOptionMenu, self.agentBreakdownHandlingOptionValue, agentBreakdownResponseList)

        # Set a default selection - maybe skip this to force a choice
        self.agentBreakdownHandlingOptionValue.set(agentBreakdownResponseList[0])
        
    def renderAgentBreakdownOptions(self):
        # Renders the agent breakdown handling option ui widgets
        self.agentBreakdownOptionLabel.grid(row=0, column=0, sticky=tk.W)
        self.agentBreakdownOptionMenu.grid(row=0, column=1, sticky=tk.W)
        self.agentBreakdownHandlingOptionLabel.grid(row=1, column=0, sticky=tk.W)
        self.agentBreakdownhandlingOptionMenu.grid(row=1, column=1, sticky=tk.W)

    def buildAgentNoBreakdownOptionSet(self, parentFrame):
        # Builds widgets relating to the case where the are no agent breakdowns
        # Clear out any subframes
        self.removeSubframes(parentFrame)

        # Currently if breakdowns cannot happen there are no options available

    def buildAgentFixedRateBreakdownOptionSet(self, parentFrame):
        # Intermediate function grouping declarations and renders relating to agent breakdowns occurring at fixed rates
        # Clear out any subframes
        self.removeSubframes(parentFrame)

        # Build a new subframe for containing everything
        self.agentBreakdownFixedRateOptionsFrame = tk.Frame(parentFrame)
        self.agentBreakdownFixedRateOptionsFrame.grid(row=0, column=2, sticky=tk.W)

        # Generate all widgets, populate them with data, and render them
        self.buildAgentBreakdownFixedRateOptions(self.agentBreakdownFixedRateOptionsFrame)
        self.populateAgentBreakdownFixedRateOptions()
        self.renderAgentBreakdownFixedRateOptions()

    def buildAgentBreakdownFixedRateOptions(self, parentFrame):
        # Build widgets related to agent breakdowns occurring at a fixed rate
        # Label
        self.agentBreakdownFixedRateLabel = tk.Label(parentFrame)

        # Numeric spinbox for setting the rate in simulation steps of breakdowns
        self.agentBreakdownFixedRateValue = tk.StringVar()
        self.validateBreakdownFixedRateCost = self.register(self.validateNumericSpinbox)
        self.agentBreakdownFixedRateSpinbox = ttk.Spinbox(parentFrame,
            width=6,
            from_=1,
            to=100000,
            increment=1,
            textvariable=self.agentBreakdownFixedRateValue,
            validate='key',
            validatecommand=(self.validateBreakdownFixedRateCost, '%P')
        )

    def populateAgentBreakdownFixedRateOptions(self):
        # Populate widgets with data
        # Set label text
        self.agentBreakdownFixedRateLabel.configure(text="Sim. steps per incident:")

    def renderAgentBreakdownFixedRateOptions(self):
        # Render the relevant widgets
        self.agentBreakdownFixedRateLabel.grid(row=0, column=0, sticky=tk.W)
        self.agentBreakdownFixedRateSpinbox.grid(row=0, column=1, sticky=tk.W)

    def buildAgentChancePerStepOptionSet(self, parentFrame):
        # Clear out any subframes
        self.removeSubframes(parentFrame)

        # Build a new subframe for containing everything
        self.agentBreakdownChancePerStepOptionsFrame = tk.Frame(parentFrame)
        self.agentBreakdownChancePerStepOptionsFrame.grid(row=0, column=2, sticky=tk.W)

        # Generate all widgets, populate them with data, and render them
        self.buildAgentChancePerStepOptions(self.agentBreakdownChancePerStepOptionsFrame)
        self.populateAgentChancePerStepOptions()
        self.renderAgentChancePerStepOptions()

    def buildAgentChancePerStepOptions(self, parentFrame):
        # Build widgets relating to breakdowns having a fixed chance to occur
        # Label
        self.agentBreakdownChancePerStepLabel = tk.Label(parentFrame)

        # Numeric spinbox for setting the rate in simulation steps of breakdowns
        self.agentBreakdownChancePerStepValue = tk.StringVar()
        self.validateBreakdownChancePerStepCost = self.register(self.validateNumericSpinbox)
        self.agentBreakdownChancePerStepSpinbox = ttk.Spinbox(parentFrame,
            width=6,
            from_=1,
            to=100000,
            increment=1,
            textvariable=self.agentBreakdownChancePerStepValue,
            validate='key',
            validatecommand=(self.validateBreakdownChancePerStepCost, '%P')
        )

        # Label to be used as descriptive text
        self.agentBreakdownChanceOverTimeLabel = tk.Text(parentFrame, fg="black", bg="SystemButtonFace", bd=0, font=(tkfont.nametofont("TkDefaultFont")))
        self.agentBreakdownChanceOverTimeLabel.configure(state=tk.DISABLED, height=3)

    def populateAgentChancePerStepOptions(self):
        # Populate widgets with data
        # Set label text
        self.agentBreakdownChancePerStepLabel.configure(text="Chance of incident per sim. step:")

        # Add a trace to the spinbox var to re-render the text
        self.agentBreakdownChancePerStepValue.trace_add("write", lambda *args, selection=self.agentBreakdownChancePerStepValue,
            targetLabel=self.agentBreakdownChanceOverTimeLabel : self.updateAgentBreakdownChancePerStepText(selection.get(), targetLabel))
        
    def updateAgentBreakdownChancePerStepText(self, value, targetLabel):
        # Calculate the odds of an incident after a few steps
        chanceInFive = (1-(1-float(value)/100000)**5)*100
        chanceInTwenty = (1-(1-float(value)/100000)**20)*100
        chanceInHundred = (1-(1-float(value)/100000)**100)*100

        # Enable editing of the text widget 
        targetLabel.configure(state=tk.NORMAL)

        # Clear the text
        targetLabel.delete('1.0', tk.END)

        # Insert new text
        targetLabel.insert(tk.END, f" The odds of an incident occurring in 5 steps is {chanceInFive:3.5f}%\n")
        targetLabel.insert(tk.END, f" The odds of an incident occurring in 20 steps is {chanceInTwenty:3.5f}%\n")
        targetLabel.insert(tk.END, f" The odds of an incident occurring in 100 steps is {chanceInHundred:3.5f}%\n")

        # Disable user interaction with the widget
        targetLabel.configure(state=tk.DISABLED, height=3)

        # Render the text
        targetLabel.grid(row=0, column=2)

    def renderAgentChancePerStepOptions(self):
        # Render relevant widgets to the window
        self.agentBreakdownChancePerStepLabel.grid(row=0, column=0, sticky=tk.W)
        self.agentBreakdownChancePerStepSpinbox.grid(row=0, column=1, sticky=tk.W)
        self.agentBreakdownChanceOverTimeLabel.grid(row=0, column=2, sticky=tk.W)

    def buildAgentStartPosOptions(self, parentFrame):
        # Build widgets that relate to agent's starting positions
        # Label
        self.agentStartPosStyleLabel = tk.Label(parentFrame)

        # OptionMenu holding style options
        self.agentStartPosStyleValue = tk.StringVar()
        self.agentStartPosStyleMenu = tk.OptionMenu(parentFrame, self.agentStartPosStyleValue, "temp")

    def populateAgentStartPosOptions(self, parentFrame):
        # Populate relevant widgets with data
        self.agentStartPosStyleLabel.configure(text="Agent starting position determined by:")

        # Menu options stored as a list
        agentStartPosStyleOptionsList = [
            "As given in Simulation Edit Window", "Home tiles (automatic assignment)"
        ]

        # Regenerate the menu with the option list
        self.updateTargetOptionMenuChoices(self.agentStartPosStyleMenu, self.agentStartPosStyleValue, agentStartPosStyleOptionsList)

        # No need to trace this menu currently
        # Set a default selection
        self.agentStartPosStyleValue.set(agentStartPosStyleOptionsList[0])

    def renderAgentStartPosOptions(self):
        # Render related widgets
        self.agentStartPosStyleLabel.grid(row=0, column=0)
        self.agentStartPosStyleMenu.grid(row=0, column=1)

    def buildAgentMiscOptions(self, parentFrame):
        # Build widgets relating to miscellaneous agent options
        # Label for whether an agent rotating takes time during simulation
        self.agentMiscOptionRotateCostLabel = tk.Label(parentFrame)

        # Optionmenu containing options related to rotation costs
        self.agentMiscOptionRotateCostValue = tk.StringVar()
        self.agentMiscOptionRotateCostMenu = tk.OptionMenu(parentFrame, self.agentMiscOptionRotateCostValue, "temp")

        # Label for whether an agent picking up or dropping off a task takes time during simulation
        self.agentMiscOptionTaskInteractCostLabel = tk.Label(parentFrame)
    
        # Optionmenu containing options related to interaction costs
        self.agentMiscOptionTaskInteractCostValue = tk.StringVar()
        self.agentMiscOptionTaskInteractCostMenu = tk.OptionMenu(parentFrame, self.agentMiscOptionTaskInteractCostValue, "temp")

    def populateAgentMiscOptions(self, parentFrame):
        # Populate relevant widgets
        # Rotation cost label
        self.agentMiscOptionRotateCostLabel.configure(text="Cost of agent rotations:")

        # Rotation cost optionmenu options list
        agentMiscOptionRotationCostList = [
            "No cost for rotation", "Rotation requires step"
        ]

        # Regenerate the option menu with the new option list
        self.updateTargetOptionMenuChoices(self.agentMiscOptionRotateCostMenu, self.agentMiscOptionRotateCostValue, agentMiscOptionRotationCostList)

        # Set a default option - maybe skip this to force a choice
        self.agentMiscOptionRotateCostValue.set(agentMiscOptionRotationCostList[0])

        # Disable unimplemented option
        self.agentMiscOptionRotateCostMenu['menu'].entryconfigure(agentMiscOptionRotationCostList[1], state=tk.DISABLED)

        # Task interaction cost label
        self.agentMiscOptionTaskInteractCostLabel.configure(text="Cost of task interactions:")

        # Task interaction cost optionmenu options list
        agentMiscOptionTaskInteractionCostList = [
            "No cost for pickup/dropoff", "Pickup/dropoff require step"
        ]
        
        # Regenerate the option menu with the new option list
        self.updateTargetOptionMenuChoices(self.agentMiscOptionTaskInteractCostMenu, self.agentMiscOptionTaskInteractCostValue, agentMiscOptionTaskInteractionCostList)

        # Disable unimplemented option
        self.agentMiscOptionTaskInteractCostMenu['menu'].entryconfigure(agentMiscOptionTaskInteractionCostList[1], state=tk.DISABLED)

        # Set a default value - maybe skip this to force a choice
        self.agentMiscOptionTaskInteractCostValue.set(agentMiscOptionTaskInteractionCostList[0])

    def renderAgentMiscOptions(self):
        # Render rotation cost option widgets
        self.agentMiscOptionRotateCostLabel.grid(row=0, column=0)
        self.agentMiscOptionRotateCostMenu.grid(row=0, column=1)

        # Render task interaction cost option widgets
        self.agentMiscOptionTaskInteractCostLabel.grid(row=1, column=0)
        self.agentMiscOptionTaskInteractCostMenu.grid(row=1, column=1)

    def buildTaskGenerationPage(self):
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

        # Stringvar to hold the option selection
        self.taskFixedRateSelectionStringvar = tk.StringVar()

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
        self.taskFixedCustomRateOptionsFrame.grid(row=0, column=2, sticky=tk.W)
        self.taskFixedRateCustomIntervalLabel.grid(row=0, column=0, sticky=tk.W)
        self.taskFixedRateCustomIntervalSpinbox.grid(row=0, column=1, sticky=tk.W)

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
        self.taskFixedRateCustomTasksPerIntervalLabel.grid(row=1, column=0, sticky=tk.W)
        self.taskFixedRateCustomTasksPerIntervalSpinnbox.grid(row=1, column=1, sticky=tk.W)

        # Radiobuttons to select task batching strategy
        self.taskFixedRateCustomTaskBatchingStrategyFrame = tk.Frame(self.taskFixedCustomRateOptionsFrame)
        self.taskFixedRateCustomTaskBatchingStrategyValue = tk.StringVar()
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
        self.taskAsAvailableOptionsFrame.grid(row=0, column=2, sticky=tk.W)
        self.taskAsAvailableDelayLabel.grid(row=1, column=0, sticky=tk.W)
        self.taskAsAvailableDelaySpinbox.grid(row=1, column=1, sticky=tk.W)

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
        self.algorithmChoiceMenu.grid(row=1, column=0, sticky=tk.W)

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
        self.frameDelayLabel.grid(row=1, column=1, sticky=tk.W)
        self.frameDelayEntry.grid(row=1, column=2, sticky=tk.W)

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

class simulationConfigurationState:
    # Holds the current state of the simulation config
    def __init__(self, parent):
        self.parent = parent
        logging.info("Simulation State Default Init")