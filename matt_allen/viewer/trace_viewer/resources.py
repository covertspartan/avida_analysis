import Tkinter as Tk
from element import Element

class Resources(Element):
    def __init__(self, parent, world, updates, resource_names, resource_positions, resource_radius):
        self.parent = parent
        self.visible = True
        self.world = world
        self.updates = updates
        self.resource_names = resource_names
        self.resource_positions = resource_positions
        self.resource_radius = resource_radius

        self.resource_sprites = []

        self.dependencies = [updates, resource_names, resource_positions, resource_radius]
        self.resolve_dependencies()
        self.initialize()

    def initialize(self):
        if self.visible:
            resource_frame = Tk.Frame(self.parent)
            resource_frame.pack()
            label_frame = Tk.Frame(resource_frame)
            label_frame.pack(side=Tk.LEFT)
            color_frame = Tk.Frame(resource_frame)
            color_frame.pack(side=Tk.LEFT)
            for i, name in enumerate(self.resource_names):
                name_label = Tk.Label(label_frame, text=name, pady=3)
                name_label.pack()
                color_box = Tk.Label(color_frame, text=u'\u2588', width=1, height=1, 
                                    fg=self.world.get_color(i), pady=3)
                color_box.pack()
                self.resource_sprites.append(None)

    def update(self, step):
        if self.visible:
            self.draw_resources(self.updates[step])

    def draw_resources(self, update):
        for i, positions in enumerate(self.resource_positions):
            color = self.world.get_color(i)
            x_cell, y_cell = positions[update]
            x = x_cell / self.world.world_size * self.world.world_draw_size
            y = y_cell / self.world.world_size * self.world.world_draw_size
            radius_cell = self.resource_radius[i]
            radius = 0
            if radius_cell is not None:
                radius = float(radius_cell) / self.world.world_size * self.world.world_draw_size
            coords = (y - radius, x - radius, y + radius, x + radius)
            if self.resource_sprites[i] is None:
                self.resource_sprites[i] = self.world.world_canvas.create_oval(coords, fill=color, 
                                                                             outline='',
                                                                             tags="resource")
            else:
                self.world.world_canvas.coords(self.resource_sprites[i], coords)
        self.world.world_canvas.tag_lower("resource")
        
