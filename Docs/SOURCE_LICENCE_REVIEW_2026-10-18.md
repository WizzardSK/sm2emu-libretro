# Source Licence And Distribution Review — 2026-10-18

## Scope And Result

Examined upstream commit `8bd0f2b210231da3d44bd10cc837d7cd5825b4cf`,
its LICENSE/NOTICE/README and representative headers, together with the port's
licence declarations, linked dependencies and binary packaging. This report began as a source/distribution audit. The approved adoption update
below supersedes its earlier pending-migration findings. No commit, push or
release is performed by this activity.

The upstream transition is implemented by the adoption update below. The user
retains SM2-Emu Libretro as the distinct distributed project name. A lone
LICENSE replacement would leave contradictory headers, metadata and packages.
This report records the author's stated terms and implementation consequences;
it does not adjudicate the enforceability of individual additional terms.

## Upstream Terms

Upstream LICENSE is the GNU GPL version 3 text; the project's NOTICE specifies
GPL-3.0-or-later plus additional terms under section 7:

- Preserve copyright/author credits in source, NOTICE and the About screen or
  an equivalent place reachable by users of a program without an About screen.
- Identify modified versions as modified, state the sm2-emu origin and link to
  `https://github.com/dmanlfc/sm2-emu` in source and the equivalent user notice.
- Use a distinct name for a distributed modified version. The NOTICE exempts
  unmodified builds and changes limited to platform build/package/install work.
  The Libretro adapter and behavioral additions extend beyond that exemption.
- MAME-derived portions retain BSD-3-Clause notices. Upstream marks combined
  files `GPL-3.0-or-later AND BSD-3-Clause` and supplies LICENSES/BSD-3-Clause.txt.

Crucially, NOTICE says releases after v0.9.50 and subsequent work use the new
terms; earlier releases keep their published terms, including source headers.
The adopted relicensing commit supplies the new notices for imported code;
the approved migration removes the superseded author restrictions while
preserving MAME and component notices and prior source history. Earlier
published artifacts retain their original terms.

The official GPL text's sections 5–7 describe modified-source notices,
corresponding-source delivery and additional terms. The upstream NOTICE is
the source for the project-specific name condition; do not attribute that
wording to the GPL alone. References:

