from __future__ import annotations

import os
from typing import TYPE_CHECKING

from nox import session

if TYPE_CHECKING:
    from typing import List, Literal

    from nox import Session

python: List[str] | Literal[False] = (
    False
    if os.environ.get("ENVIRONMENT", "production") != "testing"
    else [f"3.{minor}" for minor in range(6, 11)]
)


@session(python=python)
def black(s: Session) -> None:
    if python:
        s.install("-U", "black")

    s.run("black", ".")


@session(python=python)
def isort(s: Session) -> None:
    if python:
        s.install("-U", "isort")

    s.run("isort", ".")


@session(python=python)
def flake8(s: Session) -> None:
    if python:
        s.install("-U", "flake8")

    s.run("flake8", ".")


@session(python=python)
def mypy(s: Session) -> None:
    if python:
        s.install("-U", "mypy")

    s.run("mypy", ".")


@session(python=python)
def bandit(s: Session) -> None:
    if python:
        s.install("-U", "bandit")

    s.run("bandit", "-r", ".")


@session(python=python)
def safety(s: Session) -> None:
    if python:
        s.install("-U", "safety")

    s.run("safety", "check")


def clean(s: Session) -> None:
    s.run("python", "scripts/clean.py")


if not python:
    session(python=python)(clean)
