from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from typing import Any


DEFAULT_REQUEST = "找最近 60 日趋势较强、回撤较低、没有明显负面新闻的半导体和人工智能方向股票，生成候选观察池。"

RISK_DISCLOSURE = (
    "风险提示：以下内容仅用于学习和投研流程演示，不构成投资建议或收益承诺。"
    "市场有风险，真实交易前请结合自身风险承受能力独立判断。"
)

DEFAULT_PROFILE: dict[str, Any] = {
    "risk_level": "medium",
    "exclude_st": True,
    "max_candidates": 10,
    "preferred_markets": ["A股"],
}

THEME_ALIASES = {
    "人工智能": "人工智能",
    "AI": "人工智能",
    "大模型": "人工智能",
    "半导体": "半导体",
    "芯片": "半导体",
    "算力": "算力",
    "机器人": "机器人",
    "新能源": "新能源",
    "光伏": "光伏",
    "锂电": "锂电",
    "白酒": "白酒",
    "银行": "银行",
    "医药": "医药",
    "消费电子": "消费电子",
    "低空经济": "低空经济",
    "军工": "军工",
    "有色金属": "有色金属",
    "电网设备": "电网设备",
    "电力设备": "电力设备",
    "智能电网": "智能电网",
    "特高压": "特高压",
    "输变电": "输变电",
    "配电网": "配电网",
    "电网": "电网设备",
}

PROHIBITED_PATTERNS = {
    "guaranteed_return": ["稳赚", "保赚", "保证收益", "无风险收益"],
    "certain_price_move": ["必涨", "一定涨", "明天涨停", "翻倍"],
    "auto_trade": ["自动买入", "自动卖出", "直接买入", "直接下单", "满仓"],
    "real_trade": ["真实交易", "实盘交易", "帮我买", "替我买"],
}


@dataclass
class RoutingDecision:
    mode: str
    reason: str
    matched_signals: list[str]
    next_step: str
    not_selected: dict[str, str]


@dataclass
class StrategySpec:
    original_request: str
    market: str
    themes: list[str]
    horizon_days: int | None
    candidate_rules: list[str]
    risk_filters: list[str]
    user_preferences: dict[str, Any]
    output: str
    execution_mode: str
    requires_agent: bool
    routing_decision: RoutingDecision
    assumptions: list[str]
    clarification_questions: list[str]
    prohibited_actions: list[str]
    risk_disclosure: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def parse_strategy_request(
    request: str,
    user_profile: dict[str, Any] | None = None,
) -> StrategySpec:
    text = normalize_text(request or DEFAULT_REQUEST)
    profile = merge_profile(user_profile)

    market, market_assumptions = extract_market(text, profile)
    themes = extract_themes(text)
    horizon_days = extract_horizon_days(text)
    candidate_rules = extract_candidate_rules(text, horizon_days)
    risk_filters = extract_risk_filters(text, profile)
    prohibited_actions = detect_prohibited_actions(text)
    output = extract_output(text, prohibited_actions)
    clarification_questions = build_clarification_questions(
        text=text,
        market=market,
        themes=themes,
        horizon_days=horizon_days,
        candidate_rules=candidate_rules,
        prohibited_actions=prohibited_actions,
    )

    assumptions = list(market_assumptions)
    if profile.get("exclude_st") and "排除 ST / *ST" in risk_filters:
        assumptions.append("按用户偏好默认排除 ST / *ST 股票。")
    if not prohibited_actions:
        assumptions.append("当前阶段只生成投研计划，不输出个股名单。")

    execution_mode = classify_execution_mode(
        text=text,
        market=market,
        themes=themes,
        horizon_days=horizon_days,
        candidate_rules=candidate_rules,
        risk_filters=risk_filters,
        clarification_questions=clarification_questions,
        prohibited_actions=prohibited_actions,
    )
    routing_decision = build_routing_decision(
        text=text,
        market=market,
        themes=themes,
        horizon_days=horizon_days,
        candidate_rules=candidate_rules,
        risk_filters=risk_filters,
        output=output,
        execution_mode=execution_mode,
        clarification_questions=clarification_questions,
        prohibited_actions=prohibited_actions,
    )

    return StrategySpec(
        original_request=text,
        market=market,
        themes=themes,
        horizon_days=horizon_days,
        candidate_rules=candidate_rules,
        risk_filters=risk_filters,
        user_preferences=profile,
        output=output,
        execution_mode=execution_mode,
        requires_agent=execution_mode == "agent",
        routing_decision=routing_decision,
        assumptions=assumptions,
        clarification_questions=clarification_questions,
        prohibited_actions=prohibited_actions,
        risk_disclosure=RISK_DISCLOSURE,
    )


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def merge_profile(user_profile: dict[str, Any] | None) -> dict[str, Any]:
    profile = dict(DEFAULT_PROFILE)
    if user_profile:
        profile.update(user_profile)
    return profile


