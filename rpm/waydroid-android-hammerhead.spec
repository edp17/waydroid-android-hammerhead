Name:           waydroid-android-hammerhead
Version:        0.3.2
Release:        1
Summary:        Android-side Hammerhead compatibility payload for Waydroid
License:        Apache-2.0 AND BSD-3-Clause AND MIT
URL:            https://github.com/edp17/waydroid-android-hammerhead
ExclusiveArch:  armv7hl

Source0:        %{name}-%{version}.tar.gz

BuildRequires:  systemd

Requires:       waydroid >= 1.4.3
Requires:       waydroid-config-hammerhead >= 0.3.0
Requires:       droid-hal-hammerhead
Requires:       lxc >= 5.0.3
Requires:       python3-base
Requires:       e2fsprogs

%description
Android-side compatibility integration for Waydroid on the LG Nexus 5
(hammerhead) Sailfish OS adaptation.

The package ships the verified redistributable Android compatibility payload
and installs the validated Hammerhead integration directly into the pinned
Android images while Waydroid is stopped. system.img is not resized; vendor.img
is expanded by exactly 128 MiB. Proprietary Qualcomm graphics/JPEG/GNSS files
are not included in the RPM; they are derived locally from the installed
Hammerhead adaptation and from a checksum-pinned graphics archive supplied by
the device owner. The package also provides waydroid-hammerhead-setup for the
fully verified first-time image bootstrap and preparation.

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
install -D -m 0644 payload/system/netd.rc \
    %{buildroot}%{_datadir}/%{name}/system/netd.rc
install -D -m 0644 payload/system/waydroid-netd-direct-connect.sh \
    %{buildroot}%{_datadir}/%{name}/system/waydroid-netd-direct-connect.sh

install -D -m 0755 scripts/prepare \
    %{buildroot}%{_libexecdir}/%{name}/prepare
install -D -m 0755 scripts/setup \
    %{buildroot}%{_sbindir}/waydroid-hammerhead-setup

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
install -D -m 0644 sources/final-system-delta.txt \
    %{buildroot}%{_docdir}/%{name}/final-system-delta.txt


%preun
if [ "$1" -eq 0 ]; then
    %{_libexecdir}/%{name}/prepare --remove || :
fi


%files
%license LICENSES/Apache-2.0.txt
%license LICENSES/BSD-3-Clause.txt
%license LICENSES/MIT.txt
%{_datadir}/%{name}/open-payload.tar.gz
%{_datadir}/%{name}/open-payload.sha256
%{_datadir}/%{name}/system/netd.rc
%{_datadir}/%{name}/system/waydroid-netd-direct-connect.sh
%{_libexecdir}/%{name}/prepare
%{_sbindir}/waydroid-hammerhead-setup
%dir %{_sysconfdir}/waydroid-extra/hammerhead/proprietary
%doc %{_docdir}/%{name}/provenance.txt
%doc %{_docdir}/%{name}/repository-state.txt
%doc %{_docdir}/%{name}/source-diffs.patch
%doc %{_docdir}/%{name}/pinned-images.txt
%doc %{_docdir}/%{name}/final-system-delta.txt
