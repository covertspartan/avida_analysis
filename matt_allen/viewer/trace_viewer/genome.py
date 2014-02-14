from __future__ import division
import Tkinter as Tk
from element import Element

class Genome(Element):
    def __init__(self, parent, genome, ips, threads, num_threads):
        self.visible = True
        self.parent = parent
        self.genome = genome
        self.ips = ips
        self.threads = threads
        self.num_threads = num_threads

        self.max_jump_width = 5

        self.genome_list_height = 15
        self.genome_canvas_width = 300
        self.genome_list_offset = 30
        self.genome_jump_offset = 200
        self.genome_jump_width = 100
        self.pointer_coords = [(-2,-4), (-2, 4), (8, 0)]
        self.jumps = []
        self.jump_weights = []
        self.jump_stack = []
        self.current_ips = []
        self.start_ips = [0]
        self.ip_map = []
        self.ip_pointers = []
        self.current_step = 0

        self.colors = ('#0000ff', '#ff0000', '#00cc00', '#FFBF00', '#00FFFF', '#B404AE', '#FA5882', 
                       '#A9F5A9', '#610B0B', '#FFFF00', '#848484', '#0B0B61', '#F3E2A9', '#B40404', 
                       '#04B45F')

        self.dependencies = [self.genome, self.ips, self.threads]
        self.resolve_dependencies()
        self.initialize()

    def initialize(self):
        if self.visible:
            genome_frame = Tk.Frame(self.parent, padx=3, pady=3)
            self.parent.add(genome_frame)

            #thread checkboxes
            check_frame = Tk.Frame(genome_frame)
            check_frame.pack(fill=Tk.X, expand=False, side=Tk.TOP)
            self.check_vars = []
            for x in range(self.num_threads):
                if x % 4 == 0 and x > 0:
                    check_frame = Tk.Frame(genome_frame)
                    check_frame.pack(fill=Tk.X, expand=False, side=Tk.TOP)
                self.check_vars.append(Tk.BooleanVar())
                self.check_vars[-1].set(True)
                check = Tk.Checkbutton(check_frame, text='Thread ' + str(x), 
                                       variable=self.check_vars[-1],
                                       fg=self.get_thread_color(x))
                check.pack(side=Tk.LEFT)

            #genome canvas
            scroll = Tk.Scrollbar(genome_frame, orient=Tk.VERTICAL, 
                                  command=self.on_vsb)
            scroll.pack(side=Tk.RIGHT, fill=Tk.Y)

            self.genome_canvas = Tk.Canvas(genome_frame, bg='white', width=self.genome_canvas_width)
            self.genome_canvas.pack(fill=Tk.Y, expand=False, side=Tk.LEFT, anchor=Tk.N)
            self.genome_canvas.config(yscrollcommand=scroll.set)
            self.genome_canvas.bind('<Button-4>', 
                                   self.on_mouse_wheel)
            self.genome_canvas.bind('<Button-5>', 
                                   self.on_mouse_wheel)
            self.genome_canvas.bind('<MouseWheel>', 
                                   self.on_mouse_wheel)




            #populate genome list
            current = ''
            ip_index = -1
            draw_index = 0
            for gene_index, gene in enumerate(self.genome):
                if not gene.startswith('nop'):
                    if current != '':
                        self.genome_canvas.create_text((self.genome_list_offset, 
                                                       self.genome_list_height * draw_index), 
                                                      anchor=Tk.NW, text=current)
                        draw_index += 1
                    self.genome_canvas.create_text((self.genome_list_offset, 
                                                   self.genome_list_height * draw_index), 
                                                  anchor=Tk.NW, text=gene)
                    draw_index += 1
                    ip_index += 1
                    current = ''
                else:
                    if current == '':
                        ip_index += 1
                    current += gene[-1] + ' '

                self.ip_map.append(ip_index)

                if 'promoter' in gene:
                    if gene_index == 0:
                        self.start_ips = []
                    self.start_ips.append(gene_index + 1)

            self.genome_display_length = ip_index + 1
            self.genome_canvas_height = self.genome_list_height * self.genome_display_length
            self.genome_canvas.config(scrollregion=(0,0,self.genome_canvas_width, 
                                                   self.genome_canvas_height))

            for x in range(self.num_threads):
                #thread ip pointers
                color = self.colors[x % len(self.colors)]
                self.ip_pointers.append(self.genome_canvas.create_polygon(self.pointer_coords, 
                                                                        fill=color))
                self.jumps.append([])
                self.jump_weights.append([])
                self.current_ips.append(None)

            for _ in range(0, self.genome_display_length):
                for x in range(0, self.num_threads):
                    self.jumps[x].append([None for _ in range(0, self.genome_display_length)])
                    self.jump_weights[x].append([0 for _ in range(0, self.genome_display_length)])


    def update(self, step):
        if self.visible:
            self.draw_jumps(self.current_step, step)
            self.draw_pointers()
            self.current_step = step
            

    def draw_pointers(self):
        for thread in range(self.num_threads):
            ip = self.current_ips[thread]
            pointer = self.ip_pointers[thread]
            coords = self.pointer_coords
            if ip is None:
                ip = self.ip_map[self.start_ips[thread]]
            
            y = ip * self.genome_list_height + self.genome_list_height / 2
            new_coords = [(point[0], point[1] + y) for point in coords]
            coords_flat = [element for tuple in new_coords for element in tuple]
            self.genome_canvas.coords(pointer, *coords_flat)

    #update the jump display for the change in step
    def draw_jumps(self, current_step, target_step):
        #move through the delta in steps and update
        while target_step != current_step:
            #going forward
            if current_step < target_step:
                current_step += 1
                thread = self.threads[current_step]

                #set up start and end values for this jump
                start = self.current_ips[thread]   
                end = self.ips[current_step] + self.start_ips[thread]
                if end >= len(self.ip_map):
                    end = len(self.ip_map) - 1
                end = self.ip_map[end]
                
                self.current_ips[thread] = end
                
                #if there is no current ip, get the start from the start of the thread
                if start is None:
                    start = self.ip_map[self.start_ips[thread]]
                
                #only update if this thread is checked
                if self.check_vars[thread].get():
                    #ignore steps that do not move the ip
                    if start != end:
                        self.jump_forward(thread, start, end)
                    else:
                        #mark this step as inactive in the stack
                        thread = None
                else:
                    thread = None
                #push this jump onto the stack
                self.jump_stack.append((thread, start, end))

            #going backward
            else:
                current_step -= 1
                thread = self.threads[current_step]
                
                #only update if this thead is checked
                if self.check_vars[thread].get():
                    
                    if self.jump_stack:
                        #pop the last jump off the stack
                        thread, start, end = self.jump_stack.pop()
                        self.jump_backward(thread, start, end)


    def jump_forward(self, thread, start, end):
        #ensure start < end
        if start > end:
            start, end = end, start
                        
        #get the sprite for this jump, calculate the draw values
        jump = self.jumps[thread][start][end]
        self.jump_weights[thread][start][end] += 1
        weight = self.jump_weights[thread][start][end]                    
        top = start * self.genome_list_height + self.genome_list_height / 2
        bot = end * self.genome_list_height + self.genome_list_height / 2
        #print str(start) + ', ' + str(end)
                       
        if jump is not None:
            #if there is an arc, update it with the new width and line width
            width = 1
            if weight > self.genome_jump_width:
                width = float(weight - self.genome_jump_width)
                weight = self.genome_jump_width
                width /= 10
                width = min(width, self.max_jump_width)
                self.genome_canvas.itemconfig(jump, width=width)
                
            self.genome_canvas.coords(jump, (self.genome_jump_offset - weight, top, 
                                            self.genome_jump_offset + weight, bot))
        else:
            #if there is no existing arc, create one and save it for later
            color = self.get_thread_color(thread)

            jump = self.genome_canvas.create_arc((self.genome_jump_offset - 1, top, 
                                                 self.genome_jump_offset + 1, bot), 
                                                fill='',
                                                start=-90, extent=180, 
                                                outline=color,
                                                style=Tk.ARC)
            self.jumps[thread][start][end] = jump
            self.jump_weights[thread][start][end] = 1

    def jump_backward(self, thread, start, end):
        if thread is not None:
            #get the arc corresponding to this jump
            self.current_ips[thread] = start
            jump = self.jumps[thread][start][end]
            if jump is not None:
                weight = self.jump_weights[thread][start][end]
                if weight > 1:
                    #decrease the weight, updating the width and line width
                    weight -= 1
                    weight_total = weight
                    width = 1
                    if weight > self.genome_jump_width:
                        width = float(weight - self.genome_jump_width)
                        weight = self.genome_jump_width
                        width /= 10
                        width = min(width, self.max_jump_width)
                        self.genome_canvas.itemconfig(jump, width=width)
                    top = start * self.genome_list_height + self.genome_list_height / 2
                    bot = end * self.genome_list_height + self.genome_list_height / 2
                    self.genome_canvas.coords(jump, (self.genome_jump_offset - weight, 
                                                    top, 
                                                    self.genome_jump_offset + weight, 
                                                    bot))
                    self.jump_weights[thread][start][end] = weight_total
                else:
                    #if the weight would be 0, remove this jump
                    self.genome_canvas.delete(jump)
                    self.jumps[thread][start][end] = None

    #callback for dragging a scrollbar, update the element
    def on_vsb(self, *args):
        self.genome_canvas.yview(*args)

    #callback for scrolling on an element
    def on_mouse_wheel(self, event):
        delta = event.delta
        if(event.num == 4):
            delta = -1
        if(event.num == 5):
            delta = 1
        self.genome_canvas.yview('scroll', delta, 'units')
        return 'break'

    def get_thread_color(self, thread):
        return self.colors[thread % len(self.colors)]
