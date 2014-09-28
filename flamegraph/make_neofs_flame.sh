
PID=`ps axu | grep neofs-vms | grep volfile | awk '{print $2}'`

perf record -a -g -F 1000 -p $PID sleep 60

perf script | stackcollapse-perf.pl > out.perf-folded

FILENAME=perf-glusterfs-$1.svg

cat out.perf-folded | flamegraph.pl > $FILENAME