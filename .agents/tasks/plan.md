# Implementation Plan — Port the Strands-ship automation toolkit into SKILL DNA

Goal: finish porting the AWS-user-group "strands-ship" demo automation (bench → video → article → check) into the SKILL DNA project so the whole pipeline runs end-to-end locally, with honest numbers drawn from real run files.

Work directly in the workspace root `/Users/madhumithaa/Desktop/Skill DNA`. No git branch, no worktree, no AgentCore deployment. Do not break the FastAPI backend (`api.py`, `agentcore_handler.py`) or the React frontend. Match the existing Python style (type hints, docstrings, `from __future__ import annotations`, lazy imports of agents).

---

## Current state (verified by reading the code and running it)

Working now:
- `agent/app.py` runs the full pipeline live on Amazon Bedrock and prints `[tag]` evidence lines. Confirmed: `python3 -m agent.app --demo` reached Observer + Interviewer + (started) Knowledge Architect on real Sungudi notes with no Python errors. Tags it emits via `say()`: `plan, observer, interviewer, architect, curriculum, s3, ddb, polly`.
- `kit/make_video.py` (Playwright recorder) is adapted for SKILL DNA. Its `EVIDENCE` regex scans exactly `observer|interviewer|architect|curriculum|s3|ddb|polly|plan|metric|error`, writes `kit/results/video_run.json` + `demo.mp4`/`demo.webm`, and `--dry-run` works.
- `video.json` lives at the **project root** (not `kit/`). `make_video.py` default `--spec video.json` resolves relative to cwd=root, which is correct.
- `kit/measure.py` runs observer/interviewer cases vs a one-prompt baseline and writes `kit/results/MEASURE.md` (a real 4-case run already exists).
- `.env` has working AWS creds + `BEDROCK_MODEL_ID=amazon.nova-pro-v1:0` + `SHIP_MODEL`. Bedrock responds.
- `strands-agents 1.9.1`, `boto3 1.43.120`, `playwright` installed. `models/` imports cleanly. `from agents.orchestrator import run_skill_capture_pipeline` works.

Broken / missing:
- `kit/make_article.py` — does not exist.
- `kit/check_submission.py` — does not exist.
- `kit/ss.py` — has `bedrock/blocks/block/pipeline/measure/check` but **no** `bench`, `video`, or `article` subcommands. Its `check` is an env checklist, not an artifact-completeness check. No `./kit` executable wrapper exists.
- `kit/measure.py` — writes only `MEASURE.md` (no `results.json`); skips `knowledge_architect` cases; never scores interviewer cases against `expected_questions` or architect cases against `expected_fingerprint_keys`.
- Evidence noise: the four stage agents (`observer_agent.py`, `interviewer_agent.py`, `knowledge_architect.py`, `curriculum_agent.py`) construct their Strands `Agent` **without** `callback_handler=None`, so the live run prints `<thinking>`, `Tool #1`, and raw JSON blocks interleaved with the `[tag]` lines. `api.py` uses the agents via **return values only** (lines 528-581: `observer.analyze(...)`, `interviewer.generate_questions(...)`, `architect.build_fingerprint(...)`, `curriculum.create_lesson(...)` — no `StreamingResponse`/stdout consumption), so suppressing that noise is safe.
- `ffmpeg` is NOT installed → `make_video.py` falls back to `demo.webm`. `brew` is available at `/opt/homebrew/bin/brew`.

---

## Key decisions (recorded, not re-debated by the implementer)

1. **Article: generate new files, leave the human draft intact.** The user's `demo/BUILDER_CENTER_ARTICLE.md` is hand-written narrative with cultural context; a generator must not overwrite it. `make_article.py` writes a NEW `demo/ARTICLE_GENERATED.md` (a Builder Center article whose "Measured results" section cites real numbers) plus `demo/FACTS.md` (a compact, paste-ready list of every measured number with its source file). `demo/BUILDER_CENTER_ARTICLE.md` stays untouched.

