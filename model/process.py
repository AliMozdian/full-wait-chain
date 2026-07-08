from dataclasses import dataclass


@dataclass(frozen=True)
class Process:
    pid: int
    name: str

    def __str__(self):
        return f"{self.name} ({self.pid})"
