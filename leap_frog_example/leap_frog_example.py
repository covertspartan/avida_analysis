from avida_support.avida_file_tools import *
from avida_support.asexual_population import *

from pylab import *

from scipy.stats import f_oneway, ttest_ind, mannwhitneyu, describe

lineage_prefix = [
                "SBT_100sp_0000005mr_250ku_lc_l50_25p_fl_fi",\
                "SBT_100sp_000005mr_250ku_lc_l50_25p_fl_fi",\
                "SBT_100sp_00005mr_250ku_lc_l50_25p_fl_fi",\
                "SBT_100sp_0005mr_250ku_lc_l50_25p_fl_fi",\
                "SBT_100sp_005mr_250ku_lc_l50_25p_fl_fi",\
                "SBT_100sp_05mr_250ku_lc_l50_25p_fl_fi",\
                "SBT_control_250ku_lc_l50_25p_fl_fi"\
               ]

#create a dictionary to quickly lookup genotypes on the line of descent.
def get_lineage_dict(pop):

    ret_val = {}
    for id, genome in pop.walk_line_of_descent():
        ret_val[id]=genome['living']

    return ret_val

#count leap froggin -- but ignore the first and last data points
def count_leaps(doms, lineage):
    leaps = 0
    total = 0

    for id in doms:
        #is the dominat genotype on the line of descent?
        #remember -- one is an int the other is a string -- derp
        if(lineage.get(str(int(id)), None) == None):
            leaps += 1

        total += 1

    return leaps/float(total)

data_array = []

for treat in lineage_prefix:
    
    #get the data files
    dominant_files = find_replicates(treat,"dominant.dat","./raw_data")
    detail_dumps = find_replicates(treat,"detail-250000.pop","./raw_data")
    hist_dumps = find_replicates(treat,"historic-250000.pop","./raw_data")

    #sort the data files so that we can compare one to the other
    dominant_files.sort()
    detail_dumps.sort()
    hist_dumps.sort()

    trt_data = []
    for i, dom in enumerate(dominant_files):
        print dom, detail_dumps[i]

        #get a population -- overide default fields for old detail dump format
        pop = cASexualPopulation(detail_dumps[i],{"Sparent":1,"Iliving":3},hist_dumps[i])

        #trace the line of descent
        pop.trace_line_of_descent()

        #get the lineage
        lineage = get_lineage_dict(pop)
        
        #get a list of dominant genotype
        doms = get_column(dom,15)

        trt_data.append(count_leaps(doms, lineage))
    #quit()
    data_array.append(trt_data)

#normalize by max possible leapfrogging 
#data_array = array(data_array) / 199

#WTF scipy -- why do I have to transpose here, but not for the stats tests?
boxplot(data_array) 
ylim([0.6, 1.0])
show()


print "Anova: ", str(f_oneway(*data_array))

for trt in data_array:
    print len(trt), len(data_array[2])
    print "T-test vs optimal: ", str(ttest_ind(data_array[2],trt))
    h, p = mannwhitneyu(data_array[2],trt)
    print "U-test vs optimal: ", str((h, p*2))

    print "Versus control"
    print len(trt), len(data_array[6])
    print "T-test vs control: ", str(ttest_ind(data_array[6],trt))
    h, p = mannwhitneyu(data_array[6],trt)
    print "U-test va control: ", str((h, p*2))
    
    print describe(trt)
    print median(trt)
