import networkx as nx

from .analyzed_wake_event import AnalyzedWakeEvent


class WakeGraph:

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_event(self, analyzed_event: AnalyzedWakeEvent):

        event = analyzed_event.event

        self.graph.add_node(
            event.waker.pid,
            label=f"{event.waker.name}\n({event.waker.pid})",
            process=event.waker,
        )

        self.graph.add_node(
            event.target.pid,
            label=f"{event.target.name}\n({event.target.pid})",
            process=event.target,
        )

        if self.graph.has_edge(
            event.waker.pid,
            event.target.pid,
        ):

            edge = self.graph[
                event.waker.pid
            ][
                event.target.pid
            ]

            edge["avg_offcpu_time"] = (
                edge["avg_offcpu_time"] * edge["count"]
                + event.offcpu_time_us
            ) / (edge["count"] + 1)

            edge["count"] += 1

            edge["max_offcpu_time"] = max(
                edge["max_offcpu_time"],
                event.offcpu_time_us,
            )

            edge["events"].append(analyzed_event)

        else:

            self.graph.add_edge(
                event.waker.pid,
                event.target.pid,

                count=1,

                avg_offcpu_time=event.offcpu_time_us,

                max_offcpu_time=event.offcpu_time_us,

                events=[analyzed_event],
            )

    def add_events(
        self,
        analyzed_events: list[AnalyzedWakeEvent],
    ):

        for analyzed_event in analyzed_events:
            self.add_event(analyzed_event)
