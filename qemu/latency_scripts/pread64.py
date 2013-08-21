#!/usr/bin/env python
import sys
import re
from decimal import Decimal

event_re = re.compile('([^[]+)\[\d+\]\s+([\d.]+):\s+sys_([^:]+).*')
#event_re = re.compile(r'([^[]+)\[\d+\]\s+([\d.]+):\s+sys_([^:]+).*')

class Event(object):
    def __init__(self, process, timestamp, action):
        self.process = process
        self.timestamp = timestamp
        self.action = action

    def __str__(self):
        return '%s %s %s' % (self.process, self.timestamp, self.action)

def read_events(fobj, process_filter):
    for line in fobj:
        m = event_re.match(line)
        if m is None:
            print line,
            continue
        process, timestamp, action = m.groups()
        process = process.strip()

        if not process.startswith(process_filter):
            print line,
            continue

        timestamp = Decimal(timestamp)

        yield Event(process, timestamp, action)

class LatencyStat(object):
    def __init__(self, name):
        self.name = name
        self.wait_count = 0
        self.wait_time = Decimal()
        self.wait_min = None
        self.wait_max = None

    def __str__(self):
        if self.wait_count == 0:
            avg_wait = 0
        else:
            avg_wait = self.wait_time / self.wait_count
        return '"%s" count=%d avg_wait=%s min_wait=%s max_wait=%s total_wait=%s' % (self.name, self.wait_count, avg_wait, self.wait_min, self.wait_max, self.wait_time)

    def wakeup(self, wait_duration):
        self.wait_count += 1
        self.wait_time += wait_duration

        if self.wait_min is None:
            self.wait_min = wait_duration
        elif wait_duration < self.wait_min:
            self.wait_min = wait_duration

        if self.wait_max is None:
            self.wait_max = wait_duration
        elif wait_duration > self.wait_max:
            self.wait_max = wait_duration

class Process(object):
    def __init__(self, name):
        self.wait_timestamp = None
        self.stat = LatencyStat(name)

    def handle_event(self, event):
        if event.action == 'enter':
            self.wait_timestamp = event.timestamp
        elif event.action == 'exit':
            if self.wait_timestamp:
                wait_duration = event.timestamp - self.wait_timestamp
                self.wait_timestamp = None
                self.stat.wakeup(wait_duration)

class LatencyTracker(object):
    def __init__(self):
        self.procs = {}

    def handle_event(self, event):
        if event.process not in self.procs:
            self.procs[event.process] = Process(event.process)
        proc = self.procs[event.process]
        proc.handle_event(event)

    def get_stats(self):
        for proc in self.procs.values():
            yield proc.stat

tracker = LatencyTracker()
for event in read_events(sys.stdin, 'qemu-kvm-0.12.4-'):
    tracker.handle_event(event)

for stat in tracker.get_stats():
    print stat
feedly mini