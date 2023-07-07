import tkinter as tk
from modules.commandBar import commandBar
from modules.toolBar import toolBar
from modules.mainView import mainView
from modules.contextView import contextView
from modules.mapDataClass import mapDataClass
from modules.infoBox import infoBox
from modules.agentManager import agentManager
from modules.taskManager import taskManager
from modules.randomGenerator import randomGenerator
from modules.simulationManager import simulationConfigManager
from modules.simulationWindow import simulationWindow
from modules.simulationProcess import simulationProcess
from config.appearanceValues import appearanceValues
import logging

class App(tk.Tk):
    def __init__(self):
        # Begin process logging
        self.initLogging()

        # Main window config
        tk.Tk.__init__(self)
        logging.info("RWS Main Window Established.")
        self.title("Warehousing Simulator")

        # RNG Seeding class
        self.randomGenerator = randomGenerator(self)
        logging.info("Class 'randomGenerator' instantiated.")

        # Map information class
        self.mapData = mapDataClass(self)
        # Agent information manager class
        self.agentManager = agentManager(self)
        # Task information manager class
        self.taskManager = taskManager(self)
        # Simulation configuration information class
        # self.simulationManager = simulationConfigManager(self)

        # Window components
        # Appearance
        self.appearance = appearanceValues(self)
        # Command bar: load, save, options
        self.commandBar = commandBar(self)
        # Left pane contains choices and buttons
        self.toolBar = toolBar(self)
        # Central pane info box
        self.infoBox = infoBox(self)
        # Central pane contains the graph display
        self.mainView = mainView(self)
        # Right pane contains contextual information pane
        self.contextView = contextView(self)

        # Build cross-class references
        self.mapData.buildReferences()
        self.infoBox.buildReferences()
        self.toolBar.buildReferences()
        self.mainView.buildReferences()

        # Render the app
        self.mainloop()

    def initLogging(self):
        self.loglevel = logging.DEBUG
        self.loglevelReference = {
            0 :"NOTSET",
            10:"DEBUG",
            20:"INFO",
            30:"WARNING",
            40:"ERROR",
            50:"CRITICAL"
        }
        self.programLogger = logging.basicConfig(filename='example.log', 
            encoding='utf-8', 
            level=self.loglevel, 
            format='[{asctime}.{msecs:<3.0f}][{levelname:^8s}] Module \'{module}\': {message}',
            style='{',
            filemode='w',
            datefmt='%X')
        logging.info("Robot Warehousing Simulator program started.")
        logging.info(f"Logging started with level: {self.loglevelReference[self.loglevel]}")

    def simulationConfiguration(self):
        self.simulationConfigWindow = simulationConfigManager(self)

    def launchSimulator(self):
        print("Simulation Launched!")
        self.simulationConfigWindow.grab_release()
        self.simulationProcess = simulationProcess(self)
        self.simulationWindow = simulationWindow(self)

app = App()