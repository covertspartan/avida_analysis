 ####################################
 # Avida Analysis Toolkit - v 0.1   #
 # A. W. Covert III, Ph. D          #
 # All rights reserved              #
 ####################################

from avida_file_tools import *
from pylab import *

#function to grab fitness
def dom_fitness(dom_files):
    trt = [] #list to hold files

    for file in dom_files:  #snag the 4th column of data
        trt.append(get_column(file,4))

    #list of lists 
    return trt

def plot_all_treats(trt):
    m = trt.shape[1]
    for i in range(0,m):
        plot(trt[:,i],'k-')

    plot(median(trt,axis=1),'r-',linewidth=4)

    return None

def draw_x_label(str):
    #draw an axis which covers the entire bottom part of the plot
    axes([0.0,0.02,1.0,0.1])

    #turn off the box
    box()

    #turn off the ticks
    tick_params(right=False, top=False, left=False, bottom=False, labelbottom=False, labeltop=False, labelleft=False, labelright=False)

    #write the text
    text(0.5,0,str,fontsize="large",ha="center")
    return None

def replace_box(mls="k-",mlw=2):
    #get the xy limits
    #these must be set before replacing the box
    xl = xlim()
    yl = ylim()
    print xl,yl
    #remove the box
    box()
    tick_params(right=False, top=False)
    
    #draw our own smaller box
    plot([xl[0],xl[0]],[yl[0],yl[1]],mls,linewidth=mlw)
    plot([xl[0],xl[1]],[yl[0],yl[0]],mls,linewidth=mlw)
        
    return None

def heavy_plot():
    rcParams["lines.linewidth"] = 3
    rcParams["axes.linewidth"] = 3
    rcParams["font.size"] = 18
    rcParams["figure.figsize"] = [12, 8]
    rcParams["font.family"] = 'FreeSans'
    rcParams["font.weight"] = 1000
    rcParams["lines.markersize"] = 10
    return None

def latex_plot():
    rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
    rc('text', usetex=True)
    rc('mathtext',**{'default':'sf'})
    return None
    
       
def format_boxes_presentation(b):
    print b.viewkeys()
    _chg_line(b['whiskers'],'c','-',4)
    _chg_line(b['boxes'],'c','-',4)
    _chg_line(b['caps'],'c','-',4)
    _chg_line(b['fliers'],'c','None',4)

    _chg_line(b['medians'],'y','-',3)    

    replace_box(mlw=4)

    grid('off')



### helper function, do not call form outside plot support
def _chg_line(line_list,nColor = "b", nLinestyle = "-", nWidth = 1):
    for l in line_list:
        l.set_color(nColor)
        l.set_linestyle(nLinestyle)
        l.set_linewidth(nWidth)
    return None
