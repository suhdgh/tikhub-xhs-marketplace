"""TikHub 小红书接口的轻量 Python 客户端。

本模块仅封装请求与响应；每个资源接口在 ``TikHubXiaohongshuClient``
上以资源对象的形式提供。
"""

from __future__ import annotations

import json
from typing import Any, Callable, Mapping, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://api.tikhub.io"
DEFAULT_USER_AGENT = "tikhub-py/2.1.1"


ENDPOINTS = {
    "app": {
        "get_note_info": ("GET", "/api/v1/xiaohongshu/app/get_note_info"),
        "get_note_info_v2": ("GET", "/api/v1/xiaohongshu/app/get_note_info_v2"),
        "get_note_comments": ("GET", "/api/v1/xiaohongshu/app/get_note_comments"),
        "get_sub_comments": ("GET", "/api/v1/xiaohongshu/app/get_sub_comments"),
        "get_notes_by_topic": ("GET", "/api/v1/xiaohongshu/app/get_notes_by_topic"),
        "search_notes": ("GET", "/api/v1/xiaohongshu/app/search_notes"),
        "get_user_info": ("GET", "/api/v1/xiaohongshu/app/get_user_info"),
        "get_user_notes": ("GET", "/api/v1/xiaohongshu/app/get_user_notes"),
        "extract_share_info": ("GET", "/api/v1/xiaohongshu/app/extract_share_info"),
        "get_user_id_and_xsec_token": ("GET", "/api/v1/xiaohongshu/app/get_user_id_and_xsec_token"),
        "get_product_detail": ("GET", "/api/v1/xiaohongshu/app/get_product_detail"),
        "search_products": ("GET", "/api/v1/xiaohongshu/app/search_products"),
    },
    "app_v2": {
        "get_image_note_detail": ("GET", "/api/v1/xiaohongshu/app_v2/get_image_note_detail"),
        "get_video_note_detail": ("GET", "/api/v1/xiaohongshu/app_v2/get_video_note_detail"),
        "get_mixed_note_detail": ("GET", "/api/v1/xiaohongshu/app_v2/get_mixed_note_detail"),
        "get_note_comments": ("GET", "/api/v1/xiaohongshu/app_v2/get_note_comments"),
        "get_note_sub_comments": ("GET", "/api/v1/xiaohongshu/app_v2/get_note_sub_comments"),
        "get_user_info": ("GET", "/api/v1/xiaohongshu/app_v2/get_user_info"),
        "get_user_posted_notes": ("GET", "/api/v1/xiaohongshu/app_v2/get_user_posted_notes"),
        "get_user_faved_notes": ("GET", "/api/v1/xiaohongshu/app_v2/get_user_faved_notes"),
        "search_notes": ("GET", "/api/v1/xiaohongshu/app_v2/search_notes"),
        "search_users": ("GET", "/api/v1/xiaohongshu/app_v2/search_users"),
        "search_images": ("GET", "/api/v1/xiaohongshu/app_v2/search_images"),
        "search_products": ("GET", "/api/v1/xiaohongshu/app_v2/search_products"),
        "search_groups": ("GET", "/api/v1/xiaohongshu/app_v2/search_groups"),
        "get_product_detail": ("GET", "/api/v1/xiaohongshu/app_v2/get_product_detail"),
        "get_product_review_overview": ("GET", "/api/v1/xiaohongshu/app_v2/get_product_review_overview"),
        "get_product_reviews": ("GET", "/api/v1/xiaohongshu/app_v2/get_product_reviews"),
        "get_product_recommendations": ("GET", "/api/v1/xiaohongshu/app_v2/get_product_recommendations"),
        "get_topic_info": ("GET", "/api/v1/xiaohongshu/app_v2/get_topic_info"),
        "get_topic_feed": ("GET", "/api/v1/xiaohongshu/app_v2/get_topic_feed"),
        "get_creator_inspiration_feed": ("GET", "/api/v1/xiaohongshu/app_v2/get_creator_inspiration_feed"),
        "get_creator_hot_inspiration_feed": ("GET", "/api/v1/xiaohongshu/app_v2/get_creator_hot_inspiration_feed"),
    },
    "web": {
        "get_home_recommend": ("POST", "/api/v1/xiaohongshu/web/get_home_recommend"),
        "get_note_info_v2": ("GET", "/api/v1/xiaohongshu/web/get_note_info_v2"),
        "get_note_info_v4": ("GET", "/api/v1/xiaohongshu/web/get_note_info_v4"),
        "get_note_info_v5": ("POST", "/api/v1/xiaohongshu/web/get_note_info_v5"),
        "get_note_info_v7": ("GET", "/api/v1/xiaohongshu/web/get_note_info_v7"),
        "get_note_comments": ("GET", "/api/v1/xiaohongshu/web/get_note_comments"),
        "get_note_comment_replies": ("GET", "/api/v1/xiaohongshu/web/get_note_comment_replies"),
        "get_user_info": ("GET", "/api/v1/xiaohongshu/web/get_user_info"),
        "get_user_info_v2": ("GET", "/api/v1/xiaohongshu/web/get_user_info_v2"),
        "search_notes": ("GET", "/api/v1/xiaohongshu/web/search_notes"),
        "search_notes_v3": ("GET", "/api/v1/xiaohongshu/web/search_notes_v3"),
        "search_users": ("GET", "/api/v1/xiaohongshu/web/search_users"),
        "get_user_notes_v2": ("GET", "/api/v1/xiaohongshu/web/get_user_notes_v2"),
        "get_visitor_cookie": ("GET", "/api/v1/xiaohongshu/web/get_visitor_cookie"),
        "sign": ("POST", "/api/v1/xiaohongshu/web/sign"),
        "get_note_id_and_xsec_token": ("GET", "/api/v1/xiaohongshu/web/get_note_id_and_xsec_token"),
        "get_product_info": ("GET", "/api/v1/xiaohongshu/web/get_product_info"),
    },
    "web_v2": {
        "fetch_feed_notes": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_feed_notes"),
        "fetch_feed_notes_v2": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_feed_notes_v2"),
        "fetch_feed_notes_v3": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_feed_notes_v3"),
        "fetch_feed_notes_v4": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_feed_notes_v4"),
        "fetch_feed_notes_v5": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_feed_notes_v5"),
        "fetch_note_image": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_note_image"),
        "fetch_search_notes": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_search_notes"),
        "fetch_search_users": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_search_users"),
        "fetch_home_notes": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_home_notes"),
        "fetch_home_notes_app": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_home_notes_app"),
        "fetch_note_comments": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_note_comments"),
        "fetch_sub_comments": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_sub_comments"),
        "fetch_user_info": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_user_info"),
        "fetch_user_info_app": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_user_info_app"),
        "fetch_follower_list": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_follower_list"),
        "fetch_following_list": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_following_list"),
        "fetch_product_list": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_product_list"),
        "fetch_hot_list": ("GET", "/api/v1/xiaohongshu/web_v2/fetch_hot_list"),
    },
    "web_v3": {
        "fetch_note_detail": ("GET", "/api/v1/xiaohongshu/web_v3/fetch_note_detail"),
        "fetch_note_comments": ("GET", "/api/v1/xiaohongshu/web_v3/fetch_note_comments"),
        "fetch_sub_comments": ("GET", "/api/v1/xiaohongshu/web_v3/fetch_sub_comments"),
        "fetch_search_notes": ("GET", "/api/v1/xiaohongshu/web_v3/fetch_search_notes"),
        "fetch_search_users": ("GET", "/api/v1/xiaohongshu/web_v3/fetch_search_users"),
        "fetch_hot_list": ("GET", "/api/v1/xiaohongshu/web_v3/fetch_hot_list"),
        "fetch_search_suggest": ("GET", "/api/v1/xiaohongshu/web_v3/fetch_search_suggest"),
        "fetch_homefeed": ("GET", "/api/v1/xiaohongshu/web_v3/fetch_homefeed"),
        "fetch_homefeed_categories": ("GET", "/api/v1/xiaohongshu/web_v3/fetch_homefeed_categories"),
        "fetch_user_info": ("GET", "/api/v1/xiaohongshu/web_v3/fetch_user_info"),
        "fetch_user_notes": ("GET", "/api/v1/xiaohongshu/web_v3/fetch_user_notes"),
    },
}


