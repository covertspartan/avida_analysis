import evaluator
import asexual_lineage


class EpistasisTracker:

    def __init__(self, path_of_files_to_trace):
        self.lineage = asexual_lineage.cASexualLineage(path_of_files_to_trace)
        self.evaluator = evaluator.MutationEvaluator("~/StructuredPop/config")

    def identify_deleterious_step(self):
        parent = 1
        child = lineage[parent].get("child")
        while child is not None:
            parent_genotype = lineage[parent].get("raw")[2]
            child_genotype = lineage[child].get("raw")[2]

            mut_effect = evaluator.evaluate_effect_of_mutation(child_genotype, parent_genotype)
            if mut_effect != -1:
                parent = child
                child = lineage[parent].get("child")
                continue
            else:
                mutation = self.isolate_deleterious(child_genotype,
                                                parent_genotype)
            #what happens if two deleterious steps?            

    def isolate_deleterious(child_genotype, parent_genotype):
        for i in range(len(child_genotype)):
            if child_genotype[i] != parent_genotype[i]:
                return (child_genotype[i], i)

    def revert_sequence(self):
        pass
