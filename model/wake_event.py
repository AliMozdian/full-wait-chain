from dataclasses import dataclass

from .process import Process


@dataclass
class WakeEvent:
    waker: Process
    target: Process

    offcpu_time_us: int
