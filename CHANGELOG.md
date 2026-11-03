# CHANGELOG

## v1.1.0 · 2026-11-04

- **新增 judgment.md §8 危机与止损**：归因纪律（370）、止损先例（303 砍直播间）、扩张复盘（233）、逆周期练兵（269/167）、试错纪律（384）、最坏预案（201）、组织补课（094/248）、机制自查（189/351）、心态底线（220/170）。全部引文回源逐字核对；370 体面线点段因 OCR 错序只引干净片段。
- **新增 judgment.md §9 他明确反对的事**：12 条快速否决清单（借钱/砍价客户/捷径/盲目开新项目/all in/指责型人格/阿米巴分配/宽进宽出/贪便宜/给领导送礼/成绩后退圈/全面推进），全部带条目号。
- **SKILL.md**：路由表新增「危机」「反对清单」两行；description 触发词扩充（封号/亏损/散伙/砍业务/郭安润）。
- **install.sh**：clone 增加双镜像 fallback（ghproxy.net / gh-proxy.com），raw·github 被墙网络实测可用。
- **tools/self_check.py**：自查逻辑固化进仓库（此前靠会话临时脚本），支持 `--seed` 复现；新增「corpus 被 git 跟踪即严重报错」硬检查。
- **README**：新增示例问法 4 条、版本指引。

## v1.0.0 · 2026-11-03

- 语料深度处理：405 篇日报 → canonical（entries/chunks.jsonl/index/SHA256 台账 405/405 OK），10 张图片目识转图注。
- guoyoucai skill v1：SKILL.md 路由 + judgment.md 七类判断卡 + cases.md 轨迹 + voice.md 日报体与金句库 + anti-patterns.md + 2 个作业表。
- 对抗性审查：46 项引文核对（修 2 处出处）、6 项来源归属、指纹盲测；GitHub ZMKC404/gyc.skill 首推。
