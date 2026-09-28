# Setup

Complete this once before Exercise 01. This guide creates a launcher clone; `lab.py start` later creates each independent exercise workspace.

## 1. Check your tools

You need:

- **Git 2.23 or later**, including `git switch` and `git restore`.
- **JDK 17 or later**: both `java` and the compiler `javac` must be available.
- **Python 3.9 or later**. The lab runner uses only Python's standard library.
- A **GitHub account** and permission to push to your own fork.
- A terminal and a text editor.

```text
git --version
java -version
javac -version
python3 --version
```

On Windows, use Git Bash or PowerShell. If Python is available as `py -3`, replace `python3` with `py -3` throughout these instructions. Choose a folder you can write to, and quote paths that contain spaces. You do not need an IDE, Maven, Gradle, or any third-party Java dependency.

## 2. Fork the course repository

1. Open [oh-gnues/git-essentials-lab](https://github.com/oh-gnues/git-essentials-lab).
2. Select **Fork** and use your own GitHub account as the owner.
3. Clear **Copy the main branch only** so the fork includes all branches.
4. Create the fork, then copy its clone URL from **Code**.

The fork is a repository on GitHub. Cloning it in the next step creates a separate local repository. Pushing later transfers commits from a local branch to your fork; it does not create a pull request.

## 3. Clone your fork and fetch every lab reference

Replace `YOUR-USERNAME` with your GitHub username. If your fork has a different name, use its actual clone URL.

```text
git clone https://github.com/YOUR-USERNAME/git-essentials-lab.git
cd git-essentials-lab
git remote add upstream https://github.com/oh-gnues/git-essentials-lab.git
git fetch origin --tags
git fetch upstream --tags "+refs/heads/*:refs/remotes/upstream/*"
git remote -v
```

Do not use `--single-branch` or `--depth` for this lab. The exercises need complete prepared histories and tags, including starting points outside `main`. The explicit fetch above obtains all upstream branches and tags even if you originally copied only the default branch to your fork.

The expected remote names are:

| Name | Points to | Your use |
| --- | --- | --- |
| `origin` | Your GitHub fork | Publish your result branches here. |
| `upstream` | `oh-gnues/git-essentials-lab` | Read the original lab material and tags. |

The remote named `upstream` is different from a branch's *upstream tracking branch*. A local result branch can track a branch on `origin` while the repository also has a remote named `upstream`.

If the `upstream` remote already exists, inspect it with `git remote -v`; add it only if it is missing. If its URL is wrong, correct that existing remote instead of adding another one.

## 4. Set your commit identity

If Git does not already know your identity, set it for this launcher:

```text
git config --local user.name "Your Name"
git config --local user.email "YOUR-COMMIT-EMAIL"
```

Use the identity you normally use for coursework. Your GitHub-provided no-reply email is an option. A commit identity identifies the author in Git history; it does not authenticate a push to GitHub.

## 5. Check the launcher

```text
python3 lab.py doctor
python3 lab.py refs
python3 run.py test
```

Resolve missing-tool or missing-reference errors before starting an exercise. `refs` lists the versioned starting points and helper references used by the lab.

Keep this directory as the launcher. Work on the exercises in the separate directories created by `start`:

```text
python3 lab.py start 01
```

Use the workspace path printed by the command. Exercise workspaces keep `origin` pointed at your fork; always inspect `git remote -v` before your first push.

## 6. Make sure GitHub authentication works

Reading a public repository and pushing to your fork require different permissions. Use the HTTPS credential manager or SSH configuration you normally use with GitHub. Follow [GitHub's authentication guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github) if this is your first setup. Do not put a password, token, or private key in source files, commits, screenshots, or submitted documents.

| Message or symptom | What to inspect |
| --- | --- |
| Repository not found or permission denied | The `origin` URL, the signed-in account, and access to the fork. |
| Authentication failed | Your HTTPS or SSH authentication setup. |
| Push rejected as non-fast-forward | The destination branch history; fetch and inspect before deciding how to integrate. |
| Missing `lab-v1/...` reference | Return to the launcher and repeat the upstream fetch in step 3. |

A force push does not fix an authentication or permission problem. Exercise 11 is the dedicated place to practice rewriting a published branch with a lease.

Next: [Exercise 01](exercises/01.md).
