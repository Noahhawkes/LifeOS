---
name: Chronicle
description: "Session history analysis and personalized PAI usage tips. Mines execution logs, work session registry, and MEMORY directories to surface usage patterns, then generates ranked, personalized tips: underused skills relevant to your work, workflows that could replace manual patterns, efficiency shortcuts, and common failure modes to avoid. Four sub-commands: tips (personalized recommendations from usage patterns — default), stats (usage frequency table for all skills/workflows), review (summary of sessions in a time window), gaps (skills you've never used that match your TELOS goals). Data sources: MEMORY/SKILLS/execution.jsonl, MEMORY/STATE/work.json, MEMORY/STATE/session-names.json, MEMORY/WORK/ directories, USER/TELOS/ goals. Output: ranked tips with evidence ('you ran X 12 times but never used Y which does Z better'), skill discovery table, usage heatmap by week. USE WHEN chronicle, session history, usage tips, how am I using PAI, what skills haven't I tried, PAI tips, usage patterns, skill recommendations, what should I try, chronicle tips, chronicle stats, chronicle review, chronicle gaps, how to use PAI better, personalized tips, what am I missing."
argument-hint: [tips|stats|review|gaps] [--days N]
effort: low
---

## Customization

**Before executing, check for user customizations at:**
`~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/Chronicle/`

If this directory exists, load and apply any PREFERENCES.md found there. These override default behavior.

## 🚨 MANDATORY: Voice Notification (REQUIRED BEFORE ANY ACTION)

**Send before anything else when this skill is invoked.**

```bash
curl -s -X POST http://localhost:31337/notify \
  -H "Content-Type: application/json" \
  -d '{"message": "Running the WORKFLOWNAME workflow in the Chronicle skill to ACTION"}' \
  > /dev/null 2>&1 &
```

# Chronicle

**Purpose:** Turn your PAI session history into actionable self-improvement. Chronicle reads what you've actually done — not what you intended — and surfaces gaps, patterns, and opportunities.

The key insight: most PAI users run the same 5-8 skills repeatedly and never discover the other 37. Chronicle fixes that by matching unused skills to proven interests.

## Command Routing

| Input | Route | Action |
|-------|-------|--------|
| `/chronicle` (no args) | **tips** | Personalized recommendations — default |
| `/chronicle tips` | **tips** | Personalized recommendations from usage patterns |
| `/chronicle stats` | **stats** | Usage frequency table for all skills/workflows |
| `/chronicle review [--days N]` | **review** | Session summary for the past N days (default: 30) |
| `/chronicle gaps` | **gaps** | Skills never used that match TELOS goals |

If `$ARGUMENTS` is empty or doesn't match a subcommand, run **tips**.

## Workflows

| Workflow | File |
|----------|------|
| **Tips** | `Workflows/Tips.md` |
| **Stats** | Inline (see Stats section below) |
| **Review** | Inline (see Review section below) |
| **Gaps** | Inline (see Gaps section below) |

---

## stats

Show raw usage frequency for all skills and workflows over all time.

**Step 1 — Read execution log:**
```bash
cat ~/.claude/PAI/MEMORY/SKILLS/execution.jsonl 2>/dev/null || echo "[]"
```

**Step 2 — Parse and aggregate:**
Extract `skill` and `workflow` fields. Count invocations per skill, per workflow, and total. Compute error rate (`status: "error"` / total per skill).

**Step 3 — Output:**

```
═══ CHRONICLE STATS ══════════════════════════
📊 SKILL USAGE (all time, sorted by count):

  Skill               Runs   Workflows   Errors
  ──────────────────────────────────────────────
  [skill]             [N]    [top wf]    [E%]
  ...

📅 ACTIVITY:
  First session: [date]
  Last session:  [date]
  Total runs:    [N]
  Error rate:    [X%]

🔍 TOP WORKFLOWS (across all skills):
  1. [Skill/Workflow] — [N] runs
  2. ...
═════════════════════════════════════════════
```

Present in NATIVE mode.

---

## review [--days N]

Summarize sessions from the past N days (default: 30).

