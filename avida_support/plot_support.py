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

       
