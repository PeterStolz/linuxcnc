#!/bin/bash
# Demonstrates a conflicting duplicate key in a shipped machine config:
#   configs/by_machine/sherline/Sherline4Axis/Sherline4Axis_inch.ini
# [TRAJ]MAX_LINEAR_VELOCITY is defined twice (lines 109 and 114) with DIFFERENT
# values.  inivar reads the file exactly as LinuxCNC does and returns the FIRST
# occurrence, so the author's intended "# for gui only" value (.36) is silently
# discarded and the effective limit stays 25 in/s (~1500 ipm on a Sherline).
INI=../../../configs/by_machine/sherline/Sherline4Axis/Sherline4Axis_inch.ini
echo -n "effective value (LinuxCNC uses the first): "
inivar -ini "$INI" -sec TRAJ -var MAX_LINEAR_VELOCITY
echo -n "ignored second occurrence:                 "
inivar -ini "$INI" -sec TRAJ -var MAX_LINEAR_VELOCITY -num 2 2>/dev/null || echo "(none)"
