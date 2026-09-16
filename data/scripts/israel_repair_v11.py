#!/usr/bin/env python3
"""v1.1 repair pass (post step-5 review): container re-extraction for
Kikar and N12 from saved raw HTML.

Review findings 2+3: p-cluster fallback captured page chrome (Kikar nav/
footer/recommendations, N12 print/social prefix). Both sites carry the
article in a bounded container; re-extract from the slice, no refetch.
Rewrites corpus-candidates-v1.jsonl in place (method: container).
"""
import html as H, json, re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "israel"
START = {"kikar": 'class="article-content', "n12": 'itemprop="articleBody"'}


def paras(seg):
    seg = re.sub(r"<script.*?</script>|<style.*?</style>", " ", seg, flags=re.S)
    ps = [H.unescape(re.sub(r"<[^>]+>", " ", p)) for p in re.findall(r"<p[^>]*>(.*?)</p>", seg, re.S)]
    return [" ".join(p.split()) for p in ps if len(p.split()) > 3]


def main():
    path = DATA / "corpus-candidates-v1.jsonl"
    recs = [json.loads(l) for l in open(path, encoding="utf-8")]
    fixed = missing = 0
    for r in recs:
        if r["outlet"] not in START or not r.get("raw_path") or r.get("extract_method") == "ld-json":
            continue
        t = (DATA / r["raw_path"]).read_text(encoding="utf-8")
        i = t.find(START[r["outlet"]])
        if i < 0:
            missing += 1
            print("no container:", r["outlet"], r["url"][:80])
            continue
        j = t.find("</article>", i)
        body = "\n".join(paras(t[i:j if j > i else len(t)]))
        body = " ".join(body.split())
        if body:
            r["body_text"], r["body_words"] = body[:20000], len(body.split())
            r["extract_method"] = "container"
            fixed += 1
    with open(path, "w", encoding="utf-8") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"container re-extracted: {fixed} | no-container: {missing} | total: {len(recs)}")


if __name__ == "__main__":
    main()
