#!/usr/bin/env python3
"""Fixture stub emulating the JaVaFo CLI surface used by adapters/javafo.py.

Bare invocation prints a release line (AUM behavior). Pairing mode:
TRF -p OUT. Controlled by FAKE_JAVAFO_MODE in {ok, fail, slow, malformed,
badversion}. FAKE_JAVAFO_CAPTURE=file copies the input TRF there.
NOT a pairing engine.
"""
import os
import shutil
import sys
import time


def main():
    argv = sys.argv[1:]
    mode = os.environ.get("FAKE_JAVAFO_MODE", "ok")
    if not argv:
        if mode == "badversion":
            print("nothing recognizable")
            return 0
        print("JaVaFo (rrweb.org/javafo) - Rel. 9.9 (Build 9999)")
        return 0
    src = None
    out = None
    if "-p" in argv:
        i = argv.index("-p")
        candidates = [a for a in argv if a.endswith(".trf")]
        src = candidates[0] if candidates else None
        out = argv[i + 1] if i + 1 < len(argv) else None
    capture = os.environ.get("FAKE_JAVAFO_CAPTURE")
    if capture and src and os.path.isfile(src):
        shutil.copyfile(src, capture)
    if mode == "slow":
        time.sleep(30)
        return 0
    if mode == "fail":
        print("pairing engine error (simulated)", file=sys.stderr)
        return 0  # AUM: no output file, unclear stdout
    if mode == "malformed":
        if out:
            with open(out, "w") as fh:
                fh.write("pairs are 1 and 2\n")
        return 0
    if out:
        with open(out, "w") as fh:
            fh.write("2\n1 2\n3 0\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
