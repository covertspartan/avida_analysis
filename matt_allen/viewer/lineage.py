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
    def __init__(self, parent, app, settings, column_settings, data, max_fitness, callback, 
                 max_items=25, item_height=150, *args, **kwargs):
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
        self.item_height = item_height
        self.max_fitness = max_fitness
        self.callback = callback
        self.visible = True
        self.genotype_height = None
        self.select_start = None
        self.select_end = None
        self.dependencies = []
        self.resolve_dependencies()
        self.max_items = max_items
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
        
        self.lineage_frame = VerticalScrolledFrame(self, self.data, total_items=len(self.data), 
                                                   max_items=self.max_items, item_height=self.item_height)
        self.lineage_frame.pack(fill=Tk.BOTH, expand=True)
        self.lineage_frame.bind('<Button-1>', self._on_pressed)
        self.lineage_frame.bind('<B1-Motion>', self._on_drag)
        self.genotypes = []
        
        
        for i in range(min(len(self.data), self.max_items)):
            parent_data = {}
            if i > 0:
                parent_data = self.data[i-1]
            g = Genotype(self.lineage_frame.canvas, self.settings, self.column_settings,
                             self.data[i], parent_data, self.max_fitness,
                             selected_fitness=self.data[0]['fitness'], bd=2, index=i, height=self.item_height)
            g.id = self.lineage_frame.canvas.create_window(0, self.item_height * i, window=g, height=self.item_height,
                                        anchor=Tk.NW, tag='row')




            tkutils.bind_children(g, '<Button-1>', partial(self._on_pressed, index=i))
            tkutils.bind_children(g, '<Shift-Button-1>', partial(self._on_shift_pressed, index=i))
            tkutils.bind_children(g, '<B1-Motion>', partial(self._on_drag, index=i))
            self.lineage_frame.cache.append(g)
            self.genotypes.append(g)
        

        tkutils.bind_children(self.lineage_frame, '<Button-4>', self._on_mouse_wheel)
        tkutils.bind_children(self.lineage_frame, '<Button-5>', self._on_mouse_wheel)
        tkutils.bind_children(self.lineage_frame, '<MouseWheel>', self._on_mouse_wheel)

        self.on_column_changed()

    def _on_mouse_wheel(self, *args, **kwargs):
        self.lineage_frame._on_mouse_wheel(*args, **kwargs)
        self._update_selection()
        

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
        #for i, g in enumerate(self.genotypes):
         #   g.set_selection(start - self.min<= i <= end - self.min)
        for g in self.genotypes:
            g.set_selection(start <= g.index <= end)

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
        start = self.lineage_frame.cache_start
        offset = self.lineage_frame.cache_offset
        self.data[index]['task_list'] = tasks
        if index + 1 < len(self.data):
            self.data[index + 1]['parent_task_list'] = tasks

        if start <= index < start + self.max_items:
            self.genotypes[index - start + offset].update(index, self.data[index])
            if start <= index + 1 < start + self.max_items:
                self.genotypes[index + 1 - start + offset].update(index + 1, self.data[index + 1])
            self.genotypes[index - start + offset].update_tasks()

    def update_all(self):
        """
        Call L{Genotype.update} on every member of the list.
        """
        for g in self.genotypes:
            g.update(g.index, g.data)
            g.update_tasks()


