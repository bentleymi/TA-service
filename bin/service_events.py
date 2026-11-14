#!/usr/bin/env python3
"""Emit one JSON event per cycle with systemd service health."""
import sys

from service_common import discover, emit


def main():
    data = discover()
    emit(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
