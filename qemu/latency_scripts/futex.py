#!/usr/bin/env python
import sys
import re
from decimal import Decimal

futex_ops = {
    0: 'wait',
    1: 'wake',
}

class LockStat(object):
    def __init__(self, name):
        self.name = name
        self.wait_count = 0
        self.wait_time = Decimal()

    def __str__(self):
        if self.wait_count == 0:
            avg_wait = 0
        else:
            avg_wait = self.wait_time / self.wait_count
        return 'lock "%s" count=%d avg_wait=%s total_wait=%s' % (self.name, self.wait_count, avg_wait, self.wait_time)

    def wakeup(self, wait_duration):
        self.wait_count += 1
        self.wait_time += wait_duration

uaddr_locks = {
    0x89b800: LockStat('iothread'),
    0x89b9e0: LockStat('paio'),
}

# event_re = re.compile(r'([^[]+)\[(\d+)\]\s+([\d.]+):\s+sys_futex(.*)')
# enter_re = re.compile(r'\(uaddr: ([^,]+), op: ([^,]+).*\)')
# exit_re  = re.compile(r' -> (.*)')

event_re = re.compile('([^[]+)\[(\d+)\]\s+([\d.]+):\s+sys_futex(.*)')
enter_re = re.compile('\(uaddr: ([^,]+), op: ([^,]+).*\)')
exit_re  = re.compile(' -> (.*)')

class FutexEvent(object):
    def __init__(self, process, cpu, timestamp):
        self.process = process
        self.cpu = cpu
        self.timestamp = timestamp

    def __str__(self):
        return '%s [%03d] %s' % (self.process, self.cpu, self.timestamp)

class FutexEnterEvent(FutexEvent):
    def __init__(self, process, cpu, timestamp, uaddr, op):
        FutexEvent.__init__(self, process, cpu, timestamp)
        self.uaddr = uaddr
        self.op = op

    def __str__(self):
        return '%s: %s %s' % (FutexEvent.__str__(self), self.op, self.uaddr.name)

class FutexExitEvent(FutexEvent):
    def __init__(self, process, cpu, timestamp, ret):
        FutexEvent.__init__(self, process, cpu, timestamp)
        self.ret = ret

    def __str__(self):
        return '%s: exit 0x%x' % (FutexEvent.__str__(self), self.ret)

def read_futex_events(fobj, process_filter):
    for line in fobj:
        m = event_re.match(line)
        if m is None:
            continue
        process, cpu, timestamp, details = m.groups()
        process = process.strip()

        if not process.startswith(process_filter):
            continue

        cpu = int(cpu)
        timestamp = Decimal(timestamp)

        m = enter_re.match(details)
        if m is not None:
            uaddr, op = m.groups()
            uaddr = uaddr_locks[int(uaddr, 16)]
            op = futex_ops[int(op, 16) & 0x7f]
            yield FutexEnterEvent(process, cpu, timestamp, uaddr, op)
            continue

        m = exit_re.match(details)
        if m is not None:
            ret, = m.groups()
            ret = int(ret, 16)
            yield FutexExitEvent(process, cpu, timestamp, ret)
            continue

class Process(object):
    def __init__(self):
        self.wait_timestamp = None
        self.wait_uaddr = None

    def handle_event(self, event):
        if isinstance(event, FutexEnterEvent):
            if event.op == 'wait':
                self.wait_timestamp = event.timestamp
                self.wait_uaddr = event.uaddr
        else:
            if self.wait_timestamp:
                wait_duration = event.timestamp - self.wait_timestamp
                self.wait_timestamp = None
                self.wait_uaddr.wakeup(wait_duration)
                self.wait_uaddr = None

class LatencyTracker(object):
    def __init__(self):
        self.procs = {}

    def handle_event(self, event):
        if event.process not in self.procs:
            self.procs[event.process] = Process()
        proc = self.procs[event.process]
        proc.handle_event(event)

tracker = LatencyTracker()
for event in read_futex_events(sys.stdin, 'qemu-system-x86-'):
    tracker.handle_event(event)

for lock in uaddr_locks.values():
    print lock
feedly mini