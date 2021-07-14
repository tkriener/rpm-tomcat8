# To Build:
#
# vagrant up / vagrant provision
#

%define __jar_repack %{nil}
%define tomcat_home /usr/share/tomcat8
%define tomcat_group tomcat8
%define tomcat_user tomcat8
%define tomcat_user_home /var/lib/tomcat8
%define tomcat_cache_home /var/cache/tomcat8

Summary:    Apache Servlet/JSP Engine, RI for Servlet 3.1/JSP 2.3 API
Name:       tomcat8
Version:    8.5.69
BuildArch:  noarch
Release:    0
License:    Apache Software License
Group:      Networking/Daemons
URL:        http://tomcat.apache.org/
Source0:    apache-tomcat-%{version}.tar.gz
Source1:    %{name}.service
Source2:    %{name}.sh
Source3:    %{name}.logrotate
Source4:    %{name}.conf
Requires:   java
Requires:   jpackage-utils
Requires:   policycoreutils-python
BuildRoot:  %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Tomcat is the servlet container that is used in the official Reference
Implementation for the Java Servlet and JavaServer Pages technologies.
The Java Servlet and JavaServer Pages specifications are developed by
Sun under the Java Community Process.

Tomcat is developed in an open and participatory environment and
released under the Apache Software License. Tomcat is intended to be
a collaboration of the best-of-breed developers from around the world.
We invite you to participate in this open development project. To
learn more about getting involved, click here.

This package contains the base tomcat installation that depends on Oracle JDK and not
on JPP packages.

%prep
%setup -q -n apache-tomcat-%{version}

%build

%install
install -d -m 755 %{buildroot}/%{tomcat_home}/
cp -R * %{buildroot}/%{tomcat_home}/

# Remove all webapps. Put webapps in /var/lib and link back.
rm -rf %{buildroot}/%{tomcat_home}/webapps
install -d -m 775 %{buildroot}%{tomcat_user_home}/webapps
cd %{buildroot}/%{tomcat_home}/
ln -s %{tomcat_user_home}/webapps webapps
chmod 775 %{buildroot}/%{tomcat_user_home}
cd -