- [Upstream relicensing commit](https://github.com/dmanlfc/sm2-emu/commit/8bd0f2b210231da3d44bd10cc837d7cd5825b4cf)
- [Upstream NOTICE at the reviewed commit](https://github.com/dmanlfc/sm2-emu/blob/8bd0f2b210231da3d44bd10cc837d7cd5825b4cf/NOTICE)
- [GNU GPL v3](https://www.gnu.org/licenses/gpl.en.html)

## Initial Port Findings (Before Adoption)

| Area | Finding / Required Migration |
| --- | --- |
| LICENSE / NOTICE | Both still describe BSD-3-Clause. Adopt the upstream GPL text and additional NOTICE terms together; retain port modifications and third-party provenance explicitly. |
| Source headers | 119 tracked files under src/cmake/shaders and top-level CMakeLists contain the legacy commercial-use restriction. Map each imported file to its upstream notice; do not blanket-remove third-party notices or relicense MAME originals. Port-only BSD files may retain their own notices as components of the combined distribution. |
| Identity | Current display/documentation name SM2-Emu Libretro derives directly from the upstream name. The user subsequently confirmed SM2-Emu Libretro as the distinct name; no further rename is required. Do not rename technical option keys, SRAM identifiers or system paths merely to rename the display/project identity. |
| User-visible attribution | README already identifies an independent port and links upstream. Ensure equivalent credits, modified-version statement and link are reachable in the frontend experience as requested by NOTICE; a packaged text file alone is not proof of runtime reachability. |
| Core metadata | sm2_libretro.info still declares BSD-3-Clause. Update the combined licence label consistently with the adopted licence and retained component notices. |
| CI packaging | .github/workflows/libretro-ci.yml copies the current LICENSE/NOTICE; update it to include the GPL and retained BSD text and all linked-component notices. |
| Package validator | scripts/check-libretro-package.py hardcodes the BSD metadata and an exact 15-file set. Update the expected licence and inventory with the packaging change. Existing whitelist success does not establish licence completeness. |
| Matching source | SOURCE_COMMIT.txt records the repository revision. For GPL binaries, make corresponding source and build scripts available with the required delivery method, including pinned submodule source. A plain GitHub source archive omits submodule contents; do not call it a complete source bundle without resolving that. Prefer an accompanying complete source bundle for each release. |
| Documentation | Update README, CI/release instructions and current assertions together. Preserve historical reports as historical evidence rather than rewriting their past results. |

### Linked Dependencies

The inspected component notices are permissive: Musashi/miniz/pugixml/ImGui
and VulkanMemoryAllocator use MIT-family notices; ymfm and MAME-derived code
retain BSD-3-Clause notices; the used LZMA SDK decompression code is public
domain; the Libretro API notice is retained separately. No conflicting
noncommercial dependency condition was identified in those inspected notices.
This is not an audit of every transitive OS/driver library on all platforms.
SDL device/window ownership is excluded from the Libretro core target; do not
copy the standalone application's dependency list as a core package inventory.

**Concrete existing packaging omission:** src/libretro/CMakeLists.txt links
sm2_libretro_imgui, but CI packaging and the exact-file validator omit
3rdparty/imgui/LICENSE.txt. NOTICE contains no ImGui licence text. Add that MIT
notice to binary packages regardless of whether GPL migration is undertaken.
Other bundled/generated dependencies and platform imports must remain in the
final release inventory; no system Vulkan/MoltenVK replacement is requested.

## Approved Adoption And Verification

The user accepted **SM2-Emu Libretro** as the distinct distributed name and
requested completion on 2026-10-18. No further naming decision blocks this work.

- Imported LICENSE and BSD text from `8bd0f2b`; retained upstream NOTICE plus
  modified-port identification, repository links and the existing GTX credits.
  The existing lowercase `licenses/` directory stores BSD-3-Clause.txt to avoid
  a case-only duplicate on macOS. Historical source/releases are preserved.
- Applied corresponding upstream SPDX identifiers and author notices to the
  files present in this port. MAME combined identifiers remain GPL AND BSD;
  port-only permissive files and dependency copyrights remain intact. A final
  scan finds no obsolete commercial-use restriction in owned source/build files.
- Core-info metadata declares GPL-3.0-or-later, the modified version, upstream
  copyright/origin/link and packaged full terms. The displayed project name is
  SM2-Emu Libretro; corename, runtime library name, binary, option/save and
  system identifiers are preserved to avoid breaking established frontend paths.
  Attribution is exposed through the frontend's Core Information notes.
- Added the missing ImGui MIT text and retained BSD text to binary packaging.
  Updated README, CI instructions, submission draft and the package verifier.
- Added `scripts/package-libretro-source.py`. CI creates a complete source
  archive with seven recursively pinned, clean submodules and no Git metadata.
  The archive records every source hash and pin. Every binary package identifies
  the matching archive by name/revision/SHA-256 in SOURCE.json. Tagged-release
  assembly publishes source beside binaries. Dirty snapshots are explicitly
  local-only and fail the normal release gate.
- Source/package verification checks archive hashes, inventory, per-file hashes,
  submodule payload presence and exact licence/info/database correspondence.
  Negative checks cover dirty-release refusal and altered/missing source data.
- Package validation exposed two `--` separators inside an upstream XML comment.
  Replaced only those separators with em dashes; strict XML parsing now passes.
  No game element, attribute or runtime mapping changed.

Evidence is retained under `build-libretro-gpu/validation/licence-20261018/`.
The local source snapshot is marked dirty because earlier approved changes are
uncommitted; it is not a releasable committed artifact. The CI release path must
run on the approved clean commit when publication is requested. CI execution
on all platforms and external publication are not claimed by this local check.
No new gameplay or physical-controller qualification is implied by this work.
