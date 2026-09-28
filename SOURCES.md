# Sources

The application, prepared histories, tasks, and checking tools in this repository are original teaching material. The Git concepts and command semantics are based on these primary references. External references explain the tools; they are not complete solutions to the lab scenarios.

## Git and Pro Git

- [Git reference manual](https://git-scm.com/docs) — command behavior and options.
- [Pro Git: Recording Changes](https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository) — working tree, staging area, and commits.
- [Pro Git: Branches in a Nutshell](https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell) — branch pointers and switching.
- [Pro Git: Basic Branching and Merging](https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging) — integration and conflicts.
- [Pro Git: Remote Branches](https://git-scm.com/book/en/v2/Git-Branching-Remote-Branches) — remote-tracking references, fetch, and push.
- [Pro Git: Stashing and Cleaning](https://git-scm.com/book/en/v2/Git-Tools-Stashing-and-Cleaning) — temporarily saving local changes.
- [Pro Git: Rewriting History](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History) — amend and history editing.
- [Pro Git: Reset Demystified](https://git-scm.com/book/en/v2/Git-Tools-Reset-Demystified) — HEAD, index, working tree, and reset modes.
- [Pro Git: Rebasing](https://git-scm.com/book/en/v2/Git-Branching-Rebasing) — replaying commits onto a different base.
- [Pro Git: Maintenance and Data Recovery](https://git-scm.com/book/en/v2/Git-Internals-Maintenance-and-Data-Recovery) — locating recoverable commits.

### Command references by exercise

| Exercise | Official reference |
| --- | --- |
| 01 | [branch](https://git-scm.com/docs/git-branch), [switch](https://git-scm.com/docs/git-switch) |
| 02 | [remote](https://git-scm.com/docs/git-remote), [push](https://git-scm.com/docs/git-push) |
| 03 | [fetch](https://git-scm.com/docs/git-fetch), [pull](https://git-scm.com/docs/git-pull) |
| 04 | [merge](https://git-scm.com/docs/git-merge) |
| 05 | [restore](https://git-scm.com/docs/git-restore), [revert](https://git-scm.com/docs/git-revert) |
| 06 | [stash](https://git-scm.com/docs/git-stash) |
| 07 | [commit](https://git-scm.com/docs/git-commit) |
| 08 | [reset](https://git-scm.com/docs/git-reset) |
| 09 | [cherry-pick](https://git-scm.com/docs/git-cherry-pick) |
| 10 | [rebase](https://git-scm.com/docs/git-rebase) |
| 11 | [push, including --force-with-lease](https://git-scm.com/docs/git-push) |
| 12 | [reflog](https://git-scm.com/docs/git-reflog) |

## GitHub

- [Fork a repository](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/fork-a-repo) — create a fork, clone it, and configure an upstream remote.
- [Syncing a fork](https://docs.github.com/en/pull-requests/how-tos/work-with-forks/syncing-a-fork) — obtain changes from the original project.
- [About authentication to GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github) — account and Git authentication.
- [Creating a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) — select the base and head branches and describe a change.
- [Changing the base branch of a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/changing-the-base-branch-of-a-pull-request) — understand and correct the PR destination.
- [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow) — branch, commit, PR, review, merge, and branch cleanup.

Git and GitHub documentation can evolve; the lab's minimum supported versions are listed in [Setup](docs/SETUP.md).

## Exercise design reference

- [Eficode Git Katas](https://github.com/eficode-academy/git-katas) — a reference for independently prepared, repeatable Git exercises. This lab uses its own Java application, histories, instructions, and checker implementation; it does not redistribute Git Katas source code.
