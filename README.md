# ShellCrash sing-box 自定义规则集

ShellCrash (sing-box 内核) 自定义规则集与模板。

## 内容

- `ruleset/` - Aethersailor/Custom_OpenClash_Rules 规则转换的 sing-box .srs 二进制规则集
- `Aethersailor_RS_Full.json` - ShellCrash 模板（全分组规则 + Aethersailor 补充规则 + 去广告）
- `singbox/Custom_All.json` - **ALL 整合模板**（5 仓库规则 + 20 策略组，每日自动更新）
- `generate_singbox_all.py` - ALL 模板生成脚本

## 模板功能

`Aethersailor_RS_Full.json` 包含：

- **DustinWin 基础规则集**（remote，自动更新）：ads 拦截、ai、netflix、youtube、media、games、cn、cnip 等
- **Aethersailor 补充规则集**（remote）：custom-direct（自定义直连）、custom-proxy（自定义代理）、steam-cdn（Steam CDN 直连）、game-download-cdn（游戏下载直连）

## ALL 模板（singbox/Custom_All.json）

整合 5 个规则仓库的 sing-box 完整配置（20 策略组 + 30 规则集 + 16 分流规则），全部 remote URL 引用，每日自动更新：

| 仓库 | 内容 |
|---|---|
| Aethersailor/Custom_OpenClash_Rules | 自定义直连/代理/Steam |
| senshinya/singbox_ruleset | blackmatrix7 全集精选（流媒体/游戏/AI/大厂 25 分类） |
| REIJI007/AdBlock_Rule_For_Sing-box | 广告拦截（20 分钟更新） |
| cmontage/proxyrules-cm | GFW 规则 |
| Dreista/sing-box-rule-set-cn | 中国大陆域名/IP（每日更新） |

详细说明见 [singbox/README.md](singbox/README.md)。

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
