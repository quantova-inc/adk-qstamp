# Copyright 2026 Quantova Inc
# SPDX-License-Identifier: Apache-2.0 OR MIT

from ._recorder import QstampToolRecorder

__all__ = ["QstampToolRecorder"]

try:
    from .plugin import QstampProvenancePlugin
except ImportError:
    # The plugin needs the ADK package. The recorder works without it, so a
    # consumer that only verifies or anchors can use the recorder on its own.
    pass
else:
    __all__.append("QstampProvenancePlugin")
