seting up a landscape analysis

an example of this may be found in test_landscape.py

1) setup a config directory with apporpriate config files and avida executables 
   -this can be anywere on the local system, just make sure you don't have any actual data stored in it

2) Instantiate an cAsexualPopulation class, provide a dictionary with field headers for parent, number living, and genome


3) Instantiate an evaluator class, provide path to config directory

4) trace the lineage

5) walk the lineage and get robustness measure from each org
   -walk function returns a tuple (genomeID,population_entry)
   -basic robustness measure returns: landscape average/genome fitness, landscape average, genome fitness

More to come!
