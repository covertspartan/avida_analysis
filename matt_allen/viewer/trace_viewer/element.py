from __future__ import division
import Tkinter as Tk

class Element(Tk.Frame):
    """
    Base class for UI elements defined in this project.

    Inherits from Tk.Frame, so it is packed/grided the same way.
    """
    def __init__(self, parent, data, *args, **kwargs):
        Tk.Frame.__init__(self, parent, *args, **kwargs)
        self.data = data
        self.dependencies = []
        self.visible = True
        self.parent = parent

    def initialize(self, parent=None):
        if parent is not None:
            self.parent = parent
    
    def resolve_dependencies(self):
        for dep in self.dependencies:
            if dep is None or not dep:
                self.visible = False
