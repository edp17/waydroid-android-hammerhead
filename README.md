# waydroid-android-hammerhead

Final Android-side compatibility integration for Waydroid on the LG Nexus 5
(`hammerhead`) Sailfish OS adaptation.

## Scope

This package is the Android-side companion to `waydroid-config-hammerhead`. It
contains the final verified redistributable payload for HWC, camera, gralloc,
Codec2, clean QOMX, GNSS HIDL and networking, plus an idempotent runtime
preparer.

It does **not** rewrite `system.img` or `vendor.img`.  At container startup the
preparer builds `/home/waydroid/hammerhead-runtime` and writes
`/etc/waydroid-extra/hammerhead/config_android`; `waydroid-config-hammerhead`
then includes that LXC fragment.

## Proprietary material is deliberately not distributed

The GitHub/OBS source and RPM do not contain Qualcomm proprietary graphics,
legacy JPEG OMX or GNSS/QMI blobs.

JPEG and GNSS/QMI files are copied locally from the installed
`droid-hal-hammerhead` Android 5.1 adaptation and checksum-validated where a
production anchor is available.

The Adreno stack must be supplied locally as the exact archive:

```text
hammerhead-lineage18.1-graphics-stage.tar.gz
SHA-256: 12b0ec5a17da018f80ab9ca6341950970e6683b56f28432d909f46d5e3aec4cd
```

Preferred device location:

```text
/etc/waydroid-extra/hammerhead/proprietary/hammerhead-lineage18.1-graphics-stage.tar.gz
```

The preparer also accepts the exact archive from `/home/defaultuser/Downloads`
or `/home/defaultuser`.  The archive's `eglsubAndroid.so` is patched locally and
verified against the final production SHA.

## Image-derived files

The preparer mounts the user's own Waydroid images read-only, only while the
container is stopped.  It derives:

- `system/lib/libEGL.so`: two exact Hammerhead compatibility instruction
  patches; stock and final SHA-256 identities are enforced.
- `vendor/build.prop`: adds only `import /vendor/waydroid.prop`; stock and final
  SHA-256 identities are enforced.
- `system/apex/com.android.media.swcodec`: copies the complete 99-entry
  flattened APEX byte-for-byte and replaces only
  `lib/libsfplugin_ccodec_utils.so` with the verified NV21 fast-path build.
- `vendor/etc/vintf`: preserves the stock VINTF directory and adds only the
  Hammerhead GNSS HIDL manifest fragment.

No image is written.

## Camera bridge

`waydroid-config-hammerhead` owns the host `/dev/media*` and `/data` qcamera
mounts.  This package creates only the two required Android-data symlinks:

```text
cam_socket1 -> host_qcamera/cam_socket1
cam_socket2 -> host_qcamera/cam_socket2
```

## Networking

The open payload contains the final Stage98 netd capability workaround and the
Stage102 priority-23000 direct-connect service.  The obsolete static
`waydroid-hammerhead-netfix.sh` is intentionally not included.

The kernel-side `FRA_UID_RANGE` support remains part of the Hammerhead kernel
adaptation and is intentionally outside this RPM.

## Runtime preparation

Normally preparation happens automatically as an `ExecStartPre` of
`waydroid-container.service`, before the `waydroid-config-hammerhead` drop-in.
Manual inspection is available with:

```sh
/usr/libexec/waydroid-android-hammerhead/prepare --status
```

To prepare manually while Waydroid is stopped:

```sh
/usr/libexec/waydroid-android-hammerhead/prepare --ensure
```

The helper refuses to prepare over running/frozen Waydroid or over existing
Waydroid image loop attachments.

## OBS

Push this source tree to GitHub, create `waydroid-android-hammerhead` in the
Hammerhead adaptation OBS project, and point `_service` at an exact commit.
The RPM itself is produced by OBS; no locally built RPM is distributed.
