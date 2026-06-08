from __future__ import annotations

from llm_strategy_intake import (  # noqa: F401
    DEFAULT_XIAOMI_BASE_URL as DEFAULT_MIMO_BASE_URL,
    DEFAULT_XIAOMI_CHAT_URL as DEFAULT_MIMO_CHAT_URL,
    DEFAULT_XIAOMI_MODEL as DEFAULT_MIMO_MODEL,
    LLMConfig as MimoConfig,
    LLMConfigError as MimoConfigError,
    LLMResponseError as MimoResponseError,
    build_chat_url,
    build_curl_config,
    build_llm_payload as build_mimo_payload,
    escape_curl_config,
    extract_message_content,
    get_llm_status,
    merge_strategy_spec,
    normalize_execution_mode,
    normalize_field_value,
    parse_json_object,
    parse_strategy_request_with_llm,
    post_json,
    post_json_curl,
    post_json_requests,
    post_json_urllib,
    redact_secret,
)


def get_mimo_status(*args, **kwargs):
    return get_llm_status(*args, **kwargs)


def parse_strategy_request_with_mimo(*args, **kwargs):
    return parse_strategy_request_with_llm(*args, **kwargs)
