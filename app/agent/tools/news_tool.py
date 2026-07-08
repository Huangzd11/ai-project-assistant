# Day21_2 — 新闻检索工具
#
# 功能：从配置的 RSS 源抓取最新新闻，可按关键词过滤
# 逻辑：fetch RSS → 解析 item → 过滤 → 统一 Observation

import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from app.core.config import NEWS_ENABLED, NEWS_MAX_ITEMS, NEWS_RSS_FEEDS, TOOL_HTTP_TIMEOUT

NEWS_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "news_search",
        "description": "检索最新新闻头条，可按关键词过滤",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "可选关键词，如 AI、科技；留空则返回最新头条",
                },
            },
            "required": [],
        },
    },
}


# @brief: 抓取 RSS XML 文本
def _fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "ai-project-assistant/0.3"})
    with urllib.request.urlopen(req, timeout=TOOL_HTTP_TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


# @brief: 解析 RSS/Atom 条目
def _parse_feed(xml_text: str, feed_url: str) -> list[dict]:
    items: list[dict] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return items

    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or item.findtext("date") or "").strip()
        desc = (item.findtext("description") or "").strip()
        desc = re.sub(r"<[^>]+>", "", desc)
        if title:
            items.append(
                {
                    "title": title,
                    "link": link,
                    "published": pub,
                    "description": desc[:200],
                    "feed": feed_url,
                }
            )

    if items:
        return items

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for entry in root.findall(".//atom:entry", ns):
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
        link_el = entry.find("atom:link", ns)
        link = (link_el.get("href") if link_el is not None else "") or ""
        pub = (entry.findtext("atom:updated", default="", namespaces=ns) or "").strip()
        if title:
            items.append(
                {
                    "title": title,
                    "link": link,
                    "published": pub,
                    "description": "",
                    "feed": feed_url,
                }
            )
    return items


# @brief: 从用户消息中提取新闻关键词（供 Workflow 使用）
def extract_query(message: str) -> str | None:
    if not any(kw in message for kw in ("新闻", "头条", "热点", "资讯", "快讯", "报道")):
        return None

    text = message
    noise = (
        "最新", "今天", "今日", "有什么", "有哪些", "帮我", "查一下", "查询",
        "看看", "关于", "有关", "的", "新闻", "头条", "热点", "资讯", "快讯", "报道",
    )
    for word in noise:
        text = text.replace(word, " ")
    text = re.sub(r"[?？!！。,，]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) >= 2 else None


# @brief: 运行新闻检索工具
def run(query: str | None = None) -> dict:
    if not NEWS_ENABLED:
        return {
            "ok": False,
            "data": {"query": query},
            "summary": "新闻工具未启用（NEWS_ENABLED=false）",
            "sources": [],
        }

    keyword = (query or "").strip().lower()
    all_items: list[dict] = []

    for feed_url in NEWS_RSS_FEEDS:
        try:
            xml_text = _fetch_text(feed_url)
            all_items.extend(_parse_feed(xml_text, feed_url))
        except (urllib.error.URLError, TimeoutError) as exc:
            all_items.append(
                {
                    "title": f"[RSS 拉取失败] {feed_url}",
                    "link": "",
                    "published": "",
                    "description": str(exc),
                    "feed": feed_url,
                }
            )

    if keyword:
        filtered = [
            item
            for item in all_items
            if keyword in item.get("title", "").lower()
            or keyword in item.get("description", "").lower()
        ]
    else:
        filtered = all_items

    articles = [item for item in filtered if not item["title"].startswith("[RSS")]
    articles = articles[:NEWS_MAX_ITEMS]

    if not articles:
        hint = f"关键词「{query}」" if query else "当前 RSS 源"
        return {
            "ok": False,
            "data": {"query": query, "articles": []},
            "summary": f"未找到相关新闻（{hint}）",
            "sources": [],
        }

    lines = [f"- {a['title']}" + (f"（{a['published']}）" if a.get("published") else "") for a in articles]
    summary = "最新新闻：\n" + "\n".join(lines)
    sources = [
        {
            "source": a["title"],
            "page": 0,
            "chunk": i,
            "score": 1.0,
            "url": a.get("link") or a.get("feed", ""),
        }
        for i, a in enumerate(articles)
    ]
    return {
        "ok": True,
        "data": {"query": query, "articles": articles},
        "summary": summary,
        "sources": sources,
    }


SPEC = {
    "name": "news_search",
    "description": "检索最新新闻头条，可按关键词过滤",
    "schema": NEWS_TOOL_SCHEMA,
    "run": run,
}
