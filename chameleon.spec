Summary: Common schema transformation tool
Name: chameleon
Version: 0.1
Release: 6%{?dist}
Source0: https://fedorahosted.org/releases/c/h/%{name}/%{name}-%{version}.tar.gz
License: LGPLv3+
Group: Development/Libraries
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Requires: python >= 2.3 python-ply
Url: https://fedorahosted.org/chameleon

%description
Chameleon is a common to database specific schema transformation tool.

%define chameleon_home /usr/share/chameleon

%prep
%setup -q

%build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/%{_bindir}
mkdir -p $RPM_BUILD_ROOT/%{chameleon_home}
cp chameleon/*.py $RPM_BUILD_ROOT/%{chameleon_home}
install -m 0755 chameleon.bin $RPM_BUILD_ROOT/%{_bindir}/chameleon

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%dir %{chameleon_home}
%{chameleon_home}/*
%{_bindir}/chameleon

%doc LICENSE

%changelog
* Wed May 20 2009 jortel <jortel@redhat.com> - 0.1-6
- Rename to meet packaging guidelines.
* Tue May 5 2009 jortel <jortel@redhat.com> - 0.1-5
- Reduce output and refactor main.
* Mon May 4 2009 jortel <jortel@redhat.com> - 0.1-4
- Fix noparallel and logging.
* Mon May 4 2009 jortel <jortel@redhat.com> - 0.1-3
- Add include handling.
* Wed Apr 29 2009 jortel <jortel@redhat.com> - 0.1-2
- Fix optimizer bug.
* Tue Apr 28 2009 jortel <jortel@redhat.com> - 0.1-1
- 0.1