def extract_market(text: str, profile: dict[str, Any]) -> tuple[str, list[str]]:
    if "港股" in text:
        return "港股", []
    if "美股" in text:
        return "美股", []
    if "A股" in text or "股票" in text or "股" in text:
        return "A股", []

    preferred_markets = profile.get("preferred_markets") or []
    if preferred_markets:
        return preferred_markets[0], [f"未显式指定市场，暂按用户偏好使用 {preferred_markets[0]}。"]

    return "未指定", []


def extract_themes(text: str) -> list[str]:
    matches: list[tuple[int, str]] = []
    for alias, theme in THEME_ALIASES.items():
        index = find_alias(text, alias)
        if index >= 0:
            matches.append((index, theme))
    matches.sort(key=lambda item: item[0])
    themes = [theme for _, theme in matches]
    return dedupe(themes)


def find_alias(text: str, alias: str) -> int:
    if alias.isascii():
        return text.upper().find(alias.upper())
    return text.find(alias)


def extract_horizon_days(text: str) -> int | None:
    day_match = re.search(r"(?:最近|近)\s*(\d+)\s*(?:个)?(?:交易日|日|天)", text)
    if day_match:
        return int(day_match.group(1))

    month_match = re.search(r"(?:最近|近)\s*(\d+)\s*(?:个)?月", text)
    if month_match:
        return int(month_match.group(1)) * 30

    year_match = re.search(r"(?:最近|近)\s*(\d+)\s*年", text)
    if year_match:
        return int(year_match.group(1)) * 365

    return None


def extract_candidate_rules(text: str, horizon_days: int | None) -> list[str]:
    rules: list[str] = []
    horizon = f"近{horizon_days}日" if horizon_days else ""

    if any(token in text for token in ["趋势", "强势", "动量"]):
        rules.append(f"{horizon}趋势较强" if horizon else "趋势较强")
    if "回撤" in text:
        rules.append("最大回撤较低")
    if any(token in text for token in ["成交", "流动性", "换手"]):
        rules.append("成交活跃度足够")

    pe_match = re.search(r"市盈率\s*(?:小于|低于|不高于|<=?)\s*(\d+)", text)
    if pe_match:
        rules.append(f"市盈率小于{pe_match.group(1)}")

    pb_match = re.search(r"市净率\s*(?:小于|低于|不高于|<=?)\s*(\d+)", text)
    if pb_match:
        rules.append(f"市净率小于{pb_match.group(1)}")

    roe_match = re.search(r"ROE\s*(?:大于|高于|>=?)\s*(\d+)%?", text, flags=re.IGNORECASE)
    if roe_match:
        rules.append(f"ROE大于{roe_match.group(1)}%")

    if any(token in text for token in ["净利润增长", "利润增长", "业绩增长"]):
        rules.append("盈利增长表现较好")
    if any(token in text for token in ["股息", "分红"]):
        rules.append("分红或股息表现较好")

    return dedupe(rules)


