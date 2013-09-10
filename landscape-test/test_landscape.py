from avida_support.asexual_population import *
from avida_support.evaluator import *

#create an asexual population
lineage = cASexualPopulation("avida_files/data/detail-10000.spop",fields={"Sparent":3,"Iliving":4,"Sgenome":16})

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
    print x[0],evaluator.basic_robustness(x[1]['genome'])
    
