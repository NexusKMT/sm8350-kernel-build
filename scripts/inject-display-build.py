#!/usr/bin/env python3
"""Inject CONFIG_DISPLAY_BUILD=y into build.sh after ALL olddefconfig calls."""

import sys

BUILD_SH = "build/build.sh"

# We need to inject CONFIG_DISPLAY_BUILD=y into .config AFTER the last
# olddefconfig call (which is in the LTO section). This is a non-Kconfig
# symbol that olddefconfig strips, so it must be added after all config
# processing is done.
#
# Also inject CONFIG_DRM_MSM=y (which IS a Kconfig symbol but might be
# cleared by olddefconfig if its dependencies aren't met).

DISPLAY_CONFIGS = [
    "CONFIG_DISPLAY_BUILD=y",
    "CONFIG_DRM_MSM=y",
    "CONFIG_DRM_MSM_SDE=y",
    "CONFIG_DRM_MSM_DSI=y",
    "CONFIG_DRM_MSM_DP=y",
    "CONFIG_DRM_MSM_DP_MST=y",
    "CONFIG_DRM_SDE_WB=y",
    "CONFIG_DRM_SDE_RSC=y",
    "CONFIG_DRM_SDE_VM=y",
    "CONFIG_DSI_PARSER=y",
]

with open(BUILD_SH) as f:
    src = f.read()

if "Injecting display config after LTO" in src:
    print("Already injected, skipping")
    sys.exit(0)

# Find the LAST olddefconfig call (in the LTO section)
# The LTO section looks like:
#   (cd ${OUT_DIR} && make -s "${TOOL_ARGS[@]}" O=${OUT_DIR} "${MAKE_ARGS[@]}" olddefconfig)
#   set +x
# We inject after the last "set +x" that follows an olddefconfig.

inject_lines = [
    '',
    '    # Inject display driver config after all olddefconfig calls',
    '    echo "=== Injecting display config after LTO ==="',
]
for cfg in DISPLAY_CONFIGS:
    inject_lines.append(f'    grep -q "^{cfg.split("=")[0]}=" "${{OUT_DIR}}/.config" 2>/dev/null \\')
    inject_lines.append(f'      && sed -i "s|^{cfg.split("=")[0]}=.*|{cfg}|" "${{OUT_DIR}}/.config" \\')
    inject_lines.append(f'      || echo "{cfg}" >> "${{OUT_DIR}}/.config"')
inject_lines.append('    echo "=== Display config injected ==="')

inject_block = '\n'.join(inject_lines) + '\n'

# Find the last "set +x" after olddefconfig in the LTO section
# Pattern: olddefconfig ... set +x ... fi
# We inject after the last "set +x" before the "fi" that closes the LTO block
last_set_plus_x = src.rfind('set +x')
if last_set_plus_x < 0:
    print("ERROR: 'set +x' not found", file=sys.stderr)
    sys.exit(1)

# Find the newline after "set +x"
newline_after = src.index('\n', last_set_plus_x)
src = src[:newline_after + 1] + inject_block + src[newline_after + 1:]

with open(BUILD_SH, "w") as f:
    f.write(src)

print(f"Injected display config into {BUILD_SH}")
