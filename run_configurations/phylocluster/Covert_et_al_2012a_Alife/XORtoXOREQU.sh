#!/bin/bash

# SGE Options
#$ -S /bin/bash

##Name of the run
#$ -N XtoXE

##Maximum amount of time the run can go
#$ -l h_rt=72:00:00

##how many to run?
##These numbers correspond directly to the random number seed
#$ -t 1-200

##only do a few at a time -- don't want to overload the cluster
#$ -tc 20

##Which computes nodes to run on.
##This should never change unless Art tells you so
#$ -q wilke

# Create Working Directory
WDIR=/state/partition1/$USER/$JOB_NAME-$JOB_ID-$SGE_TASK_ID
mkdir -p $WDIR
if [ ! -d $WDIR ]
then
  echo $WDIR not created
  exit
fi
cd $WDIR

# Copy Data and Config Files
cp /home/jmc4939/config/* .

# Put your Science related commands here
# Run avida, use the TASK_ID as the random number seed
# Redirect standard io and error io to the file "run.log"
./avida -s $SGE_TASK_ID -c XOREQUavida.cfg -set EVENT_FILE XORcontrolRunWithPunish-469340-$(($SGE_TASK_ID%25+1))events.cfg >& run.log



# Copy Results Back to Home Directory
RDIR=$HOME/LocalExperiments/$JOB_NAME-$JOB_ID-$SGE_TASK_ID
mkdir -p $RDIR
cp -r * $RDIR/. 

# Cleanup 
rm -rf $WDIR
