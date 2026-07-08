from pathlib import Path

from model.process import Process
from model.wake_event import WakeEvent


def parse_offwaketime(path: str):

    with open(path) as f:
        lines = [line.rstrip() for line in f]

    events = []

    # parser goes here

    return events

def parse_process(line: str):

    parts = line.split()

    pid = int(parts[-1])

    name = " ".join(parts[1:-1])

    return Process(pid, name)