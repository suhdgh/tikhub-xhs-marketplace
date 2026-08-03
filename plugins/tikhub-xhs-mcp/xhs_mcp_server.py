"""TikHub Xiaohongshu read-only MCP server entry point."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Mapping

from mcp.server import MCPServer
from mcp.types import ToolAnnotations

from xhs_mcp_service import DEFAULT_VERSION, XhsMcpService
from xiaohongshu_tikhub import TikHubXiaohongshuClient


SERVER_NAME = "TikHub XHS Data"
SERVER_INSTRUCTIONS = (
    "This is a public, read-only TikHub Xiaohongshu MCP server. "
    "Set TIKHUB_API_KEY before starting Codex to enable data calls; the key is never requested, "
    "printed, or logged by this server. xhs_call accepts only allowlisted resource.method endpoints, "
    "not arbitrary URLs. TikHub may charge for API calls."
)
NETWORK_READ_ONLY_ANNOTATIONS = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    open_world_hint=True,
)
LOCAL_READ_ONLY_ANNOTATIONS = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    open_world_hint=False,
)


def resolve_server_api_key(environment: Mapping[str, str] | None = None) -> str | None:
    """Return the configured TikHub key, or None when it is absent or blank."""
    source = os.environ if environment is None else environment
    value = source.get("TIKHUB_API_KEY", "")
    normalized = value.strip() if isinstance(value, str) else ""
    return normalized or None


def create_server(
    api_key: str | None = None,
    *,
    request_log_path: Path | None = None,
    client_factory: Callable[..., TikHubXiaohongshuClient] = TikHubXiaohongshuClient,
    version: str = DEFAULT_VERSION,
) -> MCPServer:
    """Create the local STDIO MCP server without performing a TikHub request."""
    configured_api_key = api_key if api_key is not None else resolve_server_api_key()
    service = XhsMcpService(
        configured_api_key,
        client_factory=client_factory,
        version=version,
        request_log_path=request_log_path,
    )
    server = MCPServer(
        SERVER_NAME,
        description="Public read-only TikHub Xiaohongshu data MCP server; TikHub calls may be charged.",
        instructions=SERVER_INSTRUCTIONS,
        version=version,
    )

    @server.tool(
        description=(
            "Read-only Xiaohongshu note search. Successful identical requests use a five-minute "
            "cache; pass refresh=true only when the user explicitly requests fresh data. "
            "Requires TIKHUB_API_KEY and may incur TikHub charges."
        ),
        annotations=NETWORK_READ_ONLY_ANNOTATIONS,
    )
    def xhs_search_notes(keyword: str, page: int = 1, refresh: bool = False) -> Any:
        return service.xhs_search_notes(keyword, page=page, refresh=refresh)

    @server.tool(
        description=(
            "Read-only Xiaohongshu note detail lookup. Successful identical requests use a five-minute "
            "cache; pass refresh=true only when the user explicitly requests fresh data. "
            "Requires TIKHUB_API_KEY and may incur TikHub charges."
        ),
        annotations=NETWORK_READ_ONLY_ANNOTATIONS,
    )
    def xhs_get_note(
        note_id: str,
        xsec_token: str,
        xsec_source: str = "pc_search",
        refresh: bool = False,
    ) -> Any:
        return service.xhs_get_note(
            note_id,
            xsec_token,
            xsec_source=xsec_source,
            refresh=refresh,
        )

    @server.tool(
        description=(
            "Read-only Xiaohongshu note comments lookup. Successful identical requests use a five-minute "
            "cache; pass refresh=true only when the user explicitly requests fresh data. "
            "Requires TIKHUB_API_KEY and may incur TikHub charges."
        ),
        annotations=NETWORK_READ_ONLY_ANNOTATIONS,
    )
    def xhs_get_note_comments(
        note_id: str,
        xsec_token: str,
        cursor: str | None = None,
        xsec_source: str = "pc_search",
        refresh: bool = False,
    ) -> Any:
        return service.xhs_get_note_comments(
            note_id,
            xsec_token,
            cursor=cursor,
            xsec_source=xsec_source,
            refresh=refresh,
        )

    @server.tool(
        description=(
            "Read-only Xiaohongshu user lookup. Successful identical requests use a five-minute "
            "cache; pass refresh=true only when the user explicitly requests fresh data. "
            "Requires TIKHUB_API_KEY and may incur TikHub charges."
        ),
        annotations=NETWORK_READ_ONLY_ANNOTATIONS,
    )
    def xhs_get_user(
        user_id: str,
        xsec_token: str,
        xsec_source: str = "pc_search",
        refresh: bool = False,
    ) -> Any:
        return service.xhs_get_user(
            user_id,
            xsec_token,
            xsec_source=xsec_source,
            refresh=refresh,
        )

    @server.tool(
        description=(
            "Read-only Xiaohongshu user note lookup. Successful identical requests use a five-minute "
            "cache; pass refresh=true only when the user explicitly requests fresh data. "
            "Requires TIKHUB_API_KEY and may incur TikHub charges."
        ),
        annotations=NETWORK_READ_ONLY_ANNOTATIONS,
    )
    def xhs_get_user_notes(
        user_id: str,
        xsec_token: str,
        cursor: str | None = None,
        xsec_source: str = "pc_search",
        refresh: bool = False,
    ) -> Any:
        return service.xhs_get_user_notes(
            user_id,
            xsec_token,
            cursor=cursor,
            xsec_source=xsec_source,
            refresh=refresh,
        )

    @server.tool(
        description=(
            "Read-only Xiaohongshu hot-list lookup. Successful identical requests use a five-minute "
            "cache; pass refresh=true only when the user explicitly requests fresh data. "
            "Requires TIKHUB_API_KEY and may incur TikHub charges."
        ),
        annotations=NETWORK_READ_ONLY_ANNOTATIONS,
    )
    def xhs_get_hot_list(refresh: bool = False) -> Any:
        return service.xhs_get_hot_list(refresh=refresh)

    @server.tool(
        description="List local read-only TikHub endpoint allowlist; this does not make a TikHub API call.",
        annotations=LOCAL_READ_ONLY_ANNOTATIONS,
    )
    def xhs_list_endpoints() -> dict[str, Any]:
        return service.xhs_list_endpoints()

    @server.tool(
        description=(
            "Read-only call to an allowlisted TikHub resource.method endpoint, never an arbitrary URL. "
            "Successful identical requests use a five-minute cache; pass refresh=true only when the user "
            "explicitly requests fresh data. Requires TIKHUB_API_KEY and may incur TikHub charges."
        ),
        annotations=NETWORK_READ_ONLY_ANNOTATIONS,
    )
    def xhs_call(
        endpoint: str,
        params: dict[str, Any] | None = None,
        refresh: bool = False,
    ) -> Any:
        return service.xhs_call(endpoint, params, refresh=refresh)

    @server.tool(
        description="Show local configuration status without a TikHub API call; TIKHUB_API_KEY is required for data calls.",
        annotations=LOCAL_READ_ONLY_ANNOTATIONS,
    )
    def xhs_status() -> dict[str, Any]:
        return service.xhs_status()

    return server


def main() -> None:
    """Start the MCP server over STDIO; stdout is reserved for protocol messages."""
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
