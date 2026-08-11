# Waydroid Android compatibility package for Hammerhead

Final Android-side compatibility integration for Waydroid on the LG Nexus 5
(`hammerhead`) Sailfish OS adaptation.

## Scope

This package is the Android-side companion to `waydroid-config-hammerhead`.
Version 0.3.2 installs the validated Hammerhead compatibility payload directly
into the checksum-pinned Android 11 images while Waydroid is stopped.

The final image policy is deliberately narrow:

- `system.img` is never resized.
- `vendor.img` is expanded by exactly 128 MiB, from 162459648 to 296677376 bytes.
- there is no `/home/waydroid/hammerhead-runtime` overlay tree;
- there is no `config_android` LXC include;
- there is no per-container-start Android image preparer.

## Clean installation / pinned Android 11 images

Run as root after placing the exact proprietary graphics archive at:

```text
/etc/waydroid-extra/hammerhead/proprietary/hammerhead-lineage18.1-graphics-stage.tar.gz
SHA-256: 12b0ec5a17da018f80ab9ca6341950970e6683b56f28432d909f46d5e3aec4cd
```

Then run:

```sh
waydroid-hammerhead-setup
```

The helper pins these Waydroid images:

```text
lineage-18.1-20250510-VANILLA-waydroid_arm-system.zip
SHA-256: 33398fd5056c8e1391a88728e6bf0848cacbcb0bc66c7a8fe6634e7665d6025d

lineage-18.1-20250510-MAINLINE-waydroid_arm-vendor.zip
SHA-256: 9a40a4e28d2f22ca852709b1dd10e511323ff3b559524393af3c56d9b5aff7cc
```

and verifies the pristine extracted images before any modification:

```text
system.img
size: 1210585088
SHA-256: bc032c68d99078088244ede3fd1316fb600ff09cd36559a4f43964fbdd4d78ff

vendor.img
size: 162459648
SHA-256: 5f71b63344d22a1189a8de969137dd07b42edc5ac253545c7596fd0af1c04ec1
```

The images live under `/home/waydroid/images-lineage18.1-20250510/`; the
preinstalled-image paths under `/etc/waydroid-extra/images/` are symlinks to
those files.

The setup helper:

1. verifies the Hammerhead kernel configuration and Binder devices;
2. stops Waydroid;
3. downloads, verifies and extracts the pinned pristine images;
4. runs `waydroid init -f` through the preinstalled-image path;
5. pins the proven Android 11 metadata and Hammerhead Binder configuration;
6. applies `waydroid-config-hammerhead`;
7. invokes the one-time direct image preparer;
8. re-runs the host configurator so any legacy `config_android` include is removed;
9. verifies that system.img retained its stock size and vendor.img reached the exact final size;
10. leaves Waydroid stopped for the first controlled UI launch.

## Proven system.img delta

A complete filesystem comparison between the pristine pinned system image and
the known-working development image found no deletions and only four functional
changes. Version 0.3.2 reproduces exactly those changes:

```text
/system/lib/libEGL.so
  pristine: 2d40e33fd60cde37118a9e04e1fd9358f28205bd8efa39e7a9be5a1acec6f00e
  final:    d9ccd264653d2b1b0be206db9b56ed71f4e60cf6a362392b8a6122bdec824645

/system/lib/libsurfaceflinger.so
  pristine: 4a7bb90839543cc6d1b075e6c57bfce11d9dd13ea835cca27ee0132e999917bf
  final:    7e19b3f175267e3b97065f8da7ad36379749fbe48f612f8d40d74ec728fd3e8f

/system/etc/init/netd.rc
  final:    5fe93d766b98496e454f5d923c4662af795825b02f1d627ee57d92d8ebaa0ad4

/system/bin/waydroid-netd-direct-connect.sh
  final:    36818e6b0f7bd3287f7d67337875a428b088ef4e8c52881f4021db7ed9e783e7
```

`libEGL.so` and `libsurfaceflinger.so` are derived locally from the verified
pristine image with guarded instruction patches and final SHA verification.
The RPM does not redistribute those modified Android libraries.

The final SurfaceFlinger binary is derived from the pinned pristine binary
with six guarded byte-range patches:

```text
0x1164e0  2e    -> 38
0x1164e2  0024  -> 79a4
0x1164f8  0c9e  -> 0126
0x1166c8  00bf  -> 3830
0x1166cb  bf    -> 00
0x117bba  18b3  -> 23e0
```

The first five ranges reproduce the retained EGLConfig compatibility fixes.
The final `0x117bba` change forces the existing CPU fence-wait fallback.
Guard bytes and the complete final SHA-256 are verified before installation.

The final system deliberately does **not** install the old development
`gps.conf`/`flp.conf` copies and does **not** replace the Codec2 APEX utility.
The known-working system uses the pristine Codec2 utility SHA
`cfa508060fb0537c1baee3eb1b6eba0570127f86b864158a611a15d1203e35bb`.

## vendor.img

The vendor filesystem is expanded by exactly 128 MiB and receives the already
validated HWC, camera, gralloc, QOMX/JPEG, GNSS/QMI and Adreno payload directly.
Proprietary Qualcomm files are never distributed by this repository or RPM:
they are copied/derived locally and checksum-validated.

`vendor/build.prop` receives only:

```text
import /vendor/waydroid.prop
```

and the Hammerhead GNSS HIDL manifest is added to the existing VINTF tree.

## No loop-device mutation path

The preparer does not mount Android images and does not create loop devices.
It uses `debugfs` for ext4 file writes, and `e2fsck`/`resize2fs` only for the
vendor expansion and filesystem verification. This avoids the old Hammerhead
kernel's observed delayed loop-device detach behavior.

An interrupted preparation intentionally fails closed on the next run unless
the recorded image-state file and image hashes match. Re-extract the pinned
pristine images rather than trying to continue a partially modified image.

## Camera bridge

`waydroid-config-hammerhead` owns the host camera/qcamera mounts. This package
creates only the two Android-data symlinks:

```text
cam_socket1 -> host_qcamera/cam_socket1
cam_socket2 -> host_qcamera/cam_socket2
```

## Status

Read-only status:

```sh
waydroid-hammerhead-setup --status
/usr/libexec/waydroid-android-hammerhead/prepare --status
```

The direct preparer is normally invoked explicitly by
`waydroid-hammerhead-setup`; it is no longer an `ExecStartPre` hook.

## OBS

Push the source tree to GitHub, create/update `waydroid-android-hammerhead` in
the Hammerhead adaptation OBS project, and point `_service` at the exact tested
commit. The RPM itself is produced by OBS.