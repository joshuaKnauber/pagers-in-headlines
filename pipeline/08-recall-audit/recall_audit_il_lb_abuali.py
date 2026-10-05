#!/usr/bin/env python3
"""Recall audit: Abu Ali Express via LIVE Telegram web preview (independent of
the Wayback capture stream used by the pipeline).

Pages t.me/s/abualiexpress?before=<id> backwards over the window's message-ID
range, parses every message (id, datetime, text), and writes
data/israel/08-recall-audit/raw/abuali-live-messages.csv. Raw pages cached under
data/israel/08-recall-audit/raw/abuali/.
"""
import csv, html as H, re, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recall_audit_il_lb_common as C

LO, HI = 75560, 76640          # ~Sep 16 evening .. Sep 25 morning (from archived stream ids)
RAW = C.DATA / "israel" / "08-recall-audit" / "raw" / "abuali"
C.GAPS["t.me"] = 2.0


def parse(t):
    out = []
    for blk in re.split(r'(?=<div class="tgme_widget_message_wrap)', t)[1:]:
        m = re.search(r'data-post="abualiexpress/(\d+)"', blk)
        if not m:
            continue
        pid = int(m.group(1))
        dt = re.search(r'<time datetime="([^"]+)"', blk)
        tx = re.search(r'<div class="tgme_widget_message_text[^"]*"[^>]*>(.*?)</div>', blk, re.S)
        text = ""
        if tx:
            text = H.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<br\s*/?>", "\n", tx.group(1))))
            text = " ".join(text.split())
        media = "photo" if "tgme_widget_message_photo" in blk else ("video" if "tgme_widget_message_video" in blk else "")
        out.append((pid, dt.group(1) if dt else "", text, media))
    return out


def main():
    msgs = {}
    before = HI
    while before > LO:
        url = f"https://t.me/s/abualiexpress?before={before}"
        t, info = C.fetch(url, RAW)
        if t is None:
            print("fail", before, info, flush=True)
            before -= 20
            continue
        got = parse(t)
        if not got:
            print("empty", before, flush=True)
            before -= 20
            continue
        for g in got:
            msgs[g[0]] = g
        before = min(g[0] for g in got)
        print(before, len(msgs), flush=True)
    p = C.DATA / "israel" / "08-recall-audit" / "raw" / "abuali-live-messages.csv"
    w = csv.writer(open(p, "w", newline="", encoding="utf-8"))
    w.writerow(["post_id", "datetime", "media", "device_hits", "text"])
    for pid in sorted(msgs):
        _, dt, text, media = msgs[pid]
        n, _ = C.device_hits(text)
        w.writerow([pid, dt, media, n, text])
    print("DONE", len(msgs))


if __name__ == "__main__":
    main()
