from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from strategy_intake import RISK_DISCLOSURE, parse_strategy_request


DEFAULT_MIMO_BASE_URL = "https://token-plan-sgp.xiaomimimo.com/v1"
DEFAULT_MIMO_CHAT_URL = f"{DEFAULT_MIMO_BASE_URL}/chat/completions"
DEFAULT_MIMO_MODEL = "mimo-v2.5"

STRATEGY_FIELDS = (
    "original_request",
    "market",
    "themes",
    "horizon_days",
    "candidate_rules",
    "risk_filters",
    "user_preferences",
    "output",
    "execution_mode",
    "requires_agent",
    "assumptions",
    "clarification_questions",
    "prohibited_actions",
    "risk_disclosure",
)

LIST_FIELDS = {
    "themes",
    "candidate_rules",
    "risk_filters",
    "assumptions",
    "clarification_questions",
    "prohibited_actions",
}

Transport = Callable[[str, dict[str, str], dict[str, Any], float], dict[str, Any]]


class MimoConfigError(RuntimeError):
    """Raised when the local runtime is missing MiMo credentials."""


class MimoResponseError(RuntimeError):
    """Raised when MiMo cannot return a valid StrategySpec payload."""


@dataclass(frozen=True)
class MimoConfig:
    api_key: str
    chat_url: str = DEFAULT_MIMO_CHAT_URL
    model: str = DEFAULT_MIMO_MODEL
    timeout_seconds: float = 45.0

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "MimoConfig":
        env = os.environ if environ is None else environ
        api_key = (env.get("XIAOMI_API_KEY") or env.get("MIMO_API_KEY") or "").strip()
        if not api_key:
            raise MimoConfigError("Missing XIAOMI_API_KEY or MIMO_API_KEY in the local environment.")

        chat_url = (env.get("XIAOMI_CHAT_COMPLETIONS_URL") or env.get("MIMO_CHAT_COMPLETIONS_URL") or "").strip()
        if not chat_url:
            base_url = (env.get("XIAOMI_BASE_URL") or env.get("MIMO_BASE_URL") or DEFAULT_MIMO_BASE_URL).strip()
            chat_url = build_chat_url(base_url)

        model = (env.get("XIAOMI_MODEL") or env.get("MIMO_MODEL") or DEFAULT_MIMO_MODEL).strip()
        return cls(api_key=api_key, chat_url=chat_url, model=model)


def get_mimo_status(environ: Mapping[str, str] | None = None) -> dict[str, Any]:
    env = os.environ if environ is None else environ
    try:
        config = MimoConfig.from_env(env)
    except MimoConfigError as exc:
        base_url = (env.get("XIAOMI_BASE_URL") or env.get("MIMO_BASE_URL") or DEFAULT_MIMO_BASE_URL).strip()
        return {
            "configured": False,
            "api_key": "missing",
            "model": (env.get("XIAOMI_MODEL") or env.get("MIMO_MODEL") or DEFAULT_MIMO_MODEL).strip(),
            "chat_url": (env.get("XIAOMI_CHAT_COMPLETIONS_URL") or env.get("MIMO_CHAT_COMPLETIONS_URL") or build_chat_url(base_url)).strip(),
            "error": str(exc),
        }

    return {
        "configured": True,
        "api_key": "present",
        "model": config.model,
        "chat_url": config.chat_url,
    }


def parse_strategy_request_with_mimo(
    request: str,
    user_profile: dict[str, Any] | None = None,
    config: MimoConfig | None = None,
    transport: Transport | None = None,
) -> dict[str, Any]:
    baseline_spec = parse_strategy_request(request, user_profile=user_profile).to_dict()
    mimo_config = config or MimoConfig.from_env()
    payload = build_mimo_payload(request=request, baseline_spec=baseline_spec, model=mimo_config.model)
    headers = {
        "api-key": mimo_config.api_key,
        "Authorization": f"Bearer {mimo_config.api_key}",
        "Content-Type": "application/json",
    }

    response = (transport or post_json)(mimo_config.chat_url, headers, payload, mimo_config.timeout_seconds)
    content = extract_message_content(response)
    model_spec = parse_json_object(content)
    strategy_spec = merge_strategy_spec(baseline_spec, model_spec)

    return {
        "provider": "mimo",
        "model": mimo_config.model,
        "strategy_spec": strategy_spec,
        "baseline_spec": baseline_spec,
        "usage": response.get("usage", {}),
    }


