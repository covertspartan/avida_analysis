from __future__ import division
import Tkinter as Tk
import tkFileDialog
import sys
import os
import getopt
import gzip
import re
import math
import random
import Queue
import threading
import json
import functools
import copy
from trace_viewer.labelvalue import LabelValue
from lineage import Lineage
from avida_support.asexual_population import cASexualPopulation
from genomedisplay import GenomeDisplay
from analyzeallthread import AnalyzeAllThread
from analyzeupdatethread import AnalyzeUpdateThread
from editdialog import EditDialog
import trace_viewer.parsers as parsers
import tkutils

class LineageViewer(Tk.Frame):
    """
    Main class for the lineage viewer GUI application.

    This is a subclass of Tk.Frame, it should be added to either
    main Tk.Tk instance of the program or a Tk.Toplevel window.
    """
    
    def __init__(self, parent, settings, analyze_lock=threading.Lock(), *args, **kwargs):
        """
        Initialize an instance of the lineage viewer, does not set up the GUI.

        @param parent: Container to add this viewer to.
        @param settings: A dict of application settings.
        @param analyze_lock: The lock on Avida analyze mode. Created
                               if not supplied.
        """
        Tk.Frame.__init__(self, parent, *args, **kwargs)
        self.settings = settings
        self.parent = parent
        if self.settings.get('abscolor') is None:
            self.settings['abscolor'] = False

        if self.settings.get('deltatasks') is None:
            self.settings['deltatasks'] = False
        

        self.queue = Queue.Queue()
        self.analyze_lock = analyze_lock
        self.selected = 0

        columns = [('RF', 30, False),
                   ('PF', 30, True),
                   ('Genome', 400, True),
                   ('Tasks', 175, True),
                   ('Organism ID', 100, False),
                   ('Fitness', 100, True)]
        self.column_settings = [{'label':label, 'width':width, 'var':Tk.BooleanVar()}
                                for label, width, show in columns]
        for settings, (l, w, show) in zip(self.column_settings, columns):
            settings['var'].set(show)


    def initialize(self):
        """
        Initializes the GUI of the lineage viewer.

        Handles the creation of all GUI elements in the viewer.
        Should be called after data has been loaded.
        """
        self.menubar = Tk.Menu(self)
        self.parent.config(menu=self.menubar)
        file_menu = Tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='File', menu=file_menu)
        options_menu = Tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Options', menu=options_menu)
        column_menu = Tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Columns', menu=column_menu)
        
        file_menu.add_command(label='Save', command=self.save_json_selected,
                              accelerator='Ctrl+S')
        tkutils.bind_children(self.parent, '<Control-s>', lambda e: self.save_json_selected())
        file_menu.add_command(label='Save Selected', command=self.save_json_selected,
                              accelerator='Ctrl+S')
        tkutils.bind_children(self.parent, '<Control-s>', lambda e: self.save_json_selected())
        file_menu.add_command(label='Load', command=self.load_json_window, accelerator='Ctrl+F')
        tkutils.bind_children(self.parent, '<Control-f>', lambda e: self.load_json_window())
        window_callback = lambda:self.create_lineage_window(self.get_selected())
        file_menu.add_command(label='New window from selection', command=window_callback)
        file_menu.add_command(label='Close', command=self.parent.destroy, accelerator='Ctrl+Q')
        tkutils.bind_children(self.parent, '<Control-q>', lambda e: self.parent.destroy())
        
        options_menu.add_checkbutton(label='Absolute Colors', command=self._on_absolute_changed)

        options_menu.add_checkbutton(label='Task Deltas', command=self._on_task_delta_changed)

        for column in self.column_settings:
            column_menu.add_checkbutton(label=column['label'], variable=column['var'],
                                        command=self._on_column_changed)
        
        col_frame = Tk.PanedWindow(self, sashrelief=Tk.RAISED, sashwidth=4)
        col_frame.pack(expand=True, fill=Tk.BOTH)

        lineage_frame = Tk.LabelFrame(col_frame, text='Lineage')
        col_frame.add(lineage_frame, padx=5, pady=5)
        col_frame.paneconfig(lineage_frame, sticky=Tk.E+Tk.W+Tk.N+Tk.S, stretch='always')
        
        self.lineage = Lineage(lineage_frame, self, self.settings, self.column_settings,
                               self.lineage_data,
                               self.max_fitness,
                               self._on_lineage_click)
        self.lineage.pack(fill=Tk.BOTH, expand=True)

        right_frame = Tk.Frame(col_frame)
        col_frame.add(right_frame, padx=5, pady=5)

        info_frame = Tk.LabelFrame(right_frame, text='Genome Info')
        info_frame.pack(fill=Tk.BOTH)
        genome_label = Tk.Label(info_frame, text=('Genome (Green = insertion, Blue = mutation, '
                                                  'Red = deletion'))
        genome_label.pack()
        self.genome_display = GenomeDisplay(info_frame, '', height=3)
        self.genome_display.pack(fill=Tk.X)

        data_frame = Tk.Frame(info_frame)
        data_frame.pack(fill=Tk.X)
        label_frame = Tk.Frame(data_frame)
        label_frame.pack(side=Tk.LEFT)
        value_frame = Tk.Frame(data_frame)
        value_frame.pack(side=Tk.LEFT)
        
        self.living_var = Tk.IntVar()
        self.total_var = Tk.IntVar()
        self.merit_var = Tk.IntVar()
        self.gestation_var = Tk.IntVar()
        self.depth_var = Tk.IntVar()
        self.fitness_var = Tk.IntVar()
        self.id_var = Tk.IntVar()
        self.task_var = Tk.StringVar()

        self._label(label_frame, value_frame, self.id_var, 'ID: ')
        self._label(label_frame, value_frame, self.living_var, 'Living Now: ')
        self._label(label_frame, value_frame, self.total_var, 'Total Living: ')
        self._label(label_frame, value_frame, self.merit_var, 'Merit: ')
        self._label(label_frame, value_frame, self.gestation_var, 'Gestation: ')
        self._label(label_frame, value_frame, self.fitness_var, 'Fitness: ')
        self._label(label_frame, value_frame, self.depth_var, 'Phylogenic Depth: ')
        self._label(label_frame, value_frame, self.task_var, 'Tasks: ')

        edit_frame = Tk.LabelFrame(right_frame, text='Edit Genome')
        edit_frame.pack(fill=Tk.X)

        edit_callback = lambda: self.edit_genome_dialog([self.get_selected()[0]])
        edit_button = Tk.Button(edit_frame, text='Edit', command=edit_callback)
        #edit_button.pack(side=Tk.LEFT)
        edit_all_callback = lambda: self.edit_genome_dialog(self.lineage_data)
        edit_all_button = Tk.Button(edit_frame, text='Edit All', command=edit_all_callback)
        edit_all_button.pack(side=Tk.LEFT)
        edit_selected_callback = lambda: self.edit_genome_dialog(self.get_selected())
        edit_selected_button = Tk.Button(edit_frame, text='Edit Selected',
                                         command=edit_selected_callback)
        edit_selected_button.pack(side=Tk.LEFT)


    def edit_genome_dialog(self, data):
        """
        Spawn a dialog to edit a genome and update the
        selection to reflect the changes made.

        @param data: The selection of genomes that the edit applies to.
                     The first element will be used as the starting point
                     for the changes.
        """
        start_genome = data[0]['genome']
        dialog = EditDialog(self, start_genome)
        end_genome = dialog.result
        if end_genome is not None:
            changes = tkutils.diff_genomes(start_genome, end_genome)
            
            if changes:
                for d in data:
                    new_genome = d['genome']
                    for type, start, size, new_text in changes:
                        new_genome = new_genome[0:start] + new_text + new_genome[start+size:-1]
                    d['genome'] = new_genome
                thread = AnalyzeUpdateThread(lock=self.analyze_lock,
                                             path=self.settings['pathtoavida'], app=self,
                                             data=self.lineage_data, daemon=True)
                thread.start()

            self.lineage.update_all()
                    
        
    def load_data(self, data=None):
        """
        Load the data needed to populate the viewer.

        Chooses the correct input form using the settings dict.
        Calls the appropriate JSON, detail dump, or data loading methods.

        @param data: A list of genome data already loaded by another
                     lineage viewer instance. Used if this lineage viewer
                     is being spawned by an existing application.
        """
        self.max_fitness = 0
        
        if data is not None:
            self.lineage_data = data
            
        elif self.settings['jsonfile'] is not None:
            self.lineage_data = self._load_json(self.settings['jsonfile'])
            
        elif self.settings['detaildump'] is not None:
            self.lineage_data = self._load_detail(self.settings['detaildump'])

        else:
            raise InputException('No input supplied for lineageviewer')

        for org in self.lineage_data:
            if org['fitness'] > self.max_fitness:
                self.max_fitness = org['fitness']

    def _load_detail(self, filename):
        """
        Load the detail dump from the supplied file, using L{cASexualPopulation}
        to walk the line of descent.

        @param filename: The relative file path of the detail dump.
        @return: the list of genome data.
        """
        self.population_data = cASexualPopulation(filename,
                                                  {'Sparent':3,'Iliving':4, 
                                                   'Ffitness':9, 'Sgenome':16,
                                                   'Itotal':5, 'Fmerit':7,
                                                   'Fgest_time':8, 'Idepth':13})
        self.population_data.trace_line_of_descent()

        lineage_data = []
        for id, org in self.population_data.walk_line_of_descent():
            del org['raw']
            org['id'] = id
            lineage_data.insert(0, org)

        return lineage_data

    def _save_json(self, filename, data):
        """
        Save the supplied data to a JSON file.

        @param filename: The relative file path of the JSON file.
        @param data: The list of genomes to save.
        """
        with open(filename, 'w') as file:
            for d in data:
                del d['data']
                file.write(json.dumps(d))
                file.write('\n')

    def get_selected(self):
        """
        Get the list of genomes selected in the lineage list view.

        @return: the list of selected lineages.
        """
        start, end = 0, len(self.lineage_data)
        if self.lineage.select_start is not None and self.lineage.select_end is not None:
            start = min(self.lineage.select_start, self.lineage.select_end)
            end = max(self.lineage.select_start, self.lineage.select_end) + 1
        return self.lineage_data[start:end]
                
    def save_json_selected(self):
        """
        Save the genomes selected in the lineage view to a JSON file.

        Spawns a file save dialog to get the destination file path.
        """
        file_name = tkFileDialog.asksaveasfilename(parent=self,filetypes=[('JSON', '*.json')],
                                                   title="Save the selection as...")
        if len(file_name ) > 0:
            self._save_json(file_name, self.get_selected())

    def _load_json(self, filename):
        """
        Load the data from a JSON file, expects the file to contain JSON objects
        serialized from the genome dicts.

        @param filename: the relative file path of the JSON file.
        @returns: the list of genomes contained in the file.
        """
        with open(filename) as file:
            lineage_data = [json.loads(line) for line in file]
            return lineage_data

    def load_json_window(self):
        """
        Load the JSON data from a user supplied file.

        Spawns a file open dialog to select the source file path. Creates
        a new lineage viewer window to display the contents of the file.
        """
        file_name = tkFileDialog.askopenfilename(parent=self, title='Choose a file',
                                             filetypes=[('JSON', '*.json')])
        print file_name
        if file_name != None:
            new_data = self._load_json(file_name)
            self.create_lineage_window(new_data)
        
    def update_analyze(self):
        """
        A recurring event that checks for finished analyze mode jobs.

        Checks a L{Queue} to recieve messages from multiple worker threads.
        The messages take the form of tuples, where the first item is a string
        detailing the type of message and the remaining items are the contents of
        the message. Registers itself as an event after executing.
        """
        try:
            while True:
                message = self.queue.get_nowait()
                if message[0] == 'task_list':
                    type, index, tasks = message
                    self._update_tasks(index, tasks)
                elif message[0] == 'update':
                    type, index, data = message
                    for key, value in data.iteritems():
                        if key != 'task_list':
                            self.lineage_data[index][key] = parsers.convert(value)
                            self.lineage.genotypes[index].update()
                        else:
                            self._update_tasks(index, value)
                elif message[0] == 'update_all':
                    self.lineage.update_all()

        except Queue.Empty:
            pass
        self.after(100, self.update_analyze)

    def _update_tasks(self, index, tasks):
        """
        Update the task data of a genome.

        @param index: the index of the genome to update.
        @param tasks: the task list string of the genome.
        """
        self.lineage_data[index]['task_list'] = tasks
        if index == self.selected:
            self._on_lineage_click(None, index)
        self.lineage.update_tasks(index, tasks)


            
    def _label(self, label_frame, value_frame, var, text):
        """
        Create a pair of labels to display data.

        @param label_frame: the parent frame of the labels.
        @param value_frame: the parent frame of the values.
        @param var: the Tk variable storing the value.
        @param text: the text of the label.
        """
        label = Tk.Label(label_frame, text=text, anchor=Tk.E)
        label.pack(padx=(0,15), fill=Tk.X)
        value = Tk.Label(value_frame, textvariable=var, anchor=Tk.W)
        value.pack(fill=Tk.X)

    def _on_lineage_click(self, event, index=None):
        """
        Callback to update the detail display when a new genome is selected
        in the lineage list view.

        @param event: the event object for the mouse click.
        @param index: the index of the selected item, this is set up when
                      the L{Genotype}s are created.
        """
        if index is not None:
            self.selected = index
            data = self.lineage_data[index]
            genome = data['genome']
            last_genome = ''
            if index > 0:
                last_genome = self.lineage_data[index - 1]['genome']
            self.genome_display.update(genome, last_genome)
            self.id_var.set(data['id'])
            self.living_var.set(data['living'])
            self.total_var.set(data['total'])
            self.merit_var.set(data['merit'])
            self.gestation_var.set(data['gest_time'])
            self.fitness_var.set(data['fitness'])
            self.depth_var.set(data['depth'])
            tasks = data.get('task_list')
            if tasks is not None:
                result = ''
                for t, name in zip(tasks, self.settings['tasks']):
                    if t == '1':
                        result += ' ' + name
                self.task_var.set(result)
            else:
                self.task_var.set('Loading')

    def _on_absolute_changed(self, *args, **kwargs):
        """
        Callback for toggling the absolute color mode.
        """
        self.settings['abscolor'] = not self.settings['abscolor']
        self.lineage.update_colors()

    def _on_task_delta_changed(self, *args, **kwargs):
        """
        Callback for toggling the task delta mode.
        """
        self.settings['deltatasks'] = not self.settings['deltatasks']
        self.lineage.update_all()

    def _on_column_changed(self, *args, **kwargs):
        """
        Callback for a change in column visibility selection.
        """
        self.lineage.on_column_changed(*args, **kwargs)
        
    def create_lineage_window(self, data):
        """
        Spawn a new lineage viewer window to display a sub-lineage.

        @param data: The list of genomes to display in the new window.
                     A deep copy is performed on the data so that changes 
                     in the new window do not propogate to the current window.
        """
        new_data = copy.deepcopy(data)

        window = Tk.Toplevel()
        app = LineageViewer(window, self.settings, analyze_lock=self.analyze_lock)
        app.pack(fill=Tk.BOTH, expand=True)
        app.load_data(data=new_data)
        app.initialize()
        app.after(100, app.update_analyze)

        
