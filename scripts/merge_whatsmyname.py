#!/usr/bin/env python3
"""
Скачивает WhatsMyName (wmn-data.json, CC BY-SA 4.0) и объединяет с data/sites.json.
Новые ключи: WMN_<имя>. См. лицензию в самом wmn-data.json.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

WMN_URL = "https://raw.githubusercontent.com/WebBreacher/WhatsMyName/main/wmn-data.json"
ROOT = Path(__file__).resolve().parents[1]
SITES_PATH = ROOT / "data" / "sites.json"


def sanitize_key(name: str, used: set[str]) -> str:
    base = re.sub(r"[^a-zA-Z0-9_]+", "_", name).strip("_")[:80]
    if not base:
        base = "wm"
    k = "WMN_" + base
    orig = k
    n = 0
    while k in used:
        n += 1
        k = f"{orig}_{n}"
    used.add(k)
    return k


def url_main_from(uri: str) -> str:
    u = urlparse(uri.replace("{}", "probe"))
    if u.scheme and u.netloc:
        return f"{u.scheme}://{u.netloc}/"
    return "https://example.com/"


def is_json_body(s: str) -> bool:
    s = s.strip()
    return s.startswith("{") or s.startswith("[")


def repl_account_placeholder(v):
    if isinstance(v, dict):
        return {k: repl_account_placeholder(x) for k, x in v.items()}
    if isinstance(v, list):
        return [repl_account_placeholder(x) for x in v]
    if isinstance(v, str):
        return v.replace("{account}", "{}")
    return v


def wmn_to_hunter(entry: dict, used_keys: set[str]) -> tuple[str, dict] | None:
    cat = (entry.get("cat") or "").strip()
    if cat == "xx NSFW xx":
        return None
    uri_check = entry.get("uri_check") or ""
    if "{account}" not in uri_check:
        return None

    key = sanitize_key(entry.get("name") or "site", used_keys)
    url = uri_check.replace("{account}", "{}")

    uri_pretty = entry.get("uri_pretty")
    if uri_pretty and "{account}" in str(uri_pretty):
        url_main = url_main_from(str(uri_pretty).replace("{account}", "x"))
    else:
        url_main = url_main_from(url)

    e_code = int(entry.get("e_code") or 200)
    e_string = (entry.get("e_string") or "").strip()
    m_string = (entry.get("m_string") or "").strip()
    m_code = int(entry.get("m_code") or 0)

    headers = entry.get("headers") or {}
    h: dict[str, str] = {}
    if isinstance(headers, dict):
        for a, b in headers.items():
            if isinstance(a, str) and isinstance(b, str):
                h[a] = b

    out: dict = {
        "url": url,
        "urlMain": url_main,
        "countries": ["global"],
        "category": cat or "misc",
    }

    post_body = entry.get("post_body")
    if post_body:
        pb_raw = str(post_body)
        if is_json_body(pb_raw):
            try:
                data = json.loads(pb_raw)
                out["request_payload"] = repl_account_placeholder(data)
            except json.JSONDecodeError:
                out["requestBody"] = pb_raw.replace("{account}", "{}")
        else:
            out["requestBody"] = pb_raw.replace("{account}", "{}")
        out["request_method"] = "POST"

    if h:
        out["headers"] = h

    err_msgs: list[str] = []
    if m_string:
        err_msgs.append(m_string)

    if e_string:
        out["errorType"] = "message"
        out["foundSubstring"] = e_string
        if err_msgs:
            out["errorMsg"] = err_msgs
        out["expectedHTTP"] = e_code
        if m_code:
            out["notFoundHTTP"] = m_code
    else:
        out["errorType"] = "status_code"
        out["expectedHTTP"] = e_code
        if err_msgs:
            out["errorType"] = "message"
            out["errorMsg"] = err_msgs
            if m_code:
                out["notFoundHTTP"] = m_code

    return key, out


def extra_sites() -> dict[str, dict]:
    return {
        "Gravatar_MD5": {
            "url": "https://www.gravatar.com/avatar/{}?d=404&s=200",
            "urlMain": "https://gravatar.com/",
            "errorType": "status_code",
            "expectedHTTP": 200,
            "regexCheck": "^[a-fA-F0-9]{32}$",
            "countries": ["global"],
            "category": "email",
        },
        "Phone_WaMe": {
            "url": "https://api.whatsapp.com/send?phone={}",
            "urlMain": "https://www.whatsapp.com/",
            "errorType": "message",
            "errorMsg": [
                "Phone number shared via url is invalid",
                "invalid phone number",
            ],
            "foundSubstring": "api.whatsapp.com/send?phone=",
            "countries": ["global"],
            "category": "phone",
        },
    }


def main() -> int:
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if src:
        wmn = json.loads(Path(src).read_text(encoding="utf-8"))
    else:
        with urlopen(WMN_URL, timeout=120) as r:
            wmn = json.loads(r.read().decode("utf-8"))

    wmn_sites = wmn.get("sites") or []
    if not wmn_sites:
        print("No sites in WMN file", file=sys.stderr)
        return 1

    merged: dict[str, dict] = {}
    if SITES_PATH.is_file():
        merged = json.loads(SITES_PATH.read_text(encoding="utf-8"))
        if not isinstance(merged, dict):
            print("sites.json must be an object", file=sys.stderr)
            return 1

    used = set(merged.keys())
    added = 0
    for ent in wmn_sites:
        if not isinstance(ent, dict):
            continue
        got = wmn_to_hunter(ent, used)
        if not got:
            continue
        k, h = got
        merged[k] = h
        added += 1

    for k, v in extra_sites().items():
        if k not in merged:
            merged[k] = v
            used.add(k)
            added += 1

    SITES_PATH.write_text(
        json.dumps(merged, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"WMN entries converted: {added}, total keys: {len(merged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
