# flake8-errmsg

[![Actions Status][actions-badge]][actions-link]
[![GitHub Discussion][github-discussions-badge]][github-discussions-link]
[![Gitter][gitter-badge]][gitter-link]

[![PyPI version][pypi-version]][pypi-link]
[![PyPI platforms][pypi-platforms]][pypi-link]

## Intro

A checker for flake8 that helps format nice error messages. Currently there are
two checks:

- **EM101**: Check for raw usage of string literals in Exception raising.
- **EM102**: Check for raw usage of f-string literals in Exception raising.

The issue is that Python includes the line with the raise in the default
traceback (and most other formatters, like Rich and IPython to too). That means
a user gets a message like this:

```python
sub = "Some value"
raise RuntimeError(f"{sub!r} is incorrect")
```

```pytb
Traceback (most recent call last):
  File "tmp.py", line 2, in <module>
    raise RuntimeError(f"{sub!r} is incorrect")
RuntimeError: 'Some value' is incorrect
```

If this is longer or more complex, the duplication can be quite confusing for a
user unaccustomed to reading tracebacks.

While if you always assign to something like `msg`, then you get:

```python
sub = "Some value"
msg = f"{sub!r} is incorrect"
raise RunetimeError(msg)
```

```pytb
Traceback (most recent call last):
  File "tmp.py", line 3, in <module>
    raise RuntimeError(msg)
RuntimeError: 'Some value' is incorrect
```

Now there's a simpler traceback, less code, and no double message. If you have a
long message, this also often formats better when using Black, too.

Reminder: Libraries should produce tracebacks with custom error classes, and
applications should print nice errors, usually _without_ a traceback, unless
something _unexpected_ occurred. An app should not print a traceback for an
error that is known to be triggerable by a user.

## Usage

Just add this to your `.pre-commit-config.yaml` `flake8` check under
`additional_dependencies`. If you use `extend-select`, you should need no other
config.

You can also manually run this check (without flake8's `noqa` filtering) via
script entry-point (`pipx run flake8-errmsg <files>`) or module entry-point
(`python -m flake8_errmsg <files>` when installed).

## FAQ

Q: Why not look for `"".format()` too? <br/> A: Tools like pyupgrade should help
move to fstrings, so these should be rare. But it would likely be easy to add.

Q: Why Python 3.10+ only? <br/> A: This is a static checker and for developers.
Developers and static checks should be on 3.10 already. And I was lazy and match
statements are fantastic for this sort of thing. And the AST module changed in
3.8 anyway.

Q: What other sorts of checks are acceptable? <br/> A: Things that help with
nice errors. For example, maybe requiring `raise SystemExit(n)` over `sys.exit`,
`exit`, etc.

<!-- prettier-ignore-start -->
[actions-badge]:            https://github.com/henryiii/flake8-errmsg/workflows/CI/badge.svg
[actions-link]:             https://github.com/henryiii/flake8-errmsg/actions
[github-discussions-badge]: https://img.shields.io/static/v1?label=Discussions&message=Ask&color=blue&logo=github
[github-discussions-link]:  https://github.com/henryiii/flake8-errmsg/discussions
[gitter-badge]:             https://badges.gitter.im/https://github.com/henryiii/flake8-errmsg/community.svg
[gitter-link]:              https://gitter.im/https://github.com/henryiii/flake8-errmsg/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge
[pypi-link]:                https://pypi.org/project/flake8-errmsg/
[pypi-platforms]:           https://img.shields.io/pypi/pyversions/flake8-errmsg
[pypi-version]:             https://badge.fury.io/py/flake8-errmsg.svg
<!-- prettier-ignore-end -->
