#!/bin/bash

# $1 pid
# $2 time
# $3 output filename

FILENAME=bt-on-$3-$2s.svg

echo "sample-bt-on-cpu -t $2 -p $1 "
# sample-bt -u -t $2 -p $1 > a.bt
sample-bt -k -t $2 -p $1 > a.bt

echo "stackcollapse-stap.pl a.bt > a.cbt"
stackcollapse-stap.pl a.bt > a.cbt

echo "flamegraph"
flamegraph.pl a.cbt > a.svg
mv a.svg $FILENAME
