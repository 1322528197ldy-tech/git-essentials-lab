#!/usr/bin/env python3
"""Prepare isolated Git exercises; use the launcher copy for trusted checks."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid


LAUNCHER = Path(__file__).resolve().parent
STATE_NAME = "lab-state.json"
PYTHON_COMMAND = "py -3" if os.name == "nt" else "python3"


class LabError(Exception):
    """An actionable, student-facing failure."""


def command(argv, cwd=None, check=True):
    env = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                 "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
        env.pop(name, None)
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        result = subprocess.run([str(x) for x in argv], cwd=cwd, env=env,
                                text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, encoding="utf-8",
                                errors="replace")
    except OSError as exc:
        raise LabError("Cannot run {}: {}".format(argv[0], exc)) from exc
    if check and result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise LabError("{} failed (exit {}):\n{}".format(
            Path(str(argv[0])).name, result.returncode, detail))
    return result


def git(repo, *args, check=True):
    # Automation never executes a user's globally configured Git hooks.
    return command(["git", "-c", "core.hooksPath=" + str(
        Path(repo) / ".git" / "lab-disabled-hooks"), "-C", repo, *args],
        check=check)


def git_text(repo, *args):
    return git(repo, *args).stdout.strip()


def load_manifest():
    path = LAUNCHER / "exercises" / "manifest.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LabError("Cannot read the launcher's exercises/manifest.json: " + str(exc))
    if not isinstance(manifest.get("exercises"), dict):
        raise LabError("The manifest must contain an exercises mapping.")
    return manifest


def normalize_id(value):
    value = str(value).lower()
    if value.isdigit():
        value = value.zfill(2)
    if value not in [str(i).zfill(2) for i in range(1, 13)] + ["final"]:
        raise LabError("Exercise ID must be 01..12 or final.")
    return value


def exercise_spec(manifest, exercise_id, variant=None):
    try:
        spec = copy.deepcopy(manifest["exercises"][exercise_id])
    except KeyError as exc:
        raise LabError("Exercise {} is not in this manifest.".format(exercise_id)) from exc
    if variant:
        if variant != "b" or not isinstance(spec.get("variant_b"), dict):
            raise LabError("Exercise {} has no variant {}.".format(exercise_id, variant))
        spec.update(spec["variant_b"])
    spec.setdefault("solution_branch", "result/final" if exercise_id == "final"
                    else "result/ex" + exercise_id)
    return spec


def source_git_root():
    root = Path(git_text(LAUNCHER, "rev-parse", "--show-toplevel")).resolve()
    if root != LAUNCHER:
        raise LabError("Run lab.py from the root of your cloned lab repository, "
                       "not from a source directory inside another repository.")
    return root


def remote_url(repo, name):
    result = git(repo, "remote", "get-url", name, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def portable_remote(url, relative_to):
    windows_path = bool(re.match(r"^[A-Za-z]:[\\/]", url))
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", url) or (
            not windows_path and re.match(r"^[^/\\:]+:", url)):
        return url
    # A path-based fake origin must still name the same remote in a sibling clone.
    path = Path(url).expanduser()
    return str((relative_to / path).resolve()) if not path.is_absolute() else str(path)


def safe_path(repo, relative):
    path = Path(str(relative))
    if path.is_absolute() or not path.parts or any(
            part == ".." or part.casefold() == ".git" for part in path.parts):
        raise LabError("Setup path must be a worktree-relative path: " + str(relative))
    target = (repo / path).resolve()
    try:
        target.relative_to(repo.resolve())
    except ValueError as exc:
        raise LabError("Setup path escapes the exercise: " + str(relative)) from exc
    if target == repo.resolve():
        raise LabError("Setup cannot write the repository directory.")
    return target


def save_state(repo, state):
    path = repo / ".git" / STATE_NAME
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_state(repo, exercise_id):
    repo = Path(repo).expanduser().resolve()
    if not (repo / ".git").is_dir():
        raise LabError("This is not an exercise clone with its own .git directory: " + str(repo))
    root = Path(git_text(repo, "rev-parse", "--show-toplevel")).resolve()
    if root != repo:
        raise LabError("--repo must be the exercise repository root.")
    try:
        state = json.loads((repo / ".git" / STATE_NAME).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise LabError("Exercise metadata is missing or invalid. Start a fresh exercise.") from exc
    if state.get("id") != exercise_id or not state.get("setup_complete"):
        raise LabError("This workspace is not a completed setup for exercise " + exercise_id)
    return repo, state


def ref_value(value, state):
    value = str(value)
    if value == "{start}":
        return state["start_oid"]
    match = re.fullmatch(r"\{(helper|commit):([^}]+)\}", value)
    if match:
        collection = state["helpers"] if match.group(1) == "helper" else state["commits"]
        if match.group(2) not in collection:
            raise LabError("Unknown setup reference: " + value)
        return collection[match.group(2)]
    if value.startswith("-"):
        raise LabError("A setup reference cannot begin with '-'.")
    return value


def setup_commit(repo, message, paths):
    if not paths:
        raise LabError("Each setup commit must specify its paths.")
    for path in paths:
        safe_path(repo, path)
    git(repo, "add", "--", *paths)
    git(repo, "-c", "user.name=Lab Setup", "-c", "user.email=lab@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "-m", message)
    return git_text(repo, "rev-parse", "HEAD")


def apply_actions(repo, actions, state, file_only=False):
    for action in actions:
        kind = action.get("type", action.get("op"))
        if kind in ("write", "replace"):
            path = safe_path(repo, action["path"])
            if kind == "write":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(action["text"], encoding="utf-8")
            else:
                text = path.read_text(encoding="utf-8")
                old = action["old"]
                count = int(action.get("count", 1))
                if not old or count < 1 or text.count(old) != count:
                    raise LabError("Expected exactly {} occurrence(s) of {!r} in {}.".format(
                        count, old, action["path"]))
                path.write_text(text.replace(old, action["new"], count), encoding="utf-8")
        elif file_only:
            raise LabError("Remote simulation changes may only write or replace files.")
        elif kind == "commit":
            oid = setup_commit(repo, action["message"], action.get("paths", []))
            state.setdefault("setup_commits", []).append(oid)
            state["last_commit"] = oid
            state["commits"][str(len(state["setup_commits"]))] = oid
            state["commits"]["last"] = oid
            if action.get("key"):
                state["commits"][action["key"]] = oid
        elif kind == "branch":
            name = action["name"]
            git(repo, "check-ref-format", "--branch", name)
            git(repo, "branch", name, ref_value(action.get("ref", "HEAD"), state))
        elif kind == "switch":
            name = action["branch"]
            git(repo, "check-ref-format", "--branch", name)
            git(repo, "switch", name)
        elif kind == "reset":
            mode = action.get("mode", "mixed")
            if mode not in ("soft", "mixed", "hard"):
                raise LabError("Unsupported setup reset mode: " + mode)
            # Only reachable during initial preparation of this newly created clone.
            git(repo, "reset", "--" + mode, ref_value(action["ref"], state))
        else:
            raise LabError("Unsupported setup action: " + str(kind))


def setup_remote(repo, spec, state):
    remote = spec.get("remote_setup")
    if not remote:
        return
    branch = remote.get("branch", "practice")
    git(repo, "check-ref-format", "--branch", branch)
    home = repo / ".git" / "lab-remotes"
    home.mkdir()
    bare, peer = home / "practice.git", home / "peer"
    command(["git", "init", "--bare", bare])
    git(repo, "remote", "add", "practice", str(bare))
    git(repo, "push", "practice", "HEAD:refs/heads/" + branch)
    git(repo, "fetch", "practice")
    if state["id"] == "03":
        git(repo, "branch", "--set-upstream-to=practice/" + branch, state["solution_branch"])
    git(bare, "symbolic-ref", "HEAD", "refs/heads/" + branch)
    command(["git", "-c", "core.hooksPath=" + str(home / "disabled-hooks"),
             "clone", "--no-local", "--branch", branch, "--", bare, peer])
    state["known_initial_remote_tip"] = git_text(repo, "rev-parse", "HEAD")
    state["remote_branch"] = branch
    state["remote_advanced"] = False


def start(args):
    manifest = load_manifest()
    exercise_id = normalize_id(args.id)
    spec = exercise_spec(manifest, exercise_id, args.variant)
    source_git_root()
    original_origin = remote_url(LAUNCHER, "origin")
    if not original_origin:
        raise LabError("The launcher needs an origin remote. Clone your own fork first.")
    seed = spec["start"]
    seed_oid = git_text(LAUNCHER, "rev-parse", "--verify", "refs/tags/" + seed + "^{commit}")
    helpers = {role: git_text(LAUNCHER, "rev-parse", "--verify", "refs/tags/" + tag + "^{commit}")
               for role, tag in spec.get("helpers", {}).items()}
    if args.dest:
        repo = Path(args.dest).expanduser().absolute()
    else:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        repo = LAUNCHER.parent / "git-lab-work" / (
            exercise_id + ("-b" if args.variant else "") + "-" + stamp + "-" + uuid.uuid4().hex[:6])
    try:
        repo.resolve().relative_to(LAUNCHER)
    except ValueError:
        pass
    else:
        raise LabError("Create exercises outside the launcher repository.")
    if any(part.casefold() == ".git" for part in repo.parts):
        raise LabError("An exercise destination cannot be inside a .git directory.")
    # Reserve an empty directory exclusively. Never reuse, reset or delete an old workspace.
    repo.parent.mkdir(parents=True, exist_ok=True)
    try:
        repo.mkdir()
    except FileExistsError as exc:
        raise LabError("Destination already exists; choose a NEW directory: " + str(repo)) from exc
    repo = repo.resolve()
    state = {"id": exercise_id, "variant": args.variant,
             "manifest_version": manifest.get("version"), "launcher": str(LAUNCHER),
             "repo": str(repo), "start_ref": seed, "start_oid": seed_oid,
             "helpers": helpers, "solution_branch": spec["solution_branch"],
             "commits": {}, "setup_complete": False}
    try:
        command(["git", "-c", "core.hooksPath=" + str(repo / ".git" / "lab-disabled-hooks"),
                 "clone", "--no-local", "--no-checkout", "--", LAUNCHER, repo])
        save_state(repo, state)
        git(repo, "remote", "set-url", "origin", portable_remote(original_origin, LAUNCHER))
        for key in ("user.name", "user.email"):
            configured = git(LAUNCHER, "config", "--get", key, check=False)
            if configured.returncode == 0 and configured.stdout.strip():
                git(repo, "config", "--local", key, configured.stdout.strip())
        upstream = remote_url(LAUNCHER, "upstream")
        if upstream:
            git(repo, "remote", "add", "upstream", portable_remote(upstream, LAUNCHER))
        git(repo, "check-ref-format", "--branch", spec["solution_branch"])
        git(repo, "switch", "-c", spec["solution_branch"], seed_oid)
        actions = spec.get("setup_actions", [])
        if spec.get("local_setup", "none") not in ("none", "fetch", "lease") and not actions:
            raise LabError("This local exercise needs setup_actions in the manifest.")
        apply_actions(repo, actions, state)
        setup_remote(repo, spec, state)
        state["initial_head"] = git_text(repo, "rev-parse", "HEAD")
        state["setup_complete"] = True
        save_state(repo, state)
    except Exception:
        print("Setup did not finish. Existing files are preserved at: " + str(repo), file=sys.stderr)
        print("Choose a new destination for a retry; no automatic cleanup is performed.", file=sys.stderr)
        raise
    print("Ready: {} — {}".format(exercise_id, spec.get("title", exercise_id)))
    print("Workspace: " + str(repo))
    print("Branch: " + git_text(repo, "branch", "--show-current"))
    print("Open this workspace to do the exercise. Keep the launcher clone unchanged.")
    print("Workspace documents and tools are historical snapshots; use the updated launcher's instructions and check commands.")
    print("Check from the launcher: {} lab.py check {} --repo {}".format(
        PYTHON_COMMAND, exercise_id, json.dumps(str(repo))))
    if spec.get("remote_setup"):
        print("The practice remote is local and disposable; it is not GitHub.")
        print("Initial remote tip: " + state["known_initial_remote_tip"])
        print("Advance from the launcher: {} lab.py advance {} --repo {}".format(
            PYTHON_COMMAND, exercise_id, json.dumps(str(repo))))
    return 0


def advance(args):
    exercise_id = normalize_id(args.id)
    if exercise_id not in ("03", "11"):
        raise LabError("advance is available only for 03 and 11.")
    repo, state = load_state(args.repo, exercise_id)
    manifest = load_manifest()
    if state.get("manifest_version") != manifest.get("version"):
        raise LabError("The workspace and launcher manifest versions differ.")
    spec = exercise_spec(manifest, exercise_id, state.get("variant"))
    remote = spec.get("remote_setup")
    if not remote:
        raise LabError("This exercise has no remote simulation.")
    if state.get("remote_advanced"):
        raise LabError("The simulated teammate has already published this update.")
    home = repo / ".git" / "lab-remotes"
    bare, peer = (home / "practice.git").resolve(), (home / "peer").resolve()
    # Never follow an edited remote configuration to GitHub or another repository.
    for target, name in ((repo, "practice"), (peer, "origin")):
        url = remote_url(target, name)
        if not url or Path(url).resolve() != bare:
            raise LabError("Remote simulation was changed; refusing to publish anywhere else.")
    if git_text(peer, "status", "--porcelain"):
        raise LabError("The simulated teammate workspace is not clean; start a new exercise.")
    branch = remote.get("branch", "practice")
    if git_text(peer, "branch", "--show-current") != branch:
        raise LabError("The simulated teammate is on an unexpected branch.")
    # Follow the current accepted tip even if the student already rewrote it.
    # This checkout affects only the clean disposable peer, never the student's worktree.
    git(peer, "fetch", "origin")
    git(peer, "switch", "--detach", "refs/remotes/origin/" + branch)
    apply_actions(peer, remote.get("changes", []), state, file_only=True)
    paths = sorted({action["path"] for action in remote.get("changes", [])})
    tip = setup_commit(peer, remote.get("message", "Simulated teammate update"), paths)
    git(peer, "push", "origin", "HEAD:refs/heads/" + branch)
    state["remote_advanced"] = True
    state["advanced_remote_tip"] = tip
    save_state(repo, state)
    print("The simulated teammate published one update to practice/" + branch + ".")
    print("Your exercise worktree, branch and remote-tracking reference were not updated.")
    return 0


def expected_args(expected):
    args = []
    for key in ("student", "faculty", "days", "fee"):
        if key in expected:
            args += ["--" + key, str(expected[key])]
    search = expected.get("search")
    insensitive = expected.get("search_insensitive", expected.get("search-insensitive", False))
    if search in ("insensitive", "case-insensitive") or insensitive:
        args.append("--search-insensitive")
    elif search in ("sensitive", "case-sensitive") or expected.get("search_sensitive"):
        args.append("--search-sensitive")
    return args


def check_exercise(args):
    exercise_id = normalize_id(args.id)
    repo, state = load_state(args.repo, exercise_id)
    manifest = load_manifest()
    if state.get("manifest_version") != manifest.get("version"):
        raise LabError("The workspace and launcher manifest versions differ.")
    spec = exercise_spec(manifest, exercise_id, state.get("variant"))
    module_path = LAUNCHER / "tools" / "checks.py"
    if not module_path.is_file():
        raise LabError("The launcher is missing tools/checks.py.")
    module_spec = importlib.util.spec_from_file_location("lab_trusted_checks", module_path)
    module = importlib.util.module_from_spec(module_spec)
    old_bytecode = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        module_spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = old_bytecode
    report = module.check_exercise(repo, spec, state, LAUNCHER)
    if not isinstance(report, dict) or not isinstance(report.get("checks"), list):
        raise LabError("The trusted checker returned an invalid report.")
    if not report.get("application_checked", False):
        test = command([sys.executable, LAUNCHER / "run.py", "test", "--source", repo,
                        *expected_args(spec.get("expected", {}))], cwd=LAUNCHER, check=False)
        report["checks"].append({"name": "Application behavior", "passed": test.returncode == 0,
                                 "detail": (test.stdout + test.stderr).strip()})
        report["passed"] = bool(report.get("passed")) and test.returncode == 0
    report.setdefault("graded", bool(spec.get("graded", False)))
    report["id"] = exercise_id
    report["evaluation"] = {
        "ref": "HEAD",
        "branch": git_text(repo, "branch", "--show-current") or None,
        "commit": git_text(repo, "rev-parse", "--verify", "HEAD"),
        "variant": state.get("variant") or "a",
        "result_branch": spec["solution_branch"] if report["graded"] else None,
        "start_branch": spec["solution_branch"],
    }
    report["scope"] = "Local code, working-tree state and Git history; not GitHub submission."
    report["github_pr"] = {
        "required": exercise_id in ("04", "final"),
        "checked": False,
    }
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(("PASS" if report.get("passed") else "NOT YET") + " — " + spec.get("title", exercise_id))
        evaluation = report["evaluation"]
        print("Evaluated: HEAD on {} (variant {})".format(
            evaluation["branch"] or "detached HEAD", evaluation["variant"].upper()))
        print("Commit: " + evaluation["commit"])
        if report["graded"]:
            print("Required submission branch: " + evaluation["result_branch"])
        else:
            print("Start branch: " + evaluation["start_branch"])
            recovery = spec.get("checks", {}).get("recovery_branch")
            if recovery:
                print("Recovery branch: " + recovery)
        print("Scope: " + report["scope"])
        if report["github_pr"]["required"]:
            print("GitHub PR: NOT CHECKED. Complete and verify the required PR separately.")
        if not report["graded"]:
            print("Practice only: this exercise is not graded.")
        for item in report["checks"]:
            print("[{}] {}".format("OK" if item.get("passed") else "--", item.get("name", "Check")))
            if item.get("detail"):
                print("  " + str(item["detail"]).replace("\n", "\n  "))
        print("These checks describe the current result; they do not prove which commands you used.")
    return 0 if report.get("passed") else 1


def doctor(args):
    failures = []
    print("Python: " + sys.version.split()[0])
    if sys.version_info < (3, 9):
        failures.append("Python 3.9 or newer is required.")
    for tool, minimum, argv, pattern in (
            ("Git", (2, 23), ["git", "--version"], r"^git version (\d+)\.(\d+)"),
            ("Java", (17,), ["java", "-version"], r'^(?:openjdk|java)(?: version)? "?(\d+)'),
            ("Java compiler", (17,), ["javac", "-version"], r"^javac (\d+)")):
        try:
            result = command(argv, check=False)
            output = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
            version_line = next((line for line in output.splitlines()
                                 if re.search(pattern, line)), None)
            match = re.search(pattern, version_line) if version_line else None
            print(tool + ": " + (version_line or (output.splitlines()[0] if output else "no version output")))
            if result.returncode or not match or tuple(map(int, match.groups())) < minimum:
                failures.append(tool + " is missing or too old.")
        except LabError as exc:
            failures.append(str(exc))
    try:
        manifest = load_manifest()
        source_git_root()
        missing = []
        for spec in manifest["exercises"].values():
            tags = [spec["start"], *spec.get("helpers", {}).values()]
            variant = spec.get("variant_b", {})
            if variant.get("start"):
                tags.append(variant["start"])
            tags += list(variant.get("helpers", {}).values())
            for tag in tags:
                if git(LAUNCHER, "rev-parse", "--verify", "refs/tags/" + tag + "^{commit}", check=False).returncode:
                    missing.append(tag)
        if missing:
            failures.append("Missing seed tags: " + ", ".join(sorted(set(missing))) +
                            ". Follow the README's initial upstream fetch instructions.")
        if not remote_url(LAUNCHER, "origin"):
            failures.append("No origin remote. Use a clone of your own fork.")
        for key in ("user.name", "user.email"):
            if git(LAUNCHER, "config", "--get", key, check=False).returncode:
                print("NOTE: Set " + key + " before making your own commits.")
    except LabError as exc:
        failures.append(str(exc))
    for failure in failures:
        print("NEEDS ATTENTION: " + failure)
    print("Environment ready." if not failures else "Resolve the items above, then run doctor again.")
    return 1 if failures else 0


def refs(args):
    manifest = load_manifest()
    ids = [normalize_id(args.id)] if args.id else list(manifest["exercises"])
    for exercise_id in ids:
        spec = exercise_spec(manifest, exercise_id)
        print("{}: {}".format(exercise_id, spec.get("title", exercise_id)))
        print("  start: " + spec["start"])
        for role, tag in spec.get("helpers", {}).items():
            print("  {}: {}".format(role, tag))
        if spec.get("variant_b"):
            print("  variant b: " + spec["variant_b"].get("start", spec["start"]))
            for role, tag in spec["variant_b"].get("helpers", {}).items():
                print("  variant b {}: {}".format(role, tag))
        print("  result branch: " + spec["solution_branch"])
    return 0


def instructions(args):
    manifest = load_manifest()
    if not args.id:
        print("1. Fork and clone the lab; follow README.md for the initial upstream fetch.")
        print("2. Run " + PYTHON_COMMAND + " lab.py doctor in that launcher clone.")
        print("3. Run " + PYTHON_COMMAND + " lab.py start 01 (or another ID) to create a separate workspace.")
        print("4. Read the exercise instructions, work there, then check from the launcher.")
        print("5. Submit the final result to your own fork. Local-observation exercises are practice only.")
        print("Run " + PYTHON_COMMAND + " lab.py refs to list fixed starting points.")
        return 0
    exercise_id = normalize_id(args.id)
    spec = exercise_spec(manifest, exercise_id)
    print("{} — {}".format(exercise_id, spec.get("title", exercise_id)))
    value = spec.get("instructions")
    if isinstance(value, str) and "\n" in value:
        print(value)
    else:
        candidates = [LAUNCHER / "docs" / "exercises" / (exercise_id + ".md"),
                      LAUNCHER / "exercises" / (exercise_id + ".md"),
                      LAUNCHER / "exercises" / ("ex" + exercise_id + ".md"),
                      LAUNCHER / "docs" / ("exercise-" + exercise_id + ".md")]
        if isinstance(value, str):
            candidates.insert(0, safe_path(LAUNCHER, value))
        existing = next((path for path in candidates if path.is_file()), None)
        if existing:
            print(existing.read_text(encoding="utf-8"))
        else:
            print("See the exercise section in README.md and the exercises/ directory.")
    print("Start: " + PYTHON_COMMAND + " lab.py start " + exercise_id)
    print("Result branch: " + spec["solution_branch"])
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Check local prerequisites without changing configuration").set_defaults(func=doctor)
    prepare = sub.add_parser("start", help="Create a NEW exercise clone")
    prepare.add_argument("id")
    prepare.add_argument("--variant", choices=["b"])
    prepare.add_argument("--dest", help="New directory only; existing paths are refused")
    prepare.set_defaults(func=start)
    verify = sub.add_parser("check", help="Check an exercise with the launcher's trusted tools")
    verify.add_argument("id")
    verify.add_argument("--repo", required=True)
    verify.add_argument("--json", action="store_true")
    verify.set_defaults(func=check_exercise)
    progress = sub.add_parser("advance", help="Publish one simulated teammate update locally")
    progress.add_argument("id")
    progress.add_argument("--repo", required=True)
    progress.set_defaults(func=advance)
    for name, function, help_text in (
            ("refs", refs, "List starting tags, helper tags and result branches"),
            ("instructions", instructions, "Read the setup overview or one exercise's full instructions")):
        listing = sub.add_parser(name, help=help_text, description=help_text)
        listing.add_argument("id", nargs="?", help="Exercise 01..12 or final; omit to show the overview")
        listing.set_defaults(func=function)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except BrokenPipeError:
        raise
    except (LabError, KeyError, ValueError, OSError) as exc:
        if getattr(args, "json", False):
            print(json.dumps({"passed": False, "error": str(exc)}, ensure_ascii=False))
        else:
            print("Lab: " + str(exc), file=sys.stderr)
        return 2


class QuietPipeOutput:
    """Continue evaluating the command after a reader such as head closes stdout."""

    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def mute(self):
        with open(os.devnull, "w") as sink:
            os.dup2(sink.fileno(), self.stream.fileno())

    def write(self, text):
        try:
            return self.stream.write(text)
        except BrokenPipeError:
            self.mute()
            return len(text)

    def flush(self):
        try:
            self.stream.flush()
        except BrokenPipeError:
            self.mute()
            self.stream.flush()


def cli_main():
    # Swallow only a closed output pipe, never the command's failure status.
    # The wrapper also handles argparse exits and the interpreter's final flush.
    sys.stdout = QuietPipeOutput(sys.stdout)
    return main()


if __name__ == "__main__":
    sys.exit(cli_main())
