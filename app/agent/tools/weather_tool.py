# Day21_2 — 天气查询工具
#
# 功能：通过 Open-Meteo 免费 API 查询城市实时天气（无需 API Key）
# 逻辑：geocode → forecast → 统一 Observation

import json
import re
import urllib.error
import urllib.parse
import urllib.request

from app.core.config import TOOL_HTTP_TIMEOUT, WEATHER_ENABLED

WEATHER_TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "weather_query",
        "description": "查询指定城市的实时天气（温度、湿度、风力等）",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "城市名，如 北京、上海、Tokyo",
                },
            },
            "required": ["location"],
        },
    },
}

_WMO_WEATHER: dict[int, str] = {
    0: "晴",
    1: "大部晴朗",
    2: "局部多云",
    3: "多云",
    45: "雾",
    48: "雾凇",
    51: "小毛毛雨",
    53: "中毛毛雨",
    55: "大毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    80: "小阵雨",
    81: "中阵雨",
    82: "大阵雨",
    95: "雷暴",
}


# @brief: HTTP GET 并解析 JSON
def _fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "ai-project-assistant/0.3"})
    with urllib.request.urlopen(req, timeout=TOOL_HTTP_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


# @brief: 地理编码，将城市名转为经纬度
def _geocode(location: str) -> dict | None:
    params = urllib.parse.urlencode(
        {"name": location, "count": 1, "language": "zh", "format": "json"}
    )
    data = _fetch_json(f"https://geocoding-api.open-meteo.com/v1/search?{params}")
    results = data.get("results") or []
    return results[0] if results else None


# @brief: 查询实时天气
def _fetch_weather(latitude: float, longitude: float) -> dict:
    params = urllib.parse.urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "timezone": "auto",
        }
    )
    return _fetch_json(f"https://api.open-meteo.com/v1/forecast?{params}")


# @brief: 从用户消息中提取城市名（供 Workflow 使用）
def extract_location(message: str) -> str:
    text = message
    noise = (
        "今天", "明天", "后天", "现在", "当前", "实时", "怎么样", "如何",
        "查询", "查一下", "帮我", "请问", "天气", "气温", "温度", "下雨",
        "湿度", "风力", "预报", "穿衣", "多少度", "冷不冷", "热不热",
    )
    for word in noise:
        text = text.replace(word, " ")
    text = re.sub(r"[?？!！。,，]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    cn_match = re.search(r"([\u4e00-\u9fff]{2,8})", text)
    if cn_match:
        return cn_match.group(1)

    en_match = re.search(r"([A-Za-z][A-Za-z\s\-]{1,30})", message)
    if en_match:
        return en_match.group(1).strip()

    return text or "北京"


# @brief: 运行天气查询工具
def run(location: str) -> dict:
    if not WEATHER_ENABLED:
        return {
            "ok": False,
            "data": {"location": location},
            "summary": "天气工具未启用（WEATHER_ENABLED=false）",
            "sources": [],
        }

    location = (location or "").strip() or "北京"
    try:
        geo = _geocode(location)
        if not geo:
            return {
                "ok": False,
                "data": {"location": location},
                "summary": f"未找到城市：{location}",
                "sources": [],
            }

        forecast = _fetch_weather(geo["latitude"], geo["longitude"])
        current = forecast.get("current") or {}
        code = int(current.get("weather_code", -1))
        weather_text = _WMO_WEATHER.get(code, f"天气码 {code}")

        city = geo.get("name") or location
        country = geo.get("country", "")
        temp = current.get("temperature_2m")
        humidity = current.get("relative_humidity_2m")
        wind = current.get("wind_speed_10m")

        data = {
            "location": location,
            "city": city,
            "country": country,
            "temperature_c": temp,
            "humidity_percent": humidity,
            "wind_speed_kmh": wind,
            "weather": weather_text,
            "weather_code": code,
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
        }
        place = f"{city}（{country}）" if country else city
        summary = (
            f"{place} 当前 {weather_text}，气温 {temp}°C，"
            f"湿度 {humidity}%，风速 {wind} km/h"
        )
        return {
            "ok": True,
            "data": data,
            "summary": summary,
            "sources": [
                {
                    "source": "Open-Meteo",
                    "page": 0,
                    "chunk": 0,
                    "score": 1.0,
                    "url": "https://open-meteo.com/",
                }
            ],
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "data": {"location": location},
            "summary": f"天气 API 请求失败: {exc}",
            "sources": [],
        }


SPEC = {
    "name": "weather_query",
    "description": "查询指定城市的实时天气（温度、湿度、风力等）",
    "schema": WEATHER_TOOL_SCHEMA,
    "run": run,
}