def build_mimo_payload(request: str, baseline_spec: dict[str, Any], model: str) -> dict[str, Any]:
    system_prompt = (
        "你是一个投研 Agent 的策略入口解析器。"
        "你的任务是把用户自然语言策略描述转换为 StrategySpec JSON。"
        "只返回一个 JSON 对象，不要 Markdown，不要解释过程。"
        "不得输出个股推荐、买卖建议、收益承诺或自动交易动作。"
        "如果用户意图不完整或不安全，用 clarification_questions 和 prohibited_actions 表达边界。"
    )
    user_prompt = {
        "user_request": request,
        "baseline_strategy_spec": baseline_spec,
        "schema_fields": list(STRATEGY_FIELDS),
        "field_rules": {
            "market": "目标市场，例如 A股、港股、美股；不确定时保留基线或写未指定。",
            "themes": "行业、板块或主题数组，不要放股票代码或个股名称。",
            "horizon_days": "时间窗口天数；无法判断时为 null。",
            "candidate_rules": "候选池筛选条件数组。",
            "risk_filters": "风险过滤条件数组。",
            "execution_mode": "只能是 workflow、agent、needs_clarification。",
            "requires_agent": "当 execution_mode 为 agent 时为 true，否则为 false。",
            "clarification_questions": "缺信息或不安全时需要向用户追问的问题。",
            "prohibited_actions": "只使用 guaranteed_return、certain_price_move、auto_trade、real_trade 等边界标签。",
        },
        "output_contract": "返回完整 StrategySpec JSON 对象，字段名必须和 schema_fields 一致。",
    }
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)},
        ],
        "max_completion_tokens": 1400,
        "temperature": 0.1,
        "top_p": 0.9,
        "stream": False,
        "thinking": {"type": "disabled"},
    }


