# Submission

Each exercise page says whether its result is submitted or used only for local practice. Keep the prepared `lab-v1/...` tags unchanged. Publish results to **your own fork**, using the branch names specified below.

| Exercises | Result to publish |
| --- | --- |
| 01, 02, 05, 07, 09, 10 | The corresponding `result/exNN` branch. |
| 04 | `result/ex04` after merging its `feature/ex04` PR inside your fork. |
| Final | `result/final` after merging its `feature/final` PR inside your fork. |
| 03, 06, 08, 11, 12 | Local-only practice; no remote submission. |

Exercise 05's restore action and Exercise 02's local remote configuration are also local practice, even though those exercises have a submitted result.

## Check the workspace first

From the launcher, use the check command printed by `start`. For example:

```text
python3 lab.py check 01 --repo "/PATH/TO/YOUR/EXERCISE-WORKSPACE"
```

Then inspect the exercise workspace:

```text
git status
git branch --show-current
git remote -v
git log --oneline --graph --decorate -12
```

The exercise page defines whether the working tree should be clean or should retain a deliberate local change. Do not make an extra commit merely to silence `status` when the exercise asks you to inspect staged or unstaged changes.

The checker evaluates application behavior and relevant repository state. It does not prove which command you typed. GitHub cannot reproduce a different clone's staging area, stash, or reflog, so local-only practice is not remotely graded. A PR is checked separately from an ordinary branch push.

## Publish ordinary result branches

Exercise result branches use `result/ex01` through `result/ex12`; the final target branch is `result/final`. Publish a result only when its exercise page asks you to do so.

From the relevant exercise workspace, this example publishes Exercise 01:

```text
git push -u origin result/ex01
```

Use the exercise's actual branch name. Check the branch on your fork's GitHub page afterward. Do not publish all local branches or tags: the prepared helper histories are teaching inputs, not your answers.

## Exercise 04 and Final: create a PR inside your fork

These two exercises include a pull request. Both the base repository and head repository must be **your fork**; do not request a merge into the course repository.

| Task | Base branch: receives the work | Head branch: proposes the work |
| --- | --- | --- |
| Exercise 04 | `result/ex04` | `feature/ex04` |
| Final | `result/final` | `feature/final` |

1. After starting, publish the target's original shared starting point to your fork **before** adding the feature work. Exercise 04 can publish its current `result/ex04` branch. Final must use the explicit starting-tag publication shown below, because its current local branch already has private WIP commits.
2. Create and switch to the specified `feature/...` branch. Complete the task there, then publish that branch too.
3. On GitHub, open a PR. Inspect both repository selectors and both branch selectors against the table above. Fork PRs may default to the original repository, so select your own fork as the base repository explicitly.
4. Describe what behavior changed, how you resolved competing requirements, and what you checked. Inspect **Files changed** and **Commits** before merging.
5. Merge the PR using **Create a merge commit**. These exercises preserve source-branch ancestry; squash-merge and rebase-merge produce different histories.
6. Fetch the merged target branch into the exercise workspace, inspect that result, and run the exercise check again from the launcher. Exercise 04 can fast-forward its local target; Final uses the new local inspection branch described on its exercise page.

For Exercise 04, the initial target publication is:

```text
git push -u origin result/ex04
```

For Final, publish the shared starting commit instead of the current local branch:

```text
git push origin "lab-v1/final/start^{commit}:refs/heads/result/final"
```

The two setup-created final WIP commits stay local so they can be combined on `feature/final`. See the [Final task](exercises/final.md) for the full starting-state and merged-result inspection procedure. Publishing either target does not complete the exercise; the result is the target branch after its PR is merged.

No other student has to approve the PR for this lab. You can inspect and merge your own PR when the task is ready and your repository settings permit it. If a repository rule blocks the required merge method, check the rule or ask your instructor rather than merging into a different repository or branch.

## What to provide

Provide the URL of your fork and the URLs of the completed Exercise 04 and Final PRs through the course's stated submission channel. Keep the required result branches available in that fork. Identify any variant B attempt clearly so its changed requirements can be checked against the correct scenario.

You do not need to submit terminal transcripts as proof that a particular command was used. Local checks support your own practice; the published branches and PRs are the reviewable results.

## Repeating a published task

`start` creates a new local workspace; it does not delete the earlier attempt or change GitHub. Before replacing a published result, compare the new attempt with the existing remote branch and preserve anything you want to keep. Do not force-push over an existing PR or result merely because a normal push was rejected.

For optional practice that you do not intend to submit, you can keep the new attempt local. Ask which attempt to submit if the course instructions require a particular variant.
