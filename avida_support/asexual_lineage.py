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

###########################################################################################################################
### !!!!!WARNING: For now, we are assuming the lineage is already traced from the ancestor to the final dominant!!!!!!#####
###########################################################################################################################

### @todo Implment lineage trace, load in the lineage and all associated data, do the trace manually
### @todo configurable dictionaries for each genotype entry, accept a list of column headers which corresponds to the "raw" data



class cASexualLineage():


    ### Function - cASexualLineage::__init__
    ### Purpose  - Instasiate an asexual lineage, either from scratch or from a 
    ### Input    - An optional detailDump containing a lineage from Avida analyze mode
    ### Output   - a cASexualLineage object
    def __init__ (self, detailDump=None):
        self._lin = {} #dictionary which will contain the lineage
        self._size = 0 #size of the dictionary
        self._Dom = None #ID of the dominant genotype
        self._Ancestor = None #ID of the Ancestor

        #do we have a detail dump?
        if detailDump != None:
            self._load_detail_lineage_file(detailDump)

    ### Function - cASexualLineage::_load_detail_lineage_file
    ### Purpose  - Load an asexual lineage entry
    ### Input    - 
    ### Output   - 
    def _load_detail_lineage_file(detailDump):
        


