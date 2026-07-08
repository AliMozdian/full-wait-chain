from parser.offwaketime_parser import parse_offwaketime

events = parse_offwaketime("data/sample_output.txt", "data/failed_records.txt")

for event in events:
    print(event)
