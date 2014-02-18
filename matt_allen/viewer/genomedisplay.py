from __future__ import division
import Tkinter as Tk
import tkFont
import tkutils
from trace_viewer.element import Element

class GenomeDisplay(Tk.Text):
    """
    A GUI element that displays a genome with mutation highlighting.
    """
    
    def __init__(self, parent, text, *args, **kwargs):
        """
        Create a new instance of the genome display.

        @param parent: the parent container.
        @param text: the genome text to display.
        """
        self.text = text.upper()
        Tk.Text.__init__(self, parent, *args, **kwargs)
        self.insert('1.0', self.text)
        self.config(state='disabled')

    def update(self, new_text, parent_text):
        """
        Update the state of the genome display, replacing the genome
        text and highlighting mutations.

        @param new_text: the text of the new genome.
        @param parent_text: the text of the parent genome.
        """
        self.config(state='normal')
        self.delete('1.0', 'end')
        self.insert('1.0', new_text.upper())
        self.text = new_text
        self._diff_text(self.text, parent_text)
        self.config(state='disabled')

    def _diff_text(self, new_text, parent_text):
        """
        Evaluate the differences between two genomes and highlight the changes.

        @param new_text: the text of the new genome.
        @param parent_text: the text of the parent genome.
        """
        if new_text is None or parent_text is None or len(parent_text) == 0:
            return
            
        self.tag_delete('diff')
        self.tag_delete('del')
        self.tag_delete('ins')

        changes = tkutils.diff_genomes(parent_text, new_text)

        for type, start, size, new_text in changes:
            self.tag_add(type, '1.' + str(start), '1.' + str(start + size))
        
        """s = difflib.SequenceMatcher(a=parent_text, b=new_text)
        
        oldmatch = None
        offset = 0
        for block in s.get_matching_blocks():
            if block.a + offset < block.b:
                offset += block.b - block.a
                self.tag_add('ins', '1.' + str(block.a), '1.' + str(block.b))

            elif block.a + offset > block.b:
                offset += block.b - block.a
                self.tag_add('del', '1.' + str(block.b - 1), '1.' + str(block.b))
            elif oldmatch is not None:
                start = oldmatch.a + oldmatch.size
                end = block.a
                if start != end:
                    self.tag_add('diff', '1.' + str(start), '1.' + str(end))
                    
            oldmatch = block"""

        self.tag_config('diff', foreground='blue', font=tkFont.BOLD)
        self.tag_config('ins', foreground='green', font=tkFont.BOLD)
        self.tag_config('del', foreground='red', font=tkFont.BOLD)
        
