#!/bin/bash
# Run the interpreter on test.ngc.  Capture its output (and any error message)
# regardless of exit status, so checkresult can inspect the result.
rs274 -g test.ngc 2>&1 || true
