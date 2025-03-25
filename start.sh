#!/bin/sh

# Make sure the working directory is the same as this script
DIR=`realpath -s $0`
DIR=`dirname $DIR`
cd $DIR

# Create FIFO:s if they don't exist
if [ ! -d "pipes" ]; then
    echo "Creating 'pipes' directory with FIFO pipes..."
    mkdir "pipes"
    mkfifo "pipes/send"
    mkfifo "pipes/receive"
fi

# $1 does not have to be passed,
#   defaults are used otherwise
python src/run.py $1
