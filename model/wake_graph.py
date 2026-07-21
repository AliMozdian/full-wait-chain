import networkx as nx

from .wake_event import WakeEvent


class WakeGraph:

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_event(self, event: WakeEvent):

        self.graph.add_node(
            event.waker.pid,
            label = f"{event.waker.name}\n({event.waker.pid})",
            process=event.waker,
        )

        self.graph.add_node(
            event.target.pid,
            label = f"{event.target.name}\n({event.target.pid})",
            process=event.target,
        )

        if self.graph.has_edge(event.waker.pid, event.target.pid):

            edge = self.graph[event.waker.pid][event.target.pid]
            edge["avg_offcpu_time"] = (edge["avg_offcpu_time"] * edge["count"] +
                                       event.offcpu_time_us) / (edge["count"] + 1)
            edge["count"] += 1
            edge["max_offcpu_time"] = max(edge["max_offcpu_time"], event.offcpu_time_us)

        else:

            self.graph.add_edge(
                event.waker.pid,
                event.target.pid,
                count=1,
                avg_offcpu_time=event.offcpu_time_us,
                max_offcpu_time=event.offcpu_time_us,
            )
    

    def add_events(self, events: list[WakeEvent]):
        for event in events:
            self.add_event(event)
