"""小红书 TikHub MCP 的可测试服务层。"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from xiaohongshu_tikhub import ENDPOINTS, TikHubAPIError, TikHubXiaohongshuClient


DEFAULT_VERSION = "1.0.0"


class XhsMcpToolError(RuntimeError):
    """对 Codex 可见的、已经脱敏的接口调用错误。"""


def redact_sensitive_text(value: object, *, api_key: str = "") -> str:
    """从日志和异常文本中移除认证信息。"""
    text = str(value)
    if api_key:
        text = text.replace(api_key, "[REDACTED]")
    patterns = (
        r"(?i)(authorization\s*[\":=]+\s*bearer\s+)[^\s\",}]+",
        r'(?i)(["\']?(?:api[_-]?key|token|tikhub_api_key)["\']?\s*[:=]\s*["\']?)[^\s\",}\']+',
    )
    for pattern in patterns:
        text = re.sub(pattern, r"\1[REDACTED]", text)
    return text


class XhsMcpService:
    """将现有 TikHub 客户端转换为适合 MCP 调用的只读服务。"""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        client_factory: Callable[..., TikHubXiaohongshuClient] = TikHubXiaohongshuClient,
        version: str = DEFAULT_VERSION,
        request_log_path: Path | None = None,
    ) -> None:
        self._api_key = api_key.strip() if isinstance(api_key, str) and api_key.strip() else None
        self._client_factory = client_factory
        self._version = version
        self._request_log_path = Path(request_log_path) if request_log_path else None

    def xhs_status(self) -> dict[str, Any]:
        """返回本地 MCP 状态；不会调用 TikHub。"""
        if not self._api_key:
            return {
                "status": "configuration_required",
                "version": self._version,
                "endpoint_count": sum(len(endpoints) for endpoints in ENDPOINTS.values()),
                "api_key_configured": False,
                "configuration_hint": "请设置环境变量 TIKHUB_API_KEY 后重新启动 Codex。",
            }
        return {
            "status": "ready",
            "version": self._version,
            "endpoint_count": sum(len(endpoints) for endpoints in ENDPOINTS.values()),
            "api_key_configured": True,
        }

    def xhs_list_endpoints(self) -> dict[str, Any]:
        """列出由本地客户端白名单登记的全部小红书接口。"""
        endpoints = [
            {
                "name": f"{resource_name}.{method_name}",
                "http_method": http_method,
                "path": path,
            }
            for resource_name, resource_endpoints in ENDPOINTS.items()
            for method_name, (http_method, path) in resource_endpoints.items()
        ]
        return {
            "endpoint_count": len(endpoints),
            "resources": {
                resource_name: len(resource_endpoints)
                for resource_name, resource_endpoints in ENDPOINTS.items()
            },
            "endpoints": endpoints,
        }

    def xhs_call(self, endpoint: str, params: Mapping[str, Any] | None = None) -> Any:
        """调用白名单中的一个接口，``endpoint`` 使用 ``资源.方法`` 形式。"""
        resource_name, method_name = self._parse_endpoint_name(endpoint)
        call_params = self._normalize_params(params)
        api_key = self._require_api_key()
        try:
            with self._client_factory(api_key) as client:
                resource = getattr(client, resource_name)
                method = getattr(resource, method_name)
                result = method(**call_params)
        except TikHubAPIError as error:
            self._write_request_log(endpoint, "error", status_code=error.status_code)
            raise XhsMcpToolError(self._format_api_error(error)) from error
        except Exception as error:
            self._write_request_log(endpoint, "error")
            safe_message = redact_sensitive_text(str(error), api_key=self._api_key)
            raise XhsMcpToolError(f"TikHub 调用发生本地错误：{safe_message}") from error
        self._write_request_log(endpoint, "success")
        return result

    def _require_api_key(self) -> str:
        if not self._api_key:
            raise XhsMcpToolError(
                "未配置 TikHub API Key：请在启动 Codex 前设置环境变量 TIKHUB_API_KEY，然后新建对话后重试。"
            )
        return self._api_key

    def xhs_search_notes(self, keyword: str, *, page: int = 1) -> Any:
        """按关键词搜索小红书笔记。"""
        return self.xhs_call("app_v2.search_notes", {"keyword": keyword, "page": page})

    def xhs_get_note(
        self,
        note_id: str,
        xsec_token: str,
        *,
        xsec_source: str = "pc_search",
    ) -> Any:
        """查询一篇笔记的详情。"""
        return self.xhs_call(
            "web_v3.fetch_note_detail",
            {
                "note_id": note_id,
                "xsec_token": xsec_token,
                "xsec_source": xsec_source,
            },
        )

    def xhs_get_note_comments(
        self,
        note_id: str,
        xsec_token: str,
        *,
        cursor: str | None = None,
        xsec_source: str = "pc_search",
    ) -> Any:
        """查询一篇笔记的评论。"""
        return self.xhs_call(
            "web_v3.fetch_note_comments",
            {
                "note_id": note_id,
                "xsec_token": xsec_token,
                "xsec_source": xsec_source,
                "cursor": cursor,
            },
        )

    def xhs_get_user(
        self,
        user_id: str,
        xsec_token: str,
        *,
        xsec_source: str = "pc_search",
    ) -> Any:
        """查询小红书用户资料。"""
        return self.xhs_call(
            "web_v3.fetch_user_info",
            {
                "user_id": user_id,
                "xsec_token": xsec_token,
                "xsec_source": xsec_source,
            },
        )

    def xhs_get_user_notes(
        self,
        user_id: str,
        xsec_token: str,
        *,
        cursor: str | None = None,
        xsec_source: str = "pc_search",
    ) -> Any:
        """查询一个用户发布的笔记。"""
        return self.xhs_call(
            "web_v3.fetch_user_notes",
            {
                "user_id": user_id,
                "xsec_token": xsec_token,
                "xsec_source": xsec_source,
                "cursor": cursor,
            },
        )

    def xhs_get_hot_list(self) -> Any:
        """查询小红书热榜。"""
        return self.xhs_call("web_v3.fetch_hot_list")

    @staticmethod
    def _normalize_params(params: Mapping[str, Any] | None) -> dict[str, Any]:
        if params is None:
            return {}
        if not isinstance(params, Mapping):
            raise ValueError("params 必须是 JSON 对象")
        return dict(params)

    @staticmethod
    def _parse_endpoint_name(endpoint: str) -> tuple[str, str]:
        if not isinstance(endpoint, str) or endpoint.count(".") != 1:
            raise XhsMcpToolError("endpoint 必须使用“资源.方法”格式")
        resource_name, method_name = endpoint.split(".", maxsplit=1)
        if not resource_name or not method_name or method_name not in ENDPOINTS.get(resource_name, {}):
            raise XhsMcpToolError(f"未登记的小红书接口：{endpoint}")
        return resource_name, method_name

    def _format_api_error(self, error: TikHubAPIError) -> str:
        status_hints = {
            401: "鉴权失败：请检查您自己的 TikHub API Key 是否正确或已失效。",
            402: "余额不足或该接口需要付费：请在 TikHub 后台充值或确认接口套餐。",
            403: "访问被拒绝：请勿连续重试，请联系 TikHub 支持确认访问限制。",
            404: "接口不存在：请更新此插件后重试。",
        }
        hint = status_hints.get(error.status_code, "请检查网络、接口参数或 TikHub 服务状态后重试。")
        safe_message = redact_sensitive_text(str(error), api_key=self._api_key)
        status = f"HTTP {error.status_code}" if error.status_code else "网络或响应错误"
        return f"TikHub 调用失败（{status}）：{hint} 原始信息：{safe_message}"

    def _write_request_log(
        self,
        endpoint: str,
        status: str,
        *,
        status_code: int | None = None,
    ) -> None:
        """最佳努力写入无参数、无认证信息的本地审计摘要。"""
        if self._request_log_path is None:
            return
        record: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "endpoint": endpoint,
            "status": status,
        }
        if status_code is not None:
            record["status_code"] = status_code
        try:
            self._request_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self._request_log_path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError:
            # 日志不可写时，查询结果仍应正常返回。
            return