# Remove *.bat
rm -f %{buildroot}/%{tomcat_home}/bin/*.bat

# Remove extra logging configs
sed -i -e '/^3manager/d' -e '/\[\/manager\]/d' \
    -e '/^4host-manager/d' -e '/\[\/host-manager\]/d' \
    -e '/^java.util.logging.ConsoleHandler/d' \
    -e 's/, *java.util.logging.ConsoleHandler//' \
    -e 's/, *4host-manager.org.apache.juli.AsyncFileHandler//' \
    -e 's/, *3manager.org.apache.juli.AsyncFileHandler//' \
    %{buildroot}/%{tomcat_home}/conf/logging.properties

# Put logging in /var/log and link back.
rm -rf %{buildroot}/%{tomcat_home}/logs
install -d -m 755 %{buildroot}/var/log/%{name}/
cd %{buildroot}/%{tomcat_home}/
ln -s /var/log/%{name}/ logs
cd -

# Put conf in /etc/ and link back.
install -d -m 755 %{buildroot}/%{_sysconfdir}
mv %{buildroot}/%{tomcat_home}/conf %{buildroot}/%{_sysconfdir}/%{name}
cd %{buildroot}/%{tomcat_home}/
ln -s %{_sysconfdir}/%{name} conf
cd -

# Create Catalina in /etc
install -d -m 755 %{buildroot}/%{_sysconfdir}/%{name}/Catalina

# Put temp and work to /var/cache and link back.
install -d -m 775 %{buildroot}%{tomcat_cache_home}
mv %{buildroot}/%{tomcat_home}/temp %{buildroot}/%{tomcat_cache_home}/
mv %{buildroot}/%{tomcat_home}/work %{buildroot}/%{tomcat_cache_home}/
cd %{buildroot}/%{tomcat_home}/
ln -s %{tomcat_cache_home}/temp
ln -s %{tomcat_cache_home}/work
chmod 775 %{buildroot}/%{tomcat_cache_home}/temp
chmod 775 %{buildroot}/%{tomcat_cache_home}/work
cd -

# Create PID-Dir
install -d -m 755 %{buildroot}/var/run/%{name}

# Drop systemd file
install -d -m 755 %{buildroot}/%{_unitdir}
install    -m 744 %_sourcedir/%{name}.service %{buildroot}/%{_unitdir}/%{name}.service

# Drop conf script
install    -m 644 %_sourcedir/%{name}.conf %{buildroot}/%{_sysconfdir}/%{name}

# Drop logrotate script
install -d -m 755 %{buildroot}/%{_sysconfdir}/logrotate.d
install    -m 644 %_sourcedir/%{name}.logrotate %{buildroot}/%{_sysconfdir}/logrotate.d/%{name}

%clean
rm -rf %{buildroot}

%pre
getent group %{tomcat_group} >/dev/null || groupadd -r %{tomcat_group}
getent passwd %{tomcat_user} >/dev/null || /usr/sbin/useradd --comment "Tomcat 8 Daemon User" --shell /bin/bash -M -r -g %{tomcat_group} --home %{tomcat_home} %{tomcat_user}

%files
%defattr(-,%{tomcat_user},%{tomcat_group})
/var/log/%{name}/
/var/run/%{name}/
%defattr(-,root,root)
%{tomcat_user_home}
%{tomcat_home}
%{_unitdir}/%{name}.service
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%defattr(-,root,%{tomcat_group})
%{tomcat_cache_home}
%{tomcat_cache_home}/temp
%{tomcat_cache_home}/work
%{tomcat_user_home}/webapps
%config(noreplace) %{_sysconfdir}/%{name}/*
%defattr(-,%{tomcat_user},%{tomcat_group})
%{_sysconfdir}/%{name}/Catalina

%post
semanage fcontext -a -t tomcat_exec_t '%{tomcat_home}/bin(/.*)?\.sh' 2>/dev/null || :
restorecon -R %{tomcat_home}/bin || :
semanage fcontext -a -t tomcat_unit_file_t '%{_unitdir}/%{name}.service' 2>/dev/null || :
restorecon -R %{_unitdir}/%{name}.service || :
semanage fcontext -a -t tomcat_var_lib_t '%{tomcat_user_home}(/.*)?' 2>/dev/null || :
restorecon -R %{tomcat_user_home} || :
semanage fcontext -a -t tomcat_cache_t '%{tomcat_cache_home}(/.*)?' 2>/dev/null || :
restorecon -R %{tomcat_cache_home} || :
semanage fcontext -a -t tomcat_log_t '/var/log/%{name}(/.*)?' 2>/dev/null || :
restorecon -R /var/log/%{name} || :
semanage fcontext -a -t tomcat_run_t '/var/run/%{name}(/.*)?' 2>/dev/null || :
restorecon -R /var/run/%{name} || :
semanage fcontext -a -t tomcat_cache_t '%{_sysconfdir}/%{name}/Catalina(/.*)?' 2>/dev/null || :
restorecon -R %{_sysconfdir}/%{name}/Catalina || :
# install but don't activate
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
if [ $1 -eq 0 ] ; then  # final removal
  semanage fcontext -d -t tomcat_exec_t '%{tomcat_home}/bin(/.*)?\.sh' 2>/dev/null || :
  semanage fcontext -d -t tomcat_unit_file_t '%{_unitdir}/%{name}.service' 2>/dev/null || :
  semanage fcontext -d -t tomcat_var_lib_t '%{tomcat_user_home}(/.*)?' 2>/dev/null || :
  semanage fcontext -d -t tomcat_cache_t '%{tomcat_cache_home}(/.*)?' 2>/dev/null || :
  semanage fcontext -d -t tomcat_log_t '/var/log/%{name}(/.*)?' 2>/dev/null || :
  semanage fcontext -d -t tomcat_run_t '/var/run/%{name}(/.*)?' 2>/dev/null || :
  semanage fcontext -d -t tomcat_cache_t '%{_sysconfdir}/%{name}/Catalina(/.*)?' 2>/dev/null || :
fi
%systemd_postun_with_restart %{name}.service

%changelog
* Tue Jul 13 2021 Thomas Kriener <thomas@kriener.de> - 8.5.69-0
- Use tomcat 8.5.69
- Security Fix

* Tue Mar 2 2020 Thomas Kriener <thomas@kriener.de> - 8.5.51-0
- Use tomcat 8.5.51
- Security Fix

* Tue Jun 18 2019 Thomas Kriener <thomas@kriener.de> - 8.5.42-0
- Use tomcat 8.5.42
- add /etc/tomcat8/Catalina as Base for $CATALINA_BASE/conf/[enginename]

* Fri Mar 22 2019 Thomas Kriener <thomas@kriener.de> - 8.0.53-3
- Rework systemd to prevent enabling if disabled before
- Don't replace logrotate-file on update

* Thu Mar 21 2019 Thomas Kriener <thomas@kriener.de> - 8.0.53-2
- Fix systemd-file to create /var/run/tomcat8 automatically

* Tue Oct 16 2018 Initial Version for RHEL7 with systemd - 8.0.53-1
- 8.0.53
