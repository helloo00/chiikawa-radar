#!/usr/bin/env python3
"""
ちいかわグッズの「目撃・入荷・発売」情報を Bluesky 公開検索 ＋ 公式RSS から集めて
アプリ用の sightings.json を生成する。

- サーバー不要（GitHub Actions の定期実行を想定）
- API キー不要で動く（Nominatim ジオコーディング）
- 任意で YAHOO_APP_ID / ANTHROPIC_API_KEY を環境変数で渡すと精度が上がる

出力: backend/out/sightings.json  （geocode キャッシュ: backend/out/geocode-cache.json）
"""
from __future__ import annotations
import hashlib
import html
import json
import os
import re
import sys
import time
import datetime as dt
from pathlib import Path

import requests
import feedparser

HERE = Path(__file__).parent
OUT_DIR = HERE / "out"
OUT_DIR.mkdir(exist_ok=True)
OUT_FILE = OUT_DIR / "sightings.json"
CACHE_FILE = OUT_DIR / "geocode-cache.json"

MAX_ITEMS = 200
EXPIRE_DAYS = 21
# Nominatim/Bluesky 用の識別子付き UA、RSS 用のブラウザ風 UA
BOT_UA = "ChiikawaRadar-sightings-bot/1.0 (+https://github.com/; contact via repo issues)"
RSS_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Safari/605.1"

sources = json.loads((HERE / "sources.json").read_text("utf-8"))
chains_cfg = json.loads((HERE / "chains.json").read_text("utf-8"))
CHAINS: dict[str, list[str]] = chains_cfg["chains"]
AREAS: list[str] = chains_cfg["areas"]
STORE_HINTS: list[str] = chains_cfg["store_hints"]
ITEM_KEYWORDS: list[str] = chains_cfg["item_keywords"]

TYPE_RULES = [
    ("kuji", ["一番くじ", "エニマイくじ", "ラストワン", "ダブルチャンス"]),
    ("event", ["POP UP", "ポップアップ", "催事", "期間限定ショップ", "フェア", "展示", "スタンプラリー"]),
    ("restock", ["入荷", "再入荷", "再販", "補充", "在庫復活"]),
    ("release", ["発売", "予約開始", "受注", "登場", "新作", "予約受付", "本日発売", "リリース"]),
    ("sighting", ["買えた", "売ってた", "並んでた", "ゲットした", "見つけた", "在庫あった", "残ってた", "購入した"]),
]

now = dt.datetime.now(dt.timezone.utc)


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s or "")
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def is_chiikawa(text: str) -> bool:
    t = text.lower()
    return any(k.lower() in t for k in ("ちいかわ", "チイカワ", "chiikawa"))


def classify(text: str) -> str:
    for typ, kws in TYPE_RULES:
        if any(k.lower() in text.lower() for k in kws):
            return typ
    return "news"


def extract_chain(text: str) -> str | None:
    # 「渋谷ロフト」「池袋PARCO」のような 地名+ヒント の複合を優先
    for area in AREAS:
        for hint in STORE_HINTS:
            for combo in (area + hint, hint + area):
                if combo in text:
                    return combo
    for canonical, aliases in CHAINS.items():
        if any(a in text for a in aliases):
            # チェーン名の直前に地名があれば付ける
            for area in AREAS:
                if (area + canonical) in text or (canonical + " " + area) in text or (canonical + area) in text:
                    return f"{area}{canonical}"
            return canonical
    return None


def extract_area(text: str) -> str | None:
    for area in AREAS:
        if area in text:
            return area
    return None


def extract_item(text: str) -> str | None:
    found = list(dict.fromkeys(k for k in ITEM_KEYWORDS if k in text))
    return " / ".join(found[:3]) if found else None


# ---------------------------------------------------------------- collectors

def bluesky_token() -> str | None:
    ident = os.environ.get("BSKY_IDENTIFIER")
    pw = os.environ.get("BSKY_APP_PASSWORD")
    if not ident or not pw:
        log("Bluesky: BSKY_IDENTIFIER / BSKY_APP_PASSWORD 未設定 → スキップ（RSS のみ）")
        return None
    try:
        r = requests.post("https://bsky.social/xrpc/com.atproto.server.createSession",
                          json={"identifier": ident, "password": pw},
                          headers={"User-Agent": BOT_UA}, timeout=20)
        r.raise_for_status()
        return r.json().get("accessJwt")
    except Exception as e:  # noqa: BLE001
        log(f"Bluesky auth failed: {e}")
        return None


