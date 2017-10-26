%define name    drbdlinks
%define version 1.27
%define release 1
%define prefix  %{_prefix}

Summary:       A program for managing links into a DRBD shared partition.
Name:          %{name}
Version:       %{version}
Release:       %{release}
License:       GPLv2
Group:         Applications/System
URL:           http://www.tummy.com/krud/
Source:        %{name}-%{version}.tar.gz
Packager:      Sean Reifschneider <jafo@tummy.com>
BuildRoot:     /var/tmp/%{name}-root
Requires:      python
BuildArch:     noarch

%description
drbdlinks is a program which manages links into a DRBD partition which is
shared among several machines.  A simple configuration file,
"/etc/drbdlinks.conf", specifies the links.  This can be used to manage
links for /etc/httpd, /var/lib/pgsql, and other system directories that
need to appear as if they are local to the system when running applications
after a drbd shared partition has been mounted.

When run with "start" as the mode, drbdlinks will rename the existing
files/directories, and then make symbolic links into the DRBD partition.
"stop" does the reverse.  By default, the rename appends ".drbdlinks" to
the name, but this can be overridden.

An init script is included which runs "stop" before heartbeat starts, and
after heartbeat stops.  This is done to try to ensure that when the shared
partition isn't mounted, the links are in their normal state.

%prep
%setup
%build

%install
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf "$RPM_BUILD_ROOT"

#  make directories
mkdir -p "$RPM_BUILD_ROOT"/etc//init.d/
mkdir -p "$RPM_BUILD_ROOT"/etc/ha.d/resource.d/
mkdir -p "$RPM_BUILD_ROOT"/usr/lib/ocf/resource.d/tummy/
mkdir -p "$RPM_BUILD_ROOT"/usr/sbin/
mkdir -p "$RPM_BUILD_ROOT"/var/lib/drbdlinks/configs-to-clean
mkdir -p "%{buildroot}/%{_mandir}"/man8

#  copy over files
cp drbdlinks "$RPM_BUILD_ROOT"/usr/sbin/
ln -s ../../../usr/sbin/drbdlinks "$RPM_BUILD_ROOT"/etc/ha.d/resource.d/drbdlinks
ln -s ../../../../sbin/drbdlinks "$RPM_BUILD_ROOT"/usr/lib/ocf/resource.d/tummy/drbdlinks
cp drbdlinks.conf "$RPM_BUILD_ROOT"/etc/
cp drbdlinksclean.init "$RPM_BUILD_ROOT"/etc/init.d/drbdlinksclean
cp drbdlinks.8 "%{buildroot}/%{_mandir}"/man8

%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf "$RPM_BUILD_ROOT"

%post
chkconfig --add drbdlinksclean

%preun
chkconfig --del drbdlinksclean

%files
%defattr(-,root,root)
/usr/sbin/drbdlinks
/etc/init.d/drbdlinksclean
/etc/ha.d/resource.d/drbdlinks
/usr/lib/ocf/resource.d/tummy
%dir /var/lib/drbdlinks/configs-to-clean
%config /etc/drbdlinks.conf
%doc README.markdown LICENSE
%{_mandir}/man8/*
