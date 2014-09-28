#!/bin/bash

# sh make-graph.sh win7 60 norm-usbtablet-no-useplatformclock-2
PID=`ps aux | grep qemu | grep $1 | awk '{print $2}'`

perf record -a -g -F 1000 -p $PID sleep $2

perf script | stackcollapse-perf.pl > out.perf-folded

FILENAME=perf-qemu-kvm-$3-$2s.svg

cat out.perf-folded | flamegraph.pl > $FILENAME
