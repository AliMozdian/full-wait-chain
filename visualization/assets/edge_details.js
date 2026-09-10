(function () {

    createDetailsPanel();


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


    function createDetailsPanel() {

        const panel = document.createElement(
            "div"
        );

        panel.id =
            "wake-details-panel";


        panel.innerHTML = `

            <button
                id="wake-details-close"
                title="Close"
            >
                ×
            </button>


            <div id="wake-details-content">

                <div class="empty-panel">

                    Click an edge to inspect
                    wake events.

                </div>

            </div>

        `;


        document.body.appendChild(
            panel
        );
    }


    function escapeHtml(value) {

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    function formatTime(timeUs) {

        const timeMs =
            timeUs / 1000;

        return (
            timeMs.toFixed(2)
            + " ms"
        );
    }


    function formatCategory(category) {

        return String(category)
            .replace(/_/g, " ");
    }


    function buildEvidence(evidence) {

        if (
            !evidence
            ||
            evidence.length === 0
        ) {

            return `

                <div class="no-evidence">

                    No evidence recorded.

                </div>

            `;
        }


        const items = evidence
            .map(

                item =>

                    `<li>${
                        escapeHtml(item)
                    }</li>`

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


                <div
                    class="classification-category"
                >

                    ${escapeHtml(

                        formatCategory(
                            classification.category
                        )

                    )}

                </div>


                <div
                    class="classification-description"
                >

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

                    ${formatTime(
                        event.duration_us
                    )}

                </summary>


                <div
                    class="wake-event-content"
                >


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
                    edges.get(edgeId);


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
