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
from simmodules.simulationConfigManager import simulationConfigManager
from simmodules.simulationWindow import simulationWindow
from simmodules.simulationProcess import simulationProcess
from config.appearanceValues import appearanceValues
import logging
import pprint
pp = pprint.PrettyPrinter(indent=4)
import inspect
import traceback
import functools

def log(func):
    # logging decorator
    @functools.wraps(func)
    def wrapper_log(*args, **kwargs):
        msg = ' '.join(map(str, args))
        # print("==========")
        # pp.pprint(msg)
        # print("==========")
        level = kwargs.get('level', logging.ERROR)
        if level == logging.INFO:
            logging.info(msg)
        elif level == logging.ERROR:
            logging.error(msg)
            traceback.print_exc()

    return wrapper_log

# Code stolen from: https://stackoverflow.com/questions/38464351/saving-exceptions-in-tkinter-using-python
@log
def print_to_log(s):
    pass

def handle_exception(exc_type, exc_value, exc_traceback):
    # pp.pprint(traceback.print_exc())
    # pp.pprint(inspect.getmembers(traceback.tb_frame))
    # prints traceback in the log
    message = ''.join(traceback.format_exception(exc_type,
                                                 exc_value,
                                                 exc_traceback))
    print_to_log(message)

class App(tk.Tk):
    def __init__(self):
        logging.info("Robot Warehousing Simulator program started.")
        # Main window config
        logging.debug("Attempting to create RWS Main Window . . .")
        tk.Tk.__init__(self)
        # Setup custom exception handling
        self.report_callback_exception=handle_exception
        logging.info("RWS Main Window Established.")
        self.title("Warehousing Simulator")

        # RNG Seeding class
        logging.debug("Attempting to create 'randomGenerator' class . . .")
        self.randomGenerator = randomGenerator(self)
        logging.info("Class 'randomGenerator' instantiated successfully.")
        # Map information class
        logging.debug("Attempting to create 'mapData' class . . .")
        self.mapData = mapDataClass(self)
        logging.info("Information class 'mapDataClass' instantiated successfully.")
        # Agent information manager class
        logging.debug("Attempting to create 'agentManager' class . . .")
        self.agentManager = agentManager(self)
        logging.info("Information class 'agentManager' instantiated successfully.")
        # Task information manager class
        logging.debug("Attempting to create 'taskManager' class . . .")
        self.taskManager = taskManager(self)
        logging.info("Information class 'taskManager' instantiated successfully.")

        # Window components
        # Appearance
        logging.debug("Attempting to create 'appearanceValues' class . . .")
        self.appearance = appearanceValues(self)
        logging.info("Component class 'appearanceValues' instantiated successfully.")
        # Command bar: load, save, options
        logging.debug("Attempting to create 'commandBar' class . . .")
        self.commandBar = commandBar(self)
        logging.info("Component class 'commandBar' instantiated successfully.")
        # Left pane contains choices and buttons
        self.toolBar = toolBar(self)
        logging.info("Component class 'toolBar' instantiated successfully.")
        # Central pane contains the graph display
        self.mainView = mainView(self)
        logging.info("Component class 'mainView' instantiated successfully.")
        # Central pane info box
        self.infoBox = infoBox(self)
        logging.info("Component class 'infoBox' instantiated successfully.")
        # Right pane contains contextual information pane
        self.contextView = contextView(self)
        logging.info("Component class 'contextView' instantiated successfully.")

        # Build cross-class references
        self.mapData.buildReferences()
        # self.infoBox.buildReferences()
        self.toolBar.buildReferences()
        self.mainView.buildReferences()
        logging.info("Cross-class references built successfully.")

        # Render the app
        logging.info("RWS Application Window will render. Default mode: edit.")
        self.mainView.mainCanvas.initialRender()

        # Debug session load
        # self.commandBar.fileCommand.openSession(fid="X:/GitHub/RoboWarehousingSim/save_files/random_test")
        # self.commandBar.fileCommand.openSession(fid="X:/GitHub/RoboWarehousingSim/save_files/random_test_manytask")
        # self.commandBar.fileCommand.openSession(fid="X:/GitHub/RoboWarehousingSim/save_files/oneagent_onetask_assigned")
        self.commandBar.fileCommand.openSession(fid="X:/GitHub/RoboWarehousingSim/save_files/sapf_with_blockers")

        # self.after()

        self.mainloop()

    def simulationConfiguration(self):
        self.simulationConfigWindow = simulationConfigManager(self)
        logging.info("Configuration class 'simulationConfigManager' instantiated.")

    def launchSimulator(self, simulationSettings):
        logging.debug("Simulation lanuch requested.")
        self.simulationConfigWindow.grab_release()
        self.simulationConfigWindow.withdraw()
        # self.simulationConfigWindow.deiconify()
        self.simulationManager = simulationManager(self, simulationSettings)
        # self.simulationWindow = simulationWindow(self)
        # self.simulationProcess = simulationProcess(self)

