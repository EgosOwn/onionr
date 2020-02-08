"""Add box around string.

taken from https://stackoverflow.com/a/20757491 under https://creativecommons.org/licenses/by-sa/4.0/
https://stackoverflow.com/users/816449/bunyk
"""


def bordered(text: str) -> str:
    """Add border to string."""
    lines = text.splitlines()
    width = max(len(s) for s in lines)
    res = ['┌' + '─' * width + '┐']
    for s in lines:
        res.append('│' + (s + ' ' * width)[:width] + '│')
    res.append('└' + '─' * width + '┘')
    return '\n'.join(res)
