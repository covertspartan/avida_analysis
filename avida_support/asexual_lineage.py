# Avida Analysis Toolkit - v 0.1
# A. W. Covert III, Ph. D
# All rights reserved

# Asexual Lineage Class
# Load in an asexual detail dump and save it as a dictionary of dictionaries
# Primary keys are genotype ID (as strings)
# "parent" is genotype ID of children (as string)
# "raw" is tuple containing all of the raw data
# Slightly inspired by lane's sexual scripts

import gzip
import re

from exceptions import KeyError


# !!!!!WARNING: For now, we are assuming the lineage is already traced from the ancestor to the final dominant!!!!!!

# @todo Implement lineage trace, load in the lineage and all associated data, do the trace manually
# @todo configurable dictionaries for each genotype entry

class cASexualLineage():

    # Function - cASexualLineage::__init__
    # Purpose  - Instantiate an asexual lineage, either from scratch or from a
    # Input    - An optional detailDump containing a lineage from Avida analyze mode should be a lineage that is already
    #            traced not detailXXX.spop
    # Output   - a cASexualLineage object
    def __init__ (self, detail_dump = None):
        self._lin = {}          # dictionary which will contain the lineage
        self._size = 0          # size of the dictionary
        self._Dom = None        # ID of the dominant genotype
        self._Ancestor = None   # ID of the Ancestor

        # do we have a detail dump? If so, load that puppy up!
        if detail_dump is not None:
            self._load_detail_lineage_file(detail_dump)

    # Function - cASexualLineage::__str__
    # Purpose  - Dump the lineage as a string
    # Input    - None
    # Output   - a sting representing the lineage
    # Note     - This is sloooooooooooooooooooooooooooooow -- DEBUGGING ONLY PLEASE!
    def __str__(self):

        # dummy string to hold the lineage
        lineage_str = ""

        # have to start at the bottom for now
        curr = self._lin[self._Dom]
        curr_id = self._Dom

        # next currently means the immediate parent, since we're walking backwards
        next = self._lin.get(curr["parent"], None)

        # walk up the lineage backwards
        while next is not None:
            lineage_str = curr["parent"] + "--->" + curr_id + "\n" + lineage_str
            curr_id = curr["parent"]
            curr = next
            next = self._lin.get(curr["parent"],None)

        return lineage_str

    def __len__(self):
        return self._size


    def get_final_dom(self):
        return self._Dom

    # Function - cASexualLineage::_load_detail_lineage_file
    # Purpose  - Load an asexual lineage entry into the self._lin
    # Input    - filename of a detail dump (.dat or .gz)
    # Output   - None -- updates this object
    def _load_detail_lineage_file(self, detail_dump):
        fp = None  # dummy file pointer -- filled in with depending on file type
        if detail_dump[-2:] == "gz":
            fp = gzip.open(detail_dump)  # open a gziped file
        else:
            fp = open(detail_dump)  # open a regular file

        # snag all the data at once
        # this may cause problems for exceptionaly large linages
        data = fp.readlines()

        fp.close()  # done with file, let's be neat and tidy

        count = 0
        id = None

        # NOTE: we're not going to validate every line in this file
        # for each line in this file
        for line in data:
            
            # check to make sure it starts with a genotype ID
            if re.search("^[0-9]+", line) is not None:
                raw = re.split(" ", line.strip())  # detail dumps are space delimited
                id = raw[0]                       # First item is always the genotype ID (we hope)
                self._add_entry(raw)              # Add the item to the dictionary

                # if we're at the beginning of the file, we've found the Ancestor! (we hope!)
                if count == 0:
                    self._Ancestor = id
                count += 1
            
        if id is not None:  # did the damn thing actually work?
            self._Dom = id  # then, in theory, the last genome is the final dominant!

        self._size = count



        return None

    # Function - cASexualLineage::_add_entry
    # Purpose  - Add an entry to self._lin
    # Input    - raw data in array form
    # Output   - None
    def _add_entry(self, raw):
        if self[raw[0]] is None:
            self._lin[raw[0]] = {"parent": raw[1], "raw": raw}
            return True
        else:
            return False

    # Function - cASexualLineage::update_with_child
    # Purpose  - Trace lineage and set child_id for each entry
    # Input    - None
    # Output   - None
    def update_with_child(self):
        child_id = self._Dom
        self._lin[child_id]["child"] = None
        parent_id = self._lin[child_id].get("parent")
        while parent_id != '0':
            self._lin[parent_id]["child"] = child_id
            child_id = parent_id
            parent_id = self._lin[child_id].get("parent")

    # Function - cASexualLineage::__getitem__
    # Purpose  - Retrieve the entry of a speific key
    # Input    - 
    # Output   - 
    def __getitem__(self, key):
        t = type(key)
        if t == int:
            return self._lin.get(str(key), None)
        elif t == str:
            return self._lin.get(key, None)
        elif t == tuple:
            if len(key) == 2:  # @AWC a bit of a kludge for now, need to see how the pros do it
                return self[key[0]][key[1]]
            else:
                raise KeyError
        elif type(key) == slice:
            print "WARNING: SLICING LINEAGES IS NOT YET IMPLEMENTED"
            raise KeyError
        else:
            raise KeyError