class _BaseResource:
    def __init__(self, client: "TikHubXiaohongshuClient") -> None:
        self._client = client


class XiaohongshuAppResource(_BaseResource):
    """小红书 App V1 接口。"""


class XiaohongshuAppV2Resource(_BaseResource):
    """小红书 App V2 接口。"""


class XiaohongshuWebResource(_BaseResource):
    """小红书 Web 接口。"""


class XiaohongshuWebV2Resource(_BaseResource):
    """小红书 Web V2 接口。"""


class XiaohongshuWebV3Resource(_BaseResource):
    """小红书 Web V3 接口。"""


_RESOURCE_CLASSES = {
    "app": XiaohongshuAppResource,
    "app_v2": XiaohongshuAppV2Resource,
    "web": XiaohongshuWebResource,
    "web_v2": XiaohongshuWebV2Resource,
    "web_v3": XiaohongshuWebV3Resource,
}


def _make_endpoint_method(name: str, verb: str, path: str) -> Callable[..., Any]:
    def endpoint(self: _BaseResource, **params: Any) -> Any:
        return self._client._request(verb, path, params)

    endpoint.__name__ = name
    endpoint.__qualname__ = name
    endpoint.__doc__ = f"{verb} {path}"
    return endpoint


for _resource_name, _resource_endpoints in ENDPOINTS.items():
    _resource_class = _RESOURCE_CLASSES[_resource_name]
    for _method_name, (_verb, _path) in _resource_endpoints.items():
        setattr(_resource_class, _method_name, _make_endpoint_method(_method_name, _verb, _path))