2. **`results.json` shape** (written by `measure.py` to `kit/results/results.json`). Per-case rows keyed by `id`; scoring dispatches by `label` against the case's `expected_*` field:
   ```json
   {
     "when": "2026-11-05 04:30", "model": "amazon.nova-pro-v1:0", "region": "us-east-1",
     "cases_run": 7,
     "summary": {
       "observer":           {"cases": 3, "score_avg": 1.0},
       "interviewer":        {"cases": 1, "score_avg": 0.67},
       "knowledge_architect":{"cases": 1, "score_avg": 1.0},
       "curriculum_quiz":    {"cases": 2, "score_avg": 0.5}
     },
     "baseline": {"gaps_avg": 0.92, "tacit_q_avg": 0.0, "rows": []},
     "overall_pass_rate": 0.86,
     "rows": [
       {"id":"sungudi-01","label":"observer","craft":"Madurai Sungudi",
        "agent":"observer","passed":true,"score":1.0,
        "expected":["knot tension","dye temperature","timing"],
        "matched":["knot tension","dye temperature","timing"],"missed":[],
        "latency_ms":5981,"detail":"5 gaps found; 3/3 expected matched"}
     ]
   }
   ```
   `rows[].score` is the fraction of `expected` items matched (synonym/fuzzy match, reusing the existing `_SYNONYMS` map and extending it). `passed = score == 1.0`. `overall_pass_rate = passed/total`.

3. **`video_run.json` shape** — already produced by `make_video.py` (`kit/results/video_run.json`): `{spec, scenes:[{title,command,exit,evidence,output}], started, seconds, file, under_3_min}`. `make_article.py` reads `seconds`, per-scene `exit`, `evidence` lines, and `under_3_min` from it. Do not change this shape.

4. **Evidence-tag scheme** — already aligned: `app.py` `say(tag, text)` prints `[tag] text`; `make_video.py` `EVIDENCE` regex matches the same tag set. The only fix is cleanliness (item 1) + adding a real `[metric]` line. Tags in use: `observer, interviewer, architect, curriculum, s3, ddb, polly, plan, metric, error`. Do not introduce new tags without adding them to `make_video.py`'s `EVIDENCE` regex and `BADGE_MAP`.

5. **Cloud calls (S3/Polly/DynamoDB) are best-effort.** `app.py` already wraps them in `try/except` so failures print a graceful skip line, never crash. Add a `--no-cloud` flag to `agent/app.py` that skips them entirely (prints nothing or a single clean skip note), so the video demo can run fast and clean when the S3 bucket/Dynamo table/Polly aren't provisioned. Default behavior (cloud on) is unchanged so the API/frontend are unaffected.

6. **Video output format.** `make_video.py` already produces `demo.mp4` if `ffmpeg` exists, else `demo.webm`. The implementer should `brew install ffmpeg` (medium-risk, reversible Homebrew install) to satisfy the literal `demo.mp4` verification. `check_submission.py` must accept **either** `demo.mp4` or `demo.webm` so the pipeline is not blocked if ffmpeg is absent. State which you got.

7. **Honest numbers.** Every number in `ARTICLE_GENERATED.md` / `FACTS.md` must be read from `results.json` or `video_run.json` produced by actually running `bench` then `video`. `make_article.py` must error clearly if either source file is missing rather than invent numbers. The Strands SDK version cited in the article must come from `importlib.metadata.version("strands-agents")` (currently `1.9.1`), not a hardcoded aspirational version.

---

## Ordered implementation items

