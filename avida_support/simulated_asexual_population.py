 ####################################
 # Avida Analysis Toolkit - v 0.1   #
 # A. W. Covert III, Ph. D          #
 # All rights reserved              #
 ####################################

from asexual_population import *
from numpy import *
class cSimulatedAsexualPopulation(cASexualPopulation):

    def __init__(self,size=1000,genotypes=1,ben_rate=0.01,empty = False,seed = 1,state=None):
        self._fields = {"parent":1,"living":2,"fitness":3}
        self._ben_rate = ben_rate
        self._pop_size = size
        self._num_genotypes = 0
        self._rnd = state
        if state == None:
            self._rnd = random.RandomState()
            self._rnd.seed(seed)
        self._currID = 1
        self._lin = {}

        if not empty:
            self._add_entry(["0","(none)",100,1])
        

        return None

    def __len__(self):
        return self._pop_size

    def __str__(self):
        s = ""
        for entry in self._lin:
            s += str(self[entry])+"\n"
        return s

    def step_simulated_population(self):
        nPop = cSimulatedAsexualPopulation(size=self._pop_size,ben_rate=self._ben_rate,empty=True,state=self._rnd)
        
        #total population size
        tot_fitness = self._total_fitness()#reduce(lambda x,y: x["fitness"] + y["fitness"], self._lin)
        print "Total fitness: ",tot_fitness
        #new mutation?
        tot_size = 0
        for entry in self._lin:
            if self[entry]["living"]>0:
                #print self[entry]["fitness"]
                #size of entry in next population -- straigh Wright/Fisher
                size = floor(self._pop_size * ((self[entry]["fitness"]*self[entry]["living"])/tot_fitness))
                #print "size", size
                #number of benefical mutations from this genotype, this generation
                #ben_muts = sum(self._rnd.poisson(self._ben_rate, size))
                ben_muts = 0
                prob = self._rnd.random_sample()
                print prob
                if prob < 0.1:
                    ben_muts = 1
                #print ben_muts
                #this comes out of this population
                size = size - ben_muts
                tot_size += size
                #add the benefical mutations
                if ben_muts > 0:
                    for x in xrange(0,ben_muts):
                        nPop._add_entry([str(self._currID),entry,1,self[entry]["fitness"]*1.5],self._fields)
                        self._currID += 1
                        tot_size += 1

                #add parent
                nPop._add_entry([entry,self[entry]["parent"],size,self[entry]["fitness"]],self._fields)

                nPop._currID = self._currID

        diff = self._pop_size - tot_size

        print "diff",diff
        #bring up the population size randomly
        if diff > 0:
            for i in range(0,int(diff)):
                x = nPop._get_random()
                #print nPop[str(x)]["living"]
                nPop[str(x)]["living"] = nPop[str(x)]["living"] + 1
                #print nPop[str(x)]["living"]
                #quit()

        return nPop
            
    def _get_random(self):
        l = self._lin.viewkeys()
        #print l
        return self._rnd.permutation(list(l))[-1]
        
    def _total_fitness(self):
        tot = 0.0
        #print self._lin
        #print type(self._lin)
        for entry in self._lin:
            #print entry
            #print type(entry)
            tot += self[entry]["fitness"]*self[entry]["living"]

        return tot


