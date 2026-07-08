from model.process import Process
from model.wake_event import WakeEvent


def parse_process(line: str) -> Process:
    parts = line.split()

    pid = int(parts[-1])
    name = " ".join(parts[1:-1])

    return Process(pid=pid, name=name)


def parse_offwaketime(path: str):

    with open(path) as f:
        lines = [line.rstrip() for line in f]

    events = []

    i = 0

    while i < len(lines):

        line = lines[i].strip()

        if not line.startswith("waker:"):
            i += 1
            continue

        waker = parse_process(line)

        while i < len(lines):

            i += 1

            if i >= len(lines):
                break

            current = lines[i].strip()

            if current.startswith("target:"):

                target = parse_process(current)

                i += 1

                while lines[i].strip() == "":
                    i += 1

                duration = int(lines[i].strip())

                events.append(
                    WakeEvent(
                        waker=waker,
                        target=target,
                        offcpu_time_us=duration,
                    )
                )

                break

    return events