- [ ] 1. Clean the agent evidence output and align the `[metric]` badge.
  Add `callback_handler=None` to the four Strands `Agent(...)` constructions in `agents/observer_agent.py`, `agents/interviewer_agent.py`, `agents/knowledge_architect.py`, and `agents/curriculum_agent.py`. This is safe: `api.py` consumes agent **return values**, never stdout, so suppressing the Strands callback stream changes nothing for the API/frontend. Add a `--no-cloud` flag to `agent/app.py` (skip the S3/Polly/Dynamo blocks when set; current behavior unchanged when unset). At the end of `run_demo()`, if `kit/results/results.json` exists, read `summary`/`overall_pass_rate` and print one real `[metric]` line, e.g. `[metric] Gap coverage 100% · fingerprint keys 5/5 · pass rate 86%`; if it does not exist, print `[metric] (run \`python kit/ss.py bench\` to populate measured metrics)` so the badge still renders honestly. Confirm `app.py`'s tags still match `make_video.py`'s `EVIDENCE` regex (they do).
  Files: `agents/observer_agent.py`, `agents/interviewer_agent.py`, `agents/knowledge_architect.py`, `agents/curriculum_agent.py`, `agent/app.py`
  Verify: `python3 -m agent.app --demo --no-cloud 2>&1 | grep -E '^\[(observer|interviewer|architect|curriculum|plan|metric)\]'` prints clean tagged lines with no `<thinking>`/`Tool #`/JSON noise between them; the command exits 0. Then `python3 -c "import sys; sys.path.insert(0,'.'); from agents.orchestrator import run_skill_capture_pipeline; print('ok')"` still imports.

- [ ] 2. Complete `kit/measure.py` to score every case by label and write `results.json`.
  Rewrite the case loop to dispatch by `label` and score against the case's `expected_*` field:
  - `observer` → run `ObserverAgent().analyze(text)`, score = fraction of `expected_gaps` found in `knowledge_gaps` (synonym match via existing `_SYNONYMS`).
  - `interviewer` → run `InterviewerAgent().generate_questions([text], craft)`, score = fraction of `expected_questions` whose concept appears in the generated questions (extend `_SYNONYMS` with concepts like `tactile tension`, `feel when correct`, `test method`).
  - `knowledge_architect` → build a minimal `observation` from the case text, run `KnowledgeArchitectAgent().build_fingerprint(observation, {}, craft, "Artisan")`, score = fraction of `expected_fingerprint_keys` present and non-empty in the returned fingerprint dict.
  - `curriculum_quiz` → run `CurriculumAgent().create_lesson(fingerprint_from_text)`, score = 1.0 if `expected_answer` appears in any quiz question's correct answer (case-insensitive), else 0.0.
  Keep the existing baseline comparison for observer cases. Write BOTH `kit/results/results.json` (shape in decision 2, with a `rows[]` entry per case) and `kit/results/MEASURE.md` (human-readable, regenerated from the same data). Keep `--limit N` working. `main()` returns 0 on success. Crashes per case are caught and recorded as a failed row (`passed:false`, `detail` = the error) — never hidden, matching the strands-ship pattern.
  Files: `kit/measure.py`
  Verify: `python3 kit/measure.py --limit 3` runs, prints per-case pass/fail, and writes `kit/results/results.json` that is valid JSON with a `rows` array whose length equals cases run and an `overall_pass_rate` field. `python3 -c "import json; r=json.load(open('kit/results/results.json')); assert 'rows' in r and 'overall_pass_rate' in r; print(len(r['rows']), 'rows')"` succeeds.

