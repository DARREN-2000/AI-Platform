"""A tiny starter script for the AI-Platform repo.

Run with:
    python examples/hello.py
"""

from __future__ import annotations


def greet(name: str = "world") -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}!"


def main() -> None:
    print(greet())


if __name__ == "__main__":
    main()
