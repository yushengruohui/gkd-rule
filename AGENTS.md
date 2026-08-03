# Repository Guidelines

For GKD rule authoring requirements, see [`.agents/spec/gkd-rules.md`](.agents/spec/gkd-rules.md).

## Project Structure & Module Organization

This is a TypeScript template for a GKD subscription. Keep editable
subscription definitions in `src/`:

- `subscription.ts` defines metadata and imports app rules.
- `categories.ts` and `globalGroups.ts` define shared rule data.
- `apps/` contains one rule module per Android package, named after its package
  ID (for example, `com.tencent.mm.ts`).

`scripts/check.ts` validates the subscription and `scripts/build.ts` generates
the distributable files. `dist/` is build output; change source files rather
than editing its contents. GitHub workflow definitions live in
`.github/workflows/`.

## Build, Test, and Development Commands

Use Node.js 22 or later (the repository pins Node 24 with Volta) and pnpm 10.

- `pnpm install` installs dependencies and enables Git hooks.
- `pnpm format` formats supported source and JSON files with Prettier.
- `pnpm lint` fixes ESLint findings, including unused imports and variables.
- `pnpm check` type-checks TypeScript and validates the subscription against the
  GKD API. Run it before opening a pull request.
- `pnpm build` runs the checks and writes the generated subscription to `dist/`.

There is no separate unit-test suite; `pnpm check` is the required validation
step for rule changes.

## Coding Style & Naming Conventions

Use TypeScript ES modules and the `@gkd-kit/define` helpers (such as
`defineGkdApp`). Prettier enforces two-space indentation, single quotes, and
trailing commas. Let the formatter manage layout; do not manually reformat
unrelated code. Keep app modules focused on one package, use its exact Android
package ID as the filename, and export the defined rule object as the default.

## Commit & Pull Request Guidelines

The available history contains only the initial commit, so no established
commit-message convention can be inferred. Use short, imperative subjects,
for example `Add rules for com.example.app`. Keep commits scoped to one logical
rule or metadata change. Before submitting a pull request, run `pnpm check`,
describe the affected app/groups and expected behavior, link any relevant
issue, and include screenshots or recordings when a UI selector change needs
visual evidence. Do not commit generated `dist/` changes unless the release
workflow or project policy specifically requires them.

After each content change, run the relevant validation. If it passes, commit
the completed change with Git.

## Subscription Safety

Give `src/subscription.ts` a unique, non-placeholder numeric `id` before
publishing. Review selectors carefully: broad or unstable selectors can affect
unintended screens. Keep update and support URLs accurate when customizing the
template.
