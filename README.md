# TikHub XHS Marketplace

This repository is an independent GitHub marketplace for a read-only TikHub Xiaohongshu (XHS) MCP plugin. It is maintained at [suhdgh/tikhub-xhs-marketplace](https://github.com/suhdgh/tikhub-xhs-marketplace); it is not the OpenAI official curated marketplace.

## Add the marketplace in Codex

1. In Codex, open the **Add Plugin Marketplace** dialog.
2. Enter `suhdgh/tikhub-xhs-marketplace` as the GitHub marketplace source.
3. Select and install the `tikhub-xhs-mcp` plugin.
4. Follow the plugin documentation to configure your own `TIKHUB_API_KEY`, then restart Codex.

The plugin only makes read-only calls to TikHub's Xiaohongshu endpoints. TikHub API calls may incur charges under your TikHub account, so review TikHub's current documentation and plan before making calls. You must comply with the current [TikHub User Terms](https://docs.tikhub.io/5508541m0) and the applicable Xiaohongshu platform terms when using this plugin.

See [the plugin README](plugins/tikhub-xhs-mcp/README.md) for setup and usage.
