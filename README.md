# Git Essentials Lab

Practice 12 Git topics in a small Java library application, then combine them in a final task. Each exercise starts in its own repository with a prepared history. You can repeat a topic without undoing another exercise.

The application is deliberately small: borrowing limits, loan periods, overdue fees, catalog search, and loan receipts. The learning target is Git. No framework, third-party Java library, or Maven download is required.

## Start here

1. Complete [Setup](docs/SETUP.md) once. You need Git 2.23+, JDK 17+, Python 3.9+, and your own GitHub fork.
2. Keep the clone you set up as your **launcher**. Run `lab.py` from that directory.
3. Open an exercise below and create a separate workspace with `lab.py start`.
4. Work in that workspace, then check it from the launcher. Read [Submission](docs/SUBMISSION.md) before publishing results.

Examples use `python3`. On Windows, use `py -3` if that is how you run Python 3.9 or later.

```text
python3 lab.py doctor
python3 lab.py refs
python3 lab.py start 01
```

`start` prints the new workspace path. Use that path when changing directories or passing `--repo` to a check. It creates a new directory; it does not reset your launcher or an existing workspace.

## Exercises

| Exercise | Topic | Instructions |
| --- | --- | --- |
| 01 | Branch and switch | [Open](docs/exercises/01.md) |
| 02 | Remotes, fork, and push | [Open](docs/exercises/02.md) |
| 03 | Fetch and pull | [Open](docs/exercises/03.md) |
| 04 | Merge and conflicts | [Open](docs/exercises/04.md) |
| 05 | Restore and revert | [Open](docs/exercises/05.md) |
| 06 | Stash | [Open](docs/exercises/06.md) |
| 07 | Amend | [Open](docs/exercises/07.md) |
| 08 | Reset | [Open](docs/exercises/08.md) |
| 09 | Cherry-pick | [Open](docs/exercises/09.md) |
| 10 | Rebase | [Open](docs/exercises/10.md) |
| 11 | Force push with a lease | [Open](docs/exercises/11.md) |
| 12 | Reflog | [Open](docs/exercises/12.md) |
| Final | Combined task and pull request | [Open](docs/exercises/final.md) |

Read the exercise's situation and success conditions before editing. Each page identifies its starting state, required result, checks, submission, and restart procedure. Exercises 04, 09, 10, and Final also have a variant B for another attempt with changed requirements.

Without `--variant b`, `start` uses the default scenario described first on each page. `check` reads the variant recorded when that workspace was created, so the same check command works for either variant. `python3 lab.py instructions 04` prints the current Exercise 04 page from the launcher; replace `04` with another exercise ID as needed.

## The two places you work

| Place | Purpose |
| --- | --- |
| Launcher: your original clone | Read the current instructions; run `lab.py doctor`, `start`, `check`, and `advance`. |
| Exercise workspace: the directory printed by `start` | Inspect Git history, edit the application, run Git commands, and publish the named result branch. |

For example, after starting Exercise 01, run its check **from the launcher**, replacing the example path with the path printed by `start`:

```text
python3 lab.py check 01 --repo "../git-lab-work/01-YOUR-TIMESTAMP"
```

Checks evaluate the prepared task's result. A passing result does not prove that you used a particular command or understood why it worked. Practice the topic deliberately and be ready to explain the resulting history and application behavior. Local-only practice is identified on the relevant pages and is not remotely graded.

## Explore the application

From the launcher, you can inspect the unchanged application before starting:

```text
python3 run.py demo
python3 run.py test
```

The runner compiles the Java code into a temporary directory. Exercise requirements can change the expected borrowing rules; use the exercise's `lab.py check` command to check its intended result.

Useful application files are under `src/library/`; tests are under `tests/library/`. Git exercise starting points are the versioned `lab-v1/...` tags. Keep those tags unchanged so every attempt has the same starting point.

## Help

- [Setup](docs/SETUP.md): tools, fork, all branches and tags, and remotes.
- [Submission](docs/SUBMISSION.md): what to publish and which pull-request repositories to select.
- [Hints](docs/HINTS.md): how to inspect state and recover from an interrupted operation.
- [Starting graphs](docs/GRAPHS.md): the initial histories for 04, 09, 10, and Final, including private setup commits.
- [Sources](SOURCES.md): Git, Pro Git, and GitHub references used to design the exercises.

If you need to begin again, run `start` again from the launcher. Keep the old attempt until you are satisfied with the new one.
