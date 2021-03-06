############################
# Avida Mutation Evaluator #
# Originaly by Lane Smith  #
# Maintained by Art Cvoert #
# Copyright 2011           #
############################

import os
import re
import asexual_lineage

#@TODO: make private classes private
#@TODO: More analyze mode commands
#@TODO: Test framework for analyze mode commands

#A change
class MutationEvaluator:

    def __init__(self, pathToAvida = (os.path.curdir + os.path.sep)):
        self.pathToAvida = pathToAvida
        

    def evaluate_effect_of_mutation(self, child_genotype, parent_genotype):
        genotypeFitness = self.get_fitness_of_sequence(child_genotype)
        parentFitness = self.get_fitness_of_sequence(parent_genotype)

        if genotypeFitness - parentFitness > 0.01 * parentFitness:
            #if greater than 0 will be beneficial mutation 
            #geno = 11 parent = 10
            #1 > 0.1 
            return 1
        elif parentFitness - genotypeFitness > 0.01 * parentFitness:
            #if greater than 0 have a deleterious mutation
            #Geno = 5 Parent = 10
            # 5 > 0.1
            return -1
        else:
            return 0

    #Measure the robustness of the given genotype
    def basic_robustness(self, genome):
        #use a slightly different command
        script = "LOAD_SEQUENCE {0}\nFullLandscape fullland.dat 1"

        #write the avida analyze.cfg file
        self.write_sequence_to_avida_analyze_file(genome, script)

        #run analyze mode
        self.run_avida_in_analyze_mode()

        #Get fitness of the single point landscape
        fitness, avg_land = self._get_landscape_fitness()

        if fitness == 0:
            return float('nan'), avg_land, fitness
        elif fitness == None:
            return None, None, None

        #return robustness and components
        return avg_land/fitness, avg_land, fitness

    def get_fitness_of_sequence(self, sequence):
        self.write_sequence_to_avida_analyze_file(sequence)
        self.run_avida_in_analyze_mode()
        return self.get_fitness_from_analyze_output_file()

    #get the basic fitness, but run the org a thousand times with random inputs and check it's phenotype
    def get_phenotype_fitness_of_sequence(self, sequence):
        script = 'LOAD_SEQUENCE {0}\nRECALC use_random_inputs\nDETAIL detail.dat fitness num_trials phen_avg_fitness phen_entropy'.format(sequence)
        self.write_sequence_to_avida_analyze_file(sequence, script)

        self.run_avida_in_analyze_mode()

        return self._get_phenotype_fitness()


    def write_sequence_to_avida_analyze_file(self, sequence,script = ""):
        analyzeFilePath = self.pathToAvida + "analyze.cfg"
        output = ""
        if script == "":
            output = 'LOAD_SEQUENCE {0}\nRECALCULATE\nDETAIL detail.dat fitness'.format(sequence)
        else:
            output = script.format(sequence)
        
        #if(os.path.exists(analyzeFilePath)):
            #os.remove(analyzeFilePath)
        fp = open(analyzeFilePath, 'w')
        fp.write(output)
        fp.close()

    def run_avida_in_analyze_mode(self,seed=1,debug=False):
        #The directory that runs python command needs to contain avida.cfg
        #Recommend to make a base avida directory with necessary *.cfg files
        origin = os.path.abspath(".")
        os.chdir(self.pathToAvida)
        if (debug): print os.path.abspath(".")
        command = "./avida -a -s {0:d}  > /dev/null 2> /dev/null".format(seed)
        if(debug):
            command = "./avida -a -s {0:d}".format(seed)
            print os.system(command)
        else:
            os.system(command)
        os.chdir(origin)
        return None


    #@TODO: all these get commands need to be refactored
    def get_fitness_from_analyze_output_file(self):
        #where is the file?
        outputFilePath = self.pathToAvida + "/data" + os.path.sep + 'detail.dat'

        #get the data from the file
        fp = open(outputFilePath)
        analyzeOutputFile = fp.read()
        fp.close()

        #should be one floating point number
        fitnessRegex = re.search("^\d+(\.\d*)?", analyzeOutputFile, re.MULTILINE)
        #remove the output file so we don't accidently read it twice
        os.remove(outputFilePath)
        return float(fitnessRegex.group(0))
        

    def _get_landscape_fitness(self, filename = "fullland.dat"):
        output_file = self.pathToAvida + "data" + os.path.sep + filename
        if not os.path.exists(output_file):
            return None,None
        fp = open(output_file)
        analyzeOutputFile = fp.readlines()
        fp.close()
        #print analyzeOutputFile
        for line in analyzeOutputFile:
            if(re.search("^\-?[0-9]+", line) != None):
                raw = re.split(" ",line.strip())
                os.remove(output_file)
                return float(raw[9]),float(raw[13])

    def _get_phenotype_fitness(self, filename = "detail.dat"):
        output_file = self.pathToAvida + "data" + os.path.sep + filename
        if not os.path.exists(output_file):
            return None,None,None,None
        fp = open(output_file)
        analyzeOutputFile = fp.readlines()
        fp.close()
        #print analyzeOutputFile
        for line in analyzeOutputFile:
            if(re.search("^\-?[0-9]+", line) != None):
                raw = re.split(" ",line.strip())
                os.remove(output_file)
                return float(raw[0]),int(raw[1]),float(raw[2]),float(raw[3])

            
