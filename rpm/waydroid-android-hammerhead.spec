Name:           waydroid-android-hammerhead
Version:        0.2.0
Release:        1
Summary:        Android-side Hammerhead compatibility payload for Waydroid
License:        Apache-2.0 AND BSD-3-Clause AND MIT
URL:            https://github.com/edp17/waydroid-android-hammerhead
ExclusiveArch:  armv7hl

Source0:        %{name}-%{version}.tar.gz

BuildRequires:  systemd

Requires:       waydroid >= 1.4.3
Requires:       waydroid-config-hammerhead >= 0.2.0
Requires:       droid-hal-hammerhead
Requires:       lxc
Requires:       python3-base

%description
Android-side compatibility integration for Waydroid on the LG Nexus 5
(hammerhead) Sailfish OS adaptation.

The package ships the verified redistributable Android compatibility payload
and prepares image-derived runtime overlays without modifying system.img or
vendor.img. Proprietary Qualcomm graphics/JPEG/GNSS files are not included in
the RPM; they are derived locally from the installed Hammerhead adaptation and
from a checksum-pinned graphics archive supplied by the device owner.

The package also provides waydroid-hammerhead-setup, which downloads and
verifies the exact validated LineageOS 18.1 Android 11 Waydroid image pair,
initializes Waydroid through its preinstalled-image path, and prepares the
Hammerhead runtime without resizing or modifying either Android image.

%prep
%setup -q

%build
# Payload/preparation package. Android ELF modules were built and frozen from
# their audited Android 11 source trees; OBS packages the verified artifacts.

%install
install -D -m 0644 payload/open-payload.tar.gz \
    %{buildroot}%{_datadir}/%{name}/open-payload.tar.gz
install -D -m 0644 payload/open-payload.sha256 \
    %{buildroot}%{_datadir}/%{name}/open-payload.sha256

install -D -m 0755 scripts/prepare \
    %{buildroot}%{_libexecdir}/%{name}/prepare
install -D -m 0755 scripts/setup \
    %{buildroot}%{_sbindir}/waydroid-hammerhead-setup

install -D -m 0644 systemd/05-hammerhead-android-prepare.conf \
    %{buildroot}%{_unitdir}/waydroid-container.service.d/05-hammerhead-android-prepare.conf

install -d -m 0755 \
    %{buildroot}%{_sysconfdir}/waydroid-extra/hammerhead/proprietary

install -D -m 0644 sources/provenance.txt \
    %{buildroot}%{_docdir}/%{name}/provenance.txt
install -D -m 0644 sources/repository-state.txt \
    %{buildroot}%{_docdir}/%{name}/repository-state.txt
install -D -m 0644 sources/source-diffs.patch \
    %{buildroot}%{_docdir}/%{name}/source-diffs.patch
install -D -m 0644 sources/pinned-images.txt \
    %{buildroot}%{_docdir}/%{name}/pinned-images.txt

%post
systemctl daemon-reload || :
%{_libexecdir}/%{name}/prepare --defer-ok || :

%preun
if [ "$1" -eq 0 ]; then
    %{_libexecdir}/%{name}/prepare --remove || :
fi

%postun
systemctl daemon-reload || :

%files
%license LICENSES/Apache-2.0.txt
%license LICENSES/BSD-3-Clause.txt
%license LICENSES/MIT.txt
%{_datadir}/%{name}/open-payload.tar.gz
%{_datadir}/%{name}/open-payload.sha256
%{_libexecdir}/%{name}/prepare
%{_sbindir}/waydroid-hammerhead-setup
%dir %{_unitdir}/waydroid-container.service.d
%{_unitdir}/waydroid-container.service.d/05-hammerhead-android-prepare.conf
%dir %{_sysconfdir}/waydroid-extra/hammerhead/proprietary
%doc %{_docdir}/%{name}/provenance.txt
%doc %{_docdir}/%{name}/repository-state.txt
%doc %{_docdir}/%{name}/source-diffs.patch
%doc %{_docdir}/%{name}/pinned-images.txt
