import os
import re
import asexual_lineage
#Testing for updates

class MutationEvaluator:

    def __init__(self, pathToAvida = (os.path.curdir + os.path.sep), path_to_lineage)
        self.pathToAvida = pathToAvida
        self.lineage = asexual_lineage.cASexualLineage(path_to_lineage)
        self.lineage.update_with_child()

    def identify_deleterious_step(self):
        parent = self.lineage[1]
        child = self.lineage[1].get("child")
        while child is not None:
            if -1 == self.evaluate_effect_of_mutation(self.lin[child].get("raw")[2],                                             self.lin[parent].get("raw")[2]):
            else:
                continue

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

    def get_fitness_of_sequence(self, sequence):
        self.write_sequence_to_avida_analyze_file(sequence)
        self.run_avida_in_analyze_mode()
        return self.get_fitness_from_analyze_output_file()

    def write_sequence_to_avida_analyze_file(self, sequence):
        analyzeFilePath = self.pathToAvida + "analyze.cfg"
        output = 'LOAD_SEQUENCE {0}\nRECALCULATE\nDETAIL detail.dat fitness'.format(sequence)
        #if(os.path.exists(analyzeFilePath)):
            #os.remove(analyzeFilePath)
        fp = open(analyzeFilePath, 'w')
        fp.write(output)
        fp.close()

    def run_avida_in_analyze_mode(self):
        command = self.pathToAvida + "avida -a > /dev/null 2> /dev/null"
        os.system(command)

    def get_fitness_from_analyze_output_file(self):
        outputFilePath = self.pathToAvida + "data" + os.path.sep + 'detail.dat'
        fp = open(outputFilePath)
        analyzeOutputFile = fp.read()
        fp.close()
        fitnessRegex = re.search("^\d+(\.\d*)?", analyzeOutputFile, re.MULTILINE)
        return float(fitnessRegex.group(0))
        
    def get_sequence_with_mutation_reverted(genotype, mutation):
        #@TODO
        pass
