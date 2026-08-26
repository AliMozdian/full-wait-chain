from parser.offwaketime_parser import parse_offwaketime

from model.wake_graph import WakeGraph

from visualization.graph import visualize

events = parse_offwaketime(
    "data/sample.out",
    "data/parser_ignored.txt",
)

graph = WakeGraph()

graph.add_events(events)

visualize(graph, output_file="data/wake_graph.html")