- [ ] 3. Create `kit/make_article.py` — honest-numbers article generator.
  Reads `kit/results/results.json` and `kit/results/video_run.json`. Requires BOTH to exist (error clearly, naming the missing `python kit/ss.py bench` / `python kit/ss.py video` command, if absent — do not invent numbers). Generates `demo/ARTICLE_GENERATED.md`: a Builder Center article whose "Measured results" section cites real numbers pulled verbatim from the two JSON files — cases run, per-label pass rates, `overall_pass_rate`, fingerprint-key coverage, tacit-question %, per-case matched/missed, video length (`seconds`), `under_3_min`, per-scene exit codes, evidence-line count. Include a "How to reproduce" section listing the exact `python kit/ss.py bench/video/article` commands. Also write `demo/FACTS.md`: a compact bullet list of every measured number with its source file path, paste-ready into the human article. Cite the Strands SDK version via `importlib.metadata.version("strands-agents")`. Leave `demo/BUILDER_CENTER_ARTICLE.md` untouched. Adapt the structure (Facts + article-from-measured-numbers) from `kit/strands-ship/kit/ship_kit/submit.py`'s `facts()` function, but use SKILL DNA's own metrics, not HeatSafe's.
  Files: `kit/make_article.py` (new), `demo/ARTICLE_GENERATED.md` (generated), `demo/FACTS.md` (generated)
  Verify: after items 2 and 6 have produced both source files, `python3 kit/make_article.py` writes both outputs; `python3 -c "import pathlib; t=pathlib.Path('demo/ARTICLE_GENERATED.md').read_text(); assert 'results.json' in t and str(__import__('json').load(open('kit/results/results.json'))['cases_run']) in t; print('article has real numbers')"` succeeds. Then temporarily delete `kit/results/results.json` and confirm `python3 kit/make_article.py` prints a clear error and exits non-zero instead of writing fabricated numbers.

- [ ] 4. Create `kit/check_submission.py` — submission artifact completeness check.
  Verify each artifact is present and non-empty, printing a PASS/FAIL table (adapt the row format from `kit/strands-ship/kit/ship_kit/submit.py`). Required artifacts and their paths:
  - Demo video: `kit/results/demo.mp4` OR `kit/results/demo.webm` (accept either; non-empty; report which).
  - `kit/results/video_run.json` (valid JSON with `scenes` and `under_3_min`).
  - `kit/results/results.json` (valid JSON with `rows` and `overall_pass_rate`).
  - `kit/results/MEASURE.md` (non-empty).
  - `demo/ARTICLE_GENERATED.md` (non-empty) — and note `demo/BUILDER_CENTER_ARTICLE.md` presence as advisory.
  - `kit/cases/cases.jsonl` (present; every line has a `signed_by`).
  - `README.md` (present).
  - `.env` present (do NOT print its contents).
  Add an advisory secret-scan (reuse the `SECRET` regex from strands-ship `submit.py`) over tracked files, skipping `kit/strands-ship/`, `.venv`, `__pycache__`, and `node_modules`. Print a summary line `N FAIL, M advisory`. Return `0` only if zero required FAILs; else `1`.
  Files: `kit/check_submission.py` (new)
  Verify: with all artifacts present (after items 2, 3, 6), `python3 kit/check_submission.py` prints all-PASS rows and exits 0. Then remove `kit/results/results.json` and confirm it prints a FAIL row for that artifact and exits 1.

- [ ] 5. Wire `kit/ss.py` subcommands and add the `./kit` wrapper.
  Add subcommands so the CLI matches the user's mental model:
  - `bench` → calls `kit/measure.py` (writes `results.json` + `MEASURE.md`). Keep `measure` as an alias for backward compat.
  - `video --target local` (default) → runs `kit/make_video.py`. Accept `--target` (default `local`); if anything other than `local` is passed, error: "AgentCore deployment not supported by this kit; use --target local". Pass `--spec` through (default `video.json`).
  - `article` → runs `kit/make_article.py`.
  - `check` → repurpose to run `kit/check_submission.py` (this replaces the old env checklist). Move the old env-checklist logic into a new `status` subcommand so it is not lost.
  Keep existing `bedrock`, `blocks`, `block`, `pipeline` working. Each new subcommand must `sys.path.insert(0, str(ROOT))` and load `.env`. Then create a `./kit` executable shell wrapper at the project root (mode 0755) whose body is `#!/usr/bin/env bash\nexec python3 "$(dirname "$0")/kit/ss.py" "$@"` so `./kit bench`, `./kit video --target local`, `./kit article`, `./kit check` all work.
  Files: `kit/ss.py` (modify), `kit` (new executable wrapper at project root)
  Verify: `python3 kit/ss.py --help` lists `bench`, `video`, `article`, `check`, `status`. `./kit bench --limit 2` runs and writes `kit/results/results.json`. `./kit video --dry-run` prints scenes. `./kit video --target agentcore` errors cleanly. `./kit check` prints the PASS/FAIL table. The existing `./kit bedrock` still works.

