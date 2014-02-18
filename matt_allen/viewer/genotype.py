from __future__ import division
import Tkinter as Tk
import os
from trace_viewer.element import Element
from trace_viewer.labelvalue import LabelValue
from verticalscrolledframe import VerticalScrolledFrame
from avida_support.evaluator import MutationEvaluator
from genomedisplay import GenomeDisplay

class Genotype(Tk.Frame):
    """
    An entry in the L{Lineage} view, displays information about a
    genome in columns.
    """
    
    def __init__(self, parent, settings, column_settings, data, parent_data, max_fitness,
                 selected_fitness=1,
                 *args, **kwargs):
        """
        Create a new instance of the genotype display.

        @param parent: parent frame
        @param settings: settings dictionary for the application.
        @param column_settings: list of column settings from the application.
        @param data: dict of genome data.
        @param parent_data: dict of genome data of the parent
                            genome.
        @param max_fitness: the highest fitness in the lineage,
                            used for color scaling.
        @param selected_fitness: the currently selected fitness to scale from.
        """
        Tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.settings = settings
        self.column_settings = column_settings
        self.selected_fitness = selected_fitness
        self.data = data
        self.parent_data = parent_data
        self.max_fitness = max_fitness
        self.rel_fitness = data['fitness'] / max_fitness
        self.icon_size = 25
        self.visible = True
        self.dependencies = []
        self.id_var = Tk.StringVar()
        self.fit_var = Tk.StringVar()
        self.task_var = Tk.StringVar()
        self.gestation_var = Tk.StringVar()
        self.depth_var = Tk.StringVar()
        self.initialize()

        
    def initialize(self):
        """
        Set up the interface for this widget.
        """
        self.icon_color = '#00ff00'



        self.rel_canvas = Tk.Canvas(self, width=self.icon_size, height=self.icon_size)
        self.rel_canvas.grid(row=0, column=0)
        self.rel_canvas.create_oval((1, 1, self.icon_size-1, self.icon_size-1), fill=self.icon_color,
                                    tag='icon')
        self.par_canvas = Tk.Canvas(self, width=self.icon_size, height=self.icon_size)
        self.par_canvas.grid(row=0, column=1)
        self.par_canvas.create_oval((1, 1, self.icon_size-1, self.icon_size-1),
                                     fill=self.icon_color, tag='icon')

        color = self.cget('bg')

        genome_frame = Tk.Frame(self, height=75, width=self.column_settings[2]['width'])
        genome_frame.grid(row=0, column=2)
        genome_frame.pack_propagate(False)
        self.genome_display = GenomeDisplay(genome_frame, self.data['genome'], bg=color,
                                            relief='flat')
        self.genome_display.pack(fill=Tk.BOTH, expand=True)

        self.id_var.set(self.data['id'])
        self.fit_var.set('%0.2f' % self.data['fitness'])
        self.task_var.set('...')
        self.gestation_var.set('%0.2f' % self.data['gest_time'])
        self.depth_var.set(str(self.data['depth'] + 1))

        task_frame = Tk.Frame(self, height=75, width=self.column_settings[3]['width'])
        task_frame.grid(row=0, column=3)
        task_frame.pack_propagate(False)
        task_label = Tk.Message(task_frame, textvariable=self.task_var, anchor='w', 
                                width=self.column_settings[3]['width'])
        task_label.pack(fill=Tk.BOTH, expand=True)

        id_frame = self._column_label(4, self.id_var, height=15)

        fit_frame = self._column_label(5, self.fit_var, height=15)
        
        gest_frame = self._column_label(6, self.gestation_var, height=15)

        depth_frame = self._column_label(7, self.depth_var, height=15)

        self.update_color(self.selected_fitness)
        parent_fitness = self.parent_data.get('fitness')
        self.update_color(parent_fitness, parent=True)
        self.update_tasks()
        self.genome_display._diff_text(self.data['genome'], self.parent_data.get('genome'))
        
        self.columns = [self.rel_canvas, self.par_canvas, genome_frame,  task_frame,
                        id_frame, fit_frame, gest_frame, depth_frame]
        self._retag(str(self.data['id']), *self.columns)

    def _column_label(self, col, var, **kwargs):
        frame = Tk.Frame(self, width=self.column_settings[col]['width'], **kwargs)
        frame.grid(row=0, column=col)
        frame.pack_propagate(False)
        label = Tk.Label(frame, textvariable=var,  anchor='e')
        label.pack(fill=Tk.BOTH, expand=True)
        return frame


    def _retag(self, tag, *args):
        """
        Add a tag to all supplied widgets.
        """
        for widget in args:
            widget.bindtags((tag,) + widget.bindtags())

    def on_column_changed(self, *args, **kwargs):
        """
        Callback to indicate that the column settings have changed.
        """
        for c, (column, settings) in enumerate(zip(self.columns, self.column_settings)):
            if settings['var'].get():
                column.grid(row=0, column=c)
            else:
                column.grid_forget()
        
    def update(self, **kwargs):
        """
        Update the data for this genome.

        @param kwargs: keyword arguments corresponding to the data dict.
        """
        for key, value in kwargs.iteritems():
            self.data[key] = value

        self.id_var.set(self.data['id'])
        self.fit_var.set('%0.2f' % self.data['fitness'])
        self.gestation_var.set('%0.2f' % self.data['gest_time'])
        self.depth_var.set(str(self.data['depth'] + 1))

        self.rel_fitness = 0
        if self.data['fitness'] > 0:
            self.rel_fitness = self.data['fitness'] / self.max_fitness
        self.genome_display.update(self.data['genome'], self.parent_data.get('genome'))
        self.update_color()
        self.update_color(parent=True)

    def update_tasks(self):
        """
        Callback to indicate that the task list has been updated.
        """
        tasks = self.data.get('task_list')
        parent_tasks = self.parent_data.get('task_list')
        if tasks is not None:
            if self.settings['deltatasks']:
                delta = ''
                if parent_tasks is not None:

                    if tasks != parent_tasks:
                        for t, p, task in zip(tasks, parent_tasks, self.settings['tasks']):
                            if t != p:
                                sign = '+' if t == '1' else '-'
                                delta += ' ' + sign + task

                self.task_var.set(delta)
            else:
                labels = [task for t, task in zip(tasks, self.settings['tasks']) if t == '1']
                self.task_var.set(' '.join(labels))

    def update_color(self, selected_fitness=None, absolute=False, parent=False):
        """
        Update the color of one of the fitness icons.

        @param selected_fitness: the fitness to compare to.
        @param absolute: use absolute colors or gradient.
        @param parent: update the parent or relative icon.
        """
        canvas = self.par_canvas if parent else self.rel_canvas

        if parent:
            selected_fitness = 0
            parent = self.parent_data.get('fitness')
            if parent is not None:
                selected_fitness = parent / self.max_fitness
        else:
            if selected_fitness is not None:
                selected_fitness /= self.max_fitness
                self.selected_fitness = selected_fitness
            else:
                selected_fitness = self.selected_fitness
            
        color = (0,0,0)
        if selected_fitness == 0:
            fit = self.rel_fitness
        else:
            fit = (self.rel_fitness - selected_fitness)
        if absolute:
            if fit == 0:
                color = (0, 255, 0)
            elif fit < 0:
                color = (255, 0, 0)
            else:
                color = (0, 0, 255)
        else:
            if fit <= 0:
                color = (255 * (-fit)**.25, (1-abs(fit))**4 * 255, 0)
            elif fit > 0:
                color = (0, (1-abs(fit))**4 * 255, 255 * fit**.25)
                
        self.icon_color = '#%02x%02x%02x' % color
        canvas.itemconfig('icon', fill=self.icon_color)

    def bind(self, *args, **kwargs):
        """
        Binds an event to all widgets in this container.
        """
        Tk.Frame.bind(self, *args, **kwargs)
        self.bind_class(str(self.data['id']), *args, **kwargs)
        
    def set_selection(self, selection):
        """
        Set the state of the widget to selected or not, for
        graphical purposes mainly.
        """
        if selection:
            self.config(relief=Tk.RAISED)
        else:
            self.config(relief=Tk.FLAT)
