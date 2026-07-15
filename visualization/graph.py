from pyvis.network import Network

from model.wake_graph import WakeGraph


def visualize(graph: WakeGraph, output_file="wake_graph.html"):

    net = Network(
        height="900px",
        width="100%",
        directed=True,
        bgcolor="white",
        font_color="black",
    )

    nx_graph = graph.graph

    for node, data in nx_graph.nodes(data=True):

        process = data["process"]

        net.add_node(
            node,
            label=data["label"],
            title=f"""
            <b>{process.name}</b><br>
            PID: {process.pid}
            """,
        )

    for src, dst, data in nx_graph.edges(data=True):
        net.add_edge(
            src,
            dst,
            label=str(data["count"]),
            title=f"""
            Wake count: {data['count']}<br>
            Total offcpu: {data['total_offcpu_time']} us
            Max offcpu: {data['max_offcpu_time']} us
            """,
        )

    net.write_html(output_file, notebook=False)
