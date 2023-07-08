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
        self.loglevelReference = {
            0 :"NOTSET",
            5 :"TRACE",
            10:"DEBUG",
            20:"INFO",
            30:"WARNING",
            40:"ERROR",
            50:"CRITICAL"
        }
        self.addLoggingLevel('TRACE', logging.DEBUG - 5)
        self.logLevel = logging.TRACE
        # self.logLevel = logging.DEBUG
        # self.logLevel = logging.INFO
        # self.logLevel = logging.WARNING
        # self.logLevel = logging.ERROR
        # self.logLevel = logging.CRITICAL

        self.programLogger = logging.basicConfig(filename='example.log', 
            encoding='utf-8', 
            level=self.logLevel, 
            format='[{asctime}.{msecs:0<3.0f}][{levelname:^8s}] Module \'{module}\': {message}',
            style='{',
            filemode='w',
            datefmt='%X')
        logging.info("Robot Warehousing Simulator program started.")
        logging.info(f"Logging started with level: {self.loglevelReference[self.logLevel]}")

        # Quick and dirty workaround for correctly logging {module} as the invoking module
        # Before, when in logging_extensions.py, the module would be logging_extensions
    
    def addLoggingLevel(self, levelName, levelNum, methodName=None):
            """
            https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility/35804945#35804945
            Comprehensively adds a new logging level to the `logging` module and the
            currently configured logging class.

            `levelName` becomes an attribute of the `logging` module with the value
            `levelNum`. `methodName` becomes a convenience method for both `logging`
            itself and the class returned by `logging.getLoggerClass()` (usually just
            `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
            used.

            To avoid accidental clobberings of existing attributes, this method will
            raise an `AttributeError` if the level name is already an attribute of the
            `logging` module or if the method name is already present 

            Example
            -------
            >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
            >>> logging.getLogger(__name__).setLevel("TRACE")
            >>> logging.getLogger(__name__).trace('that worked')
            >>> logging.trace('so did this')
            >>> logging.TRACE
            5

            """
            if not methodName:
                methodName = levelName.lower()

            if hasattr(logging, levelName):
                raise AttributeError('{} already defined in logging module'.format(levelName))
            if hasattr(logging, methodName):
                raise AttributeError('{} already defined in logging module'.format(methodName))
            if hasattr(logging.getLoggerClass(), methodName):
                raise AttributeError('{} already defined in logger class'.format(methodName))

            # This method was inspired by the answers to Stack Overflow post
            # http://stackoverflow.com/q/2183233/2988730, especially
            # http://stackoverflow.com/a/13638084/2988730
            def logForLevel(self, message, *args, **kwargs):
                print("Log for level")
                if self.isEnabledFor(levelNum):
                    self._log(levelNum, message, args, **kwargs)
            def logToRoot(message, *args, **kwargs):
                print("Log to root")
                logging.log(levelNum, message, *args, **kwargs)

            logging.addLevelName(levelNum, levelName)
            setattr(logging, levelName, levelNum)
            setattr(logging.getLoggerClass(), methodName, logForLevel)
            setattr(logging, methodName, logToRoot)

    def simulationConfiguration(self):
        self.simulationConfigWindow = simulationConfigManager(self)
        logging.info("Configuration class 'simulationConfigManager' instantiated.")

    def launchSimulator(self):
        logging.debug("Simulation lanuch requested.")
        self.simulationConfigWindow.grab_release()
        self.simulationProcess = simulationProcess(self)
        self.simulationWindow = simulationWindow(self)

app = App()