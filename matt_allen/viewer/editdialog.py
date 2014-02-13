from __future__ import division
import Tkinter as Tk
import tkMessageBox
from dialog import Dialog
import os
import re

class EditDialog(Dialog):
    """
    Dialog window used to allow the user to edit a genome.
    """
    def __init__(self, parent, genome, *args, **kwargs):
        """
        Create an instance of the edit dialog.

        @param parent: the parent window to spawn the dialog over.
        @param genome: the start state of the genome to edit.
        """
        self.genome = genome
        Dialog.__init__(self, parent, *args, **kwargs)

    def body(self, master):
        """
        Create the body of the edit dialog, creates a Tk.Text element.
        """
        self.text = Tk.Text(master, height=4)
        self.text.pack()
        self.text.insert('1.0', self.genome)
        return self.text

    def validate(self):
        """
        Validate the entered genome, checks for illegal characters and spawns
        an error dialog if needed.
        """
        genome = self.text.get('1.0', 'end').strip().lower()
        if re.match(r'[\w-]+$', genome):
            self.result = genome
            return True
        else:
            tkMessageBox.showwarning('Illegal Characters', 'Please only enter letters a-z')
            return False