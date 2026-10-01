#!/usr/bin/env python3
"""Fixture stub emulating the BBP CLI surface used by adapters/bbp.py.

Controlled by env: FAKE_BBP_MODE in {ok, impossible, invalid, crash, slow,
malformed, badversion, noversion}. FAKE_BBP_CAPTURE=file copies the input
TRF there for content assertions. NOT a pairing engine.
"""
import os
import shutil
import sys
import time


def main():
    argv = sys.argv[1:]
    mode = os.environ.get("FAKE_BBP_MODE", "ok")
    if "-r" in argv:
        if mode == "badversion":
            print("garbage-no-version")
            return 0
        if mode == "noversion":
            return 1
        print("bbpPairings fake 0.0-test (build 0)")
        return 0
    src = None
    out = None
    args = list(argv)
    if "-p" in args:
        i = args.index("-p")
        src = args[i - 1] if i - 1 >= 0 else None
        out = args[i + 1] if i + 1 < len(args) else None
    capture = os.environ.get("FAKE_BBP_CAPTURE")
    if capture and src and os.path.isfile(src):
        shutil.copyfile(src, capture)
    if mode == "slow":
        time.sleep(30)
        return 0
    if mode == "impossible":
        print("no valid pairing", file=sys.stderr)
        return 1
    if mode == "invalid":
        print("bad input file", file=sys.stderr)
        return 3
    if mode == "crash":
        print("boom", file=sys.stderr)
        return 99
    if mode == "malformed":
        if out:
            with open(out, "w") as fh:
                fh.write("hello pairs\n1 2 3\n")
        return 0
    # ok
    if out:
        with open(out, "w") as fh:
            fh.write("2\n1 2\n3 0\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
