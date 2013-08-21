#!/usr/bin/env python
import sys

# posix_aio_process_queue 201.878 acb=0x7f6988000b70 opaque=0x7f698802d010 type=0x1 ret=0x0 blocking_duration=0x20407

durations = []
for line in sys.stdin:
    fields = line.strip().split()
    if len(fields) != 7:
        continue

    if fields[4] != 'type=0x1':
        continue

    duration_ns = int(fields[6].split('=')[1], 16)
    durations.append(duration_ns)

if len(durations):
    avg_wait = sum(durations) / len(durations)
else:
    avg_wait = 0
print 'count=%d avg_wait=%s min_wait=%s max_wait=%s total_wait=%s' % (len(durations), avg_wait, min(durations), max(durations), sum(durations))
feedly mini