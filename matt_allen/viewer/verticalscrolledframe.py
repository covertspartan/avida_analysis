import Tkinter as Tk

class VerticalScrolledFrame(Tk.Frame):
    """A pure Tkinter scrollable frame that actually works!

    Use the 'interior' attribute to place widgets inside the scrollable frame
    Construct and pack/place/grid normally
    This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        Tk.Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Tk.Scrollbar(self, orient=Tk.VERTICAL)
        vscrollbar.pack(fill=Tk.Y, side=Tk.RIGHT, expand=False)
        #vscrollbar.grid(column=1, sticky=Tk.N+Tk.S)
        canvas = Tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)
        #canvas.grid(row=0, column=0, sticky=Tk.N+Tk.S+Tk.E+Tk.W)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Tk.Frame(canvas, takefocus=True)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=Tk.NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        self.canvas = canvas

        interior.bind('<Button-4>', self._on_mouse_wheel)
        interior.bind('<Button-5>', self._on_mouse_wheel)
        interior.bind('<MouseWheel>', self._on_mouse_wheel)

    #callback for scrolling on an element
    def _on_mouse_wheel(self, event):
        delta = event.delta
        if event.num == 4:
            delta = -1
        if event.num == 5:
            delta = 1
        self.canvas.yview('scroll', delta, 'units')


    def bind(self, *args, **kwargs):
        Tk.Frame.bind(self, *args, **kwargs)
        self.interior.bind(*args, **kwargs)

    def winfo_children(self, *args, **kwargs):
        children = Tk.Frame.winfo_children(self, *args, **kwargs)
        children.append(self.interior)
        return children