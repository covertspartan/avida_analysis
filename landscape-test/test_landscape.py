from avida_support.asexual_population import *
from avida_support.evaluator import *

#create an asexual population
lineage = cASexualPopulation("/CE_2013/sample_data/rs_consistancy_tests/C_25p_fl_su_lc_250ku_12121000/data/detail-250000.spop.gz",fields={"Sparent":3,"Iliving":4,"Sgenome":16})

#need an evaluator instance to run landscaping
evaluator = MutationEvaluator("avida_files/")

#functions to test the evaluator
#print evaluator.basic_robustness("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
#print evaluator.basic_robustness("wkjagczvvvkvyucuryyuvuavycteyAafuumsydzvfcaxgab")

#traces the line of descent -- returns nothing
lineage.trace_line_of_descent()

#look at everything on the line of descent from the final dominant to the ancestor
for x in lineage.walk_line_of_descent():
    #print the genome id and the robustness analysis
    print x[0],evaluator.get_phenotype_fitness_of_sequence(x[1]['genome'])
    
