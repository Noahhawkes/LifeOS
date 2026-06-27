# Chronicle — Tips Workflow

**Purpose:** Analyze session history and surface personalized, ranked tips for using PAI more effectively.

The workflow runs four parallel data collection threads, synthesizes patterns, then maps those patterns to concrete improvement opportunities.

---

## Phase 1 — Parallel Data Collection

Run all four reads simultaneously:

### 1A. Execution Log (Skill Usage Patterns)

```bash
cat ~/.claude/PAI/MEMORY/SKILLS/execution.jsonl 2>/dev/null
```

Parse each JSONL line. Extract:
- `skill` — which skill was invoked
- `workflow` — which workflow within that skill
- `status` — ok or error
- `ts` — timestamp (for recency weighting)
- `input` — 8-word summary of the task

Build:
- **Frequency map**: `{ skill: count }` sorted descending
- **Workflow map**: `{ "Skill/Workflow": count }` sorted descending
- **Error map**: `{ skill: error_count }` — skills with failures
- **Recency map**: last-used date per skill
- **Never-used list**: all skills in `~/.claude/skills/` whose names do NOT appear in the log

If execution.jsonl is empty or missing: note this, skip frequency analysis, proceed to goal-based tips only.

### 1B. Session Registry

```bash
cat ~/.claude/PAI/MEMORY/STATE/work.json 2>/dev/null
cat ~/.claude/PAI/MEMORY/STATE/session-names.json 2>/dev/null
```

Extract:
- Task descriptions (for theme clustering)
- Effort tiers used (E1–E5 distribution)
- Phase patterns (are sessions completing or stalling?)
- Most recent 10 session names/tasks

### 1C. WORK Directory Scan

```bash
ls -t ~/.claude/PAI/MEMORY/WORK/ 2>/dev/null | head -20
```

Extract directory name themes (e.g., "bug-fix", "newsletter", "research-X"). These reveal task categories the user works on repeatedly.

### 1D. TELOS Goals + Challenges

```bash
cat ~/.claude/PAI/USER/TELOS/GOALS.md 2>/dev/null
cat ~/.claude/PAI/USER/TELOS/CHALLENGES.md 2>/dev/null
cat ~/.claude/PAI/USER/TELOS/STRATEGIES.md 2>/dev/null
```

Extract goal keywords and challenge themes. These form the "relevance filter" — only recommend skills that connect to stated goals or active challenges.

---

## Phase 2 — Available Skill Index

Read the frontmatter `name:` and `description:` from every SKILL.md:

```bash
find ~/.claude/skills/ -name "SKILL.md" -maxdepth 2 | while read f; do
  head -10 "$f"
  echo "---FILE_SEP---"
done
```

Build a map of `{ skill_name: description_excerpt }` for all 45+ skills.

---

## Phase 3 — Pattern Analysis

Using Phase 1 and Phase 2 data, identify:

### Pattern A: Skill Overuse Without Alternatives
Skills run 10+ times — check if a more powerful skill covers the same ground.
- E.g., heavy Research use → has the user tried IterativeDepth for multi-pass deep dives?
- E.g., manual text tasks → has the user tried the relevant Fabric pattern?

### Pattern B: Goal-Skill Gaps (most valuable tips)
For each TELOS goal/challenge, check: is there a PAI skill that directly addresses it but has zero runs?
- Goal "write more" + WriteStory never used → high-priority tip
- Challenge "too many tabs / research overload" + Browser/BrightData never used → high-priority tip

### Pattern C: Workflow Underuse Within Known Skills
User runs a skill but always uses only one workflow — are there other workflows in the same skill that could help?
- E.g., PAIUpgrade used but only via Upgrade workflow — MineReflections and AlgorithmUpgrade might help too
- E.g., Knowledge used for `search` only — has user tried `mine` to harvest recent conversations?

### Pattern D: Error Patterns
Skills with >20% error rate → surface a gotcha or alternative approach.

### Pattern E: Efficiency Gaps
If sessions consistently show E3/E4/E5 effort for tasks that look like E1/E2 territory, the Algorithm mode-detection hook may not be tuned — flag it.

### Pattern F: Session Completion Rate
If work.json shows many sessions in early phases (PLAN, ANALYZE) with no COMPLETE phase — flag this as a stall pattern and recommend ISA discipline.

---

## Phase 4 — Tip Generation

Generate **5–10 ranked tips** organized into tiers:

### 🔴 HIGH IMPACT — act on these first
Tips where evidence is strong (multiple data points all pointing to the same gap) and the gain is large.

### 🟠 DISCOVERY — try these once
Skills/workflows the user has never touched that directly match a stated goal or dominant task type.

### 🟡 EFFICIENCY — do this differently
Ways to get the same outcome with less effort, fewer steps, or better quality.

### 🟢 GOOD HYGIENE — reinforce this habit
Things the user does well already that are worth being intentional about.

---

## Output Format

```
════ CHRONICLE TIPS ══════════════════════════════
📊 USAGE SNAPSHOT (last [N] sessions, [X] unique skills):
  Most used: [Skill1] ([N]×), [Skill2] ([N]×), [Skill3] ([N]×)
  Never used: [N] skills (of [total] available)
  Error-prone: [Skill] ([X%] failure rate) ← if any

──────────────────────────────────────────────────

🔴 HIGH IMPACT

  1. [Tip title — 8 words max]
     Evidence: [what the data shows]
     Action: [exact command or Skill("X", "...") to try]

  2. ...

🟠 DISCOVERY

  3. [Skill you've never tried but should]
     Why it fits: [connection to goal/task pattern]
     Try: Skill("[Name]", "[suggested starting point]")

  4. ...

🟡 EFFICIENCY

  5. [Better way to do something you already do]
     Currently: [what you do now]
     Better: [what to do instead]

🟢 GOOD HYGIENE

  6. [Something you're doing right — keep it up]

──────────────────────────────────────────────────
💡 [1-sentence takeaway — the single most valuable change]
══════════════════════════════════════════════════
```

**Rules for tip quality:**
- Every tip must cite specific evidence from the data (`"you've run Research 23 times"`, `"WriteStory has 0 runs despite 'write more' goal"`)
- No generic PAI advice — tips must be personalized to THIS user's actual patterns
- Action must be specific: exact skill invocation, workflow name, or concrete step
- If execution.jsonl is empty, skip frequency-based tips and rely entirely on goal-skill gap analysis
- Cap at 10 tips — quality over quantity

---

## After Output

Say: "These tips are based on [N] skill executions across [date range]. Run `/chronicle stats` for raw numbers or `/chronicle gaps` to see all unused skills."
