# Day21_2 — 体育赛事工具
#
# 功能：TheSportsDB 赛程/球队搜索 + BBC Sport RSS 回退
# 逻辑：球队名 → searchevents；否则 → 联赛近期赛程或 RSS 头条

import json
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from app.core.config import (
    SPORTS_DEFAULT_LEAGUE_ID,
    SPORTS_ENABLED,
    SPORTS_MAX_ITEMS,
    SPORTS_RSS_FEEDS,
    SPORTSDB_API_KEY,
    TOOL_HTTP_TIMEOUT,
)

SPORTS_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "sports_query",
        "description": "查询足球/篮球等体育赛事赛程或相关体育资讯",
        "parameters": {
            "type": "object",
            "properties": {
                "sport": {
                    "type": "string",
                    "description": "运动类型：Soccer / Basketball",
                },
                "team": {
                    "type": "string",
                    "description": "可选球队名，如 Arsenal、湖人",
                },
            },
            "required": ["sport"],
        },
    },
}

_SPORT_ALIASES: dict[str, str] = {
    "足球": "Soccer",
    "英超": "Soccer",
    "西甲": "Soccer",
    "意甲": "Soccer",
    "德甲": "Soccer",
    "欧冠": "Soccer",
    "世界杯": "Soccer",
    "篮球": "Basketball",
    "nba": "Basketball",
    "cba": "Basketball",
    "soccer": "Soccer",
    "basketball": "Basketball",
}

_LEAGUE_IDS: dict[str, str] = {
    "Soccer": SPORTS_DEFAULT_LEAGUE_ID,
    "Basketball": "4387",
}

_SPORT_KEYWORDS = (
    "体育", "足球", "篮球", "比分", "赛况", "比赛", "联赛", "赛程", "直播",
    "英超", "西甲", "意甲", "德甲", "欧冠", "世界杯", "NBA", "CBA",
)


