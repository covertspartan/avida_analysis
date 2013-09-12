from avida_support.simulated_asexual_population import *
from numpy import ones
from pylab import *

#find new orgs from the same parent
def find_new(pop,parent):
    l = []
    print type(pop)
    for x,entry in pop.walk_population():

        if entry["living"] == 1 and entry["parent"] == parent:
            l.append(x)

    return l
        

progression = []

      #cSimulatedAsexualPopulation
pop = cSimulatedAsexualPopulation()

#pop.simulate_population()

progression.append(pop)


for x in range(0,150):
    progression.append(progression[-1].step_simulated_population())
    tot= 0
    for key, entry in progression[-1].walk_population():
        tot += entry["living"]
    print "popsize", tot
    raw_input()



print len(progression)

progression_array = ones((151,1000))*-1

print progression_array.shape

#create array for pcolor
for i,pop in enumerate(progression):
    #print i
    #the seed is trivial
    if i == 0:
        progression_array[i] = i
    else:
        #print pop
        #get indexes of things alive in the last generation -- make sure they're in order
        x, indices = unique(progression_array[i-1],return_index=True)
        ids = progression_array[i-1,indices]
        print ids
        #start adding ids to the next generation
        curr = 0
        for id in ids:
            #get this id
            entry = pop[str(int(id))]
            
            if entry:
                #add the new number of living orgs
                size = entry["living"]
                progression_array[i,curr:curr+size] = id
                
                #how many so far?
                curr = curr+size

                #add the new guys
                new_orgs = find_new(pop,str(int(id)))
                
                for x in new_orgs:
                    progression_array[i,curr] = int(x)

    #print progression_array[i]



pcolormesh(transpose(progression_array))
colorbar()
xlim([0,150])
#grid()
show()
