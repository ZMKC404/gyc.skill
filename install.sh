#!/usr/bin/env bash
# gyc.skill 一行安装：curl -fsSL https://raw.githubusercontent.com/ZMKC404/gyc.skill/main/install.sh | bash
# 可选: --zcode(默认) --claude --codex --all
set -euo pipefail

REPO="https://github.com/ZMKC404/gyc.skill.git"
SKILL="guoyoucai"
TARGET="zcode"

for arg in "$@"; do
  case "$arg" in
    --zcode) TARGET="zcode" ;;
    --claude) TARGET="claude" ;;
    --codex) TARGET="codex" ;;
    --all) TARGET="all" ;;
    *) echo "未知参数: $arg（支持 --zcode --claude --codex --all）" >&2; exit 1 ;;
  esac
done

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
echo "→ 克隆 gyc.skill ..."
# 多源 fallback：github 直连失败时自动走镜像（raw 被墙的网络实测有效）
git clone --depth 1 "$REPO" "$TMP/repo" 2>/dev/null || \
git clone --depth 1 "https://ghproxy.net/$REPO" "$TMP/repo" 2>/dev/null || \
git clone --depth 1 "https://gh-proxy.com/$REPO" "$TMP/repo" 2>/dev/null || {
  echo "✗ 克隆失败（直连+镜像均不可达），检查网络后重试: $REPO" >&2; exit 1;
}

install_to() {
  local dir="$1" label="$2"
  mkdir -p "$dir"
  rm -rf "$dir/$SKILL"
  cp -R "$TMP/repo/skills/$SKILL" "$dir/$SKILL"
  echo "✓ 已安装到 $dir/$SKILL ($label)"
}

case "$TARGET" in
  zcode) install_to "$HOME/.zcode/skills" "ZCode" ;;
  claude) install_to "$HOME/.claude/skills" "Claude Code" ;;
  codex)  install_to "$HOME/.codex/skills" "Codex" ;;
  all)
    install_to "$HOME/.zcode/skills" "ZCode"
    install_to "$HOME/.claude/skills" "Claude Code"
    install_to "$HOME/.codex/skills" "Codex"
    ;;
esac

echo ""
echo "完成。使用：在任意会话中提到「郭有才 / 狗哥 / 创业迷茫 / 要不要做这个项目 / 怎么招人」等即可触发，"
echo "或显式调用：/guoyoucai"
