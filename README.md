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


## Clean installation / pinned Android 11 images

Version 0.2.0 adds the explicit first-time bootstrap command:

```sh
waydroid-hammerhead-setup
```

Run it as `root` only after the exact proprietary Hammerhead graphics archive
has been placed at:

```text
/etc/waydroid-extra/hammerhead/proprietary/hammerhead-lineage18.1-graphics-stage.tar.gz
```

The setup helper pins the exact Waydroid images used by the Hammerhead port:

```text
lineage-18.1-20250510-VANILLA-waydroid_arm-system.zip
SHA-256: 33398fd5056c8e1391a88728e6bf0848cacbcb0bc66c7a8fe6634e7665d6025d

lineage-18.1-20250510-MAINLINE-waydroid_arm-vendor.zip
SHA-256: 9a40a4e28d2f22ca852709b1dd10e511323ff3b559524393af3c56d9b5aff7cc
```

It verifies the extracted stock files as:

```text
system.img
SHA-256: bc032c68d99078088244ede3fd1316fb600ff09cd36559a4f43964fbdd4d78ff

vendor.img
SHA-256: 5f71b63344d22a1189a8de969137dd07b42edc5ac253545c7596fd0af1c04ec1
```

The large images live under:

```text
/home/waydroid/images-lineage18.1-20250510/
```

and `/etc/waydroid-extra/images/system.img` and `vendor.img` are symlinks to
those files. This keeps the large Android images off the Sailfish root
filesystem while still using Waydroid 1.4.3's recognized preinstalled-image
path.

The helper then:

1. verifies the required Hammerhead kernel configuration and Binder devices;
2. stops Waydroid;
3. downloads/verifies/extracts the exact pinned Android 11 images;
4. runs `waydroid init -f` through `/etc/waydroid-extra/images`, preventing
   Waydroid from replacing the pinned images with current OTA images;
5. pins the proven Android 11 metadata:
   `system_datetime=1746887715`, `vendor_datetime=1746876991`;
6. enforces `puddlejumper`, `vndpuddlejumper`, `hwpuddlejumper` and
   `aidl3/aidl3`;
7. corrects only the three generated Binder mount sources in `config_nodes`;
8. runs `waydroid-config-hammerhead` and the Android runtime preparer;
9. re-verifies the complete `system.img` and `vendor.img` hashes; and
10. leaves Waydroid stopped for the first controlled UI launch.

No `system.img` or `vendor.img` resize is performed. The old development-time
vendor expansion is obsolete because all Hammerhead additions are supplied as
external read-only LXC bind mounts.

`--status` is read-only:

```sh
waydroid-hammerhead-setup --status
```

`--force` permits deliberate reinitialization of an existing Waydroid
configuration; it is not needed on a clean installation.

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
