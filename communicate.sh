#!/bin/sh

# Make sure the working directory is the same as this script
DIR=`realpath -s $0`
DIR=`dirname $DIR`
cd $DIR

echo "$@" > pipes/send
cat pipes/receive
