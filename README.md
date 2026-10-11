# Full Wait Chain

A Linux off-CPU analysis and visualization project built around BCC's
`offwaketime` output.

The project parses wake-event records, models relationships between
processes, analyzes the call stacks associated with each event, and
visualizes those relationships as a directed graph. The current focus is
making the graph useful for investigation rather than simply displaying
raw off-CPU data.

> **Project status:** Active development. This README describes the
> implementation and design reached so far; it does not imply that every
> roadmap item is already implemented.

## Goals

The project aims to:

-   Turn raw `offwaketime` output into structured wake events.
-   Preserve both the waker and target call stacks for analysis.
-   Infer likely wake causes from stack evidence using extensible
    classifiers.
-   Represent process relationships as a directed graph.
-   Aggregate repeated events between the same process pair without
    discarding individual events.
-   Let users inspect the evidence behind an analysis directly from the
    visualization.

Classifier results are evidence-based diagnoses, not necessarily
definitive proof of the ultimate root cause. Confidence and supporting
evidence should remain visible.

## Current workflow

``` text
BCC offwaketime output (.out)
            |
            v
       Event parser
            |
            v
       WakeEvent objects
            |
            v
      Wake Cause Analyzer
       /             \
      v               v
 Waker-stack       Target-stack
 classification    classification
       \             /
        v           v
       WakeAnalysis
            |
            v
    Analyzed wake events
            |
            v
         WakeGraph
            |
            v
      PyVis HTML graph
```

The parser reads an `.out` file when the program runs. Events are
currently derived from that file rather than loaded from a persistent
event database. The graph is generated as HTML, and the parser also
writes `parser_ignored.txt` for records that it does not parse or
include in the graph.

## Wake-event data

A raw event contains these logical parts:

-   **Waker process:** the process or kernel task associated with waking
    the target.
-   **Waker stack:** the captured call stack on the waker side.
-   **Separator:** the `--` marker between the two stacks in the source
    format.
-   **Target stack:** the captured call stack of the task that was
    blocked.
-   **Target process:** the process that was waiting.
-   **Off-CPU duration:** the duration associated with the event.

Structured event/model objects are used after parsing so that analysis
and visualization do not need to repeatedly interpret the original text
format.

### Why `swapper` events need special treatment

Names such as `swapper/0` and `swapper/14` identify per-CPU idle tasks.
When an event names a `swapper/<cpu>` task as the waker, that name alone
usually does not explain the activity that led to the wake-up. Useful
clues may instead be in the waker stack---for example, an interrupt
handler, timer callback, work-queue scheduling path, or driver-specific
function.

The project therefore examines stack evidence and attempts to classify
the likely wake cause rather than treating `swapper` as the cause
itself. The parser's earlier special-case that discarded swapper-waker
records has been disabled so successfully parsed events can participate
in analysis and visualization.

## Wake-cause analysis

The analysis subsystem separates two questions:

1.  **Wake cause:** What activity in the waker stack most plausibly
    explains the wake-up?
2.  **Target wait:** What was the target doing while blocked, as
    suggested by the target stack?

A `WakeAnalysis` contains `wake_cause` and `target_wait`
classifications. Each classification has:

-   `category` --- a machine-readable label;
-   `description` --- a human-readable interpretation;
-   `confidence` --- the classifier's confidence level;
-   `evidence` --- stack-derived clues supporting the classification.

The analyzer is designed around a growing collection of patterns rather
than one large set of ad-hoc conditions. This makes it easier to add and
refine diagnoses as new call-stack examples are collected.

**Important:** stack patterns are heuristics. A matching function can
provide useful evidence without uniquely identifying the initiating
event. Ambiguous or incomplete stacks should receive appropriately
cautious confidence.

## Graph model and visualization

The graph is built with a directed graph model and rendered using PyVis.

-   **Nodes** represent processes.
-   **Directed edges** represent aggregated wake relationships between
    process pairs.
-   **Edge aggregates** include event count, average off-CPU duration,
    and maximum off-CPU duration.
-   **Individual analyzed events** are retained on the corresponding
    edge, so aggregation does not erase the underlying evidence.

The HTML visualization extends the default graph view:

-   Hovering over an edge shows a compact summary.
-   Clicking an edge opens a details panel.
-   The panel lists individual events, ordered by off-CPU duration, and
    lets the user expand an event to inspect its wake-cause and
    target-wait classifications, confidence, and evidence.
-   Frontend styling and interaction code are separated into assets
    rather than embedded as a large JavaScript/CSS string in the Python
    graph module.

For readability, edge labels use rounded millisecond values, while
tooltips and event details retain finer duration precision.

