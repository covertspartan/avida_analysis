from __future__ import division
import Tkinter as Tk
import sys
import getopt
import gzip
import re
import math
import parsers
from cpu import Cpu
from data import Data
from labelvalue import LabelValue
from genome import Genome
from world import World


class Viewer(Tk.Tk):
    def __init__(self, parent):
        Tk.Tk.__init__(self, parent)
        self.parent = parent
        self.playing = False
        self.play_tick = 100
        self.data = Data()

        self.step_var = Tk.IntVar()

        self.cpus = []
        self.current_step = 0

        self.relief=Tk.RAISED
        self.border=2

        #throw up a loading label while we read the files and set up the interface
        self.root = Tk.Frame(self)
        self.root.pack(fill=Tk.BOTH, expand=True, pady=0)

        self.loading = Tk.Label(self.root, text='Loading . . .')
        self.loading.pack(fill=Tk.BOTH, expand=True)
                
    def initialize(self):
        self.loading.pack_forget()
        root_frame = self.root
        self.world_size = self.settings['worldx']

        if not len(self.data.threads):
            self.data.threads = [0 for _ in range(self.data.total_steps)]

        step_frame = Tk.Frame(root_frame, bd=self.border, relief=self.relief, padx=3, pady=3)
        step_frame.pack(fill=Tk.X, expand=False, anchor=Tk.N)


        #step entry field
        step_label = Tk.Label(step_frame, text='Step:')
        step_label.pack(side=Tk.LEFT)
        self.step_entry = Tk.Entry(step_frame, textvariable=self.step_var)
        self.step_entry.pack(fill=Tk.X, expand=False, side=Tk.LEFT)
        self.step_entry.bind('<Return>', self.on_step_change)
        self.step_entry.bind('<KP_Enter>', self.on_step_change)
        #self.step_entry.bind('<FocusIn>', lambda x: self.step_entry.selection_range(0, END))

        self.step_var.set(0)

        #step scale
        self.step_scale = Tk.Scale(step_frame, command=self.on_step_change, 
                                  orient=Tk.HORIZONTAL,
                                  showvalue=0, variable=self.step_var, 
                                  to=len(self.data.cycles) - 1)
        self.step_scale.pack(fill=Tk.X, expand=True, side=Tk.LEFT)


        #playback controls
        speed_label = Tk.Label(step_frame, text='Speed:')
        speed_label.pack(side=Tk.LEFT)

        self.speed_var = Tk.IntVar()
        self.speed_entry = Tk.Entry(step_frame, textvariable=self.speed_var, width=5)
        self.speed_entry.pack(side=Tk.LEFT)
        self.speed_entry.bind('<Return>', self.on_play_pressed)
        self.speed_entry.bind('<KP_Enter>', self.on_play_pressed)
        self.bind('<space>', self.on_play_pressed)

        self.speed_var.set(1)

        self.beginning_button = Tk.Button(step_frame, text='<<', command=lambda: self.jump_to_step(0))
        self.beginning_button.pack(side=Tk.LEFT)

        self.slower_button = Tk.Button(step_frame, text='<', command=lambda: self.mult_speed(-10))
        self.slower_button.pack(side=Tk.LEFT)

        self.play_text_var = Tk.StringVar()
        self.play_text_var.set('Play')
        self.play_button = Tk.Button(step_frame, textvariable=self.play_text_var, 
                                 command=self.on_play_pressed, width=5)
        self.play_button.pack(side=Tk.LEFT)

        self.faster_button = Tk.Button(step_frame, text='>', command=lambda: self.mult_speed(10))
        self.faster_button.pack(side=Tk.LEFT)

        self.end_button = Tk.Button(step_frame, text='>>', 
                                command=lambda: self.jump_to_step(len(self.data.cycles) - 1))
        self.end_button.pack(side=Tk.LEFT)
        

        col_frame = Tk.PanedWindow(root_frame, sashrelief=Tk.RAISED, sashwidth=4)
        #col_frame = Tk.Frame(root_frame)
        col_frame.pack(fill=Tk.BOTH, expand=True, anchor=Tk.N, side=Tk.TOP)

        self.genome_view = Genome(col_frame, self.data.genome, self.data.ips,
                                 self.data.threads, self.data.num_threads)


        center_frame = Tk.Frame(col_frame, pady=6, padx=3)
        col_frame.add(center_frame)
        col_frame.paneconfig(center_frame, sticky=Tk.E+Tk.W+Tk.N+Tk.S, stretch='always')
        
        #cross thread values
        label_frame = Tk.Frame(center_frame, pady=5)
        label_frame.pack(fill=Tk.X, expand=False)
       
        self.label_values = []
        self.label_values.append(LabelValue(label_frame, self.data.last_outputs, 'Last Output: '))
        self.label_values.append(LabelValue(label_frame, self.data.merits, 'Merit: '))
        self.label_values.append(LabelValue(label_frame, self.data.bonuses, 'Bonues: '))
        self.label_values.append(LabelValue(label_frame, self.data.forage_types, 'Forage: '))
        self.label_values.append(LabelValue(label_frame, self.data.queued_eats, 'Queued Eat: '))
        self.label_values.append(LabelValue(label_frame, self.data.queued_moves, 'Queued Move: '))
        self.label_values.append(LabelValue(label_frame, self.data.queued_rots, 'Queued Rotate: '))
        self.label_values.append(LabelValue(label_frame, 
                                            self.data.queued_rot_amounts, 'Rotate Amount: '))

        #cpu monitors
        self.initialize_cpus(center_frame)

        #world display
        self.world = World(col_frame, self.world_size, self.data.updates, self.data.avatar_cells,
                           self.data.directions, self.data.resource_names,
                           self.data.resource_positions, self.data.resource_radius)


    def initialize_cpus(self, center_frame):
        cpu_frame = Tk.Frame(center_frame, pady=6)
        cpu_frame.pack(fill=Tk.BOTH, expand=True, side=Tk.TOP)
        
        for x in xrange(0, self.data.num_threads):
            self.cpus.append(Cpu(cpu_frame, x, self.data.registers, self.data.register_origins,
                                 self.data.instructions, self.data.nops, self.data.cycles))        


    #callback loop for the playback clock
    def update_clock(self):
        speed = 0
        try:
            speed = self.speed_var.get()
        except ValueError:
            speed = 0
        
        #change the step based on the current speed
        self.step_var.set(self.step_var.get() + speed)
        self.on_step_change(self.step_var.get())
        #stop when the step gets to the end or the beginning
        if self.step_var.get() >= len(self.data.cycles) - 2 or self.step_var.get() <= 0:
            self.playing = False
            self.play_text_var.set('Play')
        #callback loop
        if self.playing:
            self.after(self.play_tick, self.update_clock)

    #callback for play button, toggle play state
    def on_play_pressed(self, *args):
        
        self.playing = not self.playing
        if not self.playing:
            self.play_text_var.set('Play')
        else:
            self.play_text_var.set('Pause')
            #start clock callback loop
            self.update_clock()

    #increases or decreases the speed, 1 for increase, -1 for decrease
    def mult_speed(self, mult):
        speed = float(self.speed_var.get())
        if speed * mult > 0:
            speed *= abs(mult)
        else:
            speed /= abs(mult)
            if abs(speed) < 1:
                speed = mult / abs(mult)
        self.speed_var.set(int(speed))

    #jumps to the correct step
    def jump_to_step(self, step):
        if self.playing:
            self.on_play_pressed()
        self.step_var.set(step)
        self.on_step_change(step)

    #callback for the step variable changing, updates the values for this step
    def on_step_change(self, value):
        step = self.step_var.get()

        self.current_step = step

        self.update_label_values(step)
        self.update_cpus(step)
        self.genome_view.update(step)
        self.world.update(step)

    def update_label_values(self, step):
        for label_value in self.label_values:
            label_value.update(step)

    def update_cpus(self, step):
        thread = self.data.threads[step]
        for i, cpu in enumerate(self.cpus):
            cycle = self.data.cycles[step]
            if i == thread:
                cpu.update(step)
            else:
                cpu.update_colors(step)

