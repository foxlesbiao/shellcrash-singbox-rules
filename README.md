# ShellCrash sing-box 自定义规则集

ShellCrash (sing-box 内核) 自定义规则集与模板。

## 内容

- `ruleset/` - Aethersailor/Custom_OpenClash_Rules 规则转换的 sing-box .srs 二进制规则集
- `Aethersailor_RS_Full.json` - ShellCrash 模板（全分组规则 + Aethersailor 补充规则 + 去广告）
- `singbox/Custom_All.json` - **ALL 精选模板**（5 仓库约 30 规则集 + 20 策略组，适合小内存路由器）
- `singbox/Custom_All_full.json` - **ALL 全量模板**（senshinya 679 分类 + 5 仓库全部 = 702 规则集，适合 x86 软路由 ≥2GB 内存）
- `generate_singbox_all.py` - 模板生成脚本（全量版，可配置精选/全量）

## 模板功能

`Aethersailor_RS_Full.json` 包含：

- **DustinWin 基础规则集**（remote，自动更新）：ads 拦截、ai、netflix、youtube、media、games、cn、cnip 等
- **Aethersailor 补充规则集**（remote）：custom-direct（自定义直连）、custom-proxy（自定义代理）、steam-cdn（Steam CDN 直连）、game-download-cdn（游戏下载直连）

## ALL 模板（singbox/）

整合 5 个规则仓库的 sing-box 完整配置，全部 remote URL 引用（启动时按需下载，不占本地空间）：

| 仓库 | 内容 |
|---|---|
| Aethersailor/Custom_OpenClash_Rules | 自定义直连/代理/Steam |
| senshinya/singbox_ruleset | blackmatrix7 全集（679 分类） |
| REIJI007/AdBlock_Rule_For_Sing-box | 广告拦截（20 分钟更新） |
| cmontage/proxyrules-cm | GFW/AI/Google/Netflix 等 |
| Dreista/sing-box-rule-set-cn | 中国大陆域名/IP（每日更新） |

### 两个版本

| 版本 | 规则集数 | 适用 |
|---|---|---|
| `Custom_All.json`（精选） | ~30 | 小内存路由器（<1GB） |
| `Custom_All_full.json`（全量） | 702 | x86 软路由（≥2GB） |

### 策略组（20 个）

节点选择/自动选择/本地直连/漏网之鱼 + AI 平台/奈飞视频/油管视频/国际媒体/外服游戏/Steam平台/国内流量/广告拦截 + 6 地区节点组

## 自动更新

- `.github/workflows/auto-update-singbox-all.yml` - 每天 UTC 4:00 自动重新生成 ALL 模板
- `tools/update_asailor_rules.sh` - 每周一 4:30 更新 Aethersailor 规则集

## 使用

在 ShellCrash 中：

```
mm → 6 配置文件管理 → b 本地生成配置文件 → 2 选择规则模版 → 选模板
```

或手动设置：

```bash
sed -i 's|provider_temp_singbox=.*|provider_temp_singbox=/path/to/模板.json|' $CRASHDIR/configs/ShellCrash.cfg
```

## 来源

- Aethersailor/Custom_OpenClash_Rules - 规则来源
- juewuy/ShellCrash - ShellCrash 项目
- 修复 issue: https://github.com/juewuy/ShellCrash/issues/1326
