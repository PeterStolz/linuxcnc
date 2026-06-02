#!/usr/bin/env python3
"""Reproduce a bug in stepconf's HAL generator (build_HAL.HAL.connect_output).

When a step signal is placed on the SECOND parallel port and 'doublestep' is
active, the per-pin step-reset must be applied to that same port.  But
build_HAL.py hard-codes 'parport.0' for the reset:

    print("setp parport.0.pin-%02d-out-reset%s 1" % (num, ending), file=file)

instead of using the 'port' variable like every other line in the function.
So for a stepper on parport.1 the reset is written to parport.0's unrelated pin
(and parport.1.reset is never added to a thread either), silently breaking
doublestep pulse generation on the second port.

This drives the real connect_output() with a minimal stand-in for stepconf's
data/private-data objects (build_HAL imports only os/time/shutil, so no GTK or
linuxcnc runtime is needed).  It exits 0 if the reset targets the correct port
(bug fixed) and 1 otherwise.  All diagnostics go to stderr so a passing run
produces no stdout.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..",
                                "src", "emc", "usr_intf", "stepconf"))
import build_HAL  # noqa: E402


class SIG:  # minimal stand-in for stepconf's Private_Data (app._p)
    UNUSED_OUTPUT = "unused"
    XSTEP, YSTEP, ZSTEP, ASTEP = "xstep", "ystep", "zstep", "astep"
    USTEP, VSTEP, X2STEP, Y2STEP = "ustep", "vstep", "x2step", "y2step"
    human_output_names = hal_output_names = []


class Data(dict):  # supports both d['pp2_pin3'] and d.select_qtplasmac
    select_qtplasmac = False
    sim_hardware = False


class App:
    def __init__(self):
        self.d = Data()
        self._p = SIG

    def doublestep(self):  # True when the step time is <= 5000 ns
        return True


app = App()
hal = build_HAL.HAL(app)
hal.outputlist, hal.tandemsigs = [], {}

# Place a Y step signal on the SECOND parallel port, pin 3.
app.d["pp2_pin3"] = "ystep"
app.d["pp2_pin3inv"] = 0

buf = io.StringIO()
hal.connect_output(buf, 3, port=1)
out = buf.getvalue()
sys.stderr.write("generated HAL for a step pin on parport.1:\n")
for line in out.splitlines():
    sys.stderr.write("    %s\n" % line)

reset = [l for l in out.splitlines() if "out-reset" in l]
if not reset:
    sys.stderr.write("ERROR: no step-reset line was generated\n")
    sys.exit(1)

if "parport.1." in reset[0]:
    sys.exit(0)  # correct: reset on the same (second) port

sys.stderr.write(
    "\nBUG reproduced (stepconf build_HAL.py connect_output):\n"
    "  step pin is on parport.1 but its reset was emitted as:\n"
    "    %s\n"
    "  'parport.0' is hard-coded instead of 'parport.%%d' %% port.\n"
    % reset[0].strip())
sys.exit(1)
