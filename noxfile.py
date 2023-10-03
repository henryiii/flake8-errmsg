from __future__ import annotations

import nox

nox.options.sessions = ["lint", "pylint", "tests", "tests_flake8"]


@nox.session
def lint(session: nox.Session) -> None:
    """
    Run the linter.
    """
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@nox.session
def pylint(session: nox.Session) -> None:
    """
    Run PyLint.
    """
    # This needs to be installed into the package environment, and is slower
    # than a pre-commit check
    session.install("-e.", "pylint")
    session.run("pylint", "src", *session.posargs)


@nox.session
def tests(session: nox.Session) -> None:
    """
    Run the unit and regular tests.
    """
    session.install("-e.[test]")
    session.run("pytest", *session.posargs)


@nox.session
def build(session: nox.Session) -> None:
    """
    Build an SDist and wheel.
    """
    session.install("build")
    session.run("python", "-m", "build")


@nox.session
def tests_flake8(session: nox.Session) -> None:
    """
    Run the flake8 tests.
    """
    session.install("-e.", "flake8")
    result = session.run("flake8", "tests/example1.py", silent=True, success_codes=[1])
    if len(result.splitlines()) != 2:
        session.error(f"Expected 2 errors from flake8\n{result}")

    result = session.run(
        "flake8",
        "--errmsg-max-string-length=30",
        "tests/example1.py",
        silent=True,
        success_codes=[1],
    )
    if len(result.splitlines()) != 1:
        session.error(f"Expected 1 errors from flake8\n{result}")
