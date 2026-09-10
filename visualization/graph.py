import json
from pathlib import Path

from pyvis.network import Network

from model.wake_graph import WakeGraph


def formatted_time(time_us: float) -> str:
    """
    Format off-CPU time in microseconds to a human-readable string.
    """

    time_ms = time_us / 1000

    if time_ms < 1:
        return f"{time_ms:.2f} ms"

    return f"{time_ms:.2f} ms"


def serialize_analyzed_event(analyzed_event) -> dict:
    """
    Convert an AnalyzedWakeEvent into a JSON-serializable dictionary.

    Only visualization-relevant information is included.
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
    Build the compact tooltip shown when hovering over an edge.
    """

    return (
        f"Wake count: {data['count']}<br>"
        f"Average off-CPU: "
        f"{formatted_time(data['avg_offcpu_time'])}<br>"
        f"Maximum off-CPU: "
        f"{formatted_time(data['max_offcpu_time'])}<br><br>"
        f"<b>Click edge for detailed analysis</b>"
    )


def inject_custom_ui(output_file: str):
    """
    Add a custom edge-details side panel to the generated PyVis HTML.
    """

    output_path = Path(output_file)

    html = output_path.read_text(encoding="utf-8")

    custom_ui = r"""
<style>

    #wake-details-panel {
        position: fixed;

        top: 0;
        right: 0;

        width: 420px;
        height: 100vh;

        background: white;

        border-left: 1px solid #cccccc;

        box-shadow:
            -4px 0 12px rgba(0, 0, 0, 0.15);

        z-index: 9999;

        overflow-y: auto;

        padding: 20px;

        box-sizing: border-box;

        display: none;

        font-family:
            Arial,
            sans-serif;
    }


    #wake-details-panel.visible {
        display: block;
    }


    #wake-details-close {
        position: absolute;

        top: 12px;
        right: 16px;

        border: none;

        background: none;

        font-size: 28px;

        cursor: pointer;

        color: #555555;
    }


    #wake-details-close:hover {
        color: black;
    }


    .wake-panel-title {
        margin-top: 0;

        margin-bottom: 8px;

        padding-right: 30px;

        font-size: 22px;
    }


    .wake-panel-subtitle {
        margin-bottom: 20px;

        color: #555555;

        font-size: 14px;
    }


    .wake-summary {
        background: #f5f5f5;

        border-radius: 8px;

        padding: 12px;

        margin-bottom: 20px;
    }


    .wake-summary-row {
        display: flex;

        justify-content: space-between;

        margin-bottom: 6px;
    }


    .wake-summary-row:last-child {
        margin-bottom: 0;
    }


    .wake-events-title {
        margin-bottom: 10px;

        font-size: 18px;

        font-weight: bold;
    }


    .wake-event {
        border: 1px solid #dddddd;

        border-radius: 8px;

        margin-bottom: 10px;

        background: white;
    }


    .wake-event summary {
        padding: 12px;

        cursor: pointer;

        font-weight: bold;

        list-style: none;
    }


    .wake-event summary::-webkit-details-marker {
        display: none;
    }


    .wake-event summary::before {
        content: "▶ ";

        font-size: 12px;
    }


    .wake-event[open] summary::before {
        content: "▼ ";
    }


    .wake-event-content {
        padding:
            0
            12px
            12px
            12px;
    }


    .classification {
        border-top: 1px solid #eeeeee;

        padding-top: 12px;

        margin-top: 12px;
    }


    .classification-title {
        font-weight: bold;

        margin-bottom: 8px;

        font-size: 16px;
    }


    .classification-category {
        font-weight: bold;

        margin-bottom: 6px;
    }


    .classification-description {
        margin-bottom: 8px;

        line-height: 1.4;
    }


    .confidence {
        display: inline-block;

        border-radius: 4px;

        padding:
            3px
            7px;

        font-size: 12px;

        font-weight: bold;

        margin-bottom: 8px;

        background: #eeeeee;
    }


    .evidence-title {
        margin-top: 6px;

        font-weight: bold;
    }


    .evidence-list {
        margin-top: 5px;

        padding-left: 20px;
    }


    .evidence-list li {
        margin-bottom: 4px;

        font-family:
            monospace;

        font-size: 12px;

        word-break: break-word;
    }


    .no-evidence {
        color: #777777;

        font-style: italic;

        font-size: 13px;
    }


    .empty-panel {
        color: #777777;

        margin-top: 30px;

        text-align: center;
    }

</style>


<div id="wake-details-panel">

    <button
        id="wake-details-close"
        title="Close"
    >
        ×
    </button>

    <div id="wake-details-content">

        <div class="empty-panel">

            Click an edge to inspect wake events.

        </div>

    </div>

</div>


<script>

(function () {

    const panel =
        document.getElementById(
            "wake-details-panel"
        );


    const content =
        document.getElementById(
            "wake-details-content"
        );


    const closeButton =
        document.getElementById(
            "wake-details-close"
        );


    function escapeHtml(value) {

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    function formatTime(timeUs) {

        const timeMs = timeUs / 1000;

        return timeMs.toFixed(2) + " ms";
    }


    function formatCategory(category) {

        return String(category)
            .replace(/_/g, " ");
    }


    function buildEvidence(evidence) {

        if (!evidence || evidence.length === 0) {

            return `
                <div class="no-evidence">
                    No evidence recorded.
                </div>
            `;
        }


        const items = evidence
            .map(
                item =>
                    `<li>${escapeHtml(item)}</li>`
            )
            .join("");


        return `
            <div class="evidence-title">
                Evidence
            </div>

            <ul class="evidence-list">
                ${items}
            </ul>
        `;
    }


    function buildClassification(
        title,
        classification
    ) {

        return `
            <div class="classification">

                <div class="classification-title">
                    ${escapeHtml(title)}
                </div>


                <div class="classification-category">
                    ${escapeHtml(
                        formatCategory(
                            classification.category
                        )
                    )}
                </div>


                <div class="classification-description">
                    ${escapeHtml(
                        classification.description
                    )}
                </div>


                <div class="confidence">
                    ${escapeHtml(
                        classification.confidence
                    ).toUpperCase()}
                    confidence
                </div>


                ${buildEvidence(
                    classification.evidence
                )}

            </div>
        `;
    }


    function buildEventCard(
        event,
        index
    ) {

        return `
            <details class="wake-event">

                <summary>

                    Event #${index + 1}
                    —
                    ${formatTime(event.duration_us)}

                </summary>


                <div class="wake-event-content">

                    ${buildClassification(
                        "Wake Cause",
                        event.wake_cause
                    )}


                    ${buildClassification(
                        "Target Wait",
                        event.target_wait
                    )}

                </div>

            </details>
        `;
    }


    function showEdgeDetails(edge) {

        const events =
            edge.events || [];


        const source =
            edge.source_name
            + " ("
            + edge.source_pid
            + ")";


        const target =
            edge.target_name
            + " ("
            + edge.target_pid
            + ")";


        const eventCards =
            events
                .map(
                    (event, index) =>
                        buildEventCard(
                            event,
                            index
                        )
                )
                .join("");


        content.innerHTML = `

            <h2 class="wake-panel-title">
                Wake Events
            </h2>


            <div class="wake-panel-subtitle">

                ${escapeHtml(source)}
                →
                ${escapeHtml(target)}

            </div>


            <div class="wake-summary">

                <div class="wake-summary-row">

                    <span>
                        Wake events
                    </span>

                    <strong>
                        ${edge.count}
                    </strong>

                </div>


                <div class="wake-summary-row">

                    <span>
                        Average
                    </span>

                    <strong>
                        ${formatTime(
                            edge.avg_offcpu_time
                        )}
                    </strong>

                </div>


                <div class="wake-summary-row">

                    <span>
                        Maximum
                    </span>

                    <strong>
                        ${formatTime(
                            edge.max_offcpu_time
                        )}
                    </strong>

                </div>

            </div>


            <div class="wake-events-title">

                Individual Events

            </div>


            ${eventCards}

        `;


        panel.classList.add(
            "visible"
        );
    }


    function hidePanel() {

        panel.classList.remove(
            "visible"
        );
    }


    closeButton.addEventListener(
        "click",
        hidePanel
    );


    network.on(
        "click",

        function (params) {

            if (
                params.edges.length > 0
            ) {

                const edgeId =
                    params.edges[0];


                const edge =
                    edges.get(
                        edgeId
                    );


                showEdgeDetails(
                    edge
                );

            }

            else if (
                params.nodes.length === 0
            ) {

                hidePanel();

            }

        }

    );

})();

</script>
"""

    html = html.replace(
        "</body>",
        custom_ui + "\n</body>",
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


    for node, data in nx_graph.nodes(data=True):

        process = data["process"]


        net.add_node(
            node,

            label=data["label"],

            title=(
                f"{process.name}<br>"
                f"PID: {process.pid}"
            ),
        )


    for src, dst, data in nx_graph.edges(data=True):

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


        edge_id = (
            f"{src}->{dst}"
        )


        net.add_edge(
            src,
            dst,

            id=edge_id,

            label=formatted_time(
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


    inject_custom_ui(
        output_file
    )
