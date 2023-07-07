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
        logging.info("Information class 'mapDataClass' instantiated.")
        # Agent information manager class
        self.agentManager = agentManager(self)
        logging.info("Information class 'agentManager' instantiated.")
        # Task information manager class
        self.taskManager = taskManager(self)
        logging.info("Information class 'taskManager' instantiated.")

        # Window components
        # Appearance
        self.appearance = appearanceValues(self)
        logging.info("Component class 'appearanceValues' instantiated.")
        # Command bar: load, save, options
        self.commandBar = commandBar(self)
        logging.info("Component class 'mapDataClass' instantiated.")
        # Left pane contains choices and buttons
        self.toolBar = toolBar(self)
        logging.info("Component class 'mapDataClass' instantiated.")
        # Central pane info box
        self.infoBox = infoBox(self)
        logging.info("Component class 'mapDataClass' instantiated.")
        # Central pane contains the graph display
        self.mainView = mainView(self)
        logging.info("Component class 'mapDataClass' instantiated.")
        # Right pane contains contextual information pane
        self.contextView = contextView(self)
        logging.info("Component class 'mapDataClass' instantiated.")

        # Build cross-class references
        self.mapData.buildReferences()
        self.infoBox.buildReferences()
        self.toolBar.buildReferences()
        self.mainView.buildReferences()
        logging.info("Cross-class references built.")

        # Render the app
        logging.info("RWS Application Window will render. Default mode: edit.")
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
            format='[{asctime}.{msecs:0<3.0f}][{levelname:^8s}] Module \'{module}\': {message}',
            style='{',
            filemode='w',
            datefmt='%X')
        logging.info("Robot Warehousing Simulator program started.")
        logging.info(f"Logging started with level: {self.loglevelReference[self.loglevel]}")

    def simulationConfiguration(self):
        self.simulationConfigWindow = simulationConfigManager(self)
        logging.info("Configuration class 'simulationConfigManager' instantiated.")

    def launchSimulator(self):
        logging.debug("Simulation lanuch requested.")
        self.simulationConfigWindow.grab_release()
        self.simulationProcess = simulationProcess(self)
        self.simulationWindow = simulationWindow(self)

app = App()