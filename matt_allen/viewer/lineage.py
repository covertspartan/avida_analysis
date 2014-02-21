import Tkinter as Tk
from trace_viewer.element import Element
from trace_viewer.labelvalue import LabelValue
from verticalscrolledframe import VerticalScrolledFrame
from functools import partial
from genotype import Genotype
from analyzethread import AnalyzeThread
import tkutils

class Lineage(Element):
    """
    The list view of all genomes in the lineage.
    """
    def __init__(self, parent, app, settings, column_settings, data, max_fitness, callback, max=250,
                 min=0, *args, **kwargs):
        """
        Create an instance of the lineage list.

        @param parent: the parent frame.
        @param app: the L{LineageViewer} that contains this display.
        @param settings: the settings dict from the app.
        @param column_settings: the column settings list from the app.
        @param data: a list of genome data dicts to display.
        @param max_fitness: the highest fitness in the list of genome.
        @param callback: a function to call when an item is clicked on.
        """
        Element.__init__(self, parent, data, *args, **kwargs)
        self.app = app
        self.settings = settings
        self.column_settings = column_settings
        self.max_fitness = max_fitness
        self.callback = callback
        self.visible = True
        self.genotype_height = None
        self.select_start = None
        self.select_end = None
        self.dependencies = []
        self.resolve_dependencies()
        self.min = 0
        self.max = max
        self.initialize()

    def initialize(self):
        """
        Set up the interface for the list.
        """
        label_frame = Tk.Frame(self)
        label_frame.pack(fill=Tk.X)

        self.labels = [] 
        for c, column in enumerate(self.column_settings):
            frame = Tk.Frame(label_frame, width=column['width'], height=20)
            frame.grid(row=0, column=c)
            frame.pack_propagate(False)
            label = Tk.Label(frame, text=column['label'])
            label.pack(fill=Tk.BOTH, expand=True)
            self.labels.append(frame)
        
        self.lineage_frame = VerticalScrolledFrame(self)
        self.lineage_frame.pack(fill=Tk.BOTH, expand=True)
        self.lineage_frame.bind('<Button-1>', self._on_pressed)
        self.lineage_frame.bind('<B1-Motion>', self._on_drag)
        self.genotypes = []
        parent_data = {}
        
        for index, entry in enumerate(self.data):
            if self.min <= index < self.max:
                g = Genotype(self.lineage_frame.interior, self.settings, self.column_settings,
                             entry, parent_data, self.max_fitness,
                             selected_fitness=self.data[0]['fitness'], bd=2)
                parent_data = entry
                #g.grid(row=index, sticky='EW')
                g.pack(fill=Tk.X, expand=True)



                tkutils.bind_children(g, '<Button-1>', partial(self._on_pressed, index=index))
                tkutils.bind_children(g, '<Shift-Button-1>', partial(self._on_shift_pressed, index=index))
                tkutils.bind_children(g, '<B1-Motion>', partial(self._on_drag, index=index))
                self.genotypes.append(g)

        tkutils.bind_children(self.parent, '<Button-4>', self.lineage_frame._on_mouse_wheel)
        tkutils.bind_children(self.parent, '<Button-5>', self.lineage_frame._on_mouse_wheel)
        tkutils.bind_children(self.parent, '<MouseWheel>', self.lineage_frame._on_mouse_wheel)

        self.on_column_changed()
        

    def _on_shift_pressed(self, event, index=None):
        if index is not None:
            self.select_end = index

        self._update_selection()
                              

    def _on_pressed(self, event, index=None):
        """
        Callback for mouse click events on items of the list.

        @param event: the Tk event.
        @param index: the index of the clicked item, set up during the list
                      initialization.
        """
        if index is None:
            index = self._get_mouseover(event)
        self.select_start = index
        self.select_end = index
        for gene in self.genotypes:
            gene.update_color(selected_fitness=self.data[index]['fitness'],
                              absolute=self.settings['abscolor'])

        """if self.data[index].get('tasklist') is None:
            self._run_task_thread(index, self.data[index])"""
        self._update_selection()
        self.callback(event, index)
        return 'break'

    def _on_drag(self, event, index=None):
        """
        Callback for mouse drag after clicking a list item.

        @param event: the Tk event.
        @param index: the index of the clicked item, set up during the list
                      initialization.
        """
        old = self.select_end
        mouseover = self._get_mouseover(event, index)
        self.select_end = mouseover
        if old != mouseover:
            self._update_selection()
        return 'break'
        
    def _update_selection(self):
        """
        Set the selected state of the L{Genotype} objects.
        """
        start = min(self.select_start, self.select_end)
        end = max(self.select_start, self.select_end)
        for i, g in enumerate(self.genotypes):
            g.set_selection(start <= i <= end)

    def on_column_changed(self, *args, **kwargs):
        """
        Callback to indicate that the column settings have changed.

        Calls L{Genotype.on_column_changed} for each element in the list.
        """
        for c, (label, settings) in enumerate(zip(self.labels, self.column_settings)):
            if settings['var'].get():
                label.grid(row=0, column=c)
            else:
                label.grid_forget()
        for g in self.genotypes:
            g.on_column_changed(*args, **kwargs)                           

    def _get_mouseover(self, event, index=None):
        """
        Find out which element the mouse is over.

        @param event: the Tk event for the drag or click.
        @param index: the index of the element where the event
                      started.
        """
        if self.genotype_height is None:
            self.genotype_height = self.genotypes[0].winfo_height()
        if index is not None:
            delta = event.y // self.genotype_height
            return delta + index
        else:
            #need to implement mouseover detection if we don't know the start point
            return 0
                    
    def update_colors(self):
        """
        Update the colors of the elements in the list.
        """
        for gene in self.genotypes:
            gene.update_color(absolute=self.settings['abscolor'])
            gene.update_color(gene.parent_fitness, absolute=self.settings['abscolor'], parent=True)

    def update_tasks(self, index, tasks):
        """
        Update the task information of an element.

        @param index: the index of the element to update.
        @param tasks: the updated task list.
        """
        if self.min <= index < self.max:
            self.data[index]['task_list'] = tasks
            self.genotypes[index].update(data=self.data[index])
            if index + 1 < len(self.genotypes):
                self.data[index + 1]['parent_task_list'] = tasks
                self.genotypes[index + 1].update(data=self.data[index + 1])
            self.genotypes[index].update_tasks()

    def update_all(self):
        """
        Call L{Genotype.update} on every member of the list.
        """
        for g in self.genotypes:
            g.update()
            g.update_tasks()

