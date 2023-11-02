import tkinter as tk
import logging
from tkinter import ttk
from tkinter import font as tkfont


class simScoreView(tk.Frame):
    """
        The containing frame for the simulation data readout view
    """
    def __init__(self, parent, targetFrame):
        logging.debug("Simulation Data View UI Class initializing . . .")
        self.parent = parent
        self.targetFrame = targetFrame

        # Fetch frame style configuration
        self.appearanceValues = self.parent.parent.parent.appearance
        frameHeight = self.appearanceValues.simulationInfoPanelHeight
        frameWidth = self.appearanceValues.simulationInfoPanelWidth
        frameBorderWidth = self.appearanceValues.frameBorderWidth
        frameRelief = self.appearanceValues.frameRelief
        logging.debug("Fetched styling information.")

        # Declare frame
        tk.Frame.__init__(self, targetFrame,
            borderwidth=frameBorderWidth,
            relief=frameRelief,
            )
        logging.debug("Simulation Data View Containing Frame constructed.")
        
        # Render frame
        self.grid(row=3, column=0, sticky="ews")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

    def buildReferences(self):
        self.scoreHeaderText = tk.Label(self, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"),
            text="Simulation Score")
        self.scoreHeaderText.grid(row=0, column=0, sticky=tk.W+tk.E)
        self.scoreAlgorithmText = tk.Label(self, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"), text="Algo")
        self.scoreAlgorithmText.grid(row=0, column=1, sticky=tk.E)
        self.flatStatsFrame = tk.Frame(self)
        self.flatStatsFrame.grid(row=1, column=0, sticky="ew", columnspan=2)
        self.separator = ttk.Separator(self, orient="horizontal")
        self.separator.grid(row=2, column=0, columnspan=50, sticky="ew")
        # Table items
        self.timeTableNameHeader = tk.Label(self, text="Completed Task Stats . . .", font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"))
        self.timeTableNameHeader.grid(row=3, column=0, sticky=tk.W+tk.E)
        self.tableStatsFrame = tk.Frame(self)
        self.tableStatsFrame.grid(row=4, column=0, sticky="ew", columnspan=2)

        # Number of tasks completed
        self.taskCompletionLabel = tk.Label(self.flatStatsFrame, text="Task Completion Count:", font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"))
        self.taskCompletionLabel.grid(row=0, column=0, sticky=tk.E)
        # Dynamic text needs a stringvar
        self.taskCompletionValue = tk.StringVar(value="0")
        self.taskCompletionText = tk.Label(self.flatStatsFrame, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"), textvariable=self.taskCompletionValue)
        self.taskCompletionText.grid(row=0, column=1, sticky=tk.W)

        # Steps taken
        self.simulationStepLabel = tk.Label(self.flatStatsFrame, text="Time Steps Elapsed:", font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"))
        self.simulationStepLabel.grid(row=1, column=0, sticky=tk.E)
        # Dynamic text linked to the stepview
        self.simulationStepText = tk.Label(self.flatStatsFrame, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"), textvariable=self.parent.simStepView.simStepCountTextValue)
        self.simulationStepText.grid(row=1, column=1, sticky=tk.W)

        # Conflict count
        self.conflictCountLabel = tk.Label(self.flatStatsFrame, text="Conflict Count:", font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"))
        self.conflictCountLabel.grid(row=0, column=2, sticky=tk.E)
        # Dynamic text needs a stringvar
        self.conflictCountValue = tk.StringVar(value="0")
        self.conflictCountText = tk.Label(self.flatStatsFrame, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"), textvariable=self.conflictCountValue)
        self.conflictCountText.grid(row=0, column=3, sticky=tk.W)

        # Pathfind failures
        self.pathfindFailCountLabel = tk.Label(self.flatStatsFrame, text="Pathfinder Fails:", font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"))
        self.pathfindFailCountLabel.grid(row=1, column=2, sticky=tk.E)
        # Dynamic text needs a stringvar
        self.pathfindFailCountValue = tk.StringVar(value="?")
        self.pathfindFailCountText = tk.Label(self.flatStatsFrame, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"), textvariable=self.pathfindFailCountValue)
        self.pathfindFailCountText.grid(row=1, column=3, sticky=tk.W)

        ### Table items
        
        # Headers
        self.timeTableRawLabel = tk.Label(self.tableStatsFrame, text="Raw Time", font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"))
        self.timeTableRawLabel.grid(row=0, column=1)
        self.timeTableNormalisedLabel = tk.Label(self.tableStatsFrame, text="Normalised", font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"))
        self.timeTableNormalisedLabel.grid(row=0, column=2)

        # Service time
        self.runTimeLabel = tk.Label(self.tableStatsFrame, text="Run Time:", font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"))
        self.runTimeLabel.grid(row=1, column=0, sticky=tk.E)
        # Raw
        self.runTimeValue = tk.StringVar(value="-")
        self.runTimeText = tk.Label(self.tableStatsFrame, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"), textvariable=self.runTimeValue)
        self.runTimeText.grid(row=1, column=1)
        # Normalized
        self.normrunTimeValue = tk.StringVar(value="-")
        self.normrunTimeText = tk.Label(self.tableStatsFrame, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"), textvariable=self.normrunTimeValue)
        self.normrunTimeText.grid(row=1, column=2)

        # Service time
        self.serviceTimeLabel = tk.Label(self.tableStatsFrame, text="Service Time:", font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"))
        self.serviceTimeLabel.grid(row=2, column=0, sticky=tk.E)
        # Raw
        self.serviceTimeValue = tk.StringVar(value="-")
        self.serviceTimeText = tk.Label(self.tableStatsFrame, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"), textvariable=self.serviceTimeValue)
        self.serviceTimeText.grid(row=2, column=1)
        # Normalized
        self.normServiceTimeValue = tk.StringVar(value="-")
        self.normServiceTimeText = tk.Label(self.tableStatsFrame, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"), textvariable=self.normServiceTimeValue)
        self.normServiceTimeText.grid(row=2, column=2)

        # Life time
        self.lifeTimeLabel = tk.Label(self.tableStatsFrame, text="Lifetime:", font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"))
        self.lifeTimeLabel.grid(row=3, column=0, sticky=tk.E)
        # Raw
        self.lifeTimeValue = tk.StringVar(value="-")
        self.lifeTimeText = tk.Label(self.tableStatsFrame, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"), textvariable=self.lifeTimeValue)
        self.lifeTimeText.grid(row=3, column=1)
        # Normalized not applicable
        self.normLifeTimeText = tk.Label(self.tableStatsFrame, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"), text="-")
        self.normLifeTimeText.grid(row=3, column=2)

        # Serviceability
        # Life time
        self.serviceabilityLabel = tk.Label(self.tableStatsFrame, text="Serviceability:", font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"))
        self.serviceabilityLabel.grid(row=4, column=0, sticky=tk.E)
        # Raw
        self.serviceabilityValue = tk.StringVar(value="-")
        self.serviceabilityText = tk.Label(self.tableStatsFrame, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"), textvariable=self.serviceabilityValue)
        self.serviceabilityText.grid(row=4, column=1)
        # Normalized not applicable
        self.normserviceabilityText = tk.Label(self.tableStatsFrame, font=(tkfont.nametofont("TkDefaultFont"), 8, "bold"), text="-")
        self.normserviceabilityText.grid(row=4, column=2)