def collect_bluesky(queries: list[str]) -> list[dict]:
    token = bluesky_token()
    if not token:
        return []
    items = []
    base = "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts"
    headers = {"User-Agent": BOT_UA, "Authorization": f"Bearer {token}"}
    for q in queries:
        try:
            r = requests.get(base, params={"q": q, "limit": 40, "sort": "latest"},
                             headers=headers, timeout=20)
            if r.status_code != 200:
                log(f"bluesky {q!r} -> HTTP {r.status_code}")
                continue
            for post in r.json().get("posts", []):
                rec = post.get("record", {})
                text = rec.get("text", "")
                if not is_chiikawa(text):
                    continue
                author = post.get("author", {})
                actor = author.get("did") or author.get("handle")   # DID の方が安定
                rkey = post.get("uri", "").rsplit("/", 1)[-1]
                if not actor or not rkey or rkey.startswith("at:"):
                    continue
                url = f"https://bsky.app/profile/{actor}/post/{rkey}"
                items.append({
                    "source_name": "Bluesky",
                    "source_url": url,
                    "text": text,
                    "date": rec.get("createdAt") or post.get("indexedAt"),
                })
        except Exception as e:  # noqa: BLE001
            log(f"bluesky {q!r} error: {e}")
        time.sleep(0.5)
    return items


def collect_rss(feeds: list[str], keyword_filter: list[str], trusted_hosts: list[str]) -> list[dict]:
    items = []
    for feed_url in feeds:
        try:
            resp = requests.get(feed_url, headers={"User-Agent": RSS_UA}, timeout=25)
            if resp.status_code != 200:
                log(f"rss {feed_url} -> HTTP {resp.status_code}")
                continue
            parsed = feedparser.parse(resp.content)
            host = re.sub(r"^https?://", "", feed_url).split("/")[0]
            trusted = any(h in host for h in trusted_hosts)
            is_market = "chiikawamarket.jp" in host
            for e in parsed.entries[:60]:
                title = strip_html(getattr(e, "title", ""))
                summary = strip_html(getattr(e, "summary", ""))
                blob = f"{title} {summary}"
                if not trusted and not any(k in blob for k in keyword_filter):
                    continue
                if not trusted and not is_chiikawa(blob):
                    continue
                when = None
                for attr in ("published_parsed", "updated_parsed"):
                    tm = getattr(e, attr, None)
                    if tm:
                        when = dt.datetime(*tm[:6], tzinfo=dt.timezone.utc)
                        break
                src = "ちいかわマーケット" if is_market else (parsed.feed.get("title") or host)
                items.append({
                    "source_name": src[:40],
                    "source_url": getattr(e, "link", feed_url),
                    "text": blob,
                    "title": title or summary[:120],
                    "summary": summary or None,
                    "date": (when or now).isoformat(),
                    "type_hint": "release" if is_market else None,
                })
        except Exception as ex:  # noqa: BLE001
            log(f"rss {feed_url} error: {ex}")
    return items


# ---------------------------------------------------------------- geocoding

def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text("utf-8"))
        except Exception:  # noqa: BLE001
            return {}
    return {}


def geocode(query: str, cache: dict) -> tuple[float, float] | None:
    if not query:
        return None
    if query in cache:
        v = cache[query]
        return (v[0], v[1]) if v else None

    result = None
    yahoo_id = os.environ.get("YAHOO_APP_ID")
    try:
        if yahoo_id:
            r = requests.get("https://map.yahooapis.jp/geocode/V1/geoCoder",
                             params={"appid": yahoo_id, "query": query, "output": "json", "results": 1},
                             headers={"User-Agent": BOT_UA}, timeout=15)
            if r.status_code == 200:
                feats = r.json().get("Feature") or []
                if feats:
                    lon, lat = feats[0]["Geometry"]["Coordinates"].split(",")
                    result = (float(lat), float(lon))
        else:
            r = requests.get("https://nominatim.openstreetmap.org/search",
                             params={"q": query, "format": "json", "limit": 1, "countrycodes": "jp"},
                             headers={"User-Agent": BOT_UA}, timeout=15)
            if r.status_code == 200 and r.json():
                d = r.json()[0]
                result = (float(d["lat"]), float(d["lon"]))
            time.sleep(1.1)  # Nominatim: 1 req/sec
    except Exception as e:  # noqa: BLE001
        log(f"geocode {query!r} error: {e}")

    cache[query] = [result[0], result[1]] if result else None
    return result


# ---------------------------------------------------------------- optional LLM refine