def extract_risk_filters(text: str, profile: dict[str, Any]) -> list[str]:
    filters: list[str] = []

    if any(token in text for token in ["负面新闻", "利空", "舆情"]):
        filters.append("近期无重大负面新闻")
    if any(token in text for token in ["公告", "监管", "问询"]):
        filters.append("近期公告和监管事件无重大异常")
    if any(token in text for token in ["财务异常", "暴雷", "造假"]):
        filters.append("无明显财务异常风险")
    if profile.get("exclude_st", True):
        filters.append("排除 ST / *ST")

    return dedupe(filters)


def extract_output(text: str, prohibited_actions: list[str]) -> str:
    if prohibited_actions:
        return "风险边界提示和可替代的投研问题"
    if "观察池" in text or "自选" in text:
        return "候选观察池和证据化报告"
    if "报告" in text:
        return "证据化投研报告"
    return "结构化投研策略说明"


def build_clarification_questions(
    text: str,
    market: str,
    themes: list[str],
    horizon_days: int | None,
    candidate_rules: list[str],
    prohibited_actions: list[str],
) -> list[str]:
    questions: list[str] = []

    if prohibited_actions:
        questions.append("请求中包含高风险交易或收益确定性表述，请改为观察池、研究报告或模拟验证问题。")
        return questions

    if market == "未指定":
        questions.append("请确认目标市场，例如 A股、港股或美股。")
    if not themes:
        questions.append("请确认主题或行业范围，例如半导体、人工智能、银行等。")
    if horizon_days is None and needs_horizon(text, candidate_rules):
        questions.append("请确认观察时间窗口，例如最近 20 日、60 日或近一年。")
    if not candidate_rules:
        questions.append("请补充候选筛选规则，例如趋势、估值、财务质量、成交活跃度或回撤要求。")

    return questions


def needs_horizon(text: str, candidate_rules: list[str]) -> bool:
    dynamic_tokens = ["最近", "近", "趋势", "回撤", "涨幅", "新闻", "公告", "研报", "资金流"]
    if any(token in text for token in dynamic_tokens):
        return True
    return not candidate_rules


def detect_prohibited_actions(text: str) -> list[str]:
    actions: list[str] = []
    for action, patterns in PROHIBITED_PATTERNS.items():
        if any(pattern in text for pattern in patterns):
            actions.append(action)
    return actions


def classify_execution_mode(
    text: str,
    market: str,
    themes: list[str],
    horizon_days: int | None,
    candidate_rules: list[str],
    risk_filters: list[str],
    clarification_questions: list[str],
    prohibited_actions: list[str],
) -> str:
    if prohibited_actions:
        return "needs_clarification"
    if clarification_questions:
        return "needs_clarification"

    signals = build_routing_signals(
        text=text,
        market=market,
        themes=themes,
        horizon_days=horizon_days,
        candidate_rules=candidate_rules,
        risk_filters=risk_filters,
        output=extract_output(text, prohibited_actions),
        clarification_questions=clarification_questions,
        prohibited_actions=prohibited_actions,
    )

    if any(signal in signals for signal in ["time_sensitive", "watchlist_output", "evidence_report_output", "multi_condition", "risk_filter"]):
        return "agent"
    return "workflow"