## Current capabilities

Based on the development and tests completed so far:

-   [x] Parse wake-event records from saved `offwaketime` output.
-   [x] Keep waker and target stacks available for analysis.
-   [x] Analyze wake-cause and target-wait information separately.
-   [x] Represent analysis results with structured classifications and
    evidence.
-   [x] Retain successfully parsed swapper-waker events instead of
    filtering them out as a category.
-   [x] Aggregate multiple events between the same process pair.
-   [x] Preserve individual analyzed events on graph edges.
-   [x] Generate an interactive PyVis HTML graph.
-   [x] Display edge summaries and detailed per-event analysis.
-   [x] Separate the details-panel JavaScript and CSS from
    `visualization/graph.py`.
-   [x] Use shorter, rounded duration labels on graph edges.

These checkboxes describe the state reached in development so far. Exact
behavior still depends on the current checked-out code and input data.

## Known limitations

### Heuristic coverage

The classifier database covers only patterns that have been implemented
and reviewed. Unseen kernel paths, driver versions, optimized symbols,
truncated stacks, and missing symbols can reduce classification quality.

### Root-cause certainty

A call stack is evidence, not always a complete causal trace. An
interrupt may trigger a callback that wakes a task, while the reason the
interrupt occurred may lie outside the captured stack. The analyzer
should distinguish an observed mechanism from a more speculative
underlying cause.

### Unparsed events

`parser_ignored.txt` records data excluded by the current parser. Some
records have missing waker stacks, a separate and difficult issue. The
long-term goal is to include as much useful data as possible without
pretending incomplete records can be analyzed with the same certainty as
complete ones.

### Input and environment dependence

The parser and classifiers depend on the format and symbols present in
the captured output. Kernel versions, drivers, symbol availability, and
workload differences may change the observed stacks.

### Visualization scale

Large captures can produce many nodes, edges, and individual events.
Filtering, search, performance, and large-detail-panel behavior should
be tested with larger traces.

## Roadmap

The following is proposed future work, not a claim that these features
are already implemented.

### 1. Expand and validate classifiers

-   Collect representative examples for non-swapper wakers as well as
    swapper-waker events.
-   Add patterns incrementally and keep them organized in a classifier
    registry or database.
-   Record the stack frames and matching rules that justify each result.
-   Add tests for known examples, ambiguous cases, missing frames, and
    negative matches.
-   Track false positives and refine confidence levels.

### 2. Improve handling of incomplete records

-   Investigate events with missing waker stacks separately from
    wake-cause classification.
-   Preserve useful target-side evidence even when waker-side evidence
    is absent.
-   Represent unavailable or inconclusive classifications explicitly.
-   Reduce unnecessary exclusions while clearly communicating inference
    limits.

### 3. Improve graph exploration

-   Add search and filters for process names, PIDs, duration, event
    count, and classification category.
-   Make high-duration or high-frequency relationships easier to
    identify.
-   Consider graph-level controls and a legend for interpreting
    classifications.
-   Test interactions when many events are attached to an edge.

### 4. Improve analysis transparency

-   Show which frames or rules contributed to a classification.
-   Distinguish observed stack evidence from inferred explanations.
-   Make low-confidence and unknown results easy to recognize.
-   Consider exporting per-event analysis to JSON or another
    machine-readable format.

### 5. Improve testing and reproducibility

-   Keep small, representative `.out` fixtures for regression tests.
-   Test parsing, classification, aggregation, and HTML generation
    separately.
-   Document required packages and supported environments based on the
    actual project setup.
-   Include a reproducible example input and expected analysis output.

### 6. Evaluate against real traces

-   Compare diagnoses with known workloads or controlled experiments.
-   Review whether each reported wake cause is supported by available
    evidence.
-   Measure classifier coverage and error rates rather than judging
    quality only from plausible examples.
-   Reprioritize future work based on the results.

## Development notes

-   **Input:** saved BCC `offwaketime` output (`.out`).
-   **Entry point:** `main.py`.
-   **Graph rendering:** `visualization/graph.py`.
-   **Models:** the project's model directory.
-   **Frontend assets:** `visualization/assets/`.
-   **Ignored records:** `parser_ignored.txt`.

Exact module names and runtime commands may evolve. Before using this
README as an installation guide, confirm the current imports,
dependencies, and invocation in the checked-out branch.

## Repository

Source code:
[AliMozdian/full-wait-chain](https://github.com/AliMozdian/full-wait-chain/tree/analysis-revolution)

------------------------------------------------------------------------

The aim is not merely to draw wake relationships, but to make each
diagnosis inspectable, evidence-backed, and progressively more reliable.
