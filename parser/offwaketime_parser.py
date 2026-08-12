from model.process import Process
from model.wake_event import WakeEvent



class ParseError(Exception):
    """Raised when a single offwaketime record cannot be parsed."""
    pass


def parse_process(line: str) -> Process:
    parts = line.split()

    if len(parts) == 2:
        # No name, just PID
        # return Process(pid=-1000, name="<no-name>")
        pass # will raise error in the next if
    if len(parts) < 3:
        raise ParseError(f"Invalid process line: '{line}'")
    try:
        pid = int(parts[-1])
    except ValueError:
        raise ParseError(f"Invalid PID in line: '{line}'")

    name = " ".join(parts[1:-1])
    #if name.startswith("swapper"):
    #    raise ParseError(f"Swapper Process: '{line}'")
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

    for i, line in enumerate(record):
        stripped = line.strip()

        if stripped.startswith("waker:"):
            waker = parse_process(stripped)

        elif stripped.startswith("target:"):
            target = parse_process(stripped)

            # duration is the next non-empty line
            for next_line in record[i + 1:]:
                next_line = next_line.strip()
                if not next_line:
                    continue

                try:
                    duration = int(next_line)
                    break
                except ValueError:
                    raise ParseError(f"Invalid duration: '{next_line}'")
            break

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
    )


def parse_offwaketime(input_path: str, output_path: str):
    """
    input_path: for offwaketime results
    output_path: for logs like failed_records
    """
    with open(input_path) as f:
        lines = [line.rstrip() for line in f]

    records = split_records(lines)
    events = []
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
            events.append(event)

    if failed_records:
        with open(output_path, "w") as f:

            for failed in failed_records:
                f.write("=" * 80 + "\n")
                f.write(f"Record #{failed['record_number']}\n")
                f.write(f"Reason: {failed['reason']}\n")
                f.write("=" * 80 + "\n")
                for line in failed["record"]:
                    f.write(line + "\n")
                f.write("\n\n")

    print(
        f"Finished parsing. Parsed {len(events)}/{len(records)} "
        f"records successfully ({len(failed_records)} failed).")

    return events
