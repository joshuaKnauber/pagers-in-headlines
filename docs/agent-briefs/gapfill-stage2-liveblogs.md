# Gap fill, stage 2: live blogs as timestamped entries (brief for delegated agents)

Kept in the repo so the instructions behind the data are on record. Read
`gapfill-stage1.md` first; its project summary and hard rules 2–5 and 7 apply here too.
The differences are below.

## What stage 2 is

Live blogs and tickers were never collected as entries. The recall audit listed 60 of them in
the window (Germany 17, US 43: rows with `status` `live_blog` or `live_blog_unverified` in
`data/{germany,us}/08-recall-audit/gap-manifest.csv`, with in-window Wayback capture timestamps
in `liveblog_captures_in_window`). A reader of a live blog sees a stream of short timestamped
entries. Each entry about the attacks becomes one record.

## Rules that differ from stage 1

1. **Network: Wayback only, politely.** Never fetch a live blog from the live site (rolling
   pages now show 2025/26 content). Fetch `https://web.archive.org/web/<ts>id_/<url>` for
   captures whose timestamp is between 20240917000000 and 20240924235959.
   - One request at a time, at least 3 seconds apart.
   - Timeout 60 s, at most 3 tries with backoff 10/30/90 s.
   - Stop the run and report if 20 requests in a row fail.
   - Run long fetch loops in the background with progress written to a log file, so nothing
     hangs silently.
2. **Capture sampling.** Per blog, fetch at most 10 captures: the last in-window capture of each
   day, plus extra captures if the blog's entries roll off the page (check whether the page
   shows all entries or only the latest N; say which in the report). Entries seen in several
   captures are one entry.
3. **Write only to:**
   - `pipeline/05-extraction/round2/liveblogs.py`
   - `data/{germany,us}/05-extraction/round2/liveblog-entries.jsonl`
   - `liveblog-report.md` in the same folders
   - `liveblog-fetch-log.csv` in the same folders
   - new files `data/<country>/raw/<outlet>/r2lb-<sha16(url)>-<ts>.html.gz`
   Read-only everywhere else. Another agent works on `extract_cached_de_us.py` and the stage-1
   files: do not touch them.
4. **Entries, verbatim.** An entry is the publisher's own unit: its own timestamp, an optional
   headline and its text. Sources in order of preference:
   - JSON-LD `LiveBlogPosting.liveBlogUpdate`
   - embedded page state (`__NEXT_DATA__`, Arc/Fusion content, Apollo state)
   - the HTML entry containers
   Never split or merge entries yourself. Never invent a timestamp: if an entry has none on the
   page, leave it empty and add a warning.
5. **Which entries to keep.** Keep every entry whose headline or text mentions the attacks.
   Decide with `pipeline/08-recall-audit/recall_audit_common.py:has_mention(text, country)`,
   plus entries the blog itself links to the attacks.
   For every blog, also report the total number of distinct entries in the window, so we know
   the share the attack had.

## Output

`liveblog-entries.jsonl`, one object per kept entry:

| field | content |
|---|---|
| `outlet`, `blog_url` | outlet and the live-blog URL as in the gap manifest |
| `entry_id` | the publisher's entry id or anchor if present, else `sha256(blog_url + timestamp + first 80 chars)[:12]` |
| `entry_url` | `blog_url#<anchor>` if the page has entry anchors, else `""` |
| `published_time` | entry timestamp, ISO, as on the page (with offset or Z) |
| `published_at` | `YYYY-MM-DD` of `published_time` in the outlet's local time zone |
| `title` | entry headline or `""` |
| `body_text`, `body_words` | entry text; `\n` between paragraphs |
| `first_seen_capture`, `last_seen_capture` | Wayback timestamps |
| `raw_path` | the gzip copy of the first capture containing the entry |
| `extract_method` | e.g. `ld-json:liveBlogUpdate`, `next-data`, `container:<selector>` |
| `salience` | `central` if the attack is named in the title or the first 300 characters of the entry, else `mention` |
| `language`, `warnings` | as in stage 1 |

`liveblog-report.md`:
- per blog: captures fetched, entries total in the window, entries kept, extraction method,
  and whether earlier entries roll off the page
- failures, with reasons
- three sample entries per outlet (title, time, first 200 characters)
- judgment calls

Blogs whose captures are empty shells (the audit found this for ABC: entries load client-side):
try the embedded state once. If there is nothing, record `no_entries_in_capture` and move on.

## Validation

- **Timestamps:** every kept entry has a time inside Sep 17–24 local time, or a warning.
- **No duplicates:** no entry text appears twice for the same blog (dedup across captures).
- **Spot check:** for 3 entries per outlet, the text must be findable verbatim in the raw
  capture (after tag stripping). Report the result.
