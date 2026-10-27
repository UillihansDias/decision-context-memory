# Integration and access patterns

## Instruction file vs decision ledger

Keep stable agent operating conventions, project commands, and tool instructions in the repository's existing `AGENTS.md`/`agents.md` (respect its naming convention). Keep choices that can change during work, rejected alternatives, lasting constraints, consequential user corrections, and their reasons in project-local `decisions.md`. Do not create a competing instruction file merely to enable this skill.

When authorised to update project instructions, add a concise entry to the existing file:

> At the beginning of each work session, read the project-local `decisions.md` if available. Reconsult it before choices that may conflict with established decisions. Update it at meaningful decision boundaries for settled choices, explicit rejections, lasting constraints, and consequential user corrections. Record what and why, preserve superseded rationale, and do not log tentative proposals.

A skill cannot guarantee that a host automatically loads it or reads files. Do not claim automatic invocation unless a real host mechanism is configured and verified. Prefer a small, explicit instruction in the existing project guidance when session-start behaviour is required and authorised.

## Session lifecycle

At startup, verify the project root and read the ledger before material recommendations. During work, write at meaningful decision boundaries, not after every message. Before handoff, check omissions, duplicates, and conflicts. On context reset, re-read the ledger if the runtime permits it; chat memory alone is not equivalent to the project-local record.

## No filesystem access

If project files cannot be read or written, do not imply that a durable ledger exists. Present a compact patch or proposed lines, identify the intended project path, and explain that they have not been persisted. Do not ask for access if the user can simply apply the patch.

## Safety and collaboration

Do not record passwords, access tokens, or irrelevant personal information. Treat rationale as project data and minimise sensitive detail. Before concurrent edits, inspect the latest ledger. The supplied CLI serializes cooperating CLI processes; manual edits and other tools do not participate in its lock, so re-read immediately before writing. If merge-conflict markers exist, stop and ask for resolution rather than editing around them.
