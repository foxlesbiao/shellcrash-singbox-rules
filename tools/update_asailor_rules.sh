#!/bin/sh
# Aethersailor 规则集自动更新脚本
# 功能：从 GitHub 拉取最新 .list 规则 → 转 sing-box source → 编译 .srs → 放入 ShellCrash ruleset/
# 由 Hermes agent 2026-08-11 创建，建议每周运行一次
# 用法: sh /mnt/usb-d2304ff3/ShellCrash/tools/update_asailor_rules.sh

CRASHDIR=/mnt/usb-d2304ff3/ShellCrash
RULESET_DIR=$CRASHDIR/ruleset
TMPDIR=/tmp/asailor_update
CRASH_CORE=/tmp/ShellCrash/CrashCore

# Aethersailor 规则源（.list 格式，Clash 语法）
BASE="https://raw.githubusercontent.com/Aethersailor/Custom_OpenClash_Rules/main/rule"
FILES="Custom_Direct Custom_Proxy Steam_CDN Game_Download_CDN"

mkdir -p "$TMPDIR" "$RULESET_DIR"

convert_list() {
    # 参数: $1=输入list文件 $2=输出source json
    # 转换 Clash .list → sing-box source JSON
    outfile="$2"
    echo '{"version":1,"rules":[' > "$outfile"
    first=1
    while IFS= read -r line || [ -n "$line" ]; do
        line=$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        [ -z "$line" ] && continue
        echo "$line" | grep -q '^#' && continue
        kind=$(echo "$line" | cut -d',' -f1)
        value=$(echo "$line" | cut -d',' -f2)
        [ -z "$value" ] && continue
        [ "$first" = "0" ] && echo -n "," >> "$outfile"
        case "$kind" in
            DOMAIN-SUFFIX) echo -n "{\"domain_suffix\":\"$value\"}" >> "$outfile" ;;
            DOMAIN-KEYWORD) echo -n "{\"domain_keyword\":\"$value\"}" >> "$outfile" ;;
            DOMAIN) echo -n "{\"domain\":\"$value\"}" >> "$outfile" ;;
            IP-CIDR|IP-CIDR6) echo -n "{\"ip_cidr\":\"$value\"}" >> "$outfile" ;;
            DST-PORT) echo -n "{\"port\":$value}" >> "$outfile" ;;
            SRC-PORT) echo -n "{\"source_port\":$value}" >> "$outfile" ;;
            *) continue ;;
        esac
        first=0
    done < "$1"
    echo ']}' >> "$outfile"
}

# 检查内核可用（若服务运行则 CrashCore 在 /tmp）
if [ ! -x "$CRASH_CORE" ]; then
    # 尝试从 CRASHDIR 找
    [ -x "$CRASHDIR/CrashCore.raw" ] && CRASH_CORE="$CRASHDIR/CrashCore.raw"
    [ -x "$CRASHDIR/CrashCore" ] && CRASH_CORE="$CRASHDIR/CrashCore"
fi
if [ ! -x "$CRASH_CORE" ]; then
    echo "错误: 找不到 CrashCore 内核"
    exit 1
fi

echo "=== 开始更新 Aethersailor 规则集 ==="
ok=0
for name in $FILES; do
    echo "--- 处理 $name ---"
    # 1. 下载 .list
    dl_ok=0
    for try in 1 2 3; do
        if curl -sfL --max-time 30 "$BASE/$name.list" -o "$TMPDIR/$name.list"; then
            dl_ok=1
            break
        fi
        echo "下载重试 $try/3..."
        sleep 2
    done
    [ "$dl_ok" = "0" ] && { echo "下载失败: $name.list，保留旧文件"; continue; }
    size=$(wc -c < "$TMPDIR/$name.list")
    [ "$size" -lt 100 ] && { echo "文件过小($size字节)，跳过"; continue; }
    echo "下载 $name.list ($size 字节)"

    # 2. 转 source JSON
    convert_list "$TMPDIR/$name.list" "$TMPDIR/$name.json"
    echo "转换 $name.json"

    # 3. 编译 .srs
    if "$CRASH_CORE" rule-set compile "$TMPDIR/$name.json" -o "$RULESET_DIR/$name.srs" 2>/dev/null; then
        echo "编译 $name.srs ✅"
        # 4. 同时更新 _Domain 和 _IP 变体（供 DustinWin 模板引用）
        ok=$((ok+1))
    else
        echo "编译失败 $name"
    fi
done

# 同步 Steam_CDN_Domain / Steam_CDN_IP 变体
echo "--- 生成 Domain/IP 变体 ---"
for name in Custom_Direct Custom_Proxy Steam_CDN; do
    if [ -s "$TMPDIR/$name.json" ]; then
        # Domain 变体（只取 domain 规则）
        grep -o '{[^}]*domain[^}]*}' "$TMPDIR/$name.json" | sed 's/.*/&,/' | sed '1s/^/{"version":1,"rules":[/' > /tmp/dom_tmp.json
        echo ']}' >> /tmp/dom_tmp.json
        sed -i 's/,}]}/}]}/' /tmp/dom_tmp.json 2>/dev/null
        "$CRASH_CORE" rule-set compile /tmp/dom_tmp.json -o "$RULESET_DIR/${name}_Domain.srs" 2>/dev/null && echo "${name}_Domain.srs ✅"
        # IP 变体
        grep -o '{[^}]*ip_cidr[^}]*}' "$TMPDIR/$name.json" | sed 's/.*/&,/' | sed '1s/^/{"version":1,"rules":[/' > /tmp/ip_tmp.json
        echo ']}' >> /tmp/ip_tmp.json
        sed -i 's/,}]}/}]}/' /tmp/ip_tmp.json 2>/dev/null
        "$CRASH_CORE" rule-set compile /tmp/ip_tmp.json -o "$RULESET_DIR/${name}_IP.srs" 2>/dev/null && echo "${name}_IP.srs ✅"
    fi
done

echo "=== 更新完成: $ok 个规则集 ==="
echo "提示: 若修改了模板引用，需通过 ShellCrash 菜单重新生成配置"
