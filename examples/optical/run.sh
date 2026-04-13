#!/usr/bin/env bash
# Generate optical_prism.gdml from the GeGeDe builder.
#
# Usage:
#   ./run.sh              # writes optical_prism.gdml
#   ./run.sh -O           # also validate the in-memory GDML object
#   ./run.sh -F           # also validate the written file
#
# The script must be run from this directory (examples/optical/) so that
# Python can import optical.py.  PYTHONPATH is set automatically.

set -euo pipefail
cd "$(dirname "$0")"

# Make optical.py importable
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"

gegede "$@" -o optical_prism.gdml optical.cfg
echo "Done.  Output: optical_prism.gdml"
