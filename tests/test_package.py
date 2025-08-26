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
        == "EM101 Exceptions must not use a string literal; assign to a variable first"
    )
    assert (
        results[1].msg
        == "EM102 Exceptions must not use an f-string literal; assign to a variable first"
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
        == "EM102 Exceptions must not use an f-string literal; assign to a variable first"
    )


ERR2 = """\
raise RuntimeError("this {} is".format("that"))
"""


def test_err2():
    node = ast.parse(ERR2)
    results = list(m.ErrMsgASTPlugin(node).run())
    assert len(results) == 1
    assert results[0].line_number == 1
    assert (
        results[0].msg
        == "EM103 Exceptions must not use a .format() string directly; assign to a variable first"
    )


ERR3 = """\
raise RuntimeError
"""


def test_err3():
    node = ast.parse(ERR3)
    results = list(m.ErrMsgASTPlugin(node).run())
    assert len(results) == 1
    assert results[0].line_number == 1
    assert (
        results[0].msg
        == "EM104 Built-in Exceptions must not be thrown without being called"
    )


ERR4 = """\
raise RuntimeError()
"""


def test_err4():
    node = ast.parse(ERR4)
    results = list(m.ErrMsgASTPlugin(node).run())
    assert len(results) == 1
    assert results[0].line_number == 1
    assert results[0].msg == "EM105 Built-in Exceptions must have a useful message"
