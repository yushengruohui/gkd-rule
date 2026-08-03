---
name: gkd-rule-cli
description: Create or repair GKD TypeScript subscription rules from local GKD snapshot ZIP files. Use when inspecting a snapshot, designing a safe selector, validating a rule with the GKD inspector, building a GKD subscription, or preparing a narrowly scoped local rule commit.
---

# GKD Rule CLI

Turn local GKD snapshots into safe, validated app rules. Keep all agent-facing files and output in English.

## Inspect evidence

1. Treat a local snapshot ZIP as complete evidence. Do not require, ask for, or invent an online snapshot URL. When no URL exists, omit `snapshotUrls`.
2. Extract the ZIP before inspecting it. Never modify the original ZIP:

   ```powershell
   python .agents/skills/gkd-rule-cli/scripts/extract_snapshot.py <snapshot.zip>
   python .agents/skills/gkd-rule-cli/scripts/inspect_snapshot.py <extracted-directory> --search <target-text>
   ```

   View the screenshot from the extracted directory. Confirm the package, exact `activityId`, app version, target node, and the node that is actually clickable. Use `--all-nodes` only for focused diagnostics; normal output is limited to visible clickable candidates.
3. Record the user entry path and expected action. Every exclusion still requires local positive and negative snapshot evidence. Add `excludeSnapshotUrls` only when accessible URLs actually exist.

## Author safely

1. Read `.agents/spec/gkd-rules.md` and existing `src/apps/<package>.ts` before editing.
2. Create or update `src/apps/<package>.ts` with `defineGkdApp`; retain stable, unique app, group, and rule keys.
3. Narrow `activityIds` to the observed activity. Prefer `id`, `vid`, and `desc`. Bind text selectors to the activity and meaningful hierarchy/visibility context; never use a generic skip, close, or cancel label by itself.
4. Select the observed clickable container, not a decorative text child. Add exclusions only when local snapshots prove the false positive.
5. Validate the smallest app object in the GKD Inspector's in-memory subscription when the Inspector is available. Verify the intended click and adjacent, search, settings, and subsequent screens do not trigger. Local node and selector inspection is not Inspector validation; never claim Inspector validation unless it was run.

## Validate and commit

1. Format edited source files, then run `pnpm check` and `pnpm build`. Never edit `dist/` manually. If dependency access reports `fetch failed`, retry through the required permission process before treating it as a rule failure.
2. Review `git diff --check` and focused diffs. Follow repository policy: do not commit `dist/` by default, and restore build artifacts after review.
3. Before staging, require a clean tracked worktree (`git status --porcelain` may contain only untracked files). If tracked changes already exist, do not commit; report them and preserve them.
4. Stage only the intended source and skill files. Then run `git diff --cached --check` and verify the staged file list contains only those files. Do not stage ZIPs, extracted snapshots, caches, editor files, or generated `dist/` output.
5. Create one local commit with a short imperative subject, such as `Add rules for cn.example.app`. Do not run `git push` or trigger GitHub Actions.

## Boundaries

- Never edit a snapshot ZIP.
- Do not claim Inspector validation without performing it.
- Do not commit when evidence, validation, or a clean pre-staging tracked worktree is missing.
