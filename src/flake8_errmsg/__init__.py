#!/usr/bin/env python

"""
Copyright (c) 2022 Henry Schreiner. All rights reserved.

flake8-errmsg: Flake8 checker for raw literals inside raises.
"""

from __future__ import annotations

import ast
import dataclasses
import sys
import traceback
from pathlib import Path
from typing import Iterator, NamedTuple

__all__ = ("__version__", "run_on_file", "main", "ErrMsgASTPlugin")

__version__ = "0.2.1"


class Flake8ASTErrorInfo(NamedTuple):
    line_number: int
    offset: int
    msg: str
    cls: type  # unused


class Visitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.errors: list[Flake8ASTErrorInfo] = []

    def visit_Raise(self, node: ast.Raise) -> None:
        match node.exc:
            case ast.Call(args=[ast.Constant(value=str()), *_]):
                msg = "EM101 exception must not use a string literal, assign to variable first"
                self.errors.append(
                    Flake8ASTErrorInfo(node.lineno, node.col_offset, msg, type(self))
                )
            case ast.Call(args=[ast.JoinedStr(), *_]):
                msg = "EM102 exception must not use a f-string literal, assign to variable first"
                self.errors.append(
                    Flake8ASTErrorInfo(node.lineno, node.col_offset, msg, type(self))
                )
            case _:
                pass


@dataclasses.dataclass
class ErrMsgASTPlugin:
    tree: ast.AST

    _: dataclasses.KW_ONLY
    name: str = "flake8_errmsg"
    version: str = "0.1.0"

    def run(self) -> Iterator[Flake8ASTErrorInfo]:
        visitor = Visitor()
        visitor.visit(self.tree)
        yield from visitor.errors


def run_on_file(path: str) -> None:
    code = Path(path).read_text(encoding="utf-8")

    try:
        node = ast.parse(code)
    except SyntaxError as e:
        e.filename = path
        print("Traceback:")
        traceback.print_exception(e, limit=0)
        raise SystemExit(1) from None

    plugin = ErrMsgASTPlugin(node)
    for err in plugin.run():
        print(f"{path}:{err.line_number}:{err.offset} {err.msg}")


def main() -> None:
    for item in sys.argv[1:]:
        run_on_file(item)


if __name__ == "__main__":
    main()
