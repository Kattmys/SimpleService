#!/bin/sh

# Make sure the working directory is the same as this script
DIR=`realpath -s $0`
DIR=`dirname $DIR`
cd $DIR

# Check if input is empty
if [[ -z "$@" ]]; then
    echo "No input. Use command 'help' for a list of commands."
    exit
fi

echo "$@" > pipes/send
cat pipes/receive
