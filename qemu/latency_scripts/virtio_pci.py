#!/usr/bin/env python
import sys
from decimal import Decimal

def reset():
    global expected_event, next_event, last_timestamp
    expected_event = 'vp_notify'
    next_event     = 'vring_interrupt'
    last_timestamp = None

reset()
durations = []
for line in sys.stdin:
    fields = line.strip().split()
    timestamp = Decimal(fields[2].rstrip(':'))
    event = fields[3].rstrip(':')

    if event != expected_event:
        reset()
        continue

    if last_timestamp is None:
        last_timestamp = timestamp
    else:
        if timestamp - last_timestamp < Decimal(0):
            print timestamp, last_timestamp
        durations.append(timestamp - last_timestamp)
        last_timestamp = None

    expected_event, next_event = next_event, expected_event

print "mean latency (s):", sum(durations) / len(durations)
print "min latency (s):", min(durations)
print "max latency (s):", max(durations)