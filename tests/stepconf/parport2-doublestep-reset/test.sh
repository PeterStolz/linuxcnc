#!/bin/bash
# Reproduces a bug in stepconf's HAL generator: a step signal on the SECOND
# parallel port gets its doublestep reset emitted on parport.0 instead of
# parport.1 (build_HAL.py connect_output hard-codes the port).  gen_test.py
# drives the real generator function and exits non-zero while the bug exists.
# All diagnostics go to stderr, so a passing (fixed) run yields empty stdout
# and matches the empty 'expected' file.
python3 gen_test.py
