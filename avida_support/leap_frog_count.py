from avida_support.asexual_lineage import *
from avida_support.avida_file_tools import *
from avida_support.plot_support import *
from re import *
from pylab import *
import numpy
from scipy.stats import f_oneway, ttest_ind
from Bio.Statistics.lowess import lowess

### Function - cASexualLineage::_load_detail_lineage_file
### Purpose  - Load an asexual lineage entry into the self._lin
### Input    - filename of a detail dump (.dat or .gz)
### Output   - None -- updates this object
def count_leaps(lin, f):
    #snag the dominant ids
    doms = get_column(f, 15)

    #number of doms also in dom lineage
    n = []

    #total length of the data set
    total = len(doms)

    #count em up
    for d in doms:
        if(lin[int(d)] != None):
            n.append(1)
        else:
            n.append(0)
            
    return n, total, sum(n)

def build_leap_array(files,lineage_path, treat_str):

    new_arr = []
    sum_arr = []
    #isolate seed numbers for each dominant.dat 
    for f in files:

        #seed number
        nums = re.findall("_[0-9]+/",f)
        num = nums[0][1:-1]

        #construct a path to the lineage
        lin_path = lineage_path + treat_str + num + ".dat"
    
        #create a lineage
        lin = cASexualLineage(lin_path)
        
        #count the number of times the domiant 
        #returns an array with a true/false value at each time index
        n, t, s = count_leaps(lin, f)

        #complie the arrays for each treatment into one
        #trim the first and last values which are always 100%
        new_arr.append(n[1:-1])
        sum_arr.append(s)

    #return a sum at each time point
    return sum(new_arr,axis=0), sum_arr


treat_str = [\
            "SBT_100sp_00005mr_250ku_lc_l50_25p_fl_fi",\
             "SBT_100sp_0000005mr_250ku_lc_l50_25p_fl_fi",\
             "SBT_100sp_05mr_250ku_lc_l50_25p_fl_fi",\
             "SBT_control_250ku_lc_l50_25p_fl_fi"\
            ]

lineage_path = [
             "/home/covertar/Data/asex_sbt/raw_data/SBT_100sp_00005mr_250ku_lc_l50_25p_fl_fi/lineage.",\
                "/home/covertar/Data/asex_sbt/raw_data/SBT_100sp_0000005mr_250ku_lc_l50_25p_fl_fi/lineage.",\
                "/home/covertar/Data/asex_sbt/raw_data/SBT_100sp_05mr_250ku_lc_l50_25p_fl_fi/lineage.",\
                "/home/covertar/Data/asex_sbt/raw_data/SBT_control_250ku_lc_l50_25p_fl_fi/lineage."\
               ]

#lin = cASexualLineage("/home/covertar/Data/asex_sbt/raw_data/SBT_100sp_00005mr_250ku_lc_l50_25p_fl_fi/lineage.SBT_100sp_00005mr_250ku_lc_l50_25p_fl_fi3220500.dat")

leap_arr = []
area_arr = []

for i, s in enumerate(treat_str):
        
    #find all the treatments we have dominant.dat files for
    files = find_replicates(s, "dominant.dat","./raw_data/")

    #get all of the results
    l, n = build_leap_array(files,lineage_path[i], s)

    leap_arr.append(l)
    area_arr.append(n)
    
print leap_arr
area_arr = 199 - array(area_arr)
print f_oneway(*area_arr)
print ttest_ind(area_arr[0,:],area_arr[1,:])
print ttest_ind(area_arr[0,:],area_arr[2,:])
print ttest_ind(area_arr[0,:],area_arr[3,:])
print array(area_arr).shape
#print lowess(numpy.float(arange(0,199)),array(leap_arr, numpy.float)[0,0:199])
plot(transpose(leap_arr)[0:199:5,:])

replace_box()
legend(("optimal", "lowest", "highest", "control"),loc=1)
#xticks([8,16,24,32,40],('$\\textbf{25}$','$\\textbf{50}$','$\\textbf{100}$','$\\textbf{150}$','$\\textbf{200}$','$\\textbf{200}$'))
xticks([8,16,24,32,40],('50','100','150','200','250'))
#xticks([40,80,120,160,200],('50','100','150','200','250'))
xlabel("Updates (x1,000)")
ylabel("Lineage is Dominant?")


#legend.draw_frame(False)
#show()    
savefig("leap_frog_fig.svg")
#print lin[1,"parent"]
