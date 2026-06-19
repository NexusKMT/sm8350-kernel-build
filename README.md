# sm8350-kernel-build

Lean CI harness that builds the upstream [LineageOS OnePlus SM8350](https://github.com/LineageOS/android_kernel_oneplus_sm8350) kernel (`lineage-18.1`, msm-5.4 / lahaina).

- **Defconfig:** `vendor/lahaina-qgki_defconfig`
- **Toolchain:** AOSP Clang `r383902` (11.0.1, the one `build.config.common` declares) + GCC 4.9 aarch64 cross
- **ccache:** enabled, pinned build timestamp for determinism (~79% hot-run hit rate)
- **Outputs:** the kernel `Image` as an artifact

Runs on push to `main` and via `workflow_dispatch`.
