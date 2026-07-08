import networkx as nx

from .wake_event import WakeEvent


class WakeGraph:

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_event(self, event: WakeEvent):

        self.graph.add_node(
            event.waker.pid,
            label=event.waker.name,
            process=event.waker,
        )

        self.graph.add_node(
            event.target.pid,
            label=event.target.name,
            process=event.target,
        )

        self.graph.add_edge(
            event.waker.pid,
            event.target.pid,
            weight=event.offcpu_time_us,
        )
