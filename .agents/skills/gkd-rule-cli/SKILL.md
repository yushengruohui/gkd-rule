---
name: gkd-rule-cli
description: Create or repair GKD TypeScript subscription rules from GKD snapshot ZIP files. Use when inspecting a snapshot, designing a safe selector, validating a rule with the GKD inspector, building a GKD subscription, or preparing a narrowly scoped local rule commit.
---

# GKD Rule CLI

Turn a GKD snapshot into a safe, validated app rule. Keep all agent-facing files and output in English.

## Inspect evidence

1. Require an accessible GKD snapshot URL for each target rule. Do not invent one if it is absent; ask the user to provide it.
2. Inspect the ZIP read-only before authoring. Run:

   ```powershell
   python .agents/skills/gkd-rule-cli/scripts/inspect_snapshot.py <snapshot.zip>
   ```

   Confirm the package, exact `activityId`, app version, target node, and the node that is actually clickable. Treat screenshots as supporting evidence only.
3. Record the user entry path and expected action. For every exclusion, retain positive and negative snapshot URLs.

## Author safely

1. Read `.agents/spec/gkd-rules.md` and existing `src/apps/<package>.ts` before editing.
2. Create or update `src/apps/<package>.ts` with `defineGkdApp`; retain stable, unique app, group, and rule keys.
3. Narrow `activityIds` to the observed activity. Prefer `id`, `vid`, and `desc`. Bind text selectors to the activity and meaningful hierarchy/visibility context; never use a generic skip, close, or cancel label by itself.
4. Select the observed clickable container, not a decorative text child. Add exclusions only when a snapshot proves the false positive.
5. Test the smallest app object in the GKD inspector's in-memory subscription. Verify the intended click and adjacent, search, settings, and subsequent screens do not trigger. In-memory validation does not replace source changes.

## Validate and commit

1. Run `pnpm check`, then `pnpm build`. Never edit `dist/` manually.
2. Review `git diff --check` and focused diffs for the app source and generated `dist/` files.
3. Before staging, require a clean tracked worktree (`git status --porcelain` may contain only untracked files). If tracked changes already exist, do not commit; report them and preserve them.
4. When validation passes and the tracked worktree was clean, stage only the changed `src/apps/<package>.ts` and build-generated `dist/` files. Do not stage ZIPs, caches, editor files, or unrelated untracked files.
5. Create one local commit with a short imperative subject, such as `Add rules for cn.example.app`. Do not run `git push` or trigger GitHub Actions.

## Boundaries

- Never edit a snapshot ZIP.
- Do not claim inspector validation without performing it.
- Do not commit when evidence, validation, or a clean pre-staging tracked worktree is missing.