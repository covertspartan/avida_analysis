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
        if int(num) >= 640:
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

    print len(sum_points)
    print len(sum_points[0])
    
    #average within each random seed
    avg_arr = []
    for rep in sum_points:
        avg_arr.append(sum(rep)/8.0)

    #boxplot(99-array(avg_arr))
    
    return array(avg_arr), 99-array(avg_arr)

    #return sum(new_arr,axis=0), sum(new_arr,axis=1)


treat_str = ["XtoXE-", "XtoXN-", "XtoXEstructured-", "XtoXNstructured-"]

lineage_path = ["/Data/Jared/LocalExperiments/lineages/", "/Data/Jared/LocalExperiments/lineages/", "/Data/Jared/structure/lineages/", "/Data/Jared/structure/lineages/"]
lineage_string = ["lineageXE_", "lineageXN_", "lineage_struct_XE_", "lineage_struct_XN_"]

leap_arr = []
area_arr = []

for i, s in enumerate(treat_str):
    print i+1, s[:-1]
    #find all the treatments we have dominant.dat files for
    if (i==0) or (i==1):
        files = find_replicates(s, "dominant.dat","/Data/Jared/LocalExperiments")
    elif (i==2) or (i==3):
        files = find_replicates(s, "dominant.dat","/Data/Jared/structure")
    else:
        files = find_replicates(s, "dominant.dat","/Data/Jared/structure")
    #get all of the results
    l, n = build_leap_array(files,lineage_path[i], lineage_string[i])
    leap_arr.append(l)
    area_arr.append(n)


fig2 = figure()
rcParams['lines.linewidth'] = 2
data = area_arr

pl1 = fig2.add_subplot(121)
pl1.boxplot([data[0],data[2]])
xticks([1,2],['XE','XEStructured'])
ylabel("Leapfrog Events", horizontalalignment='center' )
ylim(88,100)
replace_box()

pl2 = fig2.add_subplot(122)
pl2.boxplot([data[1],data[3]])
xticks([1,2],['XN','XNStructured'])
ylim(88,100)
replace_box()

savefig("leap_frog_boxplotXEN.svg")
show()
#xticks([8,16,24,32,40],('$\\textbf{25}$','$\\textbf{50}$','$\\textbf{100}$','$\\textbf{150}$','$\\textbf{200}$','$\\textbf{200}$'))
#xticks([8,16,24,32,40],('50','100','150','200','250'))
#xticks([40,80,120,160,200],('50','100','150','200','250'))

#legend.draw_frame(False)
#show()    
#savefig("leap_frog_figReversion.svg")
#print lin[1,"parent"]

