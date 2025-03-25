#!/bin/sh

echo "$@" > pipes/send
cat pipes/receive
