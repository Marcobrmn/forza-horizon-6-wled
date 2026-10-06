# Changes, pull requests, and responsibilities

This is a public repository. This page is our working agreement for changes to this project, not a GitHub permission setting. The code and branch-protection settings remain the technical source of truth.

## The normal path

1. Start from `main`, make changes on a separate branch, and open a pull request (PR) targeting `main`. GitHub's **Edit → Propose changes** can create the branch and PR for you.
2. Describe the change and check **Files changed** for everything that would become public. For code changes, run relevant tests. Check the PR's **Checks** tab; `publication-safety` must pass.
3. Resolve failures and review the final diff after any new commit. Then Marco may merge the PR into `main`. Do not disable protections or use a bypass just to get a change through.

A PR is a proposal, not a release. Merging changes `main`; it does not by itself prove installation, driving behavior, or a new version is safe.

## Who does what

- **Marco can do himself:** edit README/setup text; add project-owned, non-sensitive images; create a branch/PR in GitHub's web UI; inspect the diff and checks; merge a PR after reviewing it. A screenshot helps explain desired placement, but original image files are needed when Hermes should add or edit images.
- **Hermes handles on request:** prepare larger or technical changes on a branch, review images/docs/code for obvious problems, run relevant local checks, open a PR, explain failed checks, and report the exact diff and any unverified risks. Hermes does not need to be involved in every small README change.
- **Marco decides:** what to publish and when to merge. Hermes merges a specific PR, changes repository security rules, publishes a release, or changes live installations **only after an explicit instruction covering that action**. A request to prepare or document a change is not permission to merge or release it.
- **For code, configuration, CI, or security changes:** ask Hermes for technical review rather than treating a green check as sufficient. Inspect modifications to `.github/workflows/` and `scripts/publication_safety.py` particularly carefully: a PR can change the checker as well as the content it scans.

## What the gate does—and does not do

`main` requires a PR and the `publication-safety` status check. The check scans the tracked tree and Git history for likely secrets and some private addresses/paths. **As currently configured, no second-person approval is required**; Marco can review and merge his own PR when the check passes. A successful check is not a security guarantee and does not replace looking at the diff, tests, or image contents.

**Public exposure starts before merge:** branches pushed to this public repo can be read by others. Images uploaded as GitHub `user-attachments` and embedded by URL may not be tracked in Git at all, so the repository check does not inspect them. Before uploading, inspect photos for personal information, private screens, addresses, and identifying metadata; use redacted/exported copies where appropriate. If sensitive material reaches a public branch or attachment, do not assume closing the PR or deleting a Git commit makes it private again—stop and handle the exposure separately.

## When a check fails or a change is unclear

Do not force-merge or switch off protection. Read the failed check, fix the source on the PR branch, and let it rerun. If the reason is unclear, ask Hermes to inspect it before merging. For image-only or README edits, the same diff review still applies even if no code tests are needed.
