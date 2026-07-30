import asyncio
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

from mcp import Client


PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins" / "tikhub-xhs-mcp"
sys.path.insert(0, str(PLUGIN_ROOT))

from xhs_mcp_server import create_server, resolve_server_api_key


class XhsMcpServerTests(unittest.TestCase):
    def test_environment_key_is_used_and_missing_key_keeps_status_tool_available(self):
        with mock.patch.dict("os.environ", {"TIKHUB_API_KEY": "environment-test-key"}, clear=True):
            self.assertEqual(resolve_server_api_key(), "environment-test-key")

        server = create_server(api_key=None, version="1.0.0")

        async def call_status():
            async with Client(server) as client:
                return await client.call_tool("xhs_status", {})

        result = asyncio.run(call_status())
        self.assertEqual(result.structured_content["status"], "configuration_required")
        self.assertNotIn("environment-test-key", str(result))

    def test_injected_key_makes_status_ready_and_registers_exactly_nine_tools(self):
        server = create_server(api_key="test-key", version="1.0.0")

        async def inspect_server():
            async with Client(server) as client:
                status = await client.call_tool("xhs_status", {})
            tools = await server.list_tools()
            return status, tools

        status, tools = asyncio.run(inspect_server())
        self.assertEqual(status.structured_content["status"], "ready")
        self.assertEqual(
            {tool.name for tool in tools},
            {
                "xhs_search_notes",
                "xhs_get_note",
                "xhs_get_note_comments",
                "xhs_get_user",
                "xhs_get_user_notes",
                "xhs_get_hot_list",
                "xhs_list_endpoints",
                "xhs_call",
                "xhs_status",
            },
        )


if __name__ == "__main__":
    unittest.main()