class TikHubAPIError(RuntimeError):
    """TikHub 返回错误、网络错误或无法解析 JSON 响应时抛出的异常。"""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        url: Optional[str] = None,
        response_body: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.url = url
        self.response_body = response_body


class TikHubXiaohongshuClient:
    """调用 TikHub 小红书接口的客户端。"""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        user_agent: Optional[str] = None,
        opener: Optional[Callable[[Request, float], Any]] = None,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("api_key 不能为空")
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("base_url 不能为空")
        if timeout <= 0:
            raise ValueError("timeout 必须大于 0")
        if user_agent is not None and not isinstance(user_agent, str):
            raise ValueError("user_agent 必须是字符串")

        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent.strip() if user_agent and user_agent.strip() else DEFAULT_USER_AGENT
        self._opener = opener or self._default_opener
        self._closed = False
        self.app = XiaohongshuAppResource(self)
        self.app_v2 = XiaohongshuAppV2Resource(self)
        self.web = XiaohongshuWebResource(self)
        self.web_v2 = XiaohongshuWebV2Resource(self)
        self.web_v3 = XiaohongshuWebV3Resource(self)

    @staticmethod
    def _default_opener(request: Request, timeout: float) -> Any:
        return urlopen(request, timeout=timeout)

    def _request(self, method: str, path: str, params: Mapping[str, Any]) -> Any:
        """发送单个 GET 或 POST 请求，并返回其 JSON 响应。"""
        if self._closed:
            raise RuntimeError("TikHubXiaohongshuClient is closed")

        method = method.upper()
        if method not in {"GET", "POST"}:
            raise ValueError("仅支持 GET 和 POST 请求")

        clean_params = {key: value for key, value in params.items() if value is not None}
        url = f"{self.base_url}{path}"
        data = None
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }

        if method == "GET" and clean_params:
            url = f"{url}?{urlencode(clean_params, doseq=True)}"
        elif method == "POST":
            data = json.dumps(clean_params, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(url, data=data, headers=headers, method=method)
        return self._read_json_response(request)

    def _read_json_response(self, request: Request) -> Any:
        try:
            with self._opener(request, self.timeout) as response:
                status_code = getattr(response, "status", None) or response.getcode()
                response_body = response.read().decode("utf-8", errors="replace")
        except HTTPError as error:
            response_body = error.read().decode("utf-8", errors="replace")
            raise TikHubAPIError(
                f"TikHub 请求失败，HTTP {error.code}",
                status_code=error.code,
                url=request.full_url,
                response_body=response_body,
            ) from error
        except URLError as error:
            raise TikHubAPIError(
                f"TikHub 网络请求失败：{error.reason}",
                url=request.full_url,
            ) from error

        if not 200 <= status_code < 300:
            raise TikHubAPIError(
                f"TikHub 请求失败，HTTP {status_code}",
                status_code=status_code,
                url=request.full_url,
                response_body=response_body,
            )

        try:
            return json.loads(response_body)
        except json.JSONDecodeError as error:
            raise TikHubAPIError(
                "TikHub 响应不是有效 JSON",
                status_code=status_code,
                url=request.full_url,
                response_body=response_body,
            ) from error

    def close(self) -> None:
        """关闭客户端；重复关闭安全，关闭后不再允许发送请求。"""
        if self._closed:
            return
        self._closed = True
        close_opener = getattr(self._opener, "close", None)
        if callable(close_opener):
            close_opener()

    def __enter__(self) -> "TikHubXiaohongshuClient":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()


__all__ = ["DEFAULT_USER_AGENT", "ENDPOINTS", "TikHubAPIError", "TikHubXiaohongshuClient"]
