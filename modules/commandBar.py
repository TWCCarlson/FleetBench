import tkinter as tk
from tkinter import messagebox


class commandBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)
        # Establish structure
        self.parent = parent
        self.parent.config(menu=self)
        self.file = FileCommands(self)

class FileCommands(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent, tearoff=0)
        # Establish structure
        self.parent = parent
        self.refMainApp = parent.parent
        self.refMapData = parent.parent.mapData

        # Add menu functions
        # Pass the function as a callback instead of calling it
        self.add_command(label="New Session", command=self.newSession)
        self.add_command(label="Open Session", command=self.openSession)
        self.add_command(label="Save Session", command=self.saveSession)
        self.add_command(label="Quit Session", command=self.quitSession)

        # Render the menu
        self.parent.add_cascade(label="File", menu=self)

    def newSession(self):
        # Prompt save
        self.promptSave()
        # Create a new session
        self.promptLoadMap()
        print("New Session")

    def promptLoadMap(self):
        messageBox = tk.messagebox.askquestion(title = "New Session",
            message="Load a map? This will close the current session.")
        if messageBox=="yes":
            print("Load new map")
            self.refMapData.ingestMapFromJSON()

    def openSession(self):
        # Open a saved session
        self.promptSave()
        print("Open Session")

    def promptSave(self):
        # Create a message box asking to save the current session
        print("Save?")

    def saveSession(self):
        # Save a session
        print("Save Session")

    def quitSession(self):
        # Close the current session
        print("Quit Session")