# @brief: HTTP GET 并解析 JSON
def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "ai-project-assistant/0.3"})
    with urllib.request.urlopen(req, timeout=TOOL_HTTP_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


# @brief: 抓取文本
def _fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "ai-project-assistant/0.3"})
    with urllib.request.urlopen(req, timeout=TOOL_HTTP_TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


# @brief: 解析 RSS 条目
def _parse_rss(xml_text: str, feed_url: str) -> list[dict]:
    items: list[dict] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return items
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        if title:
            items.append({"title": title, "link": link, "published": pub, "feed": feed_url})
    return items


# @brief: 从用户消息识别运动类型
def extract_sport(message: str) -> str:
    lower = message.lower()
    for alias, sport in _SPORT_ALIASES.items():
        if alias in lower or alias in message:
            return sport
    return "Soccer"


# @brief: 从用户消息提取球队名（可选）
def extract_team(message: str) -> str | None:
    text = message
    noise = (
        "今天", "今晚", "现在", "最新", "实时", "查询", "查一下", "帮我", "请问",
        "有什么", "怎么样", "体育", "足球", "篮球", "比分", "赛况", "比赛",
        "联赛", "赛程", "直播", "新闻", "英超", "西甲", "意甲", "德甲", "欧冠",
    )
    for word in noise:
        text = text.replace(word, " ")
    text = re.sub(r"[?？!！。,，]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) >= 2 and not re.fullmatch(r"[\u4e00-\u9fff]{1,2}", text):
        return text
    en = re.search(r"([A-Za-z][A-Za-z0-9\s\-]{2,40})", message)
    return en.group(1).strip() if en else None


# @brief: 格式化 TheSportsDB 赛事
def _format_event(event: dict) -> str:
    home = event.get("strHomeTeam") or "?"
    away = event.get("strAwayTeam") or "?"
    status = event.get("strStatus") or ""
    score = ""
    if event.get("intHomeScore") is not None and event.get("intAwayScore") is not None:
        if str(event["intHomeScore"]) != "None":
            score = f" {event['intHomeScore']}:{event['intAwayScore']}"
    league = event.get("strLeague") or ""
    date = (event.get("dateEvent") or event.get("strTimestamp") or "")[:10]
    parts = [f"{home} vs {away}{score}"]
    if status:
        parts.append(f"({status})")
    if league:
        parts.append(f"[{league}]")
    if date:
        parts.append(date)
    return " ".join(parts)


# @brief: 按球队搜索赛事
def _search_team_events(team: str) -> list[dict]:
    base = f"https://www.thesportsdb.com/api/v1/json/{SPORTSDB_API_KEY}"
    params = urllib.parse.urlencode({"e": team})
    data = _fetch_json(f"{base}/searchevents.php?{params}")
    events = data.get("event") or []
    return events if isinstance(events, list) else [events]


# @brief: 联赛近期赛程
def _fetch_league_events(sport: str) -> list[dict]:
    league_id = _LEAGUE_IDS.get(sport, SPORTS_DEFAULT_LEAGUE_ID)
    base = f"https://www.thesportsdb.com/api/v1/json/{SPORTSDB_API_KEY}"
    data = _fetch_json(f"{base}/eventsnextleague.php?id={league_id}")
    return data.get("events") or []


# @brief: RSS 体育头条回退
def _fetch_sports_rss(keyword: str | None = None) -> list[dict]:
    items: list[dict] = []
    for feed_url in SPORTS_RSS_FEEDS:
        try:
            items.extend(_parse_rss(_fetch_text(feed_url), feed_url))
        except (urllib.error.URLError, TimeoutError):
            continue
    if keyword:
        kw = keyword.lower()
        items = [i for i in items if kw in i["title"].lower()]
    return items[:SPORTS_MAX_ITEMS]


# @brief: 运行体育赛事查询工具
def run(sport: str = "Soccer", team: str | None = None) -> dict:
    if not SPORTS_ENABLED:
        return {
            "ok": False,
            "data": {"sport": sport, "team": team},
            "summary": "体育工具未启用（SPORTS_ENABLED=false）",
            "sources": [],
        }

    sport = sport or "Soccer"
    mode = ""
    events: list[dict] = []
    rss_items: list[dict] = []

    try:
        if team:
            events = _search_team_events(team)
            mode = f"球队「{team}」相关赛事"
        else:
            events = _fetch_league_events(sport)
            mode = f"{sport} 联赛近期赛程"

        if not events:
            rss_items = _fetch_sports_rss(team)
            mode = f"体育 RSS 头条（{sport}）"

        if events:
            events = events[:SPORTS_MAX_ITEMS]
            lines = [f"- {_format_event(e)}" for e in events]
            summary = f"{mode}：\n" + "\n".join(lines)
            sources = [
                {
                    "source": _format_event(e),
                    "page": 0,
                    "chunk": i,
                    "score": 1.0,
                    "url": "https://www.thesportsdb.com/",
                }
                for i, e in enumerate(events)
            ]
            return {
                "ok": True,
                "data": {"sport": sport, "team": team, "events": events},
                "summary": summary,
                "sources": sources,
            }

        if rss_items:
            lines = [f"- {a['title']}" for a in rss_items]
            summary = f"{mode}：\n" + "\n".join(lines)
            sources = [
                {
                    "source": a["title"],
                    "page": 0,
                    "chunk": i,
                    "score": 1.0,
                    "url": a.get("link") or a.get("feed", ""),
                }
                for i, a in enumerate(rss_items)
            ]
            return {
                "ok": True,
                "data": {"sport": sport, "team": team, "articles": rss_items},
                "summary": summary,
                "sources": sources,
            }

        return {
            "ok": False,
            "data": {"sport": sport, "team": team},
            "summary": f"未找到{mode or '体育'}数据，请换球队名或稍后再试",
            "sources": [],
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "data": {"sport": sport, "team": team},
            "summary": f"体育 API 请求失败: {exc}",
            "sources": [],
        }


SPEC = {
    "name": "sports_query",
    "description": "查询足球/篮球等体育赛事赛程或相关体育资讯",
    "schema": SPORTS_TOOL_SCHEMA,
    "run": run,
}
