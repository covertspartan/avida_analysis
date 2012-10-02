from asexual_lineage import *
from avida_file_tools import *
from plot_support import *
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

def build_leap_array(files,lineage_path, lineage_string):

    new_arr = []
    sum_arr = []
    #isolate seed numbers for each dominant.dat 
#swap loop through files and range. create a large array filled with numpy 0 
# find out what the file is divisible by and place it in that index of array
# call float() on each of the values returned by count leaps and say index[i] += float()
# may need for index in array / 8 
    treatment = [[] for i in range(80)]
    sum_points = [[] for i in range(80)]
    for f in files:
        #seed number
        nums = re.findall("-[0-9]+/",f)
        num = nums[0][1:-1]
        if int(num) > 640:
            continue
        else:
            place = int(num)%80
        #construct a path to the lineage
            lin_path = lineage_path + lineage_string + num + ".dat"
    
        #create a lineage
            lin = cASexualLineage(lin_path)

        #count the number of times the domiant 
        #returns an array with a true/false value at each time index
            n, t, s = count_leaps(lin, f)
            treatment[place].append(n)
            sum_points[place].append(s)

        #complie the arrays for each treatment into one
        #trim the first and last values which are always 100%
    for replicate in treatment:
        add_array = [0 for _ in range(len(replicate[0]))]
        for individual in replicate:
            for time_point in range(len(individual)):
                add_array[time_point] += float(individual[time_point])
        #add_array = [add_array[n]/8.0 for n in range(len(add_array))]
        add_array = array(add_array)/8.0
        #print add_array
        new_arr.append(add_array[1:-1])

    #print sum(new_arr,axis=0), sum(new_arr,axis=1)
    #print sum(new_arr,axis=0).shape, sum(new_arr,axis=1).shape
    #quit()
    
    #return a sum at each time point
    return sum(new_arr,axis=0), sum(new_arr,axis=1)


treat_str = ["XtoXE-", "XtoXN-", "XtoXEstructured-", "XtoXNstructured-", "XtoXEreverted-","XtoXNreverted-", "XtoXEstructuredReversion-","XtoXNstructuredRev-"]

lineage_path = ["/Data/Jared/LocalExperiments/lineages/", "/Data/Jared/LocalExperiments/lineages/", "/Data/Jared/structure/lineages/", "/Data/Jared/structure/lineages/", "/Data/Jared/LocalExperiments/lineages/", "/Data/Jared/LocalExperiments/lineages/", "/Data/Jared/structure/lineages/", "/Data/Jared/structure/lineages/"]
lineage_string = ["lineageXE_", "lineageXN_", "lineage_struct_XE_", "lineage_struct_XN_", "lineageXErev_", "lineageXNrev_", "lineageXtoXEstructuredRev_", "lineageXtoXNstructureRev_"]

#lin = cASexualLineage("/home/covertar/Data/asex_sbt/raw_data/SBT_100sp_00005mr_250ku_lc_l50_25p_fl_fi/lineage.SBT_100sp_00005mr_250ku_lc_l50_25p_fl_fi3220500.dat")

leap_arr = []
area_arr = []

for i, s in enumerate(treat_str):
        
    #find all the treatments we have dominant.dat files for
    if s[5] != "s":
        files = find_replicates(s, "dominant.dat","/Data/Jared/LocalExperiments")
    else:
        files = find_replicates(s, "dominant.dat","/Data/Jared/structure")
    #get all of the results
    l, n = build_leap_array(files,lineage_path[i], lineage_string[i])
    leap_arr.append(l)
    area_arr.append(n)

area_arr = 99 - array(area_arr)
print area_arr.ndim, area_arr.shape
print f_oneway(*area_arr)
print ttest_ind(area_arr[0,:],area_arr[1,:])
print ttest_ind(area_arr[0,:],area_arr[2,:])
print ttest_ind(area_arr[0,:],area_arr[3,:])
rcParams['axes.color_cycle']= ['r','b','k','c']

#print lowess(numpy.float(arange(0,199)),array(leap_arr, numpy.float)[0,0:199])
fig = figure()

pl1 = fig.add_subplot(211)
ylim([0,20])
ylabel("Lineage is Dominant?")

pl2 = fig.add_subplot(212)
xlabel("Updates (x1,000)")
ylabel("Lineage is Dominant?")
xlim([0,100])
ylim([0,20])

pl1.plot(transpose(leap_arr[:4])[0:99,:])
pl2.plot(transpose(leap_arr[4:])[0:99,:])

pl1.legend(("XE", "XN", "XEstructured", "XNstructured"),loc=1)
pl2.legend(("XEreversion", "XNreversion", "XEstructuredReversion", "XNstructuredReversion"),loc=9)
replace_box()
savefig("leap_frog_line.svg")
figure()
rcParams['lines.linewidth'] = 2
data = [area_arr[i] for i in range(len(area_arr)/2)]
boxplot(data)
xticks([1,2,3,4], ['XE','XN', "XESt", "XNSt"])
ylabel("area")

savefig("leap_frog_boxplot.svg")
#xticks([8,16,24,32,40],('$\\textbf{25}$','$\\textbf{50}$','$\\textbf{100}$','$\\textbf{150}$','$\\textbf{200}$','$\\textbf{200}$'))
#xticks([8,16,24,32,40],('50','100','150','200','250'))
#xticks([40,80,120,160,200],('50','100','150','200','250'))

#legend.draw_frame(False)
#show()    
#savefig("leap_frog_figReversion.svg")
#print lin[1,"parent"]
show()
