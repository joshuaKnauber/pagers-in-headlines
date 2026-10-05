Adversarial review, scoped to the Israel step-5 delta (triage/extraction/normalization) of a news-coverage research corpus. Work read-only from /Users/jknauber/Documents/Projects/news/data/. Be skeptical; your job is to find defects, not to approve.

Scope (only these artifacts):
1. data/israel/triage-notes.md and data/israel/normalization-notes.md — verify EVERY number against the underlying files: enumeration/*-titles-*.csv, enumeration/abuali-messages.csv, corpus-candidates-v1.jsonl, corpus-v1.jsonl. Recompute counts yourself (python3 available).
2. Extraction correctness: pick 5 records across outlets from corpus-v1.jsonl, open the matching raw/<outlet>/<hash>.html, and check the stored body is the article (not sidebar/ticker/boilerplate) and the date matches the page.
3. Tagging quality: sample 30 untagged titles from ynet-titles-*.csv containing likely event words (חיזבאללה, לבנון, מטען) and judge whether the strong/related term families missed real pager-event items (recall check). Also check 5 tagged rows for false positives.
4. data/analysis/lebanon-israel-comparison-v1.md — recompute the headline table from the two corpus-v1.jsonl files using the term families described there; flag any figure that does not reproduce.

Known/accepted (do not re-litigate): Ynet lead-only bodies are paywall policy; N12 n=10 recall limit is documented; Abu Ali 20/33-day coverage is documented.

Output: a markdown report — verdict (pass / conditional pass / fail), then a numbered findings table (finding, evidence, severity, suggested fix). Cite file paths and record ids for every claim.
