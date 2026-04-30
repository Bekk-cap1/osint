"""Add more regional sites to the database."""
import json

EXTRA_SITES = {
    # === UZ - Uzbekistan ===
    "Daryo_UZ": {
        "url": "https://daryo.uz/user/{}",
        "urlMain": "https://daryo.uz",
        "errorType": "status_code",
        "countries": ["uz"],
        "category": "news"
    },
    "Zamin_UZ": {
        "url": "https://zamin.uz/user/{}",
        "urlMain": "https://zamin.uz",
        "errorType": "status_code",
        "countries": ["uz"],
        "category": "news"
    },
    "Mybazar_UZ": {
        "url": "https://mybazar.uz/user/{}",
        "urlMain": "https://mybazar.uz",
        "errorType": "status_code",
        "countries": ["uz"],
        "category": "marketplace"
    },
    "Humans_UZ": {
        "url": "https://humans.uz/user/{}",
        "urlMain": "https://humans.uz",
        "errorType": "status_code",
        "countries": ["uz"],
        "category": "fintech"
    },
    "Uzum_Market": {
        "url": "https://uzum.uz/seller/{}",
        "urlMain": "https://uzum.uz",
        "errorType": "status_code",
        "countries": ["uz"],
        "category": "marketplace"
    },
    "Platforma_UZ": {
        "url": "https://platforma.uz/user/{}",
        "urlMain": "https://platforma.uz",
        "errorType": "status_code",
        "countries": ["uz"],
        "category": "education"
    },
    "Ustoz_UZ": {
        "url": "https://ustoz.uz/user/{}",
        "urlMain": "https://ustoz.uz",
        "errorType": "status_code",
        "countries": ["uz"],
        "category": "education"
    },
    "Head_UZ": {
        "url": "https://head.uz/user/{}",
        "urlMain": "https://head.uz",
        "errorType": "status_code",
        "countries": ["uz"],
        "category": "jobs"
    },
    "Workly_UZ": {
        "url": "https://workly.uz/user/{}",
        "urlMain": "https://workly.uz",
        "errorType": "status_code",
        "countries": ["uz"],
        "category": "jobs"
    },

    # === RU - Russia / CIS ===
    "Avito": {
        "url": "https://www.avito.ru/user/{}",
        "urlMain": "https://www.avito.ru",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "marketplace"
    },
    "Wildberries": {
        "url": "https://www.wildberries.ru/seller/{}",
        "urlMain": "https://www.wildberries.ru",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "marketplace"
    },
    "DTF": {
        "url": "https://dtf.ru/u/{}",
        "urlMain": "https://dtf.ru",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "social"
    },
    "VC_ru": {
        "url": "https://vc.ru/u/{}",
        "urlMain": "https://vc.ru",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "social"
    },
    "Yandex_Zen": {
        "url": "https://dzen.ru/{}",
        "urlMain": "https://dzen.ru",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "social"
    },
    "Rutube": {
        "url": "https://rutube.ru/channel/{}/",
        "urlMain": "https://rutube.ru",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "video"
    },
    "Sports_ru": {
        "url": "https://www.sports.ru/profile/{}/",
        "urlMain": "https://www.sports.ru",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "sports"
    },
    "2GIS": {
        "url": "https://2gis.ru/user/{}",
        "urlMain": "https://2gis.ru",
        "errorType": "status_code",
        "countries": ["ru", "uz"],
        "category": "maps"
    },
    "HH_ru": {
        "url": "https://hh.ru/resume/{}",
        "urlMain": "https://hh.ru",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "jobs"
    },
    "Freelansim": {
        "url": "https://freelansim.ru/freelancers/{}",
        "urlMain": "https://freelansim.ru",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "jobs"
    },
    "Livejournal": {
        "url": "https://{}.livejournal.com",
        "urlMain": "https://www.livejournal.com",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "social"
    },
    "Yandex_Music": {
        "url": "https://music.yandex.ru/users/{}/playlists",
        "urlMain": "https://music.yandex.ru",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "music"
    },
    "Yandex_Market": {
        "url": "https://market.yandex.ru/user/{}/reviews",
        "urlMain": "https://market.yandex.ru",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "marketplace"
    },
    "Ozon": {
        "url": "https://www.ozon.ru/seller/{}/",
        "urlMain": "https://www.ozon.ru",
        "errorType": "status_code",
        "countries": ["ru"],
        "category": "marketplace"
    },

    # === CN - China ===
    "Xiaohongshu": {
        "url": "https://www.xiaohongshu.com/user/profile/{}",
        "urlMain": "https://www.xiaohongshu.com",
        "errorType": "status_code",
        "countries": ["cn"],
        "category": "social"
    },
    "Kuaishou": {
        "url": "https://www.kuaishou.com/profile/{}",
        "urlMain": "https://www.kuaishou.com",
        "errorType": "status_code",
        "countries": ["cn"],
        "category": "video"
    },
    "Douyin": {
        "url": "https://www.douyin.com/user/{}",
        "urlMain": "https://www.douyin.com",
        "errorType": "status_code",
        "countries": ["cn"],
        "category": "video"
    },
    "Baidu_Tieba": {
        "url": "https://tieba.baidu.com/home/main?un={}",
        "urlMain": "https://tieba.baidu.com",
        "errorType": "status_code",
        "countries": ["cn"],
        "category": "social"
    },
    "QQ_Zone": {
        "url": "https://user.qzone.qq.com/{}",
        "urlMain": "https://qzone.qq.com",
        "errorType": "status_code",
        "countries": ["cn"],
        "category": "social"
    },
    "Youku": {
        "url": "https://i.youku.com/i/{}",
        "urlMain": "https://www.youku.com",
        "errorType": "status_code",
        "countries": ["cn"],
        "category": "video"
    },
    "iQIYI": {
        "url": "https://www.iqiyi.com/u/{}",
        "urlMain": "https://www.iqiyi.com",
        "errorType": "status_code",
        "countries": ["cn"],
        "category": "video"
    },
    "Jianshu": {
        "url": "https://www.jianshu.com/u/{}",
        "urlMain": "https://www.jianshu.com",
        "errorType": "status_code",
        "countries": ["cn"],
        "category": "social"
    },
    "Juejin": {
        "url": "https://juejin.cn/user/{}",
        "urlMain": "https://juejin.cn",
        "errorType": "status_code",
        "countries": ["cn"],
        "category": "development"
    },
    "V2EX": {
        "url": "https://www.v2ex.com/member/{}",
        "urlMain": "https://www.v2ex.com",
        "errorType": "status_code",
        "countries": ["cn"],
        "category": "development"
    },

    # === KR - South Korea ===
    "KakaoStory": {
        "url": "https://story.kakao.com/{}",
        "urlMain": "https://story.kakao.com",
        "errorType": "status_code",
        "countries": ["kr"],
        "category": "social"
    },
    "Tistory": {
        "url": "https://{}.tistory.com",
        "urlMain": "https://www.tistory.com",
        "errorType": "status_code",
        "countries": ["kr"],
        "category": "social"
    },
    "Velog": {
        "url": "https://velog.io/@{}",
        "urlMain": "https://velog.io",
        "errorType": "status_code",
        "countries": ["kr"],
        "category": "development"
    },

    # === JP - Japan ===
    "Note_JP": {
        "url": "https://note.com/{}",
        "urlMain": "https://note.com",
        "errorType": "status_code",
        "countries": ["jp"],
        "category": "social"
    },
    "Niconico": {
        "url": "https://www.nicovideo.jp/user/{}",
        "urlMain": "https://www.nicovideo.jp",
        "errorType": "status_code",
        "countries": ["jp"],
        "category": "video"
    },
    "Qiita": {
        "url": "https://qiita.com/{}",
        "urlMain": "https://qiita.com",
        "errorType": "status_code",
        "countries": ["jp"],
        "category": "development"
    },
    "Zenn": {
        "url": "https://zenn.dev/{}",
        "urlMain": "https://zenn.dev",
        "errorType": "status_code",
        "countries": ["jp"],
        "category": "development"
    },

    # === TR - Turkey ===
    "Eksi_Sozluk": {
        "url": "https://eksisozluk.com/biri/{}",
        "urlMain": "https://eksisozluk.com",
        "errorType": "status_code",
        "countries": ["tr"],
        "category": "social"
    },
    "Sahibinden": {
        "url": "https://www.sahibinden.com/profil/{}",
        "urlMain": "https://www.sahibinden.com",
        "errorType": "status_code",
        "countries": ["tr"],
        "category": "marketplace"
    },
    "Hepsiburada": {
        "url": "https://www.hepsiburada.com/magaza/{}",
        "urlMain": "https://www.hepsiburada.com",
        "errorType": "status_code",
        "countries": ["tr"],
        "category": "marketplace"
    },

    # === Global additions (popular sites not in Sherlock) ===
    "WhatsApp": {
        "url": "https://wa.me/{}",
        "urlMain": "https://www.whatsapp.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "messenger"
    },
    "Signal": {
        "url": "https://signal.me/#p/{}",
        "urlMain": "https://signal.org",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "messenger"
    },
    "Notion": {
        "url": "https://www.notion.so/{}",
        "urlMain": "https://www.notion.so",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "productivity"
    },
    "Calendly": {
        "url": "https://calendly.com/{}",
        "urlMain": "https://calendly.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "productivity"
    },
    "Substack": {
        "url": "https://{}.substack.com",
        "urlMain": "https://substack.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "social"
    },
    "Hashnode": {
        "url": "https://hashnode.com/@{}",
        "urlMain": "https://hashnode.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "development"
    },
    "ProductHunt": {
        "url": "https://www.producthunt.com/@{}",
        "urlMain": "https://www.producthunt.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "development"
    },
    "Figma": {
        "url": "https://www.figma.com/@{}",
        "urlMain": "https://www.figma.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "design"
    },
    "Vercel": {
        "url": "https://vercel.com/{}",
        "urlMain": "https://vercel.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "development"
    },
    "HuggingFace": {
        "url": "https://huggingface.co/{}",
        "urlMain": "https://huggingface.co",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "development"
    },
    "Buy_Me_A_Coffee": {
        "url": "https://www.buymeacoffee.com/{}",
        "urlMain": "https://www.buymeacoffee.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "other"
    },
    "Gumroad": {
        "url": "https://{}.gumroad.com",
        "urlMain": "https://gumroad.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "marketplace"
    },
    "Kaggle": {
        "url": "https://www.kaggle.com/{}",
        "urlMain": "https://www.kaggle.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "development"
    },
    "Canva": {
        "url": "https://www.canva.com/p/{}/",
        "urlMain": "https://www.canva.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "design"
    },
    "Wix": {
        "url": "https://{}.wixsite.com",
        "urlMain": "https://www.wix.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "other"
    },
    "Carrd": {
        "url": "https://{}.carrd.co",
        "urlMain": "https://carrd.co",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "other"
    },
    "Linktree": {
        "url": "https://linktr.ee/{}",
        "urlMain": "https://linktr.ee",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "social"
    },
    "Twitch": {
        "url": "https://www.twitch.tv/{}",
        "urlMain": "https://www.twitch.tv",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "video"
    },
    "Kick": {
        "url": "https://kick.com/{}",
        "urlMain": "https://kick.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "video"
    },
    "Rumble": {
        "url": "https://rumble.com/user/{}",
        "urlMain": "https://rumble.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "video"
    },
    "Letterboxd": {
        "url": "https://letterboxd.com/{}",
        "urlMain": "https://letterboxd.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "other"
    },
    "Goodreads": {
        "url": "https://www.goodreads.com/user/show/{}",
        "urlMain": "https://www.goodreads.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "other"
    },
    "Imgur": {
        "url": "https://imgur.com/user/{}",
        "urlMain": "https://imgur.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "photo"
    },
    "Giphy": {
        "url": "https://giphy.com/channel/{}",
        "urlMain": "https://giphy.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "photo"
    },
    "TradingView": {
        "url": "https://www.tradingview.com/u/{}/",
        "urlMain": "https://www.tradingview.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "finance"
    },
    "Binance": {
        "url": "https://www.binance.com/en/feed/profile/{}",
        "urlMain": "https://www.binance.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "finance"
    },
    "Etsy": {
        "url": "https://www.etsy.com/shop/{}",
        "urlMain": "https://www.etsy.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "marketplace"
    },
    "Fiverr": {
        "url": "https://www.fiverr.com/{}",
        "urlMain": "https://www.fiverr.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "jobs"
    },
    "Upwork": {
        "url": "https://www.upwork.com/freelancers/{}",
        "urlMain": "https://www.upwork.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "jobs"
    },
    "Freelancer": {
        "url": "https://www.freelancer.com/u/{}",
        "urlMain": "https://www.freelancer.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "jobs"
    },
    "AngelList": {
        "url": "https://angel.co/u/{}",
        "urlMain": "https://angel.co",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "jobs"
    },
    "Crunchbase": {
        "url": "https://www.crunchbase.com/person/{}",
        "urlMain": "https://www.crunchbase.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "business"
    },
    "F6S": {
        "url": "https://www.f6s.com/{}",
        "urlMain": "https://www.f6s.com",
        "errorType": "status_code",
        "countries": ["global"],
        "category": "business"
    },
}

def main():
    with open("data/sites.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    added = 0
    for name, info in EXTRA_SITES.items():
        if name not in data:
            data[name] = info
            added += 1
    
    with open("data/sites.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Added {added} new sites. Total: {len(data)}")
    
    # Country stats
    country_counts = {}
    for name, info in data.items():
        for c in info.get("countries", ["global"]):
            country_counts[c] = country_counts.get(c, 0) + 1
    
    print("\nSites per country tag:")
    for c, count in sorted(country_counts.items(), key=lambda x: -x[1]):
        print(f"  {c}: {count}")

if __name__ == "__main__":
    main()
