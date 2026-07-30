import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN_ROOT = REPO_ROOT / "plugins" / "tikhub-xhs-mcp"


class PluginCatalogTests(unittest.TestCase):
    def test_catalog_and_plugin_manifest_expose_the_public_plugin(self):
        self.assertTrue(MARKETPLACE.is_file())
        self.assertTrue((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").is_file())
        self.assertTrue((PLUGIN_ROOT / ".mcp.json").is_file())
        marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(marketplace["name"], "tikhub-xhs-marketplace")
        self.assertEqual(marketplace["plugins"][0]["name"], "tikhub-xhs-mcp")
        self.assertEqual(
            marketplace["plugins"][0]["source"],
            {"source": "local", "path": "./plugins/tikhub-xhs-mcp"},
        )
        self.assertEqual(
            marketplace["plugins"][0]["policy"],
            {"installation": "AVAILABLE", "authentication": "ON_USE"},
        )
        self.assertEqual(manifest["name"], "tikhub-xhs-mcp")
        self.assertEqual(manifest["mcpServers"], "./.mcp.json")
