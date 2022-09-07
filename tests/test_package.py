from __future__ import annotations

import ast

import flake8_errmsg as m

ERR1 = """\
raise Error("that")
raise Error(f"this {that}")
raise Error(1)
raise Error(msg)
"""


def test_err1():
    node = ast.parse(ERR1)

    results = list(m.ErrMsgASTPlugin(node).run())
    assert len(results) == 2
    assert results[0].line_number == 1
    assert results[1].line_number == 2

    assert results[0].offset == 0
    assert results[1].offset == 0

    assert (
        results[0].msg
        == "EM101 Exception must not use a string literal, assign to variable first"
    )
    assert (
        results[1].msg
        == "EM102 Exception must not use an f-string literal, assign to variable first"
    )


def test_string_length():
    node = ast.parse(ERR1)
    plugin = m.ErrMsgASTPlugin(node)
    m.ErrMsgASTPlugin.max_string_length = 10
    results = list(plugin.run())
    assert len(results) == 1
    assert results[0].line_number == 2

    assert (
        results[0].msg
        == "EM102 Exception must not use an f-string literal, assign to variable first"
    )
