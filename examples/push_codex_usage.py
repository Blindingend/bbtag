#!/usr/bin/env python3
"""Compatibility wrapper for the packaged Codex usage CLI."""

from bluetag.codex_usage import main


if __name__ == "__main__":
    raise SystemExit(main())
