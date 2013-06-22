 ####################################
 # Avida Analysis Toolkit - v 0.1   #
 # A. W. Covert III, Ph. D          #
 # All rights reserved              #
 ####################################

from asexual_population import *
from random import random

class cSimulatedAsexualPopulation(cASexualPopulation):

    def simulate_population(self,size=100,genotypes=1,ben_rate=0.01,empty = False,seed = 1):
        self._fields = {"parent":1,"living":2,"fitness":3}
        self._ben_rate = ben_rate
        self._pop_size = size
        self._num_genotypes = 0
        self._rnd = random()
        self._rnd.seed(seed)

        if not empty:
            self._add_entry(["(none)","0",100,1])
        

        return None

    def step_simulated_population(self):
        nPop = cSimulatedAsexualPopulatoin(size=self._pop_size,ben_rate=self._ben_rate,empty=True)
        
        #total population size
        tot_fitness = reduce(lambda x,y: x["fitness"] + y["fitness"], self._lin)

        #new mutation?
        for entry in self._lin:
            return None
            

        
    
