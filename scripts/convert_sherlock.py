"""Convert Sherlock's data.json to Hunter format with country tags."""
import json
import sys

# Country mappings based on site domain/name
COUNTRY_TAGS = {
    # UZ - Uzbekistan / Central Asia
    "uz": [
        "olx.uz", "sello.uz", "kun.uz", "daryo.uz", "zamin.uz",
        "champion.uz", "hh.uz", "humans.uz"
    ],
    # RU - Russia / CIS
    "ru": [
        "vk.com", "ok.ru", "mail.ru", "yandex", "pikabu", "habr",
        "drive2", "livejournal", "avito", "2gis", "wildberries",
        "rutube", "tjournal", "dtf.ru", "vc.ru", "freelansim",
        "fl.ru", "moikrug", "sports.ru", "coub"
    ],
    # CN - China
    "cn": [
        "weibo", "douyin", "bilibili", "zhihu", "baidu",
        "qq.com", "xiaohongshu", "douban", "csdn", "gitee",
        "163.com", "sina.com", "weixin", "wechat", "tiktok.cn",
        "kuaishou", "youku", "iqiyi"
    ],
    # JP - Japan
    "jp": [
        "nicovideo", "pixiv", "line.me", "booth.pm", "note.com",
        "aniworld"
    ],
    # KR - Korea
    "kr": [
        "naver", "kakao", "tistory"
    ],
    # DE - Germany
    "de": [
        "xing.com", "autofrage", "gutefrage", "motor-talk",
        "kleinanzeigen"
    ],
    # TR - Turkey
    "tr": [
        "turkiye", "sahibinden", "hepsiburada"
    ],
    # CZ - Czech
    "cz": [
        "bazar.cz", "avizo.cz", "lide.cz"
    ],
    # IR - Iran
    "ir": [
        "aparat", "virgool"
    ],
    # BR - Brazil
    "br": [
        "koo.app", "elo7", "mercadolivre"
    ],
}

def get_countries(name, url):
    """Determine country tags for a site."""
    url_lower = url.lower() if url else ""
    name_lower = name.lower()
    
    countries = []
    for country, keywords in COUNTRY_TAGS.items():
        for kw in keywords:
            if kw in url_lower or kw in name_lower:
                countries.append(country)
                break
    
    if not countries:
        countries = ["global"]
    
    return countries

def get_category(name, url):
    """Determine category for a site."""
    url_lower = url.lower() if url else ""
    name_lower = name.lower()
    
    dev_sites = ["github", "gitlab", "bitbucket", "codepen", "replit", "npm", "pypi",
                 "docker", "stackoverflow", "hackernews", "dev.to", "medium",
                 "arduino", "raspberry", "hackerrank", "leetcode", "codeforces",
                 "atcoder", "codechef", "codewars", "exercism", "freecodecamp"]
    social_sites = ["facebook", "instagram", "twitter", "tiktok", "snapchat",
                    "reddit", "tumblr", "pinterest", "linkedin", "bluesky", "mastodon",
                    "threads"]
    gaming_sites = ["steam", "xbox", "playstation", "epic", "twitch", "chess.com",
                    "lichess", "roblox", "minecraft", "fortnite", "battlenet"]
    messenger_sites = ["telegram", "discord", "whatsapp", "signal", "viber",
                       "line", "wechat", "qq", "kakao"]
    music_sites = ["spotify", "soundcloud", "bandcamp", "deezer", "last.fm",
                   "audiojungle", "mixcloud"]
    video_sites = ["youtube", "vimeo", "dailymotion", "rutube", "bilibili",
                   "nicovideo", "twitch"]
    photo_sites = ["flickr", "500px", "unsplash", "deviantart", "artstation",
                   "behance", "dribbble", "pixiv"]
    
    for kw in dev_sites:
        if kw in name_lower or kw in url_lower:
            return "development"
    for kw in social_sites:
        if kw in name_lower or kw in url_lower:
            return "social"
    for kw in gaming_sites:
        if kw in name_lower or kw in url_lower:
            return "gaming"
    for kw in messenger_sites:
        if kw in name_lower or kw in url_lower:
            return "messenger"
    for kw in music_sites:
        if kw in name_lower or kw in url_lower:
            return "music"
    for kw in video_sites:
        if kw in name_lower or kw in url_lower:
            return "video"
    for kw in photo_sites:
        if kw in name_lower or kw in url_lower:
            return "photo"
    
    return "other"

