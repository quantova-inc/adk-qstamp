# Copyright 2026 Quantova Inc
# SPDX-License-Identifier: Apache-2.0 OR MIT

from typing import Any, Optional

from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

from ._recorder import QstampToolRecorder


class QstampProvenancePlugin(BasePlugin):
    """An ADK plugin that anchors every tool call as a Qstamp receipt.

    It hooks after_tool_callback, fingerprints the call through the recorder, and
    returns None so the tool result is left unchanged. The call data stays in the
    process. Only the digest is anchored on chain.
    """

    def __init__(self, recorder: QstampToolRecorder, name: str = "qstamp_provenance"):
        super().__init__(name)
        self._recorder = recorder

    async def after_tool_callback(
        self,
        *,
        tool: BaseTool,
        tool_args: dict,
        tool_context: ToolContext,
        result: dict,
    ) -> Optional[dict]:
        await self._recorder.record(tool.name, tool_args, result)
        return None
