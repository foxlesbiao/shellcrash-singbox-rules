#!/usr/bin/env python3
"""
Generate sing-box FULL ruleset + policy group template (全量版).
整合 5 个规则仓库的 ALL sing-box 规则集 + 完整策略组，生成 Custom_All_full 模板。

设计目标: x86 软路由 (>=2GB 内存)。所有规则集用 remote URL 引用(启动时按需下载)。
senshinya 679 分类全部包含 + 其他仓库全部规则集。

来源:
1. senshinya/singbox_ruleset           - blackmatrix7 全集 679 分类
2. REIJI007/AdBlock_Rule_For_Sing-box  - 广告拦截 (每20分钟更新)
3. cmontage/proxyrules-cm              - GFW/AI/Google/Netflix 等
4. Dreista/sing-box-rule-set-cn        - 中国大陆域名/IP (每日更新)
5. Aethersailor/Custom_OpenClash_Rules - 自定义直连/代理/Steam (本仓库 .list 转)

输出:
- singbox/Custom_All_full.json - sing-box 完整模板 (策略组 + 规则 + 全部 rule_set)
"""
import json
import os
import urllib.request

# ============ 配置 ============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 脚本在仓库根目录，输出到同目录 singbox/
OUT_DIR = os.path.join(BASE_DIR, "singbox")
os.makedirs(OUT_DIR, exist_ok=True)

CDN = "https://testingcf.jsdelivr.net/gh"

# ============ senshinya 679 分类 ============
def get_senshinya_cats():
    """获取 senshinya 全部分类（在线拉取，失败用本地缓存）"""
    cats_path = os.path.join(BASE_DIR, "singbox", "senshinya_cats.txt")
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/senshinya/singbox_ruleset/contents/rule",
            headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            cats = [f["name"] for f in data if f["type"] == "dir"]
            with open(cats_path, "w") as f:
                f.write("\n".join(cats))
            return cats
    except Exception:
        if os.path.exists(cats_path):
            return open(cats_path).read().splitlines()
        return []

# ============ 分类映射到策略组 ============
# 国内域名/IP → 直连
CN_KEYWORDS = [
    "12306", "AirChina", "Alibaba", "Baidu", "BaiduCloud", "BiliBili", "China",
    "CloudMusic", "DingTalk", "Douban", "DouYu", "Gitee", "Huawei", "JianShu",
    "JingDong", "KuaiShou", "Meituan", "MIUI", "Migu", "NetEase", "QQ",
    "Sina", "Tencent", "Weibo", "WeiBo", "Xiaomi", "Zhihu", "IP", "Mainland",
]
# 广告/拦截 → REJECT
AD_KEYWORDS = ["Ads", "Ad", "Advertising", "Tracking", "Tracker", "Malware", "Phishing", "Spam"]
# 流媒体 → 媒体组
MEDIA_KEYWORDS = ["Netflix", "YouTube", "Disney", "Prime", "HBO", "Hulu", "AppleTV",
                  "TikTok", "Twitch", "Spotify", "Deezer", "Pandora", "SoundCloud",
                  "Dailymotion", "Vimeo", "BilibiliIntl", "BiliBiliIntl", "Tubi", "Peacock"]
# AI → AI组
AI_KEYWORDS = ["OpenAI", "Anthropic", "Claude", "Gemini", "BardAI", "Copilot", "ChatGPT", "Midjourney", "Perplexity"]
# 游戏 → 游戏组
GAME_KEYWORDS = ["Steam", "Epic", "Origin", "PlayStation", "Xbox", "Nintendo", "Riot",
                 "EA", "Ubisoft", "GOG", "Blizzard", "Battle", "Rockstar", "2K", "Capcom", "Konami", "Square"]

def classify(cat):
    """分类规则集到策略组"""
    if any(k in cat for k in CN_KEYWORDS):
        return "CN"
    if any(k in cat for k in AD_KEYWORDS):
        return "AD"
    if any(k in cat for k in MEDIA_KEYWORDS):
        return "MEDIA"
    if any(k in cat for k in AI_KEYWORDS):
        return "AI"
    if any(k in cat for k in GAME_KEYWORDS):
        return "GAME"
    return "PROXY"