def main(argv):
    """
    Main method that launches the initial lineage viewer window.

    Loades settings file and handles command line args, then starts Tk.
    """
    error = 'usage: python lineageviewer.py'
    settings = {'settingsfile':'settings.cfg', 'detaildump':None, 'jsonfile':None}
    try:
        opts, args = getopt.getopt(argv, 'hd:j:', ['detail=', 'jsonfile='])
    except getopt.GetoptError:
        print error
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print error
            sys.exit()
        elif opt in ('-d', '--detail'):
            settings['detailfile'] = arg
        elif opt in ('-j', '--jsonfile'):
            settings['jsonfile'] = arg

    #parse the settings file to get other unspecified options
    parsers.parse_data(None, settings, settings['settingsfile'], parsers.parse_config_line)
        
    if settings['detaildump'] is None and settings['jsonfile'] is None:
        print >> sys.stderr, ('A detail dump must be specified in settings.cfg as DETAIL_DUMP, '
                              'or with the -d option')
        return 1

    #fix for the trailing slash bug, makes sure the path to avida registers as a directory
    if settings['pathtoavida']:
        settings['pathtoavida'] = os.path.join(settings['pathtoavida'], '')

    lock = threading.Lock()
    main = Tk.Tk()
    app = LineageViewer(main, settings, analyze_lock=lock)
    app.pack(fill=Tk.BOTH, expand=True)
    main.title('Lineage Viewer')
    app.load_data()
    app.initialize()
    analyze_thread = AnalyzeAllThread(lock=app.analyze_lock, path=settings['pathtoavida'], app=app,
                                      data=app.lineage_data, daemon=True)
    analyze_thread.start()
    app.after(100, app.update_analyze)

    app.mainloop()

if __name__ == '__main__':
    result = main(sys.argv[1:])
    sys.exit(result)


class InputException(Exception):
    """
    Execption type returned if L{LineageViewer.load_data} cannot find a valid data source.
    """
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
