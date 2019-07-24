Name:	guardiankey-ssh	
Version:	1
Release:	0
Summary:	GuardianKey plugin for SSH

License:	GNU/GPLv3
URL:		https://guardiankey.io
Source0:	guardiankey-ssh-1.tar.gz

Requires:	epel-release,python2-crypto,python-configparser

BuildArch:    noarch
BuildRoot:    %{_tmppath}/%{name}-buildroot

%description
 GuardiaKey is a service that use AI (Artificial Intelligence) for increase security of logins.
 This is a implementation of GuardianKey Auth Securuty Lite, that is free until 10 users. More info:
 https://guardiankey.io/services/guardiankey-auth-security-lite/

%prep
%setup -q

%install
mkdir -p $RPM_BUILD_ROOT
cp -R * $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/etc/cron.d/guardiankey
/etc/guardiankey/gk.conf
/etc/guardiankey/ssh.deny
/lib/systemd/system/guardiankey-ssh.service
/usr/lib/guardiankey/gkUnlock.py
/usr/lib/guardiankey/gkparser.py
/usr/lib/guardiankey/guardiankey.py
/usr/lib/guardiankey/register.py
/usr/lib/guardiankey/tail.py
/usr/lib/guardiankey/gkssh.py
/var/log/guardiankey-ssh.log
%exclude /usr/lib/guardiankey/*.pyc
%exclude /usr/lib/guardiankey/*.pyo