def llm_refine(items: list[dict]) -> None:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key or not items:
        return
    try:
        payload = [{"i": n, "text": it["title"][:280]} for n, it in enumerate(items) if it["type"] == "news"][:40]
        if not payload:
            return
        prompt = (
            "次の各投稿について、ちいかわグッズに関する種別を restock/sighting/release/kuji/event/news から選び、"
            "店名(chain)・エリア(area)・品名(itemName)がわかれば入れて、JSON配列で返して。"
            'キーは i,type,chain,area,itemName。分からない項目は null。\n' + json.dumps(payload, ensure_ascii=False)
        )
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-5", "max_tokens": 2000,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=60,
        )
        text = r.json()["content"][0]["text"]
        m = re.search(r"\[.*\]", text, re.S)
        if not m:
            return
        for row in json.loads(m.group(0)):
            it = items[row["i"]]
            for k in ("type", "chain", "area", "itemName"):
                if row.get(k):
                    it[k] = row[k]
            it["confidence"] = max(it.get("confidence") or 0.4, 0.7)
    except Exception as e:  # noqa: BLE001
        log(f"llm_refine skipped: {e}")


# ---------------------------------------------------------------- main

def build_item(raw: dict) -> dict | None:
    text = raw.get("text", "")
    if len(text) < 8:
        return None
    title = raw.get("title") or text.strip().replace("\n", " ")
    if len(title) > 140:
        title = title[:139] + "…"
    typ = classify(text)
    if typ == "news" and raw.get("type_hint"):
        typ = raw["type_hint"]
    chain = raw.get("chain") or extract_chain(text)
    area = raw.get("area") or extract_area(text)
    try:
        when = dt.datetime.fromisoformat((raw.get("date") or now.isoformat()).replace("Z", "+00:00"))
    except Exception:  # noqa: BLE001
        when = now
    conf = 0.85 if raw["source_name"] != "Bluesky" else (0.6 if chain else 0.4)
    store_specific = bool(chain and (area or any(h in chain for h in STORE_HINTS)))
    return {
        "id": hashlib.sha1(raw["source_url"].encode()).hexdigest()[:16],
        "type": typ,
        "title": title,
        "summary": raw.get("summary"),
        "chain": chain,
        "area": area,
        "itemName": raw.get("itemName") or extract_item(text),
        "date": when.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sourceName": raw["source_name"],
        "sourceURL": raw["source_url"],
        "latitude": None,
        "longitude": None,
        "confidence": round(conf, 2),
        "_geo_query": f"{chain} {area} 日本".replace("None", "").strip() if store_specific else None,
    }


def main():
    raw = []
    raw += collect_bluesky(sources.get("bluesky_queries", []))
    raw += collect_rss(sources.get("rss", []),
                       sources.get("rss_keyword_filter", []),
                       sources.get("rss_trusted_hosts", []))
    log(f"collected {len(raw)} raw items")

    items: dict[str, dict] = {}
    variant_seen: dict[str, str] = {}  # 「…（ちいかわ）」等の色違いを1件に集約
    for r in raw:
        it = build_item(r)
        if not it:
            continue
        vkey = it["type"] + "|" + re.sub(r"[（(][^）)]*[）)]\s*$", "", it["title"]).strip()
        if vkey in variant_seen and variant_seen[vkey] != it["sourceURL"]:
            continue
        variant_seen[vkey] = it["sourceURL"]
        items[it["sourceURL"]] = it  # dedupe by URL

    # merge previous (keep still-recent ones)
    if OUT_FILE.exists():
        try:
            prev = json.loads(OUT_FILE.read_text("utf-8")).get("items", [])
            for p in prev:
                items.setdefault(p["sourceURL"], p)
        except Exception:  # noqa: BLE001
            pass

    merged = list(items.values())
    # expire old
    cutoff = now - dt.timedelta(days=EXPIRE_DAYS)
    merged = [m for m in merged if _parse(m["date"]) >= cutoff]

    llm_refine(merged)

    # geocode (only those with a specific-enough query, cached)
    cache = load_cache()
    for m in merged:
        q = m.pop("_geo_query", None)
        if m.get("latitude") is None and q:
            hit = geocode(q, cache)
            if hit:
                m["latitude"], m["longitude"] = hit
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), "utf-8")

    merged.sort(key=lambda m: m["date"], reverse=True)
    merged = merged[:MAX_ITEMS]

    OUT_FILE.write_text(json.dumps(
        {"generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "items": merged},
        ensure_ascii=False, indent=1), "utf-8")
    log(f"wrote {len(merged)} items -> {OUT_FILE}")


def _parse(s: str) -> dt.datetime:
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:  # noqa: BLE001
        return now


if __name__ == "__main__":
    main()
