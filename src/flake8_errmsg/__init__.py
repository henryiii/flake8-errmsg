#!/usr/bin/env python

"""
Copyright (c) 2022 Henry Schreiner. All rights reserved.

flake8-errmsg: Flake8 checker for raw literals inside raises.
"""

from __future__ import annotations

import argparse
import ast
import dataclasses
import traceback
from collections.abc import Iterator
from pathlib import Path
from typing import Any, ClassVar, NamedTuple

__all__ = ("__version__", "run_on_file", "main", "ErrMsgASTPlugin")

__version__ = "0.3.0"


class Flake8ASTErrorInfo(NamedTuple):
    line_number: int
    offset: int
    msg: str
    cls: type  # unused


class Visitor(ast.NodeVisitor):
    def __init__(self, max_string_len: int) -> None:
        self.errors: list[Flake8ASTErrorInfo] = []
        self.max_string_len = max_string_len

    def visit_Raise(self, node: ast.Raise) -> None:
        match node.exc:
            case ast.Call(args=[ast.Constant(value=str(value)), *_]):
                if len(value) >= self.max_string_len:
                    self.errors.append(EM101(node))
            case ast.Call(args=[ast.JoinedStr(), *_]):
                self.errors.append(EM102(node))
            case _:
                pass


def EM101(node: ast.AST) -> Flake8ASTErrorInfo:
    msg = "EM101 Exception must not use a string literal, assign to variable first"
    return Flake8ASTErrorInfo(node.lineno, node.col_offset, msg, Visitor)


def EM102(node: ast.AST) -> Flake8ASTErrorInfo:
    msg = "EM102 Exception must not use an f-string literal, assign to variable first"
    return Flake8ASTErrorInfo(node.lineno, node.col_offset, msg, Visitor)


MAX_STRING_LENGTH = 0


@dataclasses.dataclass
class ErrMsgASTPlugin:
    max_string_length: ClassVar[int] = 0

    tree: ast.AST

    _: dataclasses.KW_ONLY
    name: str = "flake8_errmsg"
    version: str = "0.1.0"
    options: Any = None

    def run(self) -> Iterator[Flake8ASTErrorInfo]:
        visitor = Visitor(self.max_string_length)
        visitor.visit(self.tree)
        yield from visitor.errors

    @staticmethod
    def add_options(optmanager: Any) -> None:
        optmanager.add_option(
            "--errmsg-max-string-length",
            parse_from_config=True,
            default=0,
            type=int,
            help="Set a maximum string length to allow inline strings. Default 0 (always disallow).",
        )

    @classmethod
    def parse_options(cls, options: argparse.Namespace) -> None:
        cls.max_string_length = options.errmsg_max_string_length


def run_on_file(path: str, max_string_length: int = 0) -> None:
    code = Path(path).read_text(encoding="utf-8")

    try:
        node = ast.parse(code)
    except SyntaxError as e:
        e.filename = path
        print("Traceback:")
        traceback.print_exception(e, limit=0)
        raise SystemExit(1) from None

    plugin = ErrMsgASTPlugin(node)
    ErrMsgASTPlugin.max_string_length = max_string_length

    for err in plugin.run():
        print(f"{path}:{err.line_number}:{err.offset} {err.msg}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--errmsg-max-string-length", type=int, default=0)
    parser.add_argument("files", nargs="+")
    namespace = parser.parse_args()

    for item in namespace.files:
        run_on_file(item, namespace.errmsg_max_string_length)


if __name__ == "__main__":
    main()