# ============ 规则集定义 ============
def build_rule_sets(senshinya_cats):
    """构建全部规则集定义"""
    rule_sets = []

    # 1. senshinya 全部分类
    for cat in senshinya_cats:
        rule_sets.append({
            "tag": f"ss_{cat}",
            "type": "remote",
            "format": "binary",
            "path": f"./ruleset/ss_{cat}.srs",
            "url": f"{CDN}/senshinya/singbox_ruleset@main/rule/{cat}/{cat}.srs",
        })

    # 2. REIJI007 广告
    rule_sets.append({
        "tag": "ads",
        "type": "remote",
        "format": "binary",
        "path": "./ruleset/ads.srs",
        "url": f"{CDN}/REIJI007/AdBlock_Rule_For_Sing-box@main/adblock_reject.srs",
    })

    # 3. cmontage (clash yaml, format: source)
    cmontage_rules = [
        ("GFW", "Clash/PROXY/GFW.yaml"),
        ("cm_AI", "Clash/PROXY/AI.yaml"),
        ("cm_ChatAI", "Clash/PROXY/ChatAI.yaml"),
        ("cm_Google", "Clash/PROXY/Google.yaml"),
        ("cm_Netflix", "Clash/PROXY/Netflix.yaml"),
        ("cm_Game", "Clash/PROXY/Game.yaml"),
        ("cm_Paypal", "Clash/PROXY/Paypal.yaml"),
        ("cm_China", "Clash/PROXY/China.yaml"),
        ("cm_Apple", "Clash/DIRECT/Apple.yaml"),
        ("cm_ChinaDIRECT", "Clash/DIRECT/China.yaml"),
        ("cm_ChinaIPs", "Clash/DIRECT/ChinaIPs.yaml"),
        ("cm_Microsoft", "Clash/DIRECT/Microsoft.yaml"),
    ]
    for tag, path in cmontage_rules:
        rule_sets.append({
            "tag": tag,
            "type": "remote",
            "format": "source",
            "path": f"./ruleset/{tag}.json",
            "url": f"{CDN}/cmontage/proxyrules-cm@main/{path}",
        })

    # 4. Dreista 中国大陆 (rule-set 分支)
    dreista_rules = [
        ("cn", "accelerated-domains.china.conf.srs"),
        ("cnip", "apnic-cn-ipv4.srs"),
        ("cn-gfw", "filter.txt.srs"),
        ("cn-apple", "apple.china.conf.srs"),
        ("cn-google", "google.china.conf.srs"),
        ("cn-chnroutes", "chnroutes.txt.srs"),
    ]
    for tag, fname in dreista_rules:
        rule_sets.append({
            "tag": tag,
            "type": "remote",
            "format": "binary",
            "path": f"./ruleset/{tag}.srs",
            "url": f"{CDN}/Dreista/sing-box-rule-set-cn@rule-set/{fname}",
        })

    # 5. Aethersailor 本仓库 (remote，从 GitHub 拉取)
    # 这些 .srs 由 update_asailor_rules.sh 生成并 push 到本仓库
    as_rules = [
        ("custom-direct", "Custom_Direct.srs"),
        ("custom-proxy", "Custom_Proxy.srs"),
        ("steam-cdn", "Steam_CDN.srs"),
        ("game-download-cdn", "Game_Download_CDN.srs"),
    ]
    for tag, fname in as_rules:
        rule_sets.append({
            "tag": tag,
            "type": "remote",
            "format": "binary",
            "path": f"./ruleset/{tag}.srs",
            "url": f"{CDN}/foxlesbiao/shellcrash-singbox-rules@main/ruleset/{fname}",
        })

    return rule_sets

# ============ 策略组 ============
def build_outbounds():
    return [
        {"tag": "🚀 节点选择", "type": "selector", "outbounds": ["♻️ 自动选择", "🎯 本地直连", "🇭🇰 香港节点", "🇺🇸 美国节点", "🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇹🇼 台湾节点", "🇰🇷 韩国节点", "🐟 漏网之鱼"]},
        {"tag": "♻️ 自动选择", "type": "urltest", "interval": "2m", "use_all_providers": True},
        {"tag": "🤖 AI 平台", "type": "selector", "outbounds": ["🚀 节点选择", "🎯 本地直连"]},
        {"tag": "🎬 奈飞视频", "type": "selector", "outbounds": ["🚀 节点选择", "🎯 本地直连"]},
        {"tag": "▶️ 油管视频", "type": "selector", "outbounds": ["🚀 节点选择", "🎯 本地直连"]},
        {"tag": "🌍 国际媒体", "type": "selector", "outbounds": ["🚀 节点选择", "🎯 本地直连"]},
        {"tag": "🎮 外服游戏", "type": "selector", "outbounds": ["🚀 节点选择", "🎯 本地直连"]},
        {"tag": "🦾 Steam平台", "type": "selector", "outbounds": ["🎯 本地直连", "🚀 节点选择"]},
        {"tag": "🀄️ 国内流量", "type": "selector", "outbounds": ["🎯 本地直连", "🚀 节点选择"]},
        {"tag": "🛑 广告拦截", "type": "selector", "outbounds": ["⛔ 禁止连接", "🎯 本地直连"]},
        {"tag": "⛔ 禁止连接", "type": "block"},
        {"tag": "🎯 本地直连", "type": "direct"},
        {"tag": "🐟 漏网之鱼", "type": "selector", "outbounds": ["🚀 节点选择", "🎯 本地直连"]},
        {"tag": "GLOBAL", "type": "selector", "outbounds": ["🚀 节点选择", "🎯 本地直连"]},
        {"tag": "🇭🇰 香港节点", "type": "urltest", "interval": "2m", "use_all_providers": True, "include": "(?i)(🇭🇰|港|hk|hongkong)"},
        {"tag": "🇺🇸 美国节点", "type": "urltest", "interval": "2m", "use_all_providers": True, "include": "(?i)(🇺🇸|美|us|united)"},
        {"tag": "🇯🇵 日本节点", "type": "urltest", "interval": "2m", "use_all_providers": True, "include": "(?i)(🇯🇵|日|jp|japan)"},
        {"tag": "🇸🇬 新加坡节点", "type": "urltest", "interval": "2m", "use_all_providers": True, "include": "(?i)(🇸🇬|新加坡|sg|singapore)"},
        {"tag": "🇹🇼 台湾节点", "type": "urltest", "interval": "2m", "use_all_providers": True, "include": "(?i)(🇹🇼|台|tw|taiwan)"},
        {"tag": "🇰🇷 韩国节点", "type": "urltest", "interval": "2m", "use_all_providers": True, "include": "(?i)(🇰🇷|韩|kr|korea)"},
    ]

