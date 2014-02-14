import sys
import Tkinter as Tk
from element import Element
from labelvalue import LabelValue

#stores and displays the state of each thread's cpu
class Cpu(Element):
    def __init__ (self, parent, thread, registers, reg_origins, instructions, nops, cycles):
        self.thread = thread
        self.parent = parent
        self.relief = Tk.GROOVE
        self.border = 3
        self.fade_duration = 10
        self.new_reg_color = .75

        self.registers = registers
        self.reg_num = len(registers[0])
        self.reg_origins = reg_origins
        self.instructions = instructions
        self.nops = nops
        self.cycles = cycles
        
        self.visible = True
        self.dependencies = [self.registers, self.reg_origins, self.instructions, 
                             self.nops, self.cycles]

        self.resolve_dependencies()
        self.initialize()

    def initialize(self):
        if self.visible:
            spacer = Tk.Frame(self.parent, height=20)
            spacer.pack()
            root = Tk.LabelFrame(self.parent, bd=self.border, relief=self.relief, pady=9, padx=3,
                              text='Thread ' + str(self.thread))
            root.pack(fill=Tk.BOTH, expand=False)

            self.label_values = []
            self.reg_vars = []
            self.reg_labels = []
            reg_frame = Tk.Frame(root, padx=3, pady=5)
            reg_frame.pack(fill=Tk.X, expand=True)
            for x in xrange(0, self.reg_num):
                label = LabelValue(reg_frame, self.registers, chr(ord('A') + x) + 'X:', index=x)
                self.reg_labels.append(label)
                self.label_values.append(label)


            var_frame = Tk.Frame(root, padx=3, pady=5)
            var_frame.pack(fill=Tk.X, expand=True)
            self.label_values.append(LabelValue(var_frame, self.instructions, 'Instruction:', 
                                               var_type=Tk.StringVar))
            self.label_values.append(LabelValue(var_frame, self.nops, 'NOPs:', var_type=Tk.StringVar))


    #update the display values of the supplied variables
    def update(self, step):
        if self.visible:
            for label_value in self.label_values:
                label_value.update(step)
            
            self.update_colors(step)
        
    #update register colors
    def update_colors(self, step):
        if self.visible:
            cycle = self.cycles[step]
            for origin, label in zip(self.reg_origins[step], self.reg_labels):
                age = cycle - origin
                if age > self.fade_duration:
                    age = self.fade_duration
                color = self.new_reg_color * (self.fade_duration - age) / self.fade_duration
                color *= 255
                color_string = hex(int(color))[2:]
                while len(color_string) < 2:
                    color_string = '0' + color_string
                color_string = '#00' + color_string[0:2] + '00'
                label.set_color(color_string)
