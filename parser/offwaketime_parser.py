from model.process import Process
from model.wake_event import WakeEvent
from datetime import datetime


class ParseError(Exception):
    """Raised when a single offwaketime record cannot be parsed."""
    pass


def parse_process(line: str) -> Process:
    parts = line.split()

    if len(parts) < 3:
        raise ParseError(f"Invalid process line: '{line}'")
    try:
        pid = int(parts[-1])
    except ValueError:
        raise ParseError(f"Invalid PID in line: '{line}'")

    name = " ".join(parts[1:-1])
    return Process(pid=pid, name=name)


def split_records(lines: list[str]) -> list[list[str]]:
    """
    Split the raw offwaketime output into independent records.
    Each record begins with a 'waker:' line.
    """

    records = []
    current = []

    for line in lines:
        if line.strip().startswith("waker:"):
            if current:
                records.append(current)
            current = [line.rstrip()]
        else:
            if current:
                current.append(line.rstrip())

    if current:
        records.append(current)

    return records


def parse_record(record: list[str]) -> WakeEvent:
    """
    Parse a single offwaketime record.
    """

    waker = None
    target = None
    duration = None
    waker_stack = []
    target_stack = []

    SF_WAKER, SF_SEPERATOR, SF_TARGET, SF_DURATION = 0, 1, 2, 3
    searching_for = SF_WAKER # status of search, needed for saving the call stacks

    for i, line in enumerate(record):
        stripped = line.strip()

        if (searching_for == SF_WAKER) and stripped.startswith("waker:"):
            waker = parse_process(stripped)
            searching_for = SF_SEPERATOR

        elif searching_for == SF_SEPERATOR:
            if stripped.startswith("--"):
                searching_for = SF_TARGET
            else:
                waker_stack.append(stripped)

        elif searching_for == SF_TARGET:
            if stripped.startswith("target:"):
                target = parse_process(stripped)
                searching_for = SF_DURATION
            else:
                target_stack.append(stripped)

        elif searching_for == SF_DURATION:
            # duration is the next non-empty line after target process-line
            if stripped:
                try:
                    duration = int(stripped)
                    break
                except ValueError:
                    raise ParseError(f"Invalid duration: '{stripped}'")

    if waker is None:
        raise ParseError("Missing waker.")
    if target is None:
        raise ParseError("Missing target.")
    if duration is None:
        raise ParseError("Missing duration.")

    return WakeEvent(
        waker=waker,
        target=target,
        offcpu_time_us=duration,
        waker_stack=waker_stack,
        target_stack=target_stack,
    )


def parse_offwaketime(input_path: str, output_path: str):
    """
    input_path: for offwaketime results
    output_path: for logs like failed_records
    """
    with open(input_path) as f:
        lines = [line.rstrip() for line in f]

    records = split_records(lines)
    events: list[WakeEvent] = []
    swapper_waker_records: list[WakeEvent] = []
    failed_records = []

    for index, record in enumerate(records, start=1):
        try:
            event = parse_record(record)

        except ParseError as e:
            print(f"WARNING: Failed parsing record #{index}: {e}")

            failed_records.append({
                    "record_number": index,
                    "reason": str(e),
                    "record": record,
                })        
        
        else:
            if event.waker.name.startswith("swapper"):
                swapper_waker_records.append(event)
            else:
                events.append(event)

    with open(output_path, "w") as f:
        f.write(f"Executed at {datetime.now()}:\n\n")

    if failed_records:
        with open(output_path, "a") as f:

            f.write("#" * 80 + "\n")
            f.write("FAILED RECORDS\n")
            f.write("#" * 80 + "\n")
            f.write('\n\n')

            for failed in failed_records:
                f.write("=" * 80 + "\n")
                f.write(f"Record #{failed['record_number']}\n")
                f.write(f"Reason: {failed['reason']}\n")
                f.write("=" * 80 + "\n")
                for line in failed["record"]:
                    f.write(line + "\n")
                f.write("\n\n")

    if swapper_waker_records:
        with open(output_path, "a") as f:

            f.write("#" * 80 + "\n")
            f.write("Swapper Waker Records\n")
            f.write("#" * 80 + "\n")
            f.write('\n\n')

            for swr in swapper_waker_records:
                f.write("=" * 80 + "\n")
                f.write(f"waker: \t\t {swr.waker}\n")
                for line in swr.waker_stack:
                    f.write(line + "\n")
                f.write('-- \t\t --\n')
                for line in swr.target_stack:
                    f.write(line + "\n")
                f.write(f'target: \t\t {swr.target}\n')
                f.write(f'duration: \t\t {swr.offcpu_time_us}\n')
                f.write("=" * 80 + "\n")
                f.write("\n\n")

    print(
        f"Finished parsing. Parsed {len(events)}/{len(records)} "
        f"records successfully ({len(failed_records)} failed).")

    return events
