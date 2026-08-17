#!/usr/bin/env python3
"""Verify a packaged .alfredworkflow archive.

Checks that the archive contains info.plist at its root, that the plist
parses, and prints the workflow identity. Used by the release CI:

    python3 tools/verify_workflow.py DeepSeek.alfredworkflow
"""

import plistlib
import sys
import zipfile


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_workflow.py <archive.alfredworkflow>")

    archive_path = sys.argv[1]
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if "info.plist" not in names:
            raise SystemExit(f"info.plist missing from package: {names}")
        with archive.open("info.plist") as handle:
            plist = plistlib.load(handle)

    print(f"Packaged OK: {plist['name']} ({plist['bundleid']}) v{plist['version']}")


if __name__ == "__main__":
    main()
