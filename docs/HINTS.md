# Hints and recovery

This page gives inspection questions and recovery tools, not complete solutions. Start with the exercise's success conditions and the first useful message from its check.

## Inspect before changing state

Run these inside the exercise workspace:

```text
git status
git branch -vv
git remote -v
git log --oneline --graph --decorate --all
git diff
git diff --staged
```

`status` distinguishes untracked, unstaged, and staged files. `diff` and `diff --staged` show different comparisons. The graph helps distinguish a missing commit, a branch pointing at the wrong commit, and a correct file change with the wrong history.

Look at a specific commit with `git show COMMIT`. Replace `COMMIT` with a reference or hash you actually inspected; sample hashes from someone else's workspace need not exist in yours.

## Questions for each topic

| Topic | Useful question |
| --- | --- |
| 01 — Branch and switch | Which branch is checked out, and which branch pointer should move when you commit? |
| 02 — Remotes and push | Does `origin` identify your fork? Which local branch and remote branch are involved? |
| 03 — Fetch and pull | What changed in the remote-tracking reference after fetch, and what stayed unchanged in your current branch? |
| 04 — Merge | What behavior does each side need to retain? Resolving conflict markers alone does not establish correctness. |
| 05 — Restore and revert | Are you correcting uncommitted content, the staging area, or an existing commit? These are different operations. |
| 06 — Stash | Which changes were saved? Are untracked files included? Has the restored work been verified before removing the stash? |
| 07 — Amend | Does the replacement commit include the intended content and message? Did you replace the latest local commit or add another? |
| 08 — Reset | Which commit should the branch name point to, and where should the removed commit's changes remain? |
| 09 — Cherry-pick | Which commit carries the needed change? What unrelated work would a full branch merge also include? |
| 10 — Rebase | Which commits belong to your work, and what base should they be replayed onto? |
| 11 — Lease | Is the remote branch still at the value you expect? What should happen if someone has updated it? |
| 12 — Reflog | Which earlier local reference value identifies the lost work, and how can you give it a branch name again? |

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

## Interpret a failed check

- **Application behavior:** compare the exercise's policy requirements with the relevant Java method. The default `run.py test` expectations describe the baseline, so use `lab.py check ID --repo PATH` for that exercise's expected behavior.
- **History or branch:** inspect the graph and current branch. Equivalent file contents can arise from different histories.
- **Working tree:** inspect staged and unstaged changes separately. Some exercises deliberately require a local intermediate state.
- **Remote:** inspect the fork URL and destination branch. Local success does not publish your work.

Run the check from the launcher so it uses the current lab definition. Editing tests or the checker in the exercise workspace does not complete a task.

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

Restarting is local: it does not remove or replace a result branch already published to your fork. Read [Submission](SUBMISSION.md) before replacing a published attempt.
