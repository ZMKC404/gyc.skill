#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""郭有才（郭安润）围观群合集 → canonical 层处理脚本。

用法: python3 -I process_corpus.py <源md> <输出根目录>
产出:
  corpus/guoyoucai/canonical/index.md          全量条目清单（编号/标题/字数/图片数）
  corpus/guoyoucai/canonical/entries/NNN.md    每篇清洗后全文（图片以图注形式内联）
  corpus/guoyoucai/canonical/chunks.jsonl      每篇一条 JSON（id/title/chars/images/text）
  corpus/guoyoucai/canonical/header.md         语料头部（自我介绍层）
  corpus/guoyoucai/00_台账/{METADATA.md,SHA256-manifest.txt,缺口清单.md}
"""
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

# 图片目识图注（2026-11-03 ZCode 逐张目识，非 OCR 臆测）
VISUAL_NOTES = {
    "ce3138167a19a1154b5b6ec4304757b4": "郭安润个人介绍照：黑色Polo衫、黑框眼镜，蓝色名片底板。右侧要点：6年小红书MCN创始人；职工200+，公司年营收过亿；自孵化博主账号300+，签约1000+；中国科技开发研究院特聘创业讲师；中国管理科学研究院高级创业讲师；烟台新媒体协会副秘书长。右上角 Guo Anrun。",
    "3661692955361_.pic": "郭安润微信个人二维码名片：头像为黑西装狗头表情形象，昵称「郭安润」，地区「山东 滨州」，底部「扫一扫上面的二维码图案，加我为朋友」。",
    "3671692955361_.pic": "公众号二维码：中央头像为抱气球男子照片，下方「郭有才合集」，底部「微信扫描二维码，关注我的公众号」。",
    "3891692957767_.pic": "优米兔公司办公室实景：大开间工位，桌面杂物多（零食、纸巾、多屏显示器），黑色天花板吊顶，落地窗百叶帘，白板与储物架，整体是忙碌的初创公司氛围（配文004条）。",
    "3901692957767_.pic": "拍摄间/直播间实景：小房间内多台环形灯、柔光灯、三脚架对着一张铺黄格桌布的桌子，桌上有零食袋、卡通碗、日历挂画，旁边是上下铺床——「简陋地方做出200万粉丝」的实证（配文004条）。",
    "4021692958871_.pic": "微信聊天记录截图（郭安润与对方语音转文字对话）：对方「瑞，这又转个2万来，总共今早晨总共是5万，早已3万，这有2万，总共5万」；郭安润回复「行啊」「20万一共」；对方继续语音（涉及存钱、卖货、没借钱）。",
    "4071692959135_.pic": "读者提问截图（绿底卡片，「宗介」问「狗哥」）：进入淘金快一年、认同朋友圈输出/塑造个人IP理念（学习穿搭游泳健身），但困惑「作为普通人，很多东西就算认可，也必然会因为身份或暂时没成功的原因，去发表这个观点是不合适的。应该怎么做？」（「狗哥」=郭安润在群内答疑的身份）。",
    "78c5f012ece7dde6fa2ed00dab2c0b57": "金句插画卡片（GROWTHBYVISUALS 风格）：白墙上斜靠一架歪歪扭扭但已架好的木梯，旁边一架笔直却未组装的梯子和散落木料。标题「粗糙的行动胜过未完成的完美」。",
    "微信图片_20251125232725_188_129": "手机备忘录清单（2025-11-25 23:19，郭安润每日动作清单上半）：发2条朋友圈（一条反馈/公司产品、一条思考）；发公司群一条日报；半篇微信公众号；一篇围观群；拍2条视频；发一篇视频号；2篇抖音号；坚持看完3条5分钟以上的质量视频；找2个客户聊天；陌拜+5个各私董会好友；锻炼30分钟；喝一杯蛋白粉；每天一个部门会议以培训为主30min。",
    "微信图片_20251125232726_189_129": "手机备忘录清单（下半，部门会议表）：拍2条视频/发一篇视频号/2篇抖音号/看完3条5分钟以上质量视频/找2个客户聊天/陌拜+5个各私董会好友/锻炼30分钟/喝一杯蛋白粉；每天一个部门会议以培训为主30min——运营部周一13:30、商务部bd·签约商务周二13:30、签约部经纪人·执客部门周三13:30、考研部周四13:30、IP流量部周五13:30。",
}


def clean(text):
    """纯净化清洗：去零宽、规范空白、清 HTML 实体残留，不动正文语序。"""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)
    text = text.replace("&#x20;", " ").replace("&amp;", "&").replace("&nbsp;", " ")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main(src_md, out_root):
    raw = src_md.read_text(encoding="utf-8", errors="replace")
    canon = out_root / "corpus" / "guoyoucai" / "canonical"
    ledger = out_root / "corpus" / "guoyoucai" / "00_台账"
    entries_dir = canon / "entries"
    entries_dir.mkdir(parents=True, exist_ok=True)
    ledger.mkdir(parents=True, exist_ok=True)

    header_end = raw.find("### 001")
    header = clean(raw[:header_end]) if header_end > 0 else ""
    body = raw[header_end:] if header_end > 0 else raw
    parts = [p for p in re.split(r"^### ", body, flags=re.M) if p.strip()]

    index_rows, jsonl_lines, manifests = [], [], []
    img_used, gaps = [], []
    last_eid = 0

    for part in parts:
        first_nl = part.find("\n")
        title_line = part[:first_nl].strip()
        m = re.match(r"^(?:(\d+)\s*)?(.*)$", title_line, re.S)
        body_raw = part[first_nl + 1:]
        text = clean(body_raw)
        eid_raw, title = m.group(1), m.group(2).strip()
        if eid_raw is None:
            # 无编号条目（源文件仅一处「做一件长期主义➕社会价值」），按上一个编号+0.5 记录
            eid = last_eid + 0.5 if last_eid else 0.5
            gaps.append("无编号条目 %r 记为 %s（位于 %d 与 %s 之间）"
                        % (title[:30], eid, last_eid, last_eid + 1))
        else:
            eid = int(eid_raw)
            last_eid = eid
        if not title:
            first_body = next((ln.strip() for ln in text.split("\n") if ln.strip()), "")
            title = (first_body[:30] + "…") if len(first_body) > 30 else (first_body or "(无标题)")
            gaps.append("条目 %s 无标题，用正文首行代替: %s" % (eid_raw, title))

        imgs = re.findall(r"!\[\]\(images/([^)]+)\)", text)
        notes = []
        for fn in imgs:
            key = Path(fn).name
            for stem, note in VISUAL_NOTES.items():
                if stem in key:
                    notes.append("[图·%s] %s" % (stem[:8], note))
                    img_used.append(stem)
                    break
            else:
                gaps.append("条目%s: 未匹配图注的图片 %s" % (eid, fn))
        text = re.sub(r"!\[\]\(images/[^)]+\)\n?", "", text)
        if notes:
            text = text + "\n\n" + "\n\n".join(notes)

        n_chars = len(re.sub(r"\s", "", text))
        fn_md = ("%03d.md" % eid) if float(eid).is_integer() else ("%03d-%s.md" % (int(eid), str(eid).split(".")[1]))
        entry_text = "# %03d %s\n\n%s\n" % (eid, title, text)
        (entries_dir / fn_md).write_text(entry_text, encoding="utf-8")
        meta = {"id": eid, "title": title, "chars": n_chars,
                "images": [Path(i).stem[:8] for i in imgs]}
        jsonl_lines.append(json.dumps(meta, ensure_ascii=False) + "\t" +
                           json.dumps({"text": text}, ensure_ascii=False) + "\n")
        index_rows.append("| %03d | %s | %d | %d |" % (eid, title, n_chars, len(imgs)))
        manifests.append((fn_md, hashlib.sha256(entry_text.encode("utf-8")).hexdigest()))

    (canon / "index.md").write_text(
        "# 郭有才围观群合集 · canonical 索引\n\n"
        "- 来源: 付费围观群合集 md（仅本地，不入 git）\n"
        "- 条目数: %d；图片图注化: %d 张\n\n| 编号 | 标题 | 字数 | 图片 |\n|---|---|---|---|\n"
        % (len(index_rows), len(img_used)) + "\n".join(index_rows) + "\n",
        encoding="utf-8")
    (canon / "chunks.jsonl").write_text("".join(jsonl_lines), encoding="utf-8")
    header_notes = []
    for fn in re.findall(r"!\[\]\(images/([^)]+)\)", header):
        key = Path(fn).name
        for stem, note in VISUAL_NOTES.items():
            if stem in key:
                header_notes.append("[图·%s] %s" % (stem[:8], note))
                img_used.append(stem)
                break
        else:
            gaps.append("头部: 未匹配图注的图片 %s" % fn)
    header_clean = re.sub(r"!\[\]\(images/[^)]+\)\n?", "", header)
    if header_notes:
        header_clean = header_clean + "\n\n" + "\n\n".join(header_notes)
    (canon / "header.md").write_text(
        "# 语料头部（自我介绍层）\n\n%s\n" % header_clean, encoding="utf-8")
    (ledger / "SHA256-manifest.txt").write_text(
        "\n".join("%s  %s" % (h, f) for f, h in manifests) + "\n", encoding="utf-8")

    src_bytes = src_md.read_bytes()
    (ledger / "METADATA.md").write_text(
        "# METADATA · 郭有才语料 canonical 层\n\n"
        "- 处理时间: 2026-11-03\n- 源文件: %s\n- 源 SHA256: %s\n- 源大小: %d bytes\n"
        "- 清洗规则: NFC 规范化、去零宽字符、HTML 实体还原(&#x20;/&amp;/&nbsp;)、压缩多余空行；不改写正文语序与用词\n"
        "- 图片处理: 10/10 张人工目识转图注（VISUAL_NOTES），原图引用从正文移除，图注按条目内联\n"
        "- 产出: index.md(%d条)、entries/%d个文件、chunks.jsonl(%d行)、header.md\n"
        "- 版权: 源内容为付费围观群合集（166元门槛），canonical 层仅本地保存，禁止推送到公开仓库\n"
        % (src_md, hashlib.sha256(src_bytes).hexdigest(), len(src_bytes),
           len(index_rows), len(manifests), len(jsonl_lines)),
        encoding="utf-8")
    (ledger / "缺口清单.md").write_text(
        "# 缺口清单\n\n"
        + ("\n".join("- %s" % g for g in gaps) if gaps else "- 无未匹配项")
        + "\n- 语音/视频内容不在语料中（源为图文 md）\n"
        "- 飞书资料包、公众号外链仅存链接文本，未爬取（外部内容另属他人版权）\n",
        encoding="utf-8")
    print("entries=%d images_noted=%d gaps=%d" % (len(index_rows), len(img_used), len(gaps)))
    for g in gaps[:5]:
        print("GAP:", g)
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
