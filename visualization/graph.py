from pyvis.network import Network

from model.wake_graph import WakeGraph


def formatted_time(time_us: int) -> str:
    """
    Format offcpu time in microseconds to a human-readable string.
    """
    time_us /= 1000  # Convert to milliseconds
    if time_us < 1:
        return f"{round(time_us, 1)} ms"
    else:
        return f"{round(time_us)} ms"

def visualize(graph: WakeGraph, output_file="wake_graph.html"):

    net = Network(
        height="900px",
        width="100%",
        directed=True,
        notebook=False,
        #select_menu=True,
        #filter_menu=True,
        bgcolor="white",
        font_color="black",
    )

    nx_graph = graph.graph

    for node, data in nx_graph.nodes(data=True):

        process = data["process"]

        net.add_node(
            node,
            label=data["label"],
            title=f"""{process.name}
            PID: {process.pid}
            """,
        )

    for src, dst, data in nx_graph.edges(data=True):
        net.add_edge(
            src,
            dst,
            label=formatted_time(data["max_offcpu_time"]),
            title=f"""Wake count: {data['count']}
            Average offcpu: {formatted_time(data['avg_offcpu_time'])}
            Max offcpu: {formatted_time(data['max_offcpu_time'])}
            """,
        )

    net.write_html(output_file, notebook=False)
