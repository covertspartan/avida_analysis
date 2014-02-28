import Tkinter as Tk
import tkutils

class VerticalScrolledFrame(Tk.Frame):
    """A pure Tkinter scrollable frame that actually works!

    Use the 'interior' attribute to place widgets inside the scrollable frame
    Construct and pack/place/grid normally
    This frame only allows vertical scrolling
    """
    def __init__(self, parent, data, total_items, max_items=100, item_height=50, *args, **kw):
        Tk.Frame.__init__(self, parent, *args, **kw)            
        self.start = 0
        self.data = data
        self.total_items = total_items
        self.max_items = max_items
        self.item_height = item_height
        self.cache_start = 0
        self.cache_offset = 0

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Tk.Scrollbar(self, orient=Tk.VERTICAL)
        vscrollbar.pack(fill=Tk.Y, side=Tk.RIGHT, expand=False)
        canvas = Tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        self.canvas = canvas
        canvas.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)
        vscrollbar.config(command=self.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it

        self.cache = []
        
        self.canvas.config(scrollregion='0 0 %s %s' % (self.canvas.winfo_reqwidth(), self.item_height*self.total_items))
        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (self.cache[0].winfo_reqwidth(), self.item_height*self.total_items)
            canvas.config(scrollregion="0 0 %s %s" % size)
            if self.cache[0].winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=self.cache[0].winfo_reqwidth())

        #self.cache[0].bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if self.cache[0].winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure('row', width=canvas.winfo_width())
        #canvas.bind('<Configure>', _configure_canvas)



            
    def yview(self, *args, **kwargs):
        self.canvas.yview(*args, **kwargs)
        ypos = self.canvas.canvasy(0)
        self.start = int(ypos / self.item_height)
        self.update_items()

    def update_items(self):
        if self.start != self.cache_start:
            delta = abs(self.cache_start - self.start)
            for i in range(delta):
                ci = i
                index = i
                dy = 0
                if self.cache_start < self.start:
                    ci = i + self.cache_offset
                    index = self.start + self.max_items - delta + i
                    dy = self.item_height * len(self.cache)
                else:
                    ci = i + self.cache_offset + len(self.cache) - delta
                    index = i + self.start
                    dy = -self.item_height * len(self.cache)
                ci = ci % len(self.cache)
                if index < self.total_items:
                    self.cache[ci].update(index, self.data[index])
                self.canvas.move(self.cache[ci].id, 0, dy)

            if self.cache_start < self.start:
                self.cache_offset += delta
                self.cache_offset = self.cache_offset % len(self.cache)
            else:
                delta = delta % len(self.cache)
                self.cache_offset -= delta
                if self.cache_offset < 0:
                    self.cache_offset += len(self.cache)
                    

            self.cache_start = self.start


    #callback for scrolling on an element
    def _on_mouse_wheel(self, event):
        delta = event.delta
        if event.num == 4:
            delta = -1
        if event.num == 5:
            delta = 1
        self.yview('scroll', delta, 'units')


    def bind(self, *args, **kwargs):
        Tk.Frame.bind(self, *args, **kwargs)
        for v in self.cache:
            v.bind(*args, **kwargs)

    def winfo_children(self, *args, **kwargs):
        children = Tk.Frame.winfo_children(self, *args, **kwargs)
        children.extend(self.cache)
        return children
