#!/bin/bash

# $1 pid
# $2 time
# $3 output filename

FILENAME=bt-off-$3-$2s.svg

echo "sample-bt-off-cpu -t $2 -p $1 "
sample-bt-off-cpu -t $2 -p $1 -k  > a.bt

echo "stackcollapse-stap.pl a.bt > a.cbt"
stackcollapse-stap.pl a.bt > a.cbt

echo "flamegraph"
flamegraph.pl a.cbt > a.svg
mv a.svg $FILENAME
