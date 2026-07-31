# Tools and endpoint allowlist

All data tools are read-only. They require your own `TIKHUB_API_KEY` and may incur TikHub charges. Call `xhs_status` first to inspect local configuration without making a TikHub request.

| Tool | Purpose |
| --- | --- |
| `xhs_search_notes` | Search notes by keyword and page. |
| `xhs_get_note` | Get a note by `note_id` and `xsec_token`. |
| `xhs_get_note_comments` | Get note comments, optionally continuing with `cursor`. |
| `xhs_get_user` | Get a user by `user_id` and `xsec_token`. |
| `xhs_get_user_notes` | Get a user's notes, optionally continuing with `cursor`. |
| `xhs_get_hot_list` | Get the Xiaohongshu hot list. |
| `xhs_list_endpoints` | List the local endpoint allowlist without a TikHub API request. |
| `xhs_call` | Call one allowlisted endpoint using a `resource.method` name and parameter object. |
| `xhs_status` | Report whether the key is configured without making a TikHub API request. |

## `xhs_call` example

```json
{
  "endpoint": "app_v2.search_notes",
  "params": {"keyword": "护肤", "page": 1}
}
```

`endpoint` is never a URL: use an exact `resource.method` value from the allowlist below. Parameter names and values follow the TikHub documentation for the selected endpoint. For an unfamiliar endpoint, open [TikHub Docs](https://docs.tikhub.io) and search for the complete `resource.method` name, then use the matching Xiaohongshu API entry as the parameter reference.

## Complete endpoint allowlist (79)

This table is generated from the plugin's `ENDPOINTS` registry. Regenerate it from that registry when endpoint definitions change; do not hand-edit or abbreviate the allowlist.

| Endpoint | HTTP method | TikHub path |
| --- | --- | --- |
| `app.get_note_info` | GET | `/api/v1/xiaohongshu/app/get_note_info` |
| `app.get_note_info_v2` | GET | `/api/v1/xiaohongshu/app/get_note_info_v2` |
| `app.get_note_comments` | GET | `/api/v1/xiaohongshu/app/get_note_comments` |
| `app.get_sub_comments` | GET | `/api/v1/xiaohongshu/app/get_sub_comments` |
| `app.get_notes_by_topic` | GET | `/api/v1/xiaohongshu/app/get_notes_by_topic` |
| `app.search_notes` | GET | `/api/v1/xiaohongshu/app/search_notes` |
| `app.get_user_info` | GET | `/api/v1/xiaohongshu/app/get_user_info` |
| `app.get_user_notes` | GET | `/api/v1/xiaohongshu/app/get_user_notes` |
| `app.extract_share_info` | GET | `/api/v1/xiaohongshu/app/extract_share_info` |
| `app.get_user_id_and_xsec_token` | GET | `/api/v1/xiaohongshu/app/get_user_id_and_xsec_token` |
| `app.get_product_detail` | GET | `/api/v1/xiaohongshu/app/get_product_detail` |
| `app.search_products` | GET | `/api/v1/xiaohongshu/app/search_products` |
| `app_v2.get_image_note_detail` | GET | `/api/v1/xiaohongshu/app_v2/get_image_note_detail` |
| `app_v2.get_video_note_detail` | GET | `/api/v1/xiaohongshu/app_v2/get_video_note_detail` |
| `app_v2.get_mixed_note_detail` | GET | `/api/v1/xiaohongshu/app_v2/get_mixed_note_detail` |
| `app_v2.get_note_comments` | GET | `/api/v1/xiaohongshu/app_v2/get_note_comments` |
| `app_v2.get_note_sub_comments` | GET | `/api/v1/xiaohongshu/app_v2/get_note_sub_comments` |
| `app_v2.get_user_info` | GET | `/api/v1/xiaohongshu/app_v2/get_user_info` |
| `app_v2.get_user_posted_notes` | GET | `/api/v1/xiaohongshu/app_v2/get_user_posted_notes` |
| `app_v2.get_user_faved_notes` | GET | `/api/v1/xiaohongshu/app_v2/get_user_faved_notes` |
| `app_v2.search_notes` | GET | `/api/v1/xiaohongshu/app_v2/search_notes` |
| `app_v2.search_users` | GET | `/api/v1/xiaohongshu/app_v2/search_users` |
| `app_v2.search_images` | GET | `/api/v1/xiaohongshu/app_v2/search_images` |
| `app_v2.search_products` | GET | `/api/v1/xiaohongshu/app_v2/search_products` |
| `app_v2.search_groups` | GET | `/api/v1/xiaohongshu/app_v2/search_groups` |
| `app_v2.get_product_detail` | GET | `/api/v1/xiaohongshu/app_v2/get_product_detail` |
| `app_v2.get_product_review_overview` | GET | `/api/v1/xiaohongshu/app_v2/get_product_review_overview` |
| `app_v2.get_product_reviews` | GET | `/api/v1/xiaohongshu/app_v2/get_product_reviews` |
| `app_v2.get_product_recommendations` | GET | `/api/v1/xiaohongshu/app_v2/get_product_recommendations` |
| `app_v2.get_topic_info` | GET | `/api/v1/xiaohongshu/app_v2/get_topic_info` |
| `app_v2.get_topic_feed` | GET | `/api/v1/xiaohongshu/app_v2/get_topic_feed` |
| `app_v2.get_creator_inspiration_feed` | GET | `/api/v1/xiaohongshu/app_v2/get_creator_inspiration_feed` |
| `app_v2.get_creator_hot_inspiration_feed` | GET | `/api/v1/xiaohongshu/app_v2/get_creator_hot_inspiration_feed` |
| `web.get_home_recommend` | POST | `/api/v1/xiaohongshu/web/get_home_recommend` |
| `web.get_note_info_v2` | GET | `/api/v1/xiaohongshu/web/get_note_info_v2` |
| `web.get_note_info_v4` | GET | `/api/v1/xiaohongshu/web/get_note_info_v4` |
| `web.get_note_info_v5` | POST | `/api/v1/xiaohongshu/web/get_note_info_v5` |
| `web.get_note_info_v7` | GET | `/api/v1/xiaohongshu/web/get_note_info_v7` |
| `web.get_note_comments` | GET | `/api/v1/xiaohongshu/web/get_note_comments` |
| `web.get_note_comment_replies` | GET | `/api/v1/xiaohongshu/web/get_note_comment_replies` |
| `web.get_user_info` | GET | `/api/v1/xiaohongshu/web/get_user_info` |
| `web.get_user_info_v2` | GET | `/api/v1/xiaohongshu/web/get_user_info_v2` |
| `web.search_notes` | GET | `/api/v1/xiaohongshu/web/search_notes` |
| `web.search_notes_v3` | GET | `/api/v1/xiaohongshu/web/search_notes_v3` |
| `web.search_users` | GET | `/api/v1/xiaohongshu/web/search_users` |
| `web.get_user_notes_v2` | GET | `/api/v1/xiaohongshu/web/get_user_notes_v2` |
| `web.get_visitor_cookie` | GET | `/api/v1/xiaohongshu/web/get_visitor_cookie` |
| `web.sign` | POST | `/api/v1/xiaohongshu/web/sign` |
| `web.get_note_id_and_xsec_token` | GET | `/api/v1/xiaohongshu/web/get_note_id_and_xsec_token` |
| `web.get_product_info` | GET | `/api/v1/xiaohongshu/web/get_product_info` |
| `web_v2.fetch_feed_notes` | GET | `/api/v1/xiaohongshu/web_v2/fetch_feed_notes` |
| `web_v2.fetch_feed_notes_v2` | GET | `/api/v1/xiaohongshu/web_v2/fetch_feed_notes_v2` |
| `web_v2.fetch_feed_notes_v3` | GET | `/api/v1/xiaohongshu/web_v2/fetch_feed_notes_v3` |
| `web_v2.fetch_feed_notes_v4` | GET | `/api/v1/xiaohongshu/web_v2/fetch_feed_notes_v4` |
| `web_v2.fetch_feed_notes_v5` | GET | `/api/v1/xiaohongshu/web_v2/fetch_feed_notes_v5` |
| `web_v2.fetch_note_image` | GET | `/api/v1/xiaohongshu/web_v2/fetch_note_image` |
| `web_v2.fetch_search_notes` | GET | `/api/v1/xiaohongshu/web_v2/fetch_search_notes` |
| `web_v2.fetch_search_users` | GET | `/api/v1/xiaohongshu/web_v2/fetch_search_users` |
| `web_v2.fetch_home_notes` | GET | `/api/v1/xiaohongshu/web_v2/fetch_home_notes` |
| `web_v2.fetch_home_notes_app` | GET | `/api/v1/xiaohongshu/web_v2/fetch_home_notes_app` |
| `web_v2.fetch_note_comments` | GET | `/api/v1/xiaohongshu/web_v2/fetch_note_comments` |
| `web_v2.fetch_sub_comments` | GET | `/api/v1/xiaohongshu/web_v2/fetch_sub_comments` |
| `web_v2.fetch_user_info` | GET | `/api/v1/xiaohongshu/web_v2/fetch_user_info` |
| `web_v2.fetch_user_info_app` | GET | `/api/v1/xiaohongshu/web_v2/fetch_user_info_app` |
| `web_v2.fetch_follower_list` | GET | `/api/v1/xiaohongshu/web_v2/fetch_follower_list` |
| `web_v2.fetch_following_list` | GET | `/api/v1/xiaohongshu/web_v2/fetch_following_list` |
| `web_v2.fetch_product_list` | GET | `/api/v1/xiaohongshu/web_v2/fetch_product_list` |
| `web_v2.fetch_hot_list` | GET | `/api/v1/xiaohongshu/web_v2/fetch_hot_list` |
| `web_v3.fetch_note_detail` | GET | `/api/v1/xiaohongshu/web_v3/fetch_note_detail` |
| `web_v3.fetch_note_comments` | GET | `/api/v1/xiaohongshu/web_v3/fetch_note_comments` |
| `web_v3.fetch_sub_comments` | GET | `/api/v1/xiaohongshu/web_v3/fetch_sub_comments` |
| `web_v3.fetch_search_notes` | GET | `/api/v1/xiaohongshu/web_v3/fetch_search_notes` |
| `web_v3.fetch_search_users` | GET | `/api/v1/xiaohongshu/web_v3/fetch_search_users` |
| `web_v3.fetch_hot_list` | GET | `/api/v1/xiaohongshu/web_v3/fetch_hot_list` |
| `web_v3.fetch_search_suggest` | GET | `/api/v1/xiaohongshu/web_v3/fetch_search_suggest` |
| `web_v3.fetch_homefeed` | GET | `/api/v1/xiaohongshu/web_v3/fetch_homefeed` |
| `web_v3.fetch_homefeed_categories` | GET | `/api/v1/xiaohongshu/web_v3/fetch_homefeed_categories` |
| `web_v3.fetch_user_info` | GET | `/api/v1/xiaohongshu/web_v3/fetch_user_info` |
| `web_v3.fetch_user_notes` | GET | `/api/v1/xiaohongshu/web_v3/fetch_user_notes` |
