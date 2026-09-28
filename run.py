#!/usr/bin/env python3
"""Compile and run the dependency-free Java lab using a temporary directory.

With --source, only Java application sources come from that repository.
Tests always come from the directory containing this trusted runner.
"""

import argparse
import pathlib
import shutil
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parent
COMPILE_TIMEOUT = 60
RUN_TIMEOUT = 30


def nonnegative(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("expected a nonnegative integer")
    return number


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--source", type=pathlib.Path, default=ROOT,
                        help="repository containing src/ (tests remain launcher-owned)")
    commands = result.add_subparsers(dest="command", required=True)
    for command in ("test", "demo"):
        sub = commands.add_parser(command)
        # SUPPRESS preserves a --source option supplied before the subcommand.
        sub.add_argument("--source", type=pathlib.Path, default=argparse.SUPPRESS)
        if command == "test":
            sub.add_argument("--student", type=nonnegative, default=2)
            sub.add_argument("--faculty", type=nonnegative, default=2)
            sub.add_argument("--days", type=nonnegative, default=14)
            sub.add_argument("--fee", type=nonnegative, default=100)
            search = sub.add_mutually_exclusive_group()
            search.add_argument("--search-sensitive", dest="sensitive", action="store_true")
            search.add_argument("--search-insensitive", dest="sensitive", action="store_false")
            sub.set_defaults(sensitive=True)
    return result


def execute(command, timeout, cwd):
    try:
        completed = subprocess.run(command, cwd=str(cwd), timeout=timeout,
                                   capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", check=False)
    except subprocess.TimeoutExpired:
        print("ERROR: process exceeded {} seconds.".format(timeout), file=sys.stderr)
        return 124
    except OSError as error:
        print("ERROR: could not start process: {}".format(error), file=sys.stderr)
        return 127
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    return completed.returncode


def main(argv=None):
    args = parser().parse_args(argv)
    source = args.source.expanduser().resolve()
    source_dir = source / "src" / "library"
    source_files = sorted(source_dir.rglob("*.java")) if source_dir.is_dir() else []
    if not source_files:
        print("ERROR: no Java sources found in {}".format(source_dir), file=sys.stderr)
        return 2
    javac = shutil.which("javac")
    java = shutil.which("java")
    if not javac or not java:
        print("ERROR: install a JDK 17 or newer and put java and javac on PATH.", file=sys.stderr)
        return 127
    files = source_files
    if args.command == "test":
        tests = sorted((ROOT / "tests" / "library").rglob("*.java"))
        if not tests:
            print("ERROR: launcher tests/library contains no tests.", file=sys.stderr)
            return 2
        files = files + tests
    # TemporaryDirectory removes class files even after compilation or test failure.
    with tempfile.TemporaryDirectory(prefix="git-essentials-java-") as output:
        compile_command = [javac, "--release", "17", "-encoding", "UTF-8", "-d", output]
        code = execute(compile_command + [str(path) for path in files], COMPILE_TIMEOUT, source)
        if code:
            print("ERROR: compilation failed; a JDK supporting --release 17 is required.",
                  file=sys.stderr)
            return code
        command = [java, "-Dfile.encoding=UTF-8", "-cp", output]
        if args.command == "demo":
            command += ["library.Main"]
        else:
            command += ["library.LibraryTests", "--student", str(args.student),
                        "--faculty", str(args.faculty), "--days", str(args.days),
                        "--fee", str(args.fee),
                        "--search-sensitive" if args.sensitive else "--search-insensitive"]
        return execute(command, RUN_TIMEOUT, source)


if __name__ == "__main__":
    sys.exit(main())
