#!/usr/bin/env python3
"""Скачать Sherlock data.json, починить битый блок Telegram/Threads, пересобрать data/sites.json."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SHERLOCK_URL = (
    "https://raw.githubusercontent.com/sherlock-project/sherlock/"
    "master/sherlock_project/resources/data.json"
)

# Апстрим JSON сломан: внутрь Telegram попали поля Threads
BAD_TELEGRAM = """"Telegram": {
 "errorMsg": [
 " Telegram Messenger ",
 "If you have Telegram, you can contact Threads • Log in ",
 "errorType": "message",
 "headers": {
 "Sec-Fetch-Mode": "navigate"
 },
 "url": "https://www.threads.net/@{}",
 "urlMain": "https://www.threads.net/",
 "username_claimed": "zuck"
 },"""

GOOD_TELEGRAM_THREADS = """"Telegram": {
 "errorMsg": [
 " Telegram Messenger ",
 "If you have <strong>Telegram</strong>, you can contact"
 ],
 "errorType": "message",
 "url": "https://t.me/{}",
 "urlMain": "https://t.me/",
 "username_claimed": "durov"
 },
 "Threads": {
 "errorMsg": "Log in",
 "errorType": "message",
 "headers": {
 "Sec-Fetch-Mode": "navigate"
 },
 "url": "https://www.threads.net/@{}",
 "urlMain": "https://www.threads.net/",
 "username_claimed": "zuck"
 },"""

# Hunter: свои рабочие записи (перезаписывают Sherlock)
HUNTER_PATCHES = {
    "Instagram": {
        "url": "https://www.instagram.com/{}/",
        "urlMain": "https://www.instagram.com/",
        "errorType": "status_code",
        "urlProbe": "https://www.instagram.com/api/v1/users/web_profile_info/?username={}",
        "headers": {
            "X-IG-App-ID": "936619743392459",
            "Accept": "application/json",
            "Referer": "https://www.instagram.com/",
            "X-Requested-With": "XMLHttpRequest",
        },
        "countries": ["global"],
        "category": "social",
    },
    "Twitter_X": {
        "url": "https://x.com/{}",
        "urlMain": "https://x.com/",
        "errorType": "message",
        "urlProbe": "https://api.fxtwitter.com/{}",
        "errorMsg": [
            '"code":404',
            "USER_NOT_FOUND",
            "Sorry, that page does not exist",
        ],
        "countries": ["global"],
        "category": "social",
    },
}

# Доп. площадки (если ещё нет в базе после Sherlock)
MORE_SITES = {
    "Pinterest": {
        "url": "https://www.pinterest.com/{}/",
        "urlMain": "https://www.pinterest.com/",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "social",
    },
    "Vimeo_user": {
        "url": "https://vimeo.com/{}",
        "urlMain": "https://vimeo.com/",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "video",
    },
    "OpenSea": {
        "url": "https://opensea.io/{}",
        "urlMain": "https://opensea.io/",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "other",
    },
    "MyAnimeList": {
        "url": "https://myanimelist.net/profile/{}",
        "urlMain": "https://myanimelist.net/",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "other",
    },
    "SlideShare": {
        "url": "https://www.slideshare.net/{}",
        "urlMain": "https://www.slideshare.net/",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "other",
    },
    "PasteEE": {
        "url": "https://paste.ee/u/{}",
        "urlMain": "https://paste.ee/",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "development",
    },
    "Monkeytype": {
        "url": "https://monkeytype.com/profile/{}",
        "urlMain": "https://monkeytype.com/",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "gaming",
    },
    "Donationalerts": {
        "url": "https://www.donationalerts.com/r/{}",
        "urlMain": "https://www.donationalerts.com/",
        "errorType": "status_code",
        "countries": ["global", "ru"],
        "category": "other",
    },
    "Boosty": {
        "url": "https://boosty.to/{}",
        "urlMain": "https://boosty.to/",
        "errorType": "status_code",
        "countries": ["global", "ru"],
        "category": "other",
    },
    "LiveLib": {
        "url": "https://www.livelib.ru/reader/{}",
        "urlMain": "https://www.livelib.ru/",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "other",
    },
    "TenChat": {
        "url": "https://tenchat.ru/{}",
        "urlMain": "https://tenchat.ru/",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "social",
    },
    "Giters": {
        "url": "https://giters.com/{}",
        "urlMain": "https://giters.com/",
        "errorType": "status_code",
        "countries": ["global", "cn"],
        "category": "development",
    },
    "Perplexity": {
        "url": "https://www.perplexity.ai/collections/{}",
        "urlMain": "https://www.perplexity.ai/",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "other",
    },
    "MastodonSocial": {
        "url": "https://mastodon.social/@{}",
        "urlMain": "https://mastodon.social/",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "social",
    },
}


def main():
    try:
        import urllib.request

        raw = urllib.request.urlopen(SHERLOCK_URL, timeout=90).read().decode("utf-8")
    except Exception as e:
        print("Download failed:", e)
        sys.exit(1)

    if BAD_TELEGRAM in raw:
        raw = raw.replace(BAD_TELEGRAM, GOOD_TELEGRAM_THREADS)
        print("Patched Telegram/Threads in upstream JSON")
    else:
        print("Telegram block not found or already fixed")

    fixed = ROOT / "scripts" / "sherlock_fixed.json"
    fixed.write_text(raw, encoding="utf-8")

    sys.path.insert(0, str(ROOT / "scripts"))
    import convert_sherlock  # noqa: E402

    out = ROOT / "data" / "sites.json"
    convert_sherlock.convert(str(fixed), str(out))

    data = json.loads(out.read_text(encoding="utf-8"))
    for k, v in HUNTER_PATCHES.items():
        data[k] = v

    spec = importlib.util.spec_from_file_location(
        "add_regional", ROOT / "scripts" / "add_regional.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    added = 0
    for name, info in mod.EXTRA_SITES.items():
        if name not in data:
            data[name] = info
            added += 1

    more = 0
    for name, info in MORE_SITES.items():
        if name not in data:
            data[name] = info
            more += 1

    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Regional added (new only): {added}")
    print(f"More sites added: {more}")
    print(f"Total sites: {len(data)}")


if __name__ == "__main__":
    main()
