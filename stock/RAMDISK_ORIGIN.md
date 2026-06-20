# `stock/ramdisk.cpio.gz` — provenance

This is the **stock boot ramdisk**, extracted verbatim from the device's stock
`alpha_boot_a.img` using the **official AOSP `unpack_bootimg`** tool
(`platform/system/tools/mkbootimg`).

It is reused as-is when repacking a flashable boot.img — we swap only the
kernel (`Image`), never the ramdisk.

## How it was extracted

Via the `Parse stock boot.img` workflow (`parse-boot.yml`), which:

1. Downloads `alpha_boot_a.img` from the `stock-boot-template` release.
2. Runs `unpack_bootimg.py` (official) → emits `kernel` + `ramdisk`.
3. Uploads both as the `stock-boot-payload` artifact.

This file is the `ramdisk` from that artifact.

```
$ file stock/ramdisk.cpio.gz
gzip compressed data, from Unix  (8969915 bytes)
```

## Corresponding boot header parameters (used by build.yml `repack` job)

Captured by `unpack_bootimg --format=info` from the same image:

| Field | Value |
|---|---|
| header version | 3 |
| os version | 11.0.0 |
| os patch level | 2020-10 |
| cmdline | (empty) |

## AVB salt (used by build.yml `repack` job)

Captured by `avbtool info_image`:

```
884ddade7c249ddee8f6a5b05eeb04c6db23c08d9966acf0adfbaceacae173be
```

The stock vbmeta uses `Algorithm: NONE` (unsigned) but carries a sha256 hash
descriptor over the boot image. After swapping the kernel, build.yml re-runs
`avbtool add_hash_footer` with this salt + `NONE` so the bootloader's
integrity check passes.

## Re-deriving from source

If this file or the pinned parameters ever need refreshing, re-run
`parse-boot.yml` (workflow_dispatch) and re-download the `stock-boot-payload`
artifact.
