# Standard Gun Input Fallback

Date: 2026-10-11

## Symptom And Cause

The user reports a stationary cursor in Standard and Lightgun Only without a
physical gun, while Mouse Only and Mouse + Analog Stick accept Mouse movement.
Standard previously counted IS_OFFSCREEN alone as Lightgun activity. A constant
off-screen report therefore selected the absolute Lightgun position every frame
and discarded relative Mouse and Stick movement. This is a reproduced adapter
bug; the exact callback values in the user's RetroArch session have not yet
been captured.

## Correction

In Standard, Lightgun coordinate changes or Trigger/Reload/Aux A commands can
select absolute aim. A stationary off-screen status alone cannot select it.
Off-screen status applies to aim only when the Lightgun source is selected;
Mouse edge reload and explicit reload shortcuts retain their own rules.
Lightgun Only remains restricted to Lightgun callbacks and does not add a
core-side Mouse fallback. RetroArch's Cocoa input implementation derives
Lightgun absolute coordinates from its window pointer; availability in the
specific running RetroArch build still requires runtime evidence.

## Verification And Limits

The existing ROM-free input checks reproduce the failure before the fix, using
constant off-screen Lightgun status and changing Mouse/Stick input. The checks
cover BEL positional and Virtua Cop serial paths. Existing dedicated-Lightgun
and off-screen-trigger tests also remain part of the suite. No calibration,
coordinate curve, ROM data or BEL RAM workaround is changed. Pending upstream
gun integration is excluded from the normal build, preserving its deployment
boundary. This does not qualify physical hardware or the user's exact session.

Evidence: build-libretro-gpu/validation/gun-standard-fallback-20261011/.
