#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gyc.skill 深度自查脚本（固化版，替代会话内临时脚本）。

用法: python3 -I tools/self_check.py [--seed N]
检查 6 项:
  1) skills/guoyoucai 结构完整（SKILL.md frontmatter、references 4、assets 2）
  2) SKILL.md 路由表链接目标存在
  3) 引文真实性抽查 8 条（随机，与 canonical/entries 逐字比对）
  4) anti-patterns.md 来源归属与语料一致
  5) install.sh 语法 + README/install.sh 仓库名一致
  6) corpus/ 未被 git 跟踪（付费语料绝不外泄）
退出码 0=全过，1=有问题。--seed 固定随机种子便于复现。
"""
import re
import subprocess
import sys
import unicodedata
import random
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "guoyoucai"
ENTRIES = REPO / "corpus" / "guoyoucai" / "canonical" / "entries"


def norm(s):
    return re.sub(r"\s+", "", unicodedata.normalize("NFC", s))


def main():
    args = sys.argv[1:]
    seed = int(args[args.index("--seed") + 1]) if "--seed" in args else None
    rng = random.Random(seed)
    issues = []

    # 1) 结构
    need = ["SKILL.md", "references/judgment.md", "references/cases.md",
            "references/voice.md", "references/anti-patterns.md",
            "assets/创业自检清单.md", "assets/日报模板.md"]
    for f in need:
        if not (SKILL / f).exists():
            issues.append("结构缺失: %s" % f)
    fm = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    if not re.match(r"^---\nname: guoyoucai\ndescription: .+", fm):
        issues.append("SKILL.md frontmatter 异常")

    # 2) 路由链接
    for m in re.finditer(r"\]\((references/[^)]+|assets/[^)]+)\)", fm):
        if not (SKILL / m.group(1)).exists():
            issues.append("路由缺失: %s" % m.group(1))

    # 3) 引文抽查
    raw_j = (SKILL / "references" / "judgment.md").read_text(encoding="utf-8")
    raw_v = (SKILL / "references" / "voice.md").read_text(encoding="utf-8")
    pairs = []
    for m in re.finditer(r'"([^"」]{6,60})"（(\d{1,3}(?:\.\d)?)(?:、\d{1,3}(?:\.\d)?)*）', raw_j):
        pairs.append((m.group(1), m.group(2)))
    for m in re.finditer(r'\| ([^|"]{6,60}) \| (\d{1,3})', raw_v):
        pairs.append((m.group(1).strip(), m.group(2)))
    if len(pairs) < 8:
        issues.append("引文池不足: %d" % len(pairs))
    else:
        print("引文抽查:")
        for q, eid in rng.sample(pairs, 8):
            ep = ENTRIES / ("%03d.md" % int(float(eid)))
            ok = ep.exists() and norm(q) in norm(ep.read_text(encoding="utf-8"))
            print("  %s %s %s" % (eid, "OK" if ok else "FAIL", q[:24]))
            if not ok:
                issues.append("引文未命中: %s @%s" % (q[:30], eid))

    # 4) 来源归属
    ap = (SKILL / "references" / "anti-patterns.md").read_text(encoding="utf-8")
    for kw, eid in [("刘思毅", 21), ("摘录狗哥", 43), ("毛文超", 75),
                    ("马克", 76), ("丰田", 369), ("名创优品", 387)]:
        e = ENTRIES / ("%03d.md" % eid)
        if not (norm(kw) in norm(e.read_text(encoding="utf-8")) and kw in ap):
            issues.append("归属不一致: %s @%d" % (kw, eid))

    # 5) install.sh / README
    r = subprocess.run(["bash", "-n", str(REPO / "install.sh")], capture_output=True)
    if r.returncode != 0:
        issues.append("install.sh 语法错误: %s" % r.stderr.decode()[:120])
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    if readme.count("ZMKC404/gyc.skill") < 1 or "ZMKC404/gyc.skill" not in (REPO / "install.sh").read_text(encoding="utf-8"):
        issues.append("仓库名不一致")

    # 6) corpus 不外泄
    st = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                        capture_output=True, text=True).stdout
    if "corpus" in st:
        issues.append("corpus 出现在 git status！")
    ls = subprocess.run(["git", "ls-files"], cwd=REPO,
                        capture_output=True, text=True).stdout
    if "corpus/" in ls:
        issues.append("corpus 被 git 跟踪！严重！")

    print("ISSUES=%d" % len(issues))
    for i in issues:
        print("ISSUE:", i)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