#read the command line args, load the files, and start the GUI
def main(argv):
    settings = {'settingsfile': None, 'tracefile': None, 'genomefile': None, 'resourcefile': None,
    'environmentfile': None, 'numregs': 1, 'worldx': 1, 'worldy': 1}

    error = 'usage: viewer.py -s <settingsfile> -t <tracefile> -g <genomefile> -r <resourcefile> -e <environmenfile>'

    try:
        opts, args = getopt.getopt(argv, 'hs:t:g:r:e:', ['settings=', 'trace=', 'genome=', 
                                                         'resource=', 'environment='])
    except getopt.GetoptError:
        print error
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print error
            sys.exit()
        elif opt in ('-s', '--settings'):
            settings['settingsfile'] = arg
        elif opt in ('-t', '--trace'):
            settings['tracefile'] = arg
        elif opt in ('-g', '--genome'):
            settings['genomefile'] = arg
        elif opt in ('-r', '--resource'):
            settings['resourcefile'] = arg
        elif opt in ('-e', '--environment'):
            settings['environmentfile'] = arg
        
    if settings.get('settingsfile') is None:
        settings['settingsfile'] = 'settings.cfg'

    #parse the settings file to get other unspecified options
    parsers.parse_data(None, settings, settings['settingsfile'], parsers.parse_config_line)
        
    if settings['tracefile'] is None:
        print >> sys.stderr, 'A trace file must be specified in settings.cfg as TRACE_FILE, or with the -t option'
        return 1

    app = Viewer(None)
    app.settings = settings
    app.title('Trace Viewer '+ settings['tracefile'])
    app.after(25, lambda: parsers.parse_files(app.data, app.settings, app.initialize))
    app.mainloop()

if __name__ == '__main__':
    result = main(sys.argv[1:])
    sys.exit(result)