# ============ 路由规则 ============
def build_rules(senshinya_cats):
    """构建路由规则（按分类分组引用）"""
    groups = {"CN": [], "AD": [], "MEDIA": [], "AI": [], "GAME": [], "PROXY": []}
    for cat in senshinya_cats:
        groups[classify(cat)].append(f"ss_{cat}")

    rules = [
        {"action": "sniff"},
        {"protocol": "dns", "action": "hijack-dns"},
        {"ip_is_private": True, "outbound": "🎯 本地直连"},
        {"protocol": "quic", "action": "reject", "no_drop": True},
        {"protocol": "bittorrent", "action": "reject"},
        # 国内直连（Dreista + senshinya CN 分类 + cmontage）
        {"rule_set": ["cn", "cnip", "cn-chnroutes", "cn-apple", "cn-google", "cm_China", "cm_ChinaIPs", "cm_ChinaDIRECT", "cm_Apple", "cm_Microsoft"] + groups["CN"], "outbound": "🀄️ 国内流量"},
        # 广告拦截
        {"rule_set": ["ads"] + groups["AD"], "outbound": "🛑 广告拦截"},
        # 流媒体
        {"rule_set": ["ss_Netflix", "ss_PrimeVideo", "ss_HBO", "ss_Hulu", "ss_AppleTV", "cm_Netflix"], "outbound": "🎬 奈飞视频"},
        {"rule_set": ["ss_YouTube", "cm_Google"], "outbound": "▶️ 油管视频"},
        {"rule_set": ["ss_Disney", "ss_TikTok", "ss_Twitch", "ss_Spotify"] + groups["MEDIA"], "outbound": "🌍 国际媒体"},
        # AI 平台
        {"rule_set": ["ss_OpenAI", "ss_Anthropic", "ss_Gemini", "ss_Copilot", "cm_AI", "cm_ChatAI"] + groups["AI"], "outbound": "🤖 AI 平台"},
        # 游戏
        {"rule_set": ["ss_Steam"], "outbound": "🦾 Steam平台"},
        {"rule_set": ["ss_Epic", "ss_PlayStation", "ss_Xbox", "ss_Nintendo", "ss_Riot", "cm_Game"] + groups["GAME"], "outbound": "🎮 外服游戏"},
        # GFW + 其他
        {"rule_set": ["GFW", "cn-gfw", "cm_Paypal"] + groups["PROXY"], "outbound": "🚀 节点选择"},
        # 兜底
        {"outbound": "🐟 漏网之鱼"}
    ]
    return rules

# ============ 主函数 ============
def main():
    print("获取 senshinya 分类...")
    cats = get_senshinya_cats()
    print(f"  senshinya: {len(cats)} 分类")

    rule_sets = build_rule_sets(cats)
    outbounds = build_outbounds()
    rules = build_rules(cats)

    template = {
        "outbounds": outbounds,
        "route": {
            "rules": rules,
            "rule_set": rule_sets,
            "final": "🐟 漏网之鱼"
        }
    }

    template_path = os.path.join(OUT_DIR, "Custom_All_full.json")
    with open(template_path, "w", encoding="utf-8") as f:
        json.dump(template, f, ensure_ascii=False, indent=1)

    print(f"\n✅ 模板生成: {template_path}")
    print(f"   规则集: {len(rule_sets)}")
    print(f"   策略组: {len(outbounds)}")
    print(f"   路由规则: {len(rules)}")
    print(f"   大小: {os.path.getsize(template_path)} bytes")

    # 分类统计
    groups = {"CN": [], "AD": [], "MEDIA": [], "AI": [], "GAME": [], "PROXY": []}
    for cat in cats:
        groups[classify(cat)].append(cat)
    print(f"\n分类统计: CN={len(groups['CN'])} AD={len(groups['AD'])} MEDIA={len(groups['MEDIA'])} AI={len(groups['AI'])} GAME={len(groups['GAME'])} PROXY={len(groups['PROXY'])}")

if __name__ == "__main__":
    main()
