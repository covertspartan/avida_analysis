from __future__ import division
import Tkinter as Tk
import os

class Dialog(Tk.Toplevel):
    """
    Base class for custom dialog boxes with arbitrary contents and behaviors
    """
    def __init__(self, parent, title=None, *args, **kwargs):
        """
        Create an instance of a dialog.

        @param parent: the parent window to spawn over.
        @param title: the window manager title of the dialog.
        """
        Tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.transient(parent)

        if title is not None:
            self.title(title)

        self.parent = parent
        self.result = None
        body = Tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self._buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol('WM_DELETE_WINDOW', self._cancel)
        self.geometry('+%d+%d' % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master):
        """
        Defines the layout of the main body, override to add widgets to the dialog.
        """
        pass

    def _buttonbox(self):
        """
        Adds the standard "OK" and "Cancel" buttons to the bottom of the dialog.

        Creates keybindings for <Return> and <Escape>.
        """
        box = Tk.Frame(self)
        ok = Tk.Button(box, text='OK', width=10, command=self._ok, default=Tk.ACTIVE)
        ok.pack(side=Tk.LEFT, padx=5, pady=5)
        cancel = Tk.Button(box, text='Cancel', width=10, command=self._cancel)
        cancel.pack(side=Tk.LEFT, padx=5, pady=5)

        self.bind('<Return>', self._ok)
        self.bind('<Escape>', self._cancel)

        box.pack()

    def _ok(self, event=None):
        """
        Callback for the "OK" action.

        Checks input with L{validate}, then calls L{apply}.
        """
        if not self.validate():
            self.initial_focus.focus_set()
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()
        self._cancel()

    def _cancel(self, event=None):
        """
        Callback for the "Cancel" action, destroys the dialog.
        """
        self.parent.focus_set()
        self.destroy()

    def validate(self):
        """
        Checks to see if the dialog is in a valid state.

        Override to check any user input for consistency. An error
        dialog can be spawned to alert the user if needed.

        @returns: the validity of the current state.
        """
        return True

    def apply(self):
        """
        Apply the user's input and take any actions needed.

        Override to implement dialog behavior. The result field
        can be used to store a result that will be accessable to the
        calling object.
        """
        pass