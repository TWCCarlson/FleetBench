import tkinter as tk

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

        # Add menu functions
        # Pass the function as a callback instead of calling it
        self.add_command(label="New Session", command=self.newSession)
        self.add_command(label="Open Session", command=self.openSession)
        self.add_command(label="Save Session", command=self.saveSession)
        self.add_command(label="Quit Session", command=self.quitSession)

        # Render the menu
        self.parent.add_cascade(label="File", menu=self)

    def newSession(self):
        # Create a new session
        print("New Session")

    def openSession(self):
        # Open a saved session
        print("Open Session")

    def saveSession(self):
        # Save a session
        print("Save Session")

    def quitSession(self):
        # Close the current session
        print("Quit Session")