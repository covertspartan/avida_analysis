import evaluator
import asexual_lineage


class EpistasisTracker:

    def __init__(self, path_of_files_to_trace):
        self.lineage = asexual_lineage.cASexualLineage(path_of_files_to_trace)
        self.lineage.update_with_child()
        self.evaluator = evaluator.MutationEvaluator("~/StructuredPop/config")

    def identify_deleterious_step(self):
        parent = 1
        child = self.lineage[parent].get("child")
        mutation = None
        while child is not None:
            parent_genotype = self.lineage[parent].get("raw")[2]
            child_genotype = self.lineage[child].get("raw")[2]
            print parent
            mut_effect = evaluator.evaluate_effect_of_mutation(child_genotype, parent_genotype)
            if mut_effect != -1:
                parent = child
                child = self.lineage[parent].get("child")
                continue
            else:
                mutation = self._isolate_deleterious(child_genotype,
                                                parent_genotype)
            #what happens if two deleterious steps?            
        if mutation:
            return tuple([child])+mutation
        else:
            print "No deleterious steps in {0}".format(self.lineage)


    def _isolate_deleterious(child_genotype, parent_genotype):
        for i in range(len(child_genotype)):
            if child_genotype[i] != parent_genotype[i]:
                #Need to check if it just needs to change from the mutation that was made
                #of if need to go back to parent genotype
                return (child_genotype[i], i)


    def revert_sequence_effect(self, mutation, genome_to_revert):
        reverted_genome = genome_to_revert[:mutation[1]]+mutation[0]+genome_to_revert[mutation[1]+1:]
        # return value of 1 is a beneficial mutation, -1 is a deleterious mutation, 0 is no result
        return self.evaluator.evalutate_effect_of_mutation(genome_to_revert,
                                                      reverted_genome)
