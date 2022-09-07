from __future__ import annotations


def f_a():
    raise RuntimeError("This is an example exception")


def f_b():
    example = "example"
    raise RuntimeError(f"This is an {example} exception")


def f_c():
    msg = "hello"
    raise RuntimeError(msg)
