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

        with mock.patch.dict("os.environ", {}, clear=True):
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

    def test_all_tools_are_read_only_and_network_tools_expose_refresh(self):
        server = create_server(api_key="test-key", version="1.2.0")

        tools = asyncio.run(server.list_tools())
        tool_by_name = {tool.name: tool for tool in tools}

        for tool in tools:
            self.assertTrue(tool.annotations.read_only_hint, tool.name)
            self.assertFalse(tool.annotations.destructive_hint, tool.name)

        for name in {
            "xhs_search_notes",
            "xhs_get_note",
            "xhs_get_note_comments",
            "xhs_get_user",
            "xhs_get_user_notes",
            "xhs_get_hot_list",
            "xhs_call",
        }:
            self.assertIn("refresh", tool_by_name[name].input_schema["properties"], name)

        self.assertNotIn("refresh", tool_by_name["xhs_status"].input_schema["properties"])
        self.assertNotIn("refresh", tool_by_name["xhs_list_endpoints"].input_schema["properties"])


if __name__ == "__main__":
    unittest.main()
