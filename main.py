from parser.offwaketime_parser import parse_offwaketime

events = parse_offwaketime("data/sample_output.txt")

for event in events:
    print(event)
