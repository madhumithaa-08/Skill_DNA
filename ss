#!/usr/bin/env bash
# ./ss — executable wrapper around kit/ss.py (the SKILL DNA automation CLI).
#
# The plan called for a ./kit wrapper, but kit/ is already a directory here, and
# a file cannot share a directory entry name with a directory. So the wrapper is
# ./ss (matching the upstream strands-ship `ss` convention). `python kit/ss.py`
# remains the canonical form used by the verification steps.
exec python3 "$(dirname "$0")/kit/ss.py" "$@"