def convert(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Remove $schema key
    data.pop("$schema", None)
    
    result = {}
    for name, info in data.items():
        entry = {
            "url": info.get("url", ""),
            "urlMain": info.get("urlMain", ""),
            "errorType": info.get("errorType", "status_code"),
        }
        
        if info.get("urlProbe"):
            entry["urlProbe"] = info["urlProbe"]
        
        if info.get("errorMsg"):
            msg = info["errorMsg"]
            if isinstance(msg, str):
                entry["errorMsg"] = [msg]
            elif isinstance(msg, list):
                entry["errorMsg"] = msg
        
        if info.get("errorUrl"):
            entry["errorUrl"] = info["errorUrl"]
        
        if info.get("regexCheck"):
            entry["regexCheck"] = info["regexCheck"]
        
        if info.get("headers"):
            entry["headers"] = info["headers"]
        
        if info.get("request_method"):
            entry["request_method"] = info["request_method"]

        if info.get("request_payload") is not None:
            entry["request_payload"] = info["request_payload"]
        
        entry["countries"] = get_countries(name, info.get("url", "") + " " + info.get("urlMain", ""))
        entry["category"] = get_category(name, info.get("url", "") + " " + info.get("urlMain", ""))
        
        # Skip NSFW unless explicitly needed
        if info.get("isNSFW"):
            entry["nsfw"] = True
        
        result[name] = entry
    
    # Add regional sites not in Sherlock
    extra_sites = {
        "Telegram": {
            "url": "https://t.me/{}",
            "urlMain": "https://t.me",
            "errorType": "message",
            "errorMsg": ["If you have <strong>Telegram</strong>, you can contact"],
            "countries": ["global", "uz", "ru", "ir"],
            "category": "messenger"
        },
        "OLX_UZ": {
            "url": "https://www.olx.uz/d/list/user/{}",
            "urlMain": "https://www.olx.uz",
            "errorType": "status_code",
            "countries": ["uz"],
            "category": "marketplace"
        },
        "Sello_UZ": {
            "url": "https://sello.uz/user/{}",
            "urlMain": "https://sello.uz",
            "errorType": "status_code",
            "countries": ["uz"],
            "category": "marketplace"
        },
        "HH_UZ": {
            "url": "https://hh.uz/resume/{}",
            "urlMain": "https://hh.uz",
            "errorType": "status_code",
            "countries": ["uz"],
            "category": "jobs"
        },
        "VK": {
            "url": "https://vk.com/{}",
            "urlMain": "https://vk.com",
            "errorType": "message",
            "errorMsg": ["Unfortunately, this page is not available"],
            "countries": ["ru", "uz"],
            "category": "social"
        },
        "OK_ru": {
            "url": "https://ok.ru/{}",
            "urlMain": "https://ok.ru",
            "errorType": "status_code",
            "countries": ["ru"],
            "category": "social"
        },
        "Mail_ru": {
            "url": "https://my.mail.ru/mail/{}/",
            "urlMain": "https://mail.ru",
            "errorType": "status_code",
            "countries": ["ru"],
            "category": "social"
        },
        "Pikabu": {
            "url": "https://pikabu.ru/@{}",
            "urlMain": "https://pikabu.ru",
            "errorType": "status_code",
            "countries": ["ru"],
            "category": "social"
        },
        "Habr": {
            "url": "https://habr.com/ru/users/{}/",
            "urlMain": "https://habr.com",
            "errorType": "status_code",
            "countries": ["ru"],
            "category": "development"
        },
        "Drive2": {
            "url": "https://www.drive2.ru/users/{}",
            "urlMain": "https://www.drive2.ru",
            "errorType": "status_code",
            "countries": ["ru"],
            "category": "auto"
        },
        "Weibo": {
            "url": "https://weibo.com/n/{}",
            "urlMain": "https://weibo.com",
            "errorType": "status_code",
            "countries": ["cn"],
            "category": "social"
        },
        "Bilibili": {
            "url": "https://space.bilibili.com/{}",
            "urlMain": "https://bilibili.com",
            "errorType": "status_code",
            "countries": ["cn"],
            "category": "video"
        },
        "Zhihu": {
            "url": "https://www.zhihu.com/people/{}",
            "urlMain": "https://www.zhihu.com",
            "errorType": "status_code",
            "countries": ["cn"],
            "category": "social"
        },
        "CSDN": {
            "url": "https://blog.csdn.net/{}",
            "urlMain": "https://csdn.net",
            "errorType": "status_code",
            "countries": ["cn"],
            "category": "development"
        },
        "Gitee": {
            "url": "https://gitee.com/{}",
            "urlMain": "https://gitee.com",
            "errorType": "status_code",
            "countries": ["cn"],
            "category": "development"
        },
        "Douban": {
            "url": "https://www.douban.com/people/{}",
            "urlMain": "https://www.douban.com",
            "errorType": "status_code",
            "countries": ["cn"],
            "category": "social"
        },
        "Naver": {
            "url": "https://blog.naver.com/{}",
            "urlMain": "https://www.naver.com",
            "errorType": "status_code",
            "countries": ["kr"],
            "category": "social"
        },
        "Pixiv": {
            "url": "https://www.pixiv.net/users/{}",
            "urlMain": "https://www.pixiv.net",
            "errorType": "status_code",
            "countries": ["jp"],
            "category": "photo"
        },
        "Kun_UZ": {
            "url": "https://kun.uz/user/{}",
            "urlMain": "https://kun.uz",
            "errorType": "status_code",
            "countries": ["uz"],
            "category": "news"
        },
        "Champion_UZ": {
            "url": "https://champion.uz/user/{}",
            "urlMain": "https://champion.uz",
            "errorType": "status_code",
            "countries": ["uz"],
            "category": "sports"
        }
    }
    
    # Merge (don't overwrite existing)
    for name, info in extra_sites.items():
        if name not in result:
            result[name] = info
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Converted {len(result)} sites to {output_path}")
    
    # Stats
    country_counts = {}
    for name, info in result.items():
        for c in info.get("countries", ["global"]):
            country_counts[c] = country_counts.get(c, 0) + 1
    
    print("\nSites per country tag:")
    for c, count in sorted(country_counts.items(), key=lambda x: -x[1]):
        print(f"  {c}: {count}")

if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "sherlock_data.json"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "../data/sites.json"
    convert(input_path, output_path)
