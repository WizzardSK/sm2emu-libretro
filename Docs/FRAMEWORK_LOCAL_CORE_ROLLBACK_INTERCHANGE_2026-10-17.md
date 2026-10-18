# Local Core Deployment And Rollback — SM2-Emu To Framework

## User Decision

Do not keep a copy of the replaced installed core for a routine local update
when the core can be rebuilt from the project's source. Verify the installed
artifact against the just-built artifact by hash. If the change must be undone,
revert the scoped source change and rebuild, preserving unrelated work.

A binary backup is justified only by a concrete recovery need, such as an
artifact or state that cannot be reconstructed, or by the user's explicit
request. The rule concerns duplicate installed-core binaries, not ROMs, saves,
source history, release artifacts or other data with different ownership and
recovery requirements.

This is a reusable deployment criterion for Libretro projects where local
builds are reproducible. Each destination retains its designated install path,
authorization boundaries and platform checks. An earlier report that kept a
backup remains historical evidence; it does not impose that procedure on new
deployments.

## SM2 Application

The installed normal RetroArch core and the build both have SHA-256
`ca63872af3b9f832a8b7d7d360e052192a1a64b0ce49aa359a2f04fd7c8b9874`.
The redundant copy of the replaced binary made during the menu-order update
was deleted. The deployment record at
`build-libretro-gpu/validation/framework-menu-order-20261017/deployment.json`
retains source and installed identity without a backup reference. The rule is
also recorded in this repository's `AGENTS.md` under Local RetroArch Deployment.

## Requested Framework Integration

Clarify F20 or the equivalent local-deployment contract: routine reproducible
core installs require artifact identity checks, not automatic retention of the
previous installed binary. Treat exceptional recovery needs separately. Carry
this as a general policy candidate to the destination core chats; do not edit
their deployment instructions or old evidence without checking applicability.
