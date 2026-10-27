---
name: decision-context-memory
description: "Maintain a project-local decisions.md ledger of settled decisions, rejected alternatives, lasting constraints, and user corrections with rationale. Use when starting or resuming long-running work, revisiting prior choices, changing requirements, or preserving project context across sessions. Do not use as a chat transcript, general memory dump, or private-data store."
---

# Decision Context Memory

Keep established project choices consistent across sessions and context loss. The project-local `decisions.md` records settled project decisions; `AGENTS.md` (or the project's existing instruction file) remains the source for stable agent instructions. Neither file outranks current user authorization or higher-priority instructions. Never assume local files are accessible unless filesystem access is available.

## Workflow

1. **Establish scope.** Identify the project root and relevant subproject. A ledger belongs to one project/scope, not the agent's home folder by default. If the root is ambiguous and could change which decisions apply, ask; otherwise use the active project directory.
2. **Start or resume.** Check for `decisions.md` and read it before material recommendations. If absent and work is complex, ongoing, or explicitly asks for persistence, initialise it from `assets/decisions.template.md`. Preserve existing content; never silently overwrite or replace a ledger.
3. **Capture at decision boundaries.** Record only settled choices, explicit exclusions, lasting constraints, and consequential user corrections. Capture what and why, plus rejected alternatives and their rationale when relevant. Do not log tentative options, routine implementation details, or transient state.
4. **Consult before changing course.** Reconsult relevant entries before revisiting or proposing an excluded approach. If current evidence or instructions conflict with a ledger entry, surface the conflict and follow the applicable authority; do not quietly rewrite history.
5. **Handoff.** Check for important omissions, duplicate active entries, and unresolved conflicts. Report the path and any material unresolved issue. Never claim persistence unless the write succeeded.

## Recording protocol

- Prefer one line per item with a unique ID, status, category, statement, rationale, and (when relevant) rejected alternative and reason.
- Format: `- D-0001 | active | decision | Choose X | because Y | rejected Z because W`. Omit the rejection field when irrelevant. A superseded entry keeps its original text and ends with `| superseded by D-0002`.
- Categories: `decision`, `rejection`, `constraint`, `correction`. Statuses: `active`, `superseded`.
- Preserve the user's rationale faithfully. If it is unknown, ask only when material; otherwise record `reason not provided`. Never invent a rationale.
- Consolidate duplicate active entries. When superseding, retain the old statement and rationale and link it to the replacement; do not erase history. A reference may point to a later-superseded decision, preserving a valid chain.
- Record only durable, project-relevant information. Minimise sensitive content; never store secrets, credentials, or unrelated personal data.
- Do not treat the ledger as a transcript, task list, source of truth for current state, or override to higher-priority instructions.

## Resources and CLI

- Read `references/lifecycle-and-conflicts.md` when reconciling contradictory instructions, repairing a messy ledger, handling multiple scopes, or migrating an older format.
- Read `references/integration.md` when integrating with project instructions, configuring session startup, or operating without filesystem access.
- Use `assets/decisions.template.md` only when initialising a new ledger.
- The optional `scripts/decisions.py` serializes cooperating CLI operations and uses atomic writes:
  - `init --root <project>` creates a ledger but preserves and validates an existing one.
  - `add --root <project> --category decision --decision 'Choose X' [--why 'Reason'] [--rejected 'Alternative because reason']` appends a new active entry. Omitted `--why` becomes `reason not provided`.
  - `supersede --root <project> --id D-0001 --by D-0002` marks an active entry superseded after its active replacement exists.
  - `validate --root <project>` checks syntax, unique IDs, duplicate active statements, and supersession references. It cannot determine whether differently worded decisions conflict semantically; review that yourself.
- Direct editing is acceptable if the same schema, history preservation, conflict review, and validation are maintained. Never overwrite a ledger to “repair” it; preserve a recoverable copy and reconcile entries deliberately.

## Verification

Before finishing, ensure the ledger exists when access permits; check new entries for clear disposition and faithful rationale; review duplicate or conflicting active entries; validate structure and references when the helper is usable; and inspect the final file after writing. If filesystem access is unavailable, provide exact proposed lines and their intended project path instead. Distinguish structural validation from semantic conflict review.
