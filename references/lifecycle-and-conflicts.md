# Lifecycle and conflict handling

## Capture threshold

Capture confirmed outcomes: settled decisions, explicit exclusions, enduring constraints, and consequential user corrections. Do not promote an agent suggestion, brainstorming candidate, hypothesis, routine implementation detail, or temporary state into a decision. When a user corrects the agent, preserve the correction's substance and the reason actually supplied; do not defend the earlier assumption in the ledger.

## Conflict resolution

1. Identify active entries for the same project scope and compare their actual requirements, conditions, and assumptions.
2. Distinguish contradiction from different scopes, dates, environments, or assumptions. Do not resolve semantic conflicts by choosing the newest entry automatically.
3. If the user clearly replaces an earlier decision, add the replacement first, then mark the old entry superseded and link it to the replacement. Preserve the old rationale.
4. If replacement is unclear, surface the conflict and ask for resolution rather than silently choosing.
5. If higher-priority instructions or current authorization conflict with the ledger, follow the higher authority and flag the ledger for reconciliation. The ledger is context, not permission.
6. If external evidence changes, verify its authority and freshness before treating it as grounds to supersede a durable choice.

## Scope and maintenance

A ledger belongs to one project or working directory. Avoid reusing it for unrelated projects. A monorepo may use scoped subproject ledgers when choices materially differ; state the scope in the entries where it is not obvious. Preserve superseded rationale rather than deleting it. Periodically consolidate exact duplicates while retaining materially distinct corrections or conditions.

Structural validation can catch malformed entries, duplicate IDs, repeated active statements, and broken replacement references. It cannot reliably decide whether differently worded statements conflict; the agent must review meaning and scope.

## Example

- D-0001 | superseded | decision | Use polling for updates | because initial integration was simpler | rejected webhooks because endpoint access was unavailable | superseded by D-0003
- D-0002 | active | constraint | Do not collect customer email in telemetry | because minimisation is required
- D-0003 | active | decision | Use signed webhooks for updates | because endpoint access is now available and latency matters | rejected polling because it adds avoidable delay
