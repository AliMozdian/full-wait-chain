from parser.offwaketime_parser import parse_offwaketime

from analysis.analyzer import WakeAnalyzer

from model.analyzed_wake_event import AnalyzedWakeEvent
from model.wake_graph import WakeGraph

from visualization.graph import visualize


events = parse_offwaketime(
    "data/sample.out",
    "data/parser_ignored.txt",
)


analyzer = WakeAnalyzer()


analyzed_events = []

for event in events:

    analysis = analyzer.analyze(event)

    analyzed_event = AnalyzedWakeEvent(
        event=event,
        analysis=analysis,
    )

    analyzed_events.append(analyzed_event)


graph = WakeGraph()

graph.add_events(analyzed_events)


visualize(
    graph,
    output_file="data/wake_graph.html",
)