def post_json(url: str, headers: dict[str, str], payload: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    try:
        return post_json_requests(url, headers, payload, timeout_seconds)
    except ImportError:
        return post_json_urllib(url, headers, payload, timeout_seconds)
    except MimoResponseError as exc:
        if "MiMo request failed:" not in str(exc):
            raise
        try:
            return post_json_curl(url, headers, payload, timeout_seconds)
        except MimoResponseError:
            raise


def post_json_requests(url: str, headers: dict[str, str], payload: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    import requests

    api_key = headers.get("api-key", "")
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)
    except requests.RequestException as exc:
        raise MimoResponseError(f"MiMo request failed: {exc}") from exc

    if response.status_code >= 400:
        raise MimoResponseError(f"MiMo HTTP {response.status_code}: {redact_secret(response.text, api_key)}")

    try:
        return response.json()
    except ValueError as exc:
        raise MimoResponseError("MiMo returned non-JSON HTTP response.") from exc


def post_json_curl(url: str, headers: dict[str, str], payload: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        raise MimoResponseError("MiMo request failed and curl fallback is unavailable.")

    api_key = headers.get("api-key", "")
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as body_file:
        json.dump(payload, body_file, ensure_ascii=False)
        body_path = Path(body_file.name)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as response_file:
        response_path = Path(response_file.name)

    try:
        config = build_curl_config(url, headers, body_path, response_path)
        completed = subprocess.run(
            [curl, "--config", "-"],
            input=config,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
            check=False,
        )
    finally:
        try:
            body_path.unlink()
        except OSError:
            pass

    try:
        response_text = response_path.read_text(encoding="utf-8")
    finally:
        try:
            response_path.unlink()
        except OSError:
            pass

    if completed.returncode != 0:
        message = response_text.strip() or (completed.stderr or "").strip() or (completed.stdout or "").strip()
        raise MimoResponseError(f"MiMo curl fallback failed: {redact_secret(message, api_key)}")

    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise MimoResponseError("MiMo returned non-JSON HTTP response.") from exc
    if isinstance(data, dict) and "error" in data:
        raise MimoResponseError(f"MiMo error: {redact_secret(response_text, api_key)}")
    return data


def post_json_urllib(url: str, headers: dict[str, str], payload: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    api_key = headers.get("api-key", "")
    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise MimoResponseError(f"MiMo HTTP {exc.code}: {redact_secret(body, api_key)}") from exc
    except urllib.error.URLError as exc:
        raise MimoResponseError(f"MiMo request failed: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise MimoResponseError("MiMo returned non-JSON HTTP response.") from exc


def extract_message_content(response: dict[str, Any]) -> str:
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise MimoResponseError("MiMo response did not contain choices[0].message.content.") from exc
    if not isinstance(content, str) or not content.strip():
        raise MimoResponseError("MiMo returned an empty message content.")
    return content


def parse_json_object(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise MimoResponseError("MiMo response was not a JSON object.")
        value = json.loads(text[start : end + 1])

    if not isinstance(value, dict):
        raise MimoResponseError("MiMo response JSON must be an object.")
    return value


def merge_strategy_spec(baseline_spec: dict[str, Any], model_spec: dict[str, Any]) -> dict[str, Any]:
    merged = dict(baseline_spec)

    for field in STRATEGY_FIELDS:
        if field not in model_spec:
            continue
        value = normalize_field_value(field, model_spec[field], baseline_spec.get(field))
        if value is not None:
            merged[field] = value

    merged["original_request"] = baseline_spec["original_request"]
    merged["risk_disclosure"] = RISK_DISCLOSURE
    merged["user_preferences"] = baseline_spec.get("user_preferences", {})
    merged["execution_mode"] = normalize_execution_mode(str(merged.get("execution_mode") or "needs_clarification"))

    if merged.get("prohibited_actions") or merged.get("clarification_questions"):
        merged["execution_mode"] = "needs_clarification"

    merged["requires_agent"] = merged["execution_mode"] == "agent"
    return merged


def normalize_field_value(field: str, value: Any, fallback: Any) -> Any:
    if field in LIST_FIELDS:
        if isinstance(value, list):
            items = [str(item).strip() for item in value if str(item).strip()]
            return items if items else fallback
        if isinstance(value, str) and value.strip():
            return [value.strip()]
        return fallback

    if field == "horizon_days":
        if value is None:
            return fallback
        try:
            number = int(value)
        except (TypeError, ValueError):
            return fallback
        return number if number > 0 else fallback

    if field == "user_preferences":
        return value if isinstance(value, dict) else fallback

    if field == "requires_agent":
        return bool(value)

    if isinstance(value, str):
        return value.strip() or fallback
    return value


def normalize_execution_mode(value: str) -> str:
    if value in {"workflow", "agent", "needs_clarification"}:
        return value
    return "needs_clarification"


def build_chat_url(base_url: str) -> str:
    url = base_url.strip().rstrip("/")
    if not url:
        return DEFAULT_MIMO_CHAT_URL
    if url.endswith("/chat/completions"):
        return url
    return f"{url}/chat/completions"


def build_curl_config(url: str, headers: dict[str, str], body_path: Path, response_path: Path) -> str:
    lines = [
        "silent",
        "show-error",
        "fail-with-body",
        'request = "POST"',
        f'url = "{escape_curl_config(url)}"',
        f'data-binary = "@{escape_curl_config(body_path.as_posix())}"',
        f'output = "{escape_curl_config(response_path.as_posix())}"',
    ]
    for name, value in headers.items():
        lines.append(f'header = "{escape_curl_config(f"{name}: {value}")}"')
    return "\n".join(lines) + "\n"


def escape_curl_config(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def redact_secret(message: str, secret: str) -> str:
    if secret:
        return message.replace(secret, "<redacted>")
    return message
