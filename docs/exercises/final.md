# Final: Repair the tangled release

**Mode:** Submitted result and PR.

## Situation

The current release bypasses borrowing limits and charges negative fees for early returns. Separate histories contain student and faculty policies, a search improvement, and the fee fix. Your own release checklist is split across two private WIP commits. Prepare a correct release without losing existing work or bringing in unrelated experiments.

## Start

Run from the launcher:

```text
python3 lab.py start final
```

The workspace begins on `result/final`. The shared release starting point is `lab-v1/final/start`; setup adds **two private WIP commits** for `docs/release-checklist.md` on top. These two local commits may be rewritten. The shared starting history must remain intact.

| Reference | Meaning |
| --- | --- |
| `lab-v1/final/start` | Shared release history, including the useful release notes. |
| `lab-v1/final/bad-policy` | The earlier commit that bypassed borrowing limits. |
| `lab-v1/final/student` | Student borrowing-policy history. |
| `lab-v1/final/faculty` | Faculty borrowing-policy history. |
| `lab-v1/final/search` | Case-insensitive title-search history. |
| `lab-v1/final/donor` | A history containing the fee fix between unrelated reservation and debug changes. |

The starting application intentionally fails some behavior checks. Inspect the histories and patches before deciding which changes to combine.

The [starting commit graph](../GRAPHS.md#final-shared-release-history-and-private-checklist-work) separates the shared release history, helper histories, and two private checklist commits.

## Task

1. **Establish the PR base before feature work.** Publish the shared starting commit to `result/final` in your own fork, using the setup command below. Do not publish the two local WIP commits as the PR base.
2. Create and switch to `feature/final` from the current local HEAD, retaining both WIP commits. Squash those two private checklist commits into one meaningful commit before adding other integration work.
3. Revert the bad-policy commit while preserving the shared history and release notes. Retain the generated revert identification in the corrective commit message.
4. Merge the student, faculty, and search histories. Resolve conflicts according to all the required behaviors below, retaining the source histories as ancestors.
5. Identify and cherry-pick only the needed fee fix from the donor history. Exclude its reservation prototype and debug notes.
6. Check the feature result, publish `feature/final`, and open a PR **inside your own fork**, from `feature/final` into `result/final`. Explain the integration decisions and checks. Merge using **Create a merge commit**.
7. Fetch and inspect the merged target using the final-check procedure below.

Run this initial publication command from the new exercise workspace, before creating the feature branch:

```text
git push origin "lab-v1/final/start^{commit}:refs/heads/result/final"
```

It publishes the immutable shared starting commit as the remote target branch. It does not publish your two private WIP commits. If `result/final` already exists from another attempt, stop and inspect that earlier result before deciding which attempt to submit.

## Success conditions

| Area | Required result |
| --- | --- |
| Borrowing limits | **3 student books** and **5 faculty books**. |
| Loan period | **14 days**, unchanged. |
| Overdue fees | Never negative; **100 per positive overdue day**. |
| Catalog search | Case-insensitive substring matching using locale-independent normalization. |
| Existing release notes | Preserve `docs/release-notes.md` and its existing return-workflow requirement. |
| Release checklist | Keep both `Review borrowing limits.` and `Run regression checks.` in `docs/release-checklist.md`, introduced through one coherent commit after the shared start. |
| History | Preserve the shared starting history; add a revert; retain the student, faculty, and search histories through merges. No WIP commit messages remain in the completed segment after the shared start. |
| Excluded work | Neither `src/library/Reservation.java` nor `docs/debug-notes.md` is present. The donor history is not merged wholesale. |
| PR | Merged into `result/final` in your own fork using a merge commit. |

## Check

Before publishing the feature branch, run from the launcher:

```text
python3 lab.py check final --repo "/PATH/TO/YOUR/WORKSPACE"
```

After merging the PR on GitHub, run inside the exercise workspace:

```text
git fetch origin
git switch -c submitted/final origin/result/final
```

Then repeat the launcher check against that same workspace. `submitted/final` is a local inspection branch for the merged result. This avoids discarding the earlier local `result/final` pointer, which still identifies the initial private-WIP state. Run the switch only with a clean working tree; if the inspection branch already exists, inspect it before reusing its name.

The local check verifies behavior and history, not the existence of a PR. Confirm the PR repository selectors, branch selectors, merge method, and merged status on GitHub as well.

## Submission

Keep the completed remote `result/final` branch and provide the PR URL with your fork URL. Follow [Submission](../SUBMISSION.md). Do not open this PR against the original course repository.

## Variant B

Run `python3 lab.py start final --variant b` for a new workspace. The shared start and bad-policy tags remain `lab-v1/final/start` and `lab-v1/final/bad-policy`.

Use the student, faculty, search, and donor helper tags under **`lab-v1/final-b/`**. The changed requirements are **4 student books, 6 faculty books, and 200 per positive overdue day**. The 14-day loan period, case-insensitive search, preserved documents, excluded experiments, private-WIP cleanup, and PR requirements stay the same.

## Restart

Run `python3 lab.py start final` again from the launcher, adding `--variant b` if needed. This creates a new local attempt without changing the old one or the result already published on GitHub. Review any existing final branch or PR before attempting another publication under the same names.

[Hints](../HINTS.md) · [Submission guide](../SUBMISSION.md) · [Sources](../../SOURCES.md)
