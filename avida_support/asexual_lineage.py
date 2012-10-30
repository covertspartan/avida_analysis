 ####################################
 # Avida Analysis Toolkit - v 0.1   #
 # A. W. Covert III, Ph. D          #
 # All rights reserved              #
 ####################################

### Asexual Lineage Class
### Load in an asexual deatil dump and save it as a dictionary of dictionaries
### Primary keys are genotype ID (as strings)
### "parent" is genotype ID of children (as string)
### "raw" is tuple containing all of the raw data
### Slightly inspried by lane's sexual scripts

import gzip, re

from exceptions import KeyError

###########################################################################################################################
### !!!!!WARNING: For now, we are assuming the lineage is already traced from the ancestor to the final dominant!!!!!!#####
###########################################################################################################################

### @todo Implment lineage trace, load in the lineage and all associated data, do the trace manually
### @todo configurable dictionaries for each genotype entry, accept a list of column headers which corresponds to the "raw" data




class cASexualLineage():


    ### Function - cASexualLineage::__init__
    ### Purpose  - Instasiate an asexual lineage, either from scratch or from a 
    ### Input    - An optional detailDump containing a lineage from Avida analyze mode should be a lineage that is already traced not detailx.spop
    ### Output   - a cASexualLineage object
    def __init__ (self, detailDump=None):
        self._lin = {} #dictionary which will contain the lineage
        self._size = 0 #size of the dictionary
        self._Dom = None #ID of the dominant genotype
        self._Ancestor = None #ID of the Ancestor

        #do we have a detail dump? If so, load that puppy up!
        if detailDump != None:
            self._load_detail_lineage_file(detailDump)

    ### Function - cASexualLineage::__str__
    ### Purpose  - Dump the lineage as a string
    ### Input    - None
    ### Output   - a sting representing the lineage
    ### Note     - This is sloooooooooooooooooooooooooooooow -- DEBUGGING ONLY PLEASE!
    def __str__(self):
        linStr = "" #dummy string to hold the lineage

        curr = self._lin[self._Dom] #have to start at the bottom for now
        currID = self._Dom
        next = self._lin.get(curr["parent"],None) #next currently means the immediate parent, since we're walking backwards

        #walk up the lineage backwards
        while next != None:
            linStr = curr["parent"] + "--->" + currID + "\n" + linStr
            currID = curr["parent"]
            curr = next
            next = self._lin.get(curr["parent"],None)



        return linStr

    def __len__(self):
        return self._size


    def get_final_dom(self):
        return self._Dom

    ### Function - cASexualLineage::_load_detail_lineage_file
    ### Purpose  - Load an asexual lineage entry into the self._lin
    ### Input    - filename of a detail dump (.dat or .gz)
    ### Output   - None -- updates this object
    def _load_detail_lineage_file(self, detailDump):
        fp = None #file pointer -- need to detrmine if we need 
        if(detailDump[-2:] == "gz"):
            fp = gzip.open(detailDump) #open a gziped file
        else:
            fp = open(detailDump) #open a regular file

        #snag all the data at once (pretty sure this is faster when you need the whole file)
        data = fp.readlines()

        fp.close() #done with this, let's be neat and tidy

        count = 0
        ID = None

        ### NOTE: we're not going to validate every line in this file
        #for each line in this file
        for line in data:
            
            #check to make sure it starts with a genotype ID
            if(re.search("^[0-9]+", line) != None):
                raw = re.split(" ",line.strip()) #detail dumps are space delimited
                ID = raw[0] #First item is always the genotype ID (we hope)
                self._add_entry(raw) #Add the item to the dictionary

                #if we're at the beginning of the file, we've found the Ancestor! (we hope!)
                if count == 0:
                    self._Ancestor = ID
                count += 1
            
        if ID != None: #did the damn thing actually work?
            self._Dom = ID#then, in theory, the last genome is the final dominant!

        self._size = count



        return None

    ### Function - cASexualLineage::_load_detail_lineage_file
    ### Purpose  - Load an asexual lineage entry into the self._lin
    ### Input    - 
    ### Output   - 
    def _add_entry(self,raw):
        if self[raw[0]] == None:
            self._lin[raw[0]] = {"parent":raw[1], "raw":raw}
            return True
        else:
            return False


    def update_with_child(self):
        child_ID = self._Dom
        self._lin[child_ID]["child"] = None
        parent_ID = self._lin[child_ID].get("parent")
        while parent_ID != '0':
            #print type(self._lin[parent_ID])
            self._lin[parent_ID]["child"] = child_ID
            child_ID = parent_ID
            parent_ID = self._lin[child_ID].get("parent")

    ### Function - cASexualLineage::_get_key
    ### Purpose  - Retrieve the entry of a speific key
    ### Input    - 
    ### Output   - 
    def __getitem__(self,key):
        t = type(key)
        if t == int:
            return self._lin.get(str(key),None)
        elif t == str:
            return self._lin.get(key,None)
        elif t == tuple:
            if len(key) == 2: # @AWC a bit of a kludge for now, need to see how the pros do it
                return self[key[0]][key[1]]
            else:
                raise KeyError
        elif type(key) == slice:
            print "WARNING: SLICING LINEAGES IS NOT YET IMPLEMENTED"
            return None
        else:
            raise KeyError







