# ShellCrash sing-box 自定义规则集

ShellCrash (sing-box 内核) 自定义规则集与模板。

## 内容

- `ruleset/` - Aethersailor/Custom_OpenClash_Rules 规则转换的 sing-box .srs 二进制规则集
- `Aethersailor_RS_Full.json` - ShellCrash 模板（全分组规则 + Aethersailor 补充规则 + 去广告）

## 模板功能

`Aethersailor_RS_Full.json` 包含：

- **DustinWin 基础规则集**（remote，自动更新）：ads 拦截、ai、netflix、youtube、media、games、cn、cnip 等
- **Aethersailor 补充规则集**（remote）：custom-direct（自定义直连）、custom-proxy（自定义代理）、steam-cdn（Steam CDN 直连）、game-download-cdn（游戏下载直连）

## 使用

在 ShellCrash 中：

```
mm → 6 配置文件管理 → b 本地生成配置文件 → 2 选择规则模版 → 选 Aethersailor_RS_Full
```

或手动设置：

```bash
sed -i 's|provider_temp_singbox=.*|provider_temp_singbox=/path/to/Aethersailor_RS_Full.json|' $CRASHDIR/configs/ShellCrash.cfg
```

## 自动更新规则集

`tools/update_asailor_rules.sh` 从 Aethersailor 仓库拉取最新 .list → 转 sing-box source → 编译 .srs。

```bash
# 每周一 4:30 自动更新
30 4 * * 1 sh $CRASHDIR/tools/update_asailor_rules.sh >> /tmp/asailor_update.log 2>&1
```

更新后需重新 push 本仓库的 ruleset/ 到 GitHub（或自行替换）。

## 来源

- Aethersailor/Custom_OpenClash_Rules - 规则来源
- juewuy/ShellCrash - ShellCrash 项目
- 修复 issue: https://github.com/juewuy/ShellCrash/issues/1326
