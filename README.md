# gyc.skill

以 **郭有才（郭安润）405 篇创业日报** 为语料底座的创业导师 skill。一条命令安装：

```bash
curl -fsSL https://raw.githubusercontent.com/ZMKC404/gyc.skill/main/install.sh | bash
```

可选目标：`--zcode`（默认）/ `--claude` / `--codex` / `--all`。

> raw.githubusercontent 被墙/重置的网络，用镜像行：
> ```bash
> curl -fsSL https://ghproxy.net/https://raw.githubusercontent.com/ZMKC404/gyc.skill/main/install.sh | bash
> ```

## 这是什么

- **导师定位**：不是语录机器人。基于他日报里的判断、实战细节（含原始数字与条目号出处）做诊断，每次回答附「下一步」最小动作，必要时用他的"会死人能倒闭"优先级主动指出你没问但更要紧的事。
- **防幻觉纪律**：所有引文带条目号（如 日报 006）；语料没有的判断明确标注"这是我的推断"；经验句式不当统计定律；跨行业迁移标注类比。
- **触发词**：郭有才 / 狗哥 / 创业迷茫 / 要不要做这个项目 / 怎么招人 / 没流量 / 变现定价 / 创业焦虑……

## 结构

```
skills/guoyoucai/
  SKILL.md                 # 路由 + 判断纪律 + 主动引导机制
  references/judgment.md   # 7 大类判断卡（谋定/流量/生意/组织/交付/心态/人情），全带条目号
  references/cases.md      # 成长轨迹 + 业务事实 + 图片目识资产
  references/voice.md      # 日报体指纹 + 38 条金句库（逐字出处）
  references/anti-patterns.md  # 来源归属 + 跑偏点 + 他自述踩坑
  assets/创业自检清单.md    # 用户作业表
  assets/日报模板.md        # 他的每日动作清单 + 日报三段式
```

## 语料与版权

- 语料为付费围观群内容（166 元门槛），**只存本地不进仓库**；仓库只含 skill、方法卡与带出处的短引文。
- 语料处理脚本 `tools/process_corpus.py`（405 条 → canonical/entries + chunks.jsonl + SHA256 台账，10 张图片目识转图注）留在仓库供复现流程，不含数据。

## 来源

- 人物：郭安润（网名郭有才，公众号"郭有才合集"，因撞名 2025 年改名"闲人郭老板"），优米兔创始人，6 年小红书 MCN，2 年破亿营收。
- 本仓库为第三方方法论整理，非官方产品；引文版权归原作者所有。
