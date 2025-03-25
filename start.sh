#!/bin/sh

# Make sure the working directory is the same as this script
DIR=`realpath -s $0`
DIR=`dirname $DIR`
cd $DIR

# $1 does not have to be passed,
#   defaults are used otherwise
python src/run.py $1
