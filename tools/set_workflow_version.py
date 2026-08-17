#!/usr/bin/env python3
"""Set the version field of Workflow/info.plist.

Used by the GitHub Actions release workflow (tools are run from the repo root)
and can also be run locally:

    python3 tools/set_workflow_version.py 1.2.0
"""

import plistlib
import sys


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: set_workflow_version.py <version>")

    version = sys.argv[1].lstrip("v")
    path = "Workflow/info.plist"

    with open(path, "rb") as handle:
        plist = plistlib.load(handle)
    plist["version"] = version
    with open(path, "wb") as handle:
        plistlib.dump(plist, handle, sort_keys=False)

    print(f"Set workflow version to {version} in {path}")


if __name__ == "__main__":
    main()
