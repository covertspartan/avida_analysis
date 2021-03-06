#!/bin/bash

# SGE Options
#$ -S /bin/bash

##Name of the run
#$ -N Control_PNAS_2013

##Maximum amount of time the run can go
#$ -l h_rt=48:00:00

##how many to run?
##These numbers correspond directly to the random number seed
#$ -t 1-50
#$ -tc 10

##Which computes nodes to run on.
##This should never change unless Art tells you so
#$ -q wilke
#$ -pe serial 1

source ~/.basrhc

# Project Directory 
PROJ=$WORK/avida_demo
echo "Work directory: ${WORK}"

# Create Working Directory -- This NEVER CHANGES
WDIR=/state/partition1/$USER/$JOB_NAME-$JOB_ID-$SGE_TASK_ID

# Create Return Diretory -- This NEVER CHANGES
RDIR=$PROJ/$JOB_NAME-$JOB_ID-$SGE_TASK_ID

mkdir -p $WDIR
if [ ! -d $WDIR ]
then
  echo $WDIR not created
  exit
fi
cd $WDIR

# Copy Data and Config Files
cp $PROJ/config/* .

# Put your Science related commands here
# Run avida, use the TASK_ID as the random number seed
# Redirect standard io and error io to the file "run.log"
./avida -s $SGE_TASK_ID >& run.log

gzip -r *

# Copy Results Back to Home Directory
mkdir -p $RDIR
cp -r * $RDIR/. 

# Cleanup 
rm -rf $WDIR
