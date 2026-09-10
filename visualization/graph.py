import json
from pathlib import Path

from pyvis.network import Network

from model.wake_graph import WakeGraph


ASSETS_DIR = Path(__file__).parent / "assets"


def format_detailed_time(time_us: float) -> str:
    """
    Format time for tooltips and detailed views.
    """

    time_ms = time_us / 1000

    return f"{time_ms:.2f} ms"


def format_edge_time(time_us: float) -> str:
    """
    Format time for graph edge labels.

    Edge labels use 1 ms precision to keep the graph readable.
    """

    time_ms = time_us / 1000

    return f"{time_ms:.0f} ms"


def serialize_analyzed_event(analyzed_event) -> dict:
    """
    Convert an AnalyzedWakeEvent into JSON-compatible data.
    """

    event = analyzed_event.event
    analysis = analyzed_event.analysis

    return {
        "duration_us": event.offcpu_time_us,

        "wake_cause": {
            "category": analysis.wake_cause.category,
            "description": analysis.wake_cause.description,
            "confidence": analysis.wake_cause.confidence.value,
            "evidence": analysis.wake_cause.evidence,
        },

        "target_wait": {
            "category": analysis.target_wait.category,
            "description": analysis.target_wait.description,
            "confidence": analysis.target_wait.confidence.value,
            "evidence": analysis.target_wait.evidence,
        },
    }


def build_edge_title(data: dict) -> str:
    """
    Build the edge hover tooltip.
    """

    return (
        f"Wake count: {data['count']}\n"
        f"Average off-CPU: "
        f"{format_detailed_time(data['avg_offcpu_time'])}\n"
        f"Maximum off-CPU: "
        f"{format_detailed_time(data['max_offcpu_time'])}\n\n"
        f"Click edge for detailed analysis"
    )


def load_asset(filename: str) -> str:
    """
    Load a visualization asset from the assets directory.
    """

    asset_path = ASSETS_DIR / filename

    return asset_path.read_text(
        encoding="utf-8",
    )


def inject_visualization_assets(
    output_file: str,
):
    """
    Inject custom CSS and JavaScript into the generated HTML.
    """

    output_path = Path(output_file)

    html = output_path.read_text(
        encoding="utf-8",
    )

    css = load_asset(
        "edge_details.css",
    )

    javascript = load_asset(
        "edge_details.js",
    )

    css_tag = (
        "<style>\n"
        f"{css}\n"
        "</style>"
    )

    javascript_tag = (
        "<script>\n"
        f"{javascript}\n"
        "</script>"
    )

    html = html.replace(
        "</head>",
        f"{css_tag}\n</head>",
    )

    html = html.replace(
        "</body>",
        f"{javascript_tag}\n</body>",
    )

    output_path.write_text(
        html,
        encoding="utf-8",
    )


def visualize(
    graph: WakeGraph,
    output_file="wake_graph.html",
):

    net = Network(
        height="900px",
        width="100%",
        directed=True,
        bgcolor="white",
        font_color="black",
    )

    nx_graph = graph.graph

    for node, data in nx_graph.nodes(
        data=True,
    ):

        process = data["process"]

        net.add_node(
            node,

            label=data["label"],

            title=(
                f"{process.name}\n"
                f"PID: {process.pid}"
            ),
        )

    for src, dst, data in nx_graph.edges(
        data=True,
    ):

        sorted_events = sorted(
            data["events"],

            key=lambda analyzed_event:
                analyzed_event.event.offcpu_time_us,

            reverse=True,
        )

        serialized_events = [

            serialize_analyzed_event(
                analyzed_event
            )

            for analyzed_event
            in sorted_events

        ]

        source_process = nx_graph.nodes[src][
            "process"
        ]

        target_process = nx_graph.nodes[dst][
            "process"
        ]

        edge_id = f"{src}->{dst}"

        net.add_edge(
            src,
            dst,

            id=edge_id,

            label=format_edge_time(
                data["max_offcpu_time"]
            ),

            title=build_edge_title(
                data
            ),

            events=serialized_events,

            count=data["count"],

            avg_offcpu_time=
                data["avg_offcpu_time"],

            max_offcpu_time=
                data["max_offcpu_time"],

            source_name=
                source_process.name,

            source_pid=
                source_process.pid,

            target_name=
                target_process.name,

            target_pid=
                target_process.pid,
        )

    net.write_html(
        output_file,
        notebook=False,
    )

    inject_visualization_assets(
        output_file,
    )
