#!/bin/sh

# Make sure the working directory is the same as this script
DIR=`realpath -s $0`
DIR=`dirname $DIR`
cd $DIR

# Do not send input if input is empty
if [[ ! -z "$@" ]]; then
    echo "$@" > pipes/send
fi

cat pipes/receive