**Step 1 — Read session registry:**
```bash
cat ~/.claude/PAI/MEMORY/STATE/work.json 2>/dev/null
cat ~/.claude/PAI/MEMORY/STATE/session-names.json 2>/dev/null
```

**Step 2 — Filter by date window:**
Use the `--days` argument (default 30) to filter entries by their timestamp.

**Step 3 — Scan WORK/ directories for recent ISAs:**
```bash
find ~/.claude/PAI/MEMORY/WORK/ -maxdepth 1 -type d -newer $(date -d "-${DAYS} days" +%Y-%m-%d 2>/dev/null || date -v-${DAYS}d +%Y-%m-%d) 2>/dev/null | tail -20
```

**Step 4 — Output:**

```
═══ CHRONICLE REVIEW (last [N] days) ══════
📋 SESSIONS ([count]):
  - [slug] — [task] | [phase] | [effort]
  ...

🗂️ WORK DIRECTORIES ([count]):
  - [dir-name] (recent)
  ...

📈 ACTIVITY TREND:
  [Week-by-week summary if enough data]
════════════════════════════════════════════
```

Present in NATIVE mode.

---

## gaps

Find skills you've never used that match your TELOS goals and active projects.

**Step 1 — Read execution log to find USED skills:**
```bash
cat ~/.claude/PAI/MEMORY/SKILLS/execution.jsonl 2>/dev/null
```

**Step 2 — Read all available skills:**
```bash
find ~/.claude/skills/ -name "SKILL.md" -maxdepth 2
```
For each, extract the `name:` and `description:` from frontmatter.

**Step 3 — Read TELOS goals and projects:**
```bash
cat ~/.claude/PAI/USER/TELOS/GOALS.md 2>/dev/null
cat ~/.claude/PAI/USER/TELOS/CHALLENGES.md 2>/dev/null
cat ~/.claude/PAI/USER/PROJECTS/PROJECTS.md 2>/dev/null
```

**Step 4 — Match unused skills to goals:**
For each skill never in the execution log, check if its description semantically overlaps with any TELOS goal, challenge, or project theme. Surface only genuine matches — not every skill, just relevant ones.

**Step 5 — Output:**

```
═══ CHRONICLE GAPS ═══════════════════════
🔍 SKILLS YOU'VE NEVER USED (relevant to your goals):

  [Skill] — "[why it matches goal X]"
  Invoke: Skill("[Skill]", "...")
  ...

✅ ALL AVAILABLE SKILLS: [N total, N used, N untried]
══════════════════════════════════════════
```

Present in NATIVE mode.

---

## Gotchas

- **execution.jsonl may be empty on fresh installs.** If so, the tips and stats commands will say so and fall through to goal-based recommendations only.
- **work.json schema can vary.** Extract what you can; skip malformed entries silently.
- **Tips are only as good as the execution log.** The more workflows a user runs, the richer the recommendations.
- **Never surface security, health, finances, contacts, or relationship data** even if those files are visible — Chronicle reads only SKILLS/, STATE/, WORK/, and TELOS/GOALS+CHALLENGES.

## Examples

**Example 1: Quick tips**
```
User: "/chronicle tips"
→ Reads execution.jsonl → identifies top skills (Research, ExtractWisdom, PAIUpgrade used 20+ times)
→ Reads TELOS goals → notes "write more" as a goal
→ Finds WriteStory skill never used despite writing goal
→ Returns: "You've run Research 23 times but never tried WriteStory — it pairs research with narrative drafting"
```

**Example 2: Usage stats**
```
User: "/chronicle stats"
→ Aggregates all execution.jsonl entries
→ Returns table: Research (47 runs), PAIUpgrade (31), ExtractWisdom (28), Knowledge (12)...
```

**Example 3: Review last 7 days**
```
User: "/chronicle review --days 7"
→ Filters session registry to last 7 days
→ Returns: 6 sessions, 3 work directories, top tasks: "API debugging" / "newsletter draft"
```

## Execution Log

After completing any workflow, append a single JSONL entry:

```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","skill":"Chronicle","workflow":"WORKFLOW_USED","input":"8_WORD_SUMMARY","status":"ok|error","duration_s":SECONDS}' >> ~/.claude/PAI/MEMORY/SKILLS/execution.jsonl
```
