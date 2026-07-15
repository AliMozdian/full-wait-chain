from parser.offwaketime_parser import parse_offwaketime

from model.wake_graph import WakeGraph

from visualization.graph import visualize

events = parse_offwaketime(
    "sample.txt",
    "failed_records.txt",
)

graph = WakeGraph()

graph.add_events(events)

visualize(graph)
