from __future__ import annotations

import ast
import sys

import pytest

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


@pytest.mark.usefixtures("_reset_max_string_length")
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


ERR2B = """\
raise RuntimeError(f"this {x} is".format())
"""


def test_err2b_fstring_format():
    node = ast.parse(ERR2B)
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


# --- EM106 tests ---

ERR6 = """\
x = 1
raise ValueError(msg := f"Bad thing: {x}")
"""


def test_err6_positional_namedexpr():
    node = ast.parse(ERR6)
    results = list(m.ErrMsgASTPlugin(node).run())
    assert len(results) == 1
    assert results[0].line_number == 2
    assert (
        results[0].msg
        == "EM106 Exceptions must not use walrus assignment in raise calls"
    )


ERR7 = """\
raise RuntimeError(_ := "oops")
"""


def test_err7_simple_namedexpr_constant():
    node = ast.parse(ERR7)
    results = list(m.ErrMsgASTPlugin(node).run())
    assert len(results) == 1
    assert results[0].line_number == 1
    assert (
        results[0].msg
        == "EM106 Exceptions must not use walrus assignment in raise calls"
    )


ERR8 = """\
raise MyErr(message=(m := "oops"))
"""


def test_err8_keyword_namedexpr():
    node = ast.parse(ERR8)
    results = list(m.ErrMsgASTPlugin(node).run())
    assert len(results) == 1
    assert results[0].line_number == 1
    assert (
        results[0].msg
        == "EM106 Exceptions must not use walrus assignment in raise calls"
    )


ERR9 = """\
def make_msg(x):
    return (m := f"...{x}...")

raise ValueError(make_msg(1))
"""


def test_err9_namedexpr_outside_raise_ok():
    node = ast.parse(ERR9)
    results = list(m.ErrMsgASTPlugin(node).run())
    # No EM106 should be reported; raise does not contain a walrus expression directly
    assert results == []


ERR10 = """\
raise ValueError(sorted(xs, key=lambda v: (k := v))[0])
"""


def test_err10_namedexpr_in_lambda_ok():
    node = ast.parse(ERR10)
    results = list(m.ErrMsgASTPlugin(node).run())
    # The walrus binds in the lambda's own scope, not the raise's, so no EM106.
    assert results == []


# --- max_string_length boundary ---


@pytest.fixture
def _reset_max_string_length():
    """Restore the class-level option, which several tests mutate in place."""
    original = m.ErrMsgASTPlugin.max_string_length
    yield
    m.ErrMsgASTPlugin.max_string_length = original


@pytest.mark.usefixtures("_reset_max_string_length")
def test_string_length_boundary():
    node = ast.parse('raise RuntimeError("12345")\n')  # length 5

    m.ErrMsgASTPlugin.max_string_length = 5  # len == max is still flagged (>=)
    assert len(list(m.ErrMsgASTPlugin(node).run())) == 1

    m.ErrMsgASTPlugin.max_string_length = 6  # len < max is ignored
    assert list(m.ErrMsgASTPlugin(node).run()) == []


# --- CLI / run_on_file ---


@pytest.mark.usefixtures("_reset_max_string_length")
def test_run_on_file_reports_errors(tmp_path, capsys):
    path = tmp_path / "example.py"
    path.write_text('raise RuntimeError("a long message")\n', encoding="utf-8")

    m.run_on_file(str(path))

    out = capsys.readouterr().out
    assert f"{path}:1:0 EM101" in out


@pytest.mark.usefixtures("_reset_max_string_length")
def test_run_on_file_respects_max_string_length(tmp_path, capsys):
    path = tmp_path / "example.py"
    path.write_text('raise RuntimeError("short")\n', encoding="utf-8")

    m.run_on_file(str(path), max_string_length=100)

    assert capsys.readouterr().out == ""


def test_run_on_file_syntax_error(tmp_path, capsys):
    path = tmp_path / "broken.py"
    path.write_text("raise RuntimeError(\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        m.run_on_file(str(path))

    assert exc.value.code == 1
    assert "Traceback:" in capsys.readouterr().out


@pytest.mark.usefixtures("_reset_max_string_length")
def test_main(tmp_path, capsys, monkeypatch):
    path = tmp_path / "example.py"
    path.write_text('raise RuntimeError("a long message")\n', encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["flake8-errmsg", str(path)])
    m.main()

    assert "EM101" in capsys.readouterr().out
