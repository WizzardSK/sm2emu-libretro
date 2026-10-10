# Upstream Texture Interpolation Package — 2026-10-08

## Scope and Adaptation

Imports the rendering fix from upstream
`277a4828ae01fe3d39e3aa3c6db2bbec42d7741e`: interpolate texture coordinates
across a whole convex polygon using its edge ring, instead of independently
across the triangles of a fan. This addresses texture warping along their
shared diagonal. The same shader serves Vulkan and OpenGL.

The full integrated baseline remains 0.9.13 (`5ddf84a`), with this explicit
backport and the preceding 68000 Save State fix (`1a60aff`). No submodule pins,
Core Option names, stored values or defaults changed.

- `PolyGeom` and its population/interpolation algorithm follow upstream.
- Both GPU passes allocate, upload, bind and destroy the new geometry buffer.
- Geometry retains upstream binding 5. Vulkan leaves binding 4 unused because
  the port has no replacement-texture atlas. Pool/layout/write counts follow
  the resources actually present in this port.
- Existing texture filtering, stipple, composition and frontend ownership are
  retained. No replacement-texture system was introduced.
- Upstream's standalone `--load-state` CLI addition in the same commit is not
  part of this renderer backport; Libretro has its own state interface.

## Verification

Evidence root: `/tmp/sm2-warp-package-20261008/`.

| Check | Result |
| --- | --- |
| macOS Release core, headless and standalone builds | Passed; Vulkan and OpenGL passes compiled |
| Linux x86_64 cached builder, core and EGL host | Passed using existing installed dependencies |
| VF2 Vulkan old/new, 1,800 native frames, 1× Faithful | Video changes; entire PCM is identical; 1,800 hardware frames and no duplicates |
| Pristine upstream `277a482`, Vulkan VF2, 1,800 frames | Exact RGB match with the updated port when automatic initial NVRAM setup is disabled in the test |
| Headless versus pristine upstream, VF2 1,800 frames | Software frame, PCM, NVRAM, frame/cycle and CPU checks passed |
| Vulkan 2×, anisotropic 16×, context recreation at frame 950 | Valid hardware frame after recreation; three load/reset/unload cycles passed |
| Mesa OpenGL ES and desktop OpenGL, VF2 1,800 frames each | Exact image, PCM and NVRAM match between these two paths |
| Installed core in RetroArch 1.22.2 macOS, Vulkan 2×/anisotropic 16× | 2,300 frames, gameplay screenshot inspected, non-silent recorded audio, 16,576-byte Save RAM and exit 0 |

The exact pristine-reference RGB digest is
`be4e59fcf05280013952da1af3729abe9147411f947573a0cb6dea454c6231de`.
`comparison.json` records the image and PCM comparisons. Old/new Vulkan PCM:
`c8712a45155e62031134b8f40ff7c455e716bbaaf77c8e76534db46559024391`.

The initial standalone/core captures reached different attract scenes because
the core seeds initial NVRAM. Both GPU runners now expose
`--initial-nvram-setup enabled|disabled` (default remains enabled), permitting
an aligned pristine comparison without changing user defaults.

Mesa and MoltenVK are not pixel-identical: 176 of 190,464 pixels differ in the
seeded VF2 capture. No cross-driver bit-exactness is claimed. The exact upstream
comparison uses the same Vulkan backend/host; OpenGL ES versus desktop uses the
same Mesa host. Timing figures include different build/load conditions and are
not a performance benchmark. This package does not establish catalog-wide or
Windows/Batocera gameplay coverage or subjective audio quality.

## Installed Artifacts

Both local RetroArch copies, `sm2_libretro.dylib` and `sm2_dev_libretro.dylib`,
were replaced atomically and their hashes checked against the final build:
`65f9726a084be1a7d354e4a25c4924dbbc9e9cff13db6939371c615d72ac59fa`.
Prior copies are backed up in `installed-backup` under the evidence root.
No commit or push was performed. The adjacent mainstream checkout was untouched;
pristine upstream was built from a Git archive with matching dependency pins.

## Remaining Rendering Work

Virtual-On water/texture timing, Top Skater geometry, shadow detail, higher
resolution and gun-flash integration remain in the roadmap. This report closes
only the texture-interpolation substep.