class simulationManager:
    """
        Containing class to group referencing in the simulation classes
    """
    def __init__(self, parent, simulationSettings):
        self.parent = parent

        # Display classes
        self.simulationWindow = simulationWindow(self)
        
        # Information classes
        self.simulationProcess = simulationProcess(self, simulationSettings)

        self.buildReferences()

        self.simulationProcess.simGraphData.pushDataToCanvas()
        self.simulationProcess.simAgentManager.pushDataToCanvas()
        self.simulationWindow.simMainView.simCanvas.renderGraphState()
        self.simulationWindow.simInfoBox.simInfoBoxFrame.buildInfoBox()

    def buildReferences(self):
        # Build necessary references for inner classes
        self.simulationWindow.simControlPanel.buildReferences()
        self.simulationWindow.simDataView.buildReferences()
        self.simulationWindow.simInfoBox.simInfoBoxFrame.buildReferences()
        self.simulationProcess.buildReferences()

def initLogging():
    loglevelReference = {
        0 :"NOTSET",
        10:"DEBUG",
        20:"INFO",
        30:"WARNING",
        40:"ERROR",
        50:"CRITICAL"
    }
    logLevel = logging.DEBUG
    # logLevel = logging.INFO
    # logLevel = logging.WARNING
    # logLevel = logging.ERROR
    # logLevel = logging.CRITICAL

    logging.basicConfig(filename='example.log', 
        encoding='utf-8', 
        level=logLevel, 
        format='[{asctime}.{msecs:0<3.0f}][{levelname:^8s}][\'{module}\'][{lineno:>4n}:{funcName}] {message}',
        style='{',
        filemode='w',
        datefmt='%X')
    logging.info(f"Logging started with level: {loglevelReference[logLevel]}")
    
# def addLoggingLevel(levelName, levelNum, methodName=None):
#     """
#     https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility/35804945#35804945
#     Comprehensively adds a new logging level to the `logging` module and the
#     currently configured logging class.

#     `levelName` becomes an attribute of the `logging` module with the value
#     `levelNum`. `methodName` becomes a convenience method for both `logging`
#     itself and the class returned by `logging.getLoggerClass()` (usually just
#     `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
#     used.

#     To avoid accidental clobberings of existing attributes, this method will
#     raise an `AttributeError` if the level name is already an attribute of the
#     `logging` module or if the method name is already present 

#     Example
#     -------
#     >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
#     >>> logging.getLogger(__name__).setLevel("TRACE")
#     >>> logging.getLogger(__name__).trace('that worked')
#     >>> logging.trace('so did this')
#     >>> logging.TRACE
#     5

#     """
#     if not methodName:
#         methodName = levelName.lower()

#     if hasattr(logging, levelName):
#         raise AttributeError('{} already defined in logging module'.format(levelName))
#     if hasattr(logging, methodName):
#         raise AttributeError('{} already defined in logging module'.format(methodName))
#     if hasattr(logging.getLoggerClass(), methodName):
#         raise AttributeError('{} already defined in logger class'.format(methodName))

#     # This method was inspired by the answers to Stack Overflow post
#     # http://stackoverflow.com/q/2183233/2988730, especially
#     # http://stackoverflow.com/a/13638084/2988730
#     def logForLevel(self, message, *args, **kwargs):
#         if self.isEnabledFor(levelNum):
#             self._log(levelNum, message, args, **kwargs)
#     def logToRoot(message, *args, **kwargs):
#         logging.log(levelNum, message, *args, **kwargs)

#     logging.addLevelName(levelNum, levelName)
#     setattr(logging, levelName, levelNum)
#     setattr(logging.getLoggerClass(), methodName, logForLevel)
#     setattr(logging, methodName, logToRoot)

# Begin process logging
initLogging()
# Launch the application
app = App()