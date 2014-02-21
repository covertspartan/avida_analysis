from __future__ import division
import Tkinter as Tk
import difflib

def bind_children(widget, *args, **kwargs):
    """
    Bind an event to a widget and every child of that
    widget, recursively. Works like the normal bind function.

    @param widget: the root widget to bind to.
    """
    widget.bind(*args, **kwargs)
    for child in widget.winfo_children():
        bind_children(child, *args, **kwargs)

def diff_genomes(start_genome, end_genome, debug=False):
    """
    Compare two genomes to find how they differ, return
    the result as a list of tuples containing details of the
    changed regions.

    @param start_genome: the starting genome as a string.
    @param end_genome: the ending genome as a string.
    @returns: list of changes, each change is a tuple of the
              form ("type", start_index, size, new_text)
              corresponding to a region of text in the genome.
    """
    if start_genome is None or end_genome is None:
        return []
    s = difflib.SequenceMatcher(a=start_genome, b=end_genome)

    changes = []

    oldmatch = None
    offset = 0
    for block in s.get_matching_blocks():
        if debug:
            print block
        if block.a + offset < block.b:
            offset += block.b - block.a
            changes.append(('ins', block.a, block.b-block.a, end_genome[block.a:block.b]))

        elif block.a + offset > block.b:
            offset += block.b - block.a
            changes.append(('del', block.b, block.a - block.b, ''))
        elif block.a != 0:
            if oldmatch is not None:
                start = oldmatch.a + oldmatch.size
                end = block.a
            else:
                start = block.a - 1
                end = block.a
            if start != end:
                changes.append(('diff', start, end-start, end_genome[start:end]))

        oldmatch = block

    return changes

def transform_ops(operations, index, delta):
    for i in range(len(operations)):
        etype, estart, esize, etext = operations[i]

        if estart >= index:
            operations[i] = (etype, estart + delta, esize, etext)
    return operations
