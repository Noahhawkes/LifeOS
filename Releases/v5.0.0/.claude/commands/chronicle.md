---
name: chronicle
description: Review session history and surface personalized PAI usage tips. Analyzes skill execution logs, session registry, and TELOS goals to recommend what to try next, what to do differently, and what you're underusing.
argument-hint: [tips|stats|review|gaps] [--days N]
---

# chronicle — Redirect

This command routes to the **Chronicle** skill.

**Invoke the skill directly:**

```
Skill("Chronicle", "$ARGUMENTS")
```

Sub-commands:
- `/chronicle tips` — personalized recommendations from your usage patterns (default)
- `/chronicle stats` — raw usage frequency table for all skills/workflows
- `/chronicle review [--days N]` — session summary for the past N days
- `/chronicle gaps` — skills you've never used that match your TELOS goals
