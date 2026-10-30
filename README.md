# adk-qstamp

Post quantum on chain provenance for Google ADK tool calls.

The Agent Development Kit runs tools through agents but keeps no cryptographic, tamper evident record of what a tool did. This plugin fills that gap. It hooks the ADK tool callback so every tool call is fingerprinted and anchored as a post quantum Qstamp receipt on the Quantova network, while the call data stays in the process.

Only the 32 byte digest of each call leaves. The arguments and the result stay with you. An auditor who holds the record recomputes the digest and checks it against the anchored commitment, so the content stays private while the proof that the call happened in one exact form at a point in time is public and tamper evident.

## Install

```
pip install adk-qstamp
```

The ADK plugin needs the Agent Development Kit. The recorder works without it, so code that only computes and anchors digests can use the recorder on its own.

## Use

```python
from google.adk.apps import App
from adk_qstamp import QstampProvenancePlugin, QstampToolRecorder

recorder = QstampToolRecorder(
    anchor=my_anchor,
    kind="7757",
    on_receipt=lambda receipt, name: store(name, receipt),
)

app = App(name="my_app", root_agent=agent, plugins=[QstampProvenancePlugin(recorder)])
```

The anchor is supplied by you. It takes the digests for one tool call and the record kind and returns the receipts, synchronous or awaitable, so you can wire it to an in process client or to a network call to the Quantova network.

## What is anchored

By default the receipt binds the tool name and the result. Pass a project function to the recorder to choose exactly what is committed, for example to include the arguments.

## Failure handling

An audit layer must never break the tool it wraps. A failure to anchor is routed to the on_error callback and the tool call proceeds. Pass on_error to observe anchoring failures.

## Verifying

Digests and receipts verify with the reference Qstamp SDK, offline in Python with the qstamp library, or offline in Go with the qstamp-go module.

## Tests

```
python -m unittest discover -s tests
```

The suite covers the recorder end to end, the privacy property that neither the arguments nor the result reach the anchor, a deterministic digest that matches plain SHA3, synchronous and awaitable anchors, failure routing with and without an error handler, and rejection of bad construction.

## License

Apache 2.0 or MIT. See the LICENSE files.