- [ ] 6. (Environment) Install ffmpeg for mp4 output, then run the full pipeline end-to-end.
  `brew install ffmpeg` (medium-risk, reversible Homebrew package install — confirm with the user before running if you prefer; it only adds a formula, removes nothing). Then run the pipeline in dependency order and capture real artifacts:
  1. `./kit bench` (or `python3 kit/ss.py bench`) → `kit/results/results.json` + `kit/results/MEASURE.md`.
  2. `./kit video --target local` → `kit/results/demo.mp4` + `kit/results/video_run.json` (under 3 min).
  3. `./kit article` → `demo/ARTICLE_GENERATED.md` + `demo/FACTS.md`.
  4. `./kit check` → all PASS.
  Files: (none — runs the pipeline; artifacts land in `kit/results/` and `demo/`)
  Verify: all four commands succeed in order; `kit/results/demo.mp4` exists and `ffprobe` (from ffmpeg) reports a duration `< 180`; `kit/results/video_run.json` has `"under_3_min": true` and every scene `exit: 0`; `./kit check` exits 0.

---

## Verification checklist the implementer must achieve before done

1. `python3 -m agent.app "<a sungudi craft step>" --no-cloud` runs the full pipeline and prints tagged evidence lines, no Python errors, no `<thinking>`/`Tool #` noise.
2. `python3 kit/ss.py bench` (or `./kit bench`) writes `kit/results/results.json` with per-case metrics and `overall_pass_rate`.
3. `python3 kit/ss.py video --target local` (or `./kit video --target local`) produces `demo.mp4` (or `demo.webm` if ffmpeg absent) and `kit/results/video_run.json` with real latencies/evidence and `under_3_min: true`.
4. `python3 kit/ss.py article` produces/refreshes `demo/ARTICLE_GENERATED.md` + `demo/FACTS.md` with numbers drawn only from `run.json`/`results.json`; `demo/BUILDER_CENTER_ARTICLE.md` unchanged.
5. `python3 kit/ss.py check` (or `./kit check`) passes when all artifacts are present and prints a clear PASS/FAIL report.
6. Final report: which steps passed live and which (if any) could not be verified and why.

## Notes on API keys / live-vs-mock verification

The `.env` contains a working AWS key (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `BEDROCK_MODEL_ID=amazon.nova-pro-v1:0`). Do not echo secret values anywhere in code, output, or the article. The agent stages (Observer/Interviewer/Architect/Curriculum) need this key and it is confirmed working live (the demo reached the Architect stage on real Bedrock calls). Therefore `bench` and `video` should be verified **live** against the real agents.

The cloud side-services (S3 `skill-dna-fingerprints-902605180945`, DynamoDB, Polly) are best-effort: if those resources aren't provisioned, `app.py`'s `try/except` prints a graceful skip line and the pipeline continues. If cloud retries risk pushing the video over 3 minutes, run the video with `--no-cloud` (item 1 flag) and state in the final report that cloud save was skipped (it is Phase 2 per the existing article). The honest-numbers rule still holds: whatever the video actually ran is what `video_run.json` records and what the article cites.

If at any point the Bedrock key is exhausted mid-run, the automation scripts (`make_article.py`, `check_submission.py`, `ss.py`) must still work against whatever `results.json`/`video_run.json` were already produced — verify them against an existing run even if a fresh full run can't complete, and state clearly what was verified live vs. what still needs a fresh key.
