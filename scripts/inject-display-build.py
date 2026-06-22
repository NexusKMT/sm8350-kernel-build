#!/usr/bin/env python3
"""Inject display driver config into .config before the final make."""

import sys
import os

# Display config symbols to inject into .config
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

BUILD_SH = "build/build.sh"

# Find the .config path from build.sh
# It's ${OUT_DIR}/.config where OUT_DIR is set by _setup_env.sh
# We inject after the POST_DEFCONFIG_CMDS eval (which runs olddefconfig)
# and before the LTO olddefconfig.

ANCHOR = "eval ${POST_DEFCONFIG_CMDS}"

with open(BUILD_SH) as f:
    src = f.read()

if ANCHOR not in src:
    print(f"ERROR: anchor '{ANCHOR}' not found in {BUILD_SH}", file=sys.stderr)
    sys.exit(1)

if "Injecting display config" in src:
    print("Already injected, skipping")
    sys.exit(0)

# Inject after the POST_DEFCONFIG_CMDS eval
inject_lines = [
    '    # Inject display driver config into .config',
    '    echo "=== Injecting display config ==="',
]
for cfg in DISPLAY_CONFIGS:
    inject_lines.append(f'    grep -q "^{cfg}$" "${{OUT_DIR}}/.config" 2>/dev/null || echo "{cfg}" >> "${{OUT_DIR}}/.config"')
inject_lines.append('    # Remove "not set" lines for our configs')
for cfg in DISPLAY_CONFIGS:
    key = cfg.split('=')[0]
    inject_lines.append(f'    sed -i "/^# {key} is not set$/d" "${{OUT_DIR}}/.config"')
inject_lines.append('    (cd ${OUT_DIR} && make -s "${TOOL_ARGS[@]}" O=${OUT_DIR} "${MAKE_ARGS[@]}" olddefconfig)')
inject_lines.append('    echo "=== Display config injected ==="')

inject_block = '\n'.join(inject_lines) + '\n'

# Insert after the eval line
src = src.replace(
    ANCHOR + '\n',
    ANCHOR + '\n' + inject_block,
    1
)

with open(BUILD_SH, "w") as f:
    f.write(src)

print(f"Injected display config into {BUILD_SH}")
