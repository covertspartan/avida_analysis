import evaluator
import asexual_lineage


class EpistasisTracker:

    def __init__(self, path_of_files_to_trace, rep_number):
        self.lineage = asexual_lineage.cASexualLineage(path_of_files_to_trace)
        self.lineage.update_with_child()
        self.evaluator = evaluator.MutationEvaluator("/home/jmc4939/BaseAvida/")
        writefile = "EpistsasisOccurenceNoStruct{}.txt".format(rep_number)
        self.pointer = open(writefile, "w")

    def identify_deleterious_steps(self):
        self.pointer.write("1.) Parent Genotype\n2.) Parent Fitness\n3.) Deleterious Genotype\n4.) Deleterious Fitness\n5.) Percentage Fitness Lost\n6.) Recovery Genotype\n7.) Recovery Fitness\n8.) Percentage Fitness Recovered\n9.) Depth of Recovery\n")
        parent = 1
        child = self.lineage[parent].get("child")
        mutation = None
        while child is not None:
            parent_genotype = self.lineage[parent].get("raw")[2]
            child_genotype = self.lineage[child].get("raw")[2]

            mut_effect = self.evaluator.evaluate_effect_of_mutation(child_genotype, parent_genotype)
            
            if mut_effect==-1:
                mutation = self._isolate_deleterious(child_genotype, parent_genotype)
                recovery = self.revert_sequence_effect(mutation, parent)
                parent_fit = str(self.evaluator.get_fitness_of_sequence(parent_genotype))
                child_fit = str(self.evaluator.get_fitness_of_sequence(child_genotype))
                recovery_fit = str(recovery[1])
                fitness_lost = str(1-float(child_fit)/float(parent_fit))
                if recovery_fit != 'N/A':
                    fitness_recovered = str(float(recovery_fit)/float(parent_fit)-1)
                else:
                    fitness_recovered = 'N/A'
                self.pointer.write(parent_genotype+" "+parent_fit+' '+child_genotype+" "+child_fit+' '+fitness_lost+' '+recovery[0]+" "+recovery_fit+" "+fitness_recovered+' '+str(recovery[2])+'\n')
            #print mutation
            parent = child
            child = self.lineage[parent].get("child")


    def _isolate_deleterious(self, child_genotype, parent_genotype):
        for i in range(len(child_genotype)):
            if child_genotype[i] != parent_genotype[i]:
                return (parent_genotype[i], i, child_genotype[i])


    def revert_sequence_effect(self, mutation, organism_to_revert):
        ancestor_genome = self.lineage[organism_to_revert].get("raw")[2]
        deleterious = self.lineage[organism_to_revert].get("child")
        possible_recover = self.lineage[deleterious].get("child")
        depth = 0
        while possible_recover is not None:
            depth +=1
            recover_genome = self.lineage[possible_recover].get("raw")[2]

            if self._deleterious_still_present(recover_genome, mutation[2], mutation[1]):
                reverted_genome = recover_genome[:mutation[1]]+mutation[0]+recover_genome[mutation[1]+1:]
        # return value of 1 is a beneficial mutation, -1 is a deleterious mutation, 0 is no result
                if -1 == self.evaluator.evaluate_effect_of_mutation(reverted_genome, recover_genome):
                    if 1 == self.evaluator.evaluate_effect_of_mutation(recover_genome, ancestor_genome):
                        return (recover_genome, self.evaluator.get_fitness_of_sequence(recover_genome), depth)
            else:
                #Deleterious no longer present break off the run
                break

            hold_lineage = possible_recover
            possible_recover = self.lineage[hold_lineage].get("child")
        #Fitness was never recovered, depth of this is -1
        return ('N/A','N/A','-1')


        
    def _deleterious_still_present(self, sequence, mutation, position):
        if sequence[position] == mutation:
            return True
        else:
            return False
