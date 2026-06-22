#!/usr/bin/env python3
"""Inject display driver build into build.sh before make ${MAKE_GOALS}."""

import sys

BUILD_SH = "build/build.sh"

# Display driver build command with config overrides
DISPLAY_BUILD = '''\
    # Build display driver with command-line config overrides
    echo "=== Building display driver ==="
    make -s "${TOOL_ARGS[@]}" O="${OUT_DIR}" "${MAKE_ARGS[@]}" \\
      CONFIG_DISPLAY_BUILD=y CONFIG_DRM_MSM=y CONFIG_DRM_MSM_SDE=y \\
      CONFIG_DRM_MSM_DSI=y CONFIG_DRM_MSM_DP=y CONFIG_DRM_MSM_DP_MST=y \\
      CONFIG_DRM_SDE_WB=y CONFIG_DRM_SDE_RSC=y CONFIG_DRM_SDE_VM=y \\
      CONFIG_DSI_PARSER=y \\
      techpack/display/msm/built-in.a \\
      || echo "WARNING: display driver build failed, continuing"
    echo "=== Display driver build done ==="
'''

# Anchor: the line in build.sh that runs make ${MAKE_GOALS}
ANCHOR = "(cd ${OUT_DIR} && make -s O=${OUT_DIR}"

with open(BUILD_SH) as f:
    src = f.read()

if ANCHOR not in src:
    print(f"ERROR: anchor not found in {BUILD_SH}", file=sys.stderr)
    sys.exit(1)

if "Building display driver" in src:
    print("Already injected, skipping")
    sys.exit(0)

src = src.replace(ANCHOR, DISPLAY_BUILD + "    " + ANCHOR, 1)

with open(BUILD_SH, "w") as f:
    f.write(src)

print(f"Injected display driver build into {BUILD_SH}")
