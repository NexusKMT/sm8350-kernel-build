#!/usr/bin/env bash
# synthesize.sh — derive the verified-boot verdict from avbtool output.
# Reads out/avb_info.txt (produced by the official avbtool), writes out/avb_verdict.md.
# No guessing: every line below traces to a parsed field.
set -euo pipefail
cd "${GITHUB_WORKSPACE:-.}"

avb=out/avb_info.txt
[ -f "$avb" ] || { echo "avb_info.txt missing"; exit 1; }

get() { grep -m1 -E "^$1:" "$avb" | sed -E "s/^$1:[[:space:]]*//"; }

algorithm=$(get "Algorithm")
image_size=$(get "Image size" | head -1)
orig_size=$(awk '/^Original image size:/{print $4}' "$avb")
file_size=$(stat -c%s "out/${BOOT_ASSET:-alpha_boot_a.img}")
fingerprint=$(grep -m1 "com.android.build.boot.fingerprint ->" "$avb" | sed -E "s/.*-> '//;s/'$//")
os_ver=$(grep -m1 "com.android.build.boot.os_version ->" "$avb" | sed -E "s/.*-> '//;s/'$//")
patch=$(grep -m1 "com.android.build.boot.security_patch ->" "$avb" | sed -E "s/.*-> '//;s/'$//")
has_hash=$(grep -c "Hash descriptor" "$avb" || true)

# Algorithm NONE + hash descriptor present => integrity-checked but not signed.
if [ "$algorithm" = "NONE" ] && [ "$has_hash" -ge 1 ]; then
  verified_boot_note="**Verified-boot behavior:** vbmeta uses \`Algorithm: NONE\` — the boot image is **not cryptographically signed**, but a **sha256 hash descriptor IS present**. \
The bootloader does not verify a signature, yet it (typically) still checks the recorded hash against the image. \
Swapping the kernel changes the bytes covered by that hash, so a re-packed boot.img **must** either (a) be re-hashed (re-run \`avbtool add_hash_footer\`) so the descriptor matches, or (b) be flashed alongside a vbmeta partition that has verification disabled (\`--disable-verification\`). \
Flashing a re-packed image whose hash no longer matches, while leaving verification on, is a plausible cause of a black-screen no-boot."
elif [ "$algorithm" != "NONE" ]; then
  verified_boot_note="**Verified-boot behavior:** vbmeta uses \`Algorithm: $algorithm\` — the boot image **is signed**. A re-packed image would need re-signing with the OEM key (unavailable) or verification disabled on the device."
else
  verified_boot_note="**Verified-boot behavior:** no hash descriptor and algorithm \`NONE\` — image appears neither signed nor hashed."
fi

cat > out/avb_verdict.md <<EOF
## Verified-boot verdict (auto-derived from \`avbtool\` output)

| Field | Value |
|---|---|
| Build fingerprint | \`${fingerprint:-<none>}\` |
| OS version | ${os_ver:-?} |
| Security patch | ${patch:-?} |
| vbmeta algorithm | \`$algorithm\` |
| Hash descriptor | ${has_hash} present |
| Original image size | ${orig_size:-?} bytes |
| File size on disk | ${file_size:-?} bytes |
| AVB padding / footer | $(( ${file_size:-0} - ${orig_size:-0} )) bytes |

$verified_boot_note
EOF

cat out/avb_verdict.md
