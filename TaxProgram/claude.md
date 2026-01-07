Continuity Ledger (append-only, compaction-safe)
MANDATORY: Create an Active Session Ledger File (append-only)
Storage Location: \ContinuityDocs\
Filename Format: YYYYMMDD-HHMMSS.md (e.g., 20250124-143005.md)
Action: Your first action in a new session is to check the current system date/time and create this file.
This file is the canonical session briefing and must be append-only (do not overwrite prior entries).
Only exception: the Lessons Learned section (see below) is intentionally mutable (updated/replaced).
File Structure (Required)
1. Lessons Learned (mutable; updated/replaced)
This section is a living summary of what’s been learned so far and may be revised as new evidence emerges.
When lessons change, edit/replace this section in-place (do not append a new “version” of lessons).
2. Ledger Entries (append-only; timestamped)
All operational continuity is captured as a chronological series of timestamped entries appended to the end of the file.
Never delete or rewrite old entries. If something was wrong, append a Correction entry.
How it works
Start of Every Turn
Read the active session ledger file from \ContinuityDocs\.
Determine “current state” by using the most recent ledger entry (and the current Lessons Learned section).
Do the work.
Immediately after meaningful progress or state change, append a new timestamped entry.
Append-only rule
Do not replace/overwrite prior ledger entries.
If you need to revise understanding, append a new entry starting with Correction: and reference the earlier timestamp you’re correcting.
When to update Lessons Learned (mutable)
Update/replace Lessons Learned only when a durable lesson changes (new evidence, invalidated assumption, better approach discovered).
Update Triggers (append a new entry whenever…)
Append a new timestamped entry when there is a change in:
The primary goal or success criteria.
Constraints, assumptions, or key technical decisions.
Progress state (Done / Now / Next).
Outcomes of significant tool calls, experiments, tests, deployments, or evaluations.
Discovery of errors requiring corrections (use Correction:).
Content Standard
Keep entries concise and fact-based.
Bullets only. No transcripts.
Mark unverified information as UNCONFIRMED.
Prefer concrete identifiers: filenames, IDs, commands, PRs, issue links, etc.
Handling Uncertainty & Compaction
If you detect context compaction (loss of recent history), rebuild continuity using:
The visible context + the last ledger entry
Mark gaps as UNCONFIRMED
Ask 1–3 targeted questions only if needed to bridge critical gaps
functions.update_plan vs the Ledger
functions.update_plan: short-term tactical execution (next 3–7 micro-steps).
Active Ledger File: long-running continuity (what/why/current state over time).
Keep them aligned: when the tactical plan changes, append a ledger entry reflecting the higher-level intent/state change.
In replies
Ledger Snapshot (required): Every response begins with a brief snapshot derived from the latest ledger entry:
Goal
Now / Next
Open Questions
Full Ledger: Do not print the full file by default (it will grow). Only print:
the latest entry, if it materially changes the situation, or
the full ledger if the user explicitly asks.
Ledger Template (Paste into the file)
Lessons Learned (mutable — replace/update this section)
(Keep this as a short, curated list. Update as learnings evolve.)
Ledger Entries (append-only — add new entries at the end)
Entry — YYYY-MM-DD HH:MM:SS (local)
Goal (incl. success criteria):
…
Constraints/Assumptions:
…
Key decisions:
…
State:
Done: …
Now: …
Next: …
Open questions (mark UNCONFIRMED if needed):
…
Working set (files/ids/commands):
…
Notes / Outcomes (optional):
…
Correction (optional; if applicable):
Correction: … (reference the earlier entry timestamp you’re correcting)