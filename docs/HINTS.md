# Hints and recovery

This page gives inspection questions and recovery tools, not complete solutions. Start with the exercise's success conditions and the first useful message from its check.

## Inspect before changing state

Run these inside the exercise workspace:

```text
git status
git branch -vv
git remote -v
git log --oneline --graph --decorate HEAD -12
git diff
git diff --staged
```

`status` distinguishes untracked, unstaged, and staged files. `diff` and `diff --staged` show different comparisons. The graph helps distinguish a missing commit, a branch pointing at the wrong commit, and a correct file change with the wrong history.

Each exercise page supplies a graph command limited to its relevant refs. For example, in default Exercise 09:

```text
git log --oneline --graph --decorate HEAD lab-v1/ex09/donor
```

`--all` also includes the tags and branches of other exercises and both variants, which can hide the relevant work in a long graph. Use explicit refs while solving one exercise; use `--all` only when you intentionally want the complete repository overview.

Look at a specific commit with `git show COMMIT`. Replace `COMMIT` with a reference or hash you actually inspected; sample hashes from someone else's workspace need not exist in yours.

## Questions for each topic

| Topic | Useful question |
| --- | --- |
| 01 — Branch and switch | Which branch is checked out, and which branch pointer should move when you commit? |
| 02 — Fork, remotes, and push | Does `origin` identify your fork? Which local branch and remote branch are involved? |
| 03 — Fetch and pull | What changed in the remote-tracking reference after fetch, and what stayed unchanged in your current branch? |
| 04 — Merge, pull request, and conflict | What behavior does each side need to retain? Resolving conflict markers alone does not establish correctness. |
| 05 — Restore and revert | Are you correcting uncommitted content, the staging area, or an existing commit? These are different operations. |
| 06 — Stash interrupted work | Which changes were saved? Are untracked files included? Has the restored work been verified before removing the stash? |
| 07 — Amend an incomplete commit | Does the replacement commit include the intended content and message? Did you replace the latest local commit or add another? |
| 08 — Reset and split a commit | Which commit should the branch name point to, and where should the removed commit's changes remain? |
| 09 — Cherry-pick only the required fix | Which commit carries the needed change? What unrelated work would a full branch merge also include? |
| 10 — Rebase and clean up private commits | Which commits belong to your work, and what base should they be replayed onto? |
| 11 — Publish rewritten history with a lease | Is the remote branch still at the value you expect? What should happen if someone has updated it? |
| 12 — Recover a lost commit with reflog | Which earlier local reference value identifies the lost work, and how can you give it a branch name again? |

## Recover from an interrupted operation

When Git reports an operation in progress, read `git status` first. Resolve the relevant files and follow the operation's continuation instructions, or abort that operation if you want to return to its starting state:

```text
git merge --abort
git rebase --abort
git cherry-pick --abort
git revert --abort
```

Use only the command matching the operation actually in progress. These are alternatives, not a sequence to paste all at once. An abort is not a substitute for preserving unrelated uncommitted work before starting an operation.

After a conflicting `stash pop`, the stash is normally retained. Resolve and inspect your files, then check `git stash list` before deciding whether to remove the saved entry. Do not assume that a failed pop discarded it.

The reflog records local reference movements. It is not a backup of every edit: work that was never committed or stashed may not be recoverable there. A reflog from one clone is not automatically available in another clone or on GitHub.

If Git opens an unfamiliar editor, use the save/exit instructions in [Setup](SETUP.md#5-choose-a-git-editor-before-making-commits). Configure your editor inside the workspace before starting a rebase; changing only the launcher's local setting does not change its clones.

## Interpret a failed check

- **Application behavior:** compare the exercise's policy requirements with the relevant Java method. The default `run.py test` expectations describe the baseline, so use `lab.py check ID --repo PATH` for that exercise's expected behavior.
- **History or branch:** read the evaluated branch and commit ID in the check output, then inspect that graph. The checker evaluates current `HEAD`, not automatically the named submission branch. Equivalent file contents can arise from different histories.
- **Working tree:** inspect staged and unstaged changes separately. Some exercises deliberately require a local intermediate state.
- **Remote or PR:** inspect the fork URL and destination branch. Local success does not publish your work or verify a GitHub PR. For Exercise 04 and Final, recheck the fetched merged target and confirm PR status on GitHub.

Run the check from the launcher so it uses the current lab definition. Editing tests or the checker in the exercise workspace does not complete a task.

If an old workspace's tool says `Cannot read the launcher's exercises/manifest.json`, return to the original launcher instead of repairing files in the exercise. Run `python3 lab.py instructions ID` there to read the current page, then `python3 lab.py check ID --repo "/PATH/TO/YOUR/WORKSPACE"` to check your existing work. Replace `ID` and the path with your exercise and workspace. [Setup includes a complete example](SETUP.md#cannot-read-the-launchers-exercisesmanifestjson).

## Restart without losing the old attempt

Return to the launcher and start the same ID again:

```text
python3 lab.py start 04
```

The default creates a new workspace with a unique name. To request a specific destination, give a path that does not already exist:

```text
python3 lab.py start 04 --dest "../git-lab-work/ex04-retry"
```

Variant B is available for Exercises 04, 09, 10, and Final:

```text
python3 lab.py start 04 --variant b
```

Read the variant's changed requirements before working. Do not copy a result from the first variant without checking the new starting state.

A and B share the same result and PR branch names. Submit your assigned variant (default A if none is assigned), and keep optional practice on the other variant local. See [Choosing an A or B attempt](SUBMISSION.md#choosing-an-a-or-b-attempt).

Restarting is local: it does not remove or replace a result branch already published to your fork. Read [Submission](SUBMISSION.md) before replacing a published attempt.
