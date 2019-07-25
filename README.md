# GuardianKey SSH plugin

GuardianKey is a service that use AI (Artificial Intelligence) for increase security of logins. More info in https://guardiankey.io

This is a implementation of GuardianKey Auth Security Lite, that it free until 10 users. However, can be used in any GuardianKey versions. Info about this in https://guardiankey.io/services/guardiankey-auth-security-lite/


# Install

## Debian 9/Ubuntu 18.04

Just do download of .deb package and install with "apt" command. Example:

\# wget https://github.com/pauloangelo/guardiankey-ssh/raw/master/guardiankey-ssh_1.0-2.deb 

\# apt install ./guardiankey-ssh_1.0-2.deb

## RHEL/CentOS 7

You can install with this command:

\# yum install  https://github.com/pauloangelo/guardiankey-ssh/raw/master/guardiankey-ssh-1-0.noarch.rpm

# Configure

After install, you need create an account in GuardianKey. You can visit https://panel.guardiankey.io, or execute:

\# python /usr/lib/guardiankey/register.py

With your credencials, you should configure /etc/guardiankey/gk.conf. Finally, you starts the guardiankey-ssh service:

\# systemctl enable --now guardiankey-ssh




# Licence

This plugin is licencied by GNU/GPLv3.