def build_routing_decision(
    text: str,
    market: str,
    themes: list[str],
    horizon_days: int | None,
    candidate_rules: list[str],
    risk_filters: list[str],
    output: str,
    execution_mode: str,
    clarification_questions: list[str],
    prohibited_actions: list[str],
) -> RoutingDecision:
    signals = build_routing_signals(
        text=text,
        market=market,
        themes=themes,
        horizon_days=horizon_days,
        candidate_rules=candidate_rules,
        risk_filters=risk_filters,
        output=output,
        clarification_questions=clarification_questions,
        prohibited_actions=prohibited_actions,
    )

    if prohibited_actions:
        mode = "blocked"
        reason = "请求包含收益确定性或自动交易等禁止意图，不能进入投研执行链路。"
        next_step = "安全阻断；请改写为观察池、研究报告或模拟验证问题。"
        not_selected = {
            "workflow": "请求包含禁止意图，不能转成固定筛选流程。",
            "agent": "请求包含禁止意图，不能进入多步骤 Agent 执行。",
            "needs_clarification": "仅追问不足以继续，必须先移除收益确定性或自动交易意图。",
        }
    elif execution_mode == "needs_clarification":
        mode = "needs_clarification"
        reason = "缺少主题、时间窗口或候选规则等必要信息，继续执行前需要追问。"
        next_step = "向用户追问缺失字段后重新解析。"
        not_selected = {
            "workflow": "必要字段不足，不能直接进入固定筛选流程。",
            "agent": "必要字段不足，不能进入多步骤 Agent 执行。",
            "blocked": "未发现必须阻断的收益确定性或自动交易意图。",
        }
    elif execution_mode == "agent":
        mode = "agent"
        reason = "任务包含近期数据、风险核验或观察池输出，需要多步骤证据收集和人工确认。"
        next_step = "进入 Lab 02 Strategy Agent Loop。"
        not_selected = {
            "workflow": "固定筛选流程不足以完成近期数据、新闻风险或证据报告核验。",
            "needs_clarification": "市场、主题、时间窗口和筛选规则已足够明确。",
            "blocked": "未发现收益承诺、确定性涨跌或自动交易等禁止意图。",
        }
    else:
        mode = "workflow"
        reason = "条件固定、所需字段完整，适合按预定义筛选流程执行。"
        next_step = "进入固定筛选 workflow；后续 Lab 03 可用 mock 工具执行筛选。"
        not_selected = {
            "agent": "没有近期新闻核验、多源证据或动态规划需求。",
            "needs_clarification": "市场、主题和筛选规则已足够明确。",
            "blocked": "未发现收益承诺、确定性涨跌或自动交易等禁止意图。",
        }

    return RoutingDecision(
        mode=mode,
        reason=reason,
        matched_signals=signals,
        next_step=next_step,
        not_selected=not_selected,
    )


def build_routing_signals(
    text: str,
    market: str,
    themes: list[str],
    horizon_days: int | None,
    candidate_rules: list[str],
    risk_filters: list[str],
    output: str,
    clarification_questions: list[str],
    prohibited_actions: list[str],
) -> list[str]:
    signals: list[str] = []

    if prohibited_actions:
        signals.append("prohibited_intent")
        signals.extend(f"prohibited:{action}" for action in prohibited_actions)
        return dedupe(signals)

    if market == "未指定":
        signals.append("missing_market")
    if not themes:
        signals.append("missing_theme")
    if horizon_days is None and needs_horizon(text, candidate_rules):
        signals.append("missing_horizon")
    if not candidate_rules:
        signals.append("missing_candidate_rules")
    if clarification_questions:
        signals.append("missing_information")

    if any(token in text for token in ["新闻", "公告", "研报", "最近", "近期", "近"]):
        signals.append("time_sensitive")
    if len(candidate_rules) >= 2 or len(candidate_rules) + len(risk_filters) >= 3:
        signals.append("multi_condition")
    if any(filter_item != "排除 ST / *ST" for filter_item in risk_filters):
        signals.append("risk_filter")
    if any(rule.startswith(("市盈率", "市净率", "ROE")) for rule in candidate_rules):
        signals.append("valuation_filter")
    if "观察池" in output:
        signals.append("watchlist_output")
    if "报告" in output:
        signals.append("evidence_report_output")
    if candidate_rules and themes and not any(signal in signals for signal in ["time_sensitive", "risk_filter", "watchlist_output", "evidence_report_output"]):
        signals.append("deterministic_screening")

    return dedupe(signals)


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse an investment research request into StrategySpec JSON.")
    parser.add_argument("request", nargs="*", help="Natural-language investment research request.")
    parser.add_argument("--input-file", help="Read request text from a UTF-8 file.")
    parser.add_argument("--indent", type=int, default=2, help="JSON indentation.")
    args = parser.parse_args()

    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as file:
            request = file.read()
    elif args.request:
        request = " ".join(args.request)
    else:
        request = DEFAULT_REQUEST

    spec = parse_strategy_request(request)
    print(json.dumps(spec.to_dict(), ensure_ascii=False, indent=args.indent))


if __name__ == "__main__":
    main()
