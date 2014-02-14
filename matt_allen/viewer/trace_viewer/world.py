from __future__ import division
import Tkinter as Tk
import math
from element import Element
from resources import Resources

class World(Element):
    def __init__(self, parent, world_size, updates, avatars, directions, 
                 resource_names, resource_positions, resource_radius):
        self.visible = True
        self.parent = parent
        
        self.avatars = avatars
        self.directions = directions
        self.resource_names = resource_names
        self.resource_positions = resource_positions
        self.resource_radius = resource_radius
        self.updates = updates

        self.world_size = world_size
        self.world_draw_size = 350

        self.current_step = 0

        self.org_coords = [(-2,-4), (-2, 4), (8, 0)]
        self.org_rot = 0
        self.org_pos = (0,0)
        self.view_radius = 100.0
        self.view_coords = (-self.view_radius / self.world_size * self.world_draw_size,
                            -self.view_radius / self.world_size * self.world_draw_size, 
                            self.view_radius / self.world_size * self.world_draw_size, 
                            self.view_radius / self.world_size * self.world_draw_size)
        self.view_start_angle = -22.5
        self.view_angle = 45
        self.colors = ('#0000ff', '#ff0000', '#00cc00', '#FFBF00', '#00FFFF', '#B404AE', '#FA5882', 
                       '#A9F5A9', '#610B0B', '#FFFF00', '#848484', '#0B0B61', '#F3E2A9', '#B40404', 
                       '#04B45F')


        self.dependencies = [updates, avatars, directions]
        self.resolve_dependencies()
        self.initialize()

    def initialize(self):
        if self.visible:
            world_frame = Tk.Frame(self.parent, width=self.world_draw_size)
            self.world_canvas = Tk.Canvas(world_frame, width=self.world_draw_size, 
                                         height=self.world_draw_size,
                                         bg='white')
            self.world_canvas.bind('<Configure>', self.on_world_pane_resize)
            self.world_canvas.pack(fill=Tk.X, expand=False, anchor=Tk.N)

            #resource key
            self.resources = Resources(world_frame, self, self.updates, self.resource_names,
                                       self.resource_positions, self.resource_radius)


            self.parent.add(world_frame)
            self.parent.paneconfig(world_frame, width=self.world_draw_size, sticky=Tk.E+Tk.W+Tk.N+Tk.S, 
                                stretch='never')
            self.org_sprite = self.world_canvas.create_polygon(self.org_coords)
            self.view_sprite = self.world_canvas.create_arc(self.view_coords, 
                                                          start=self.view_start_angle, 
                                                          extent=self.view_angle)


    def update(self, step):
        if self.visible:
            self.current_step = step
            new_coords = self.org_pos
            new_rot = self.org_rot
            avatar = self.avatars[step]
            update = self.updates[step]
            new_coords = (float(avatar % self.world_size),
                         float(avatar / self.world_size))
            new_rot = self.directions[step]
            

            #update world and resources
            self.draw_org(new_coords, new_rot)
            self.resources.update(step)

    #redraw the organism and view sprites based on the supplied position and rotation
    def draw_org(self, new_pos, new_rot):
        new_pos_scaled = (new_pos[0]  / self.world_size * self.world_draw_size, 
                  new_pos[1]  / self.world_size * self.world_draw_size)
        old_pos_scaled = (self.org_pos[0]  / self.world_size * self.world_draw_size, 
                  self.org_pos[1]  / self.world_size * self.world_draw_size)
            
        if new_pos_scaled != old_pos_scaled or new_rot != self.org_rot:
            delta_rot = (new_rot / 8.0) * math.pi*2 - math.pi/2
            self.org_rot = new_rot
            rot_coords = rotate(self.org_coords, delta_rot)
            transf_coords = [(new_pos_scaled[0] + x, new_pos_scaled[1] + y)  for (x, y) in rot_coords]
            self.world_canvas.coords(self.org_sprite, 
                                    *[element for tuple in transf_coords for element in tuple])
            view_angle = 360 - int(new_rot / 8.0 * 360 - 90)
            self.world_canvas.itemconfig(self.view_sprite, start=self.view_start_angle + view_angle)
            self.world_canvas.move(self.view_sprite, new_pos_scaled[0]-old_pos_scaled[0], 
                                  new_pos_scaled[1]-old_pos_scaled[1])
            self.org_pos = new_pos


    #event callbacks

    #callback for resizing the world canvas pane
    def on_world_pane_resize(self, event):
        old_pos = (self.org_pos[0] / self.world_size * self.world_draw_size, 
                  self.org_pos[1] / self.world_size * self.world_draw_size)
        self.world_draw_size = self.world_canvas.winfo_width()
        self.world_canvas.config(width=self.world_draw_size, height=self.world_draw_size)
        new_pos = (self.org_pos[0] / self.world_size * self.world_draw_size, 
                  self.org_pos[1] / self.world_size * self.world_draw_size)
        self.world_canvas.move(self.org_sprite, new_pos[0] - old_pos[0], 
                              new_pos[1] - old_pos[1])

        view_size = self.view_radius / self.world_size * self.world_draw_size
        self.view_coords = (-view_size, -view_size, view_size, view_size)
        self.world_canvas.coords(self.view_sprite, *self.view_coords)
        self.world_canvas.move(self.view_sprite, *new_pos)
        self.resources.update(self.current_step)


    #returns the color for the UI element
    def get_color(self, c):
        return self.colors[c % len(self.colors)]


#returns the given coordinates rotated by the angle
def rotate(coords, angle):
    new_coords = []
    for (x,y) in coords:
        new_coords.append((int(x*math.cos(angle) - y*math.sin(angle)), 
                          int(y*math.cos(angle) + x*math.sin(angle))))
    return new_coords
