#!/usr/bin/env python3
"""Inject CONFIG_DISPLAY_BUILD=y into build.sh before make ${MAKE_GOALS}."""

import sys

BUILD_SH = "build/build.sh"

# We need to inject CONFIG_DISPLAY_BUILD=y into .config AFTER all olddefconfig
# calls but BEFORE make ${MAKE_GOALS}. CONFIG_DISPLAY_BUILD is not a Kconfig
# symbol, so olddefconfig strips it. We add it right before the final make.
#
# Also inject CONFIG_DRM_MSM=y and sub-configs so auto.conf includes them.

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

if "Injecting display config" in src:
    print("Already injected, skipping")
    sys.exit(0)

# Anchor: the line right before make ${MAKE_GOALS}
# In build.sh, this is:
#   (cd ${OUT_DIR} && make -s O=${OUT_DIR} "${TOOL_ARGS[@]}" "${MAKE_ARGS[@]}" ${MAKE_GOALS})
ANCHOR = "(cd ${OUT_DIR} && make -s O=${OUT_DIR}"

if ANCHOR not in src:
    print(f"ERROR: anchor not found in {BUILD_SH}", file=sys.stderr)
    sys.exit(1)

inject_lines = [
    '    # Inject display driver config after all olddefconfig calls',
    '    echo "=== Injecting display config ==="',
]
for cfg in DISPLAY_CONFIGS:
    key = cfg.split('=')[0]
    inject_lines.append(f'    if grep -q "^{key}=" "${{OUT_DIR}}/.config" 2>/dev/null; then')
    inject_lines.append(f'      sed -i "s|^{key}=.*|{cfg}|" "${{OUT_DIR}}/.config"')
    inject_lines.append(f'    elif grep -q "^# {key} is not set" "${{OUT_DIR}}/.config" 2>/dev/null; then')
    inject_lines.append(f'      sed -i "s|^# {key} is not set|{cfg}|" "${{OUT_DIR}}/.config"')
    inject_lines.append(f'    else')
    inject_lines.append(f'      echo "{cfg}" >> "${{OUT_DIR}}/.config"')
    inject_lines.append(f'    fi')
inject_lines.append('    # Force regenerate auto.conf with new configs')
inject_lines.append('    (cd ${OUT_DIR} && make -s "${TOOL_ARGS[@]}" O=${OUT_DIR} "${MAKE_ARGS[@]}" syncconfig)')
inject_lines.append('    echo "=== Display config injected ==="')
inject_lines.append('')

inject_block = '\n'.join(inject_lines)

# Insert before the ANCHOR line
src = src.replace(ANCHOR, inject_block + '    ' + ANCHOR, 1)

with open(BUILD_SH, "w") as f:
    f.write(src)

print(f"Injected display config into {BUILD_SH}")
