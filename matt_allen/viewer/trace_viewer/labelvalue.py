from __future__ import division
import Tkinter as Tk
from element import Element

class LabelValue(Element):
    def __init__(self, parent, data, text, var_type=None, index=None):
        self.dependencies = [data]
        self.visible = True
        self.parent = parent
        if var_type is None:
            var_type = Tk.IntVar
        self.index = index
        self.var = var_type()
        self.data = data
        self.text = text

        self.resolve_dependencies()
        self.initialize()

    def initialize(self):
        if self.visible:
            label_frame = Tk.Frame(self.parent)
            label_frame.pack(fill=Tk.X, expand=True, side=Tk.LEFT)

            label = Tk.Label(label_frame, text=self.text, anchor=Tk.E)
            label.pack(fill=Tk.X, expand=True, side=Tk.LEFT)
            value_frame = Tk.Frame(label_frame)
            value_frame.pack(fill=Tk.BOTH, expand=True, side=Tk.LEFT)
            value_frame.pack_propagate(False)
            value = Tk.Label(value_frame, textvariable=self.var, anchor=Tk.W)
            value.pack(fill=Tk.X, expand=True, side=Tk.LEFT)
            self.value = value

    def update(self, step):
        if self.visible:
            if self.index is None:
                self.var.set(self.data[step])
            else:
                self.var.set(self.data[step][self.index])

    def set_color(self, color):
        if self.visible:
            self.value.config(fg=color)
    

