%define name smeserver-update
Summary: Koozali SME Server rpm updater
Name: %{name}
%define version 11.0.0
%define release 8
Version: %{version}
Release: %{release}%{?dist}
License: GPL
Group: SMEServer/addon
Source: %{name}-%{version}.tar.xz

BuildRoot: /var/tmp/%{name}-%{version}-%{release}-buildroot
BuildArchitectures: noarch
Provides: smeserver-yum
Obsoletes: smeserver-yum < %{version}-%{release}
Requires: smeserver-formmagick
Requires: smeserver-base
Requires: perl(CGI::FormMagick) >= 0.91-26
Requires: python3-rpm 
Requires: distribution-gpg-keys
Requires: dnf 
Requires: dnf-automatic
Requires: python3-dnf-plugins-core
Requires: python3-dnf-plugin-post-transaction-actions
Requires: python3-dnf-plugin-versionlock
Requires: perl(File::Slurp)
Requires: mailx
BuildRequires: smeserver-devtools 
BuildRequires: python3
AutoReqProv: no

# Disable automatic bytecompilation. The python3 binary is not yet be
# available in /usr/bin when Python is built. Also, the bytecompilation fails	
# on files that test invalid syntax.	
%undefine py_auto_byte_compile

%description
%name is the Koozali SME Server updater based on dnf.

%prep
%setup

%build
perl createlinks
mkdir -p root/etc/yum.smerepos.d

%install
/bin/rm -rf $RPM_BUILD_ROOT
(cd root   ; /usr/bin/find . -depth -print | /bin/cpio -dump $RPM_BUILD_ROOT)
/bin/rm -f %{name}-%{version}-filelist
/sbin/e-smith/genfilelist \
    --file '/sbin/e-smith/dnf_update_dbs' 'attr(0700,root,root)' \
    --file '/sbin/e-smith/check4updates' 'attr(0755,root,root)' \
    --file '/sbin/e-smith/check4contribsupdates' 'attr(0755,root,root)' \
    --file '/sbin/e-smith/yumdownloadonly' 'attr(0755,root,root)' \
    --file '/etc/cron.daily/smeserver-update' 'attr(0700,root,root)' \
    --dir /var/log/dnf 'attr(2750,root,root)' \
    $RPM_BUILD_ROOT > %{name}-%{version}-%{release}-filelist

%clean
/bin/rm -rf $RPM_BUILD_ROOT

%files -f %{name}-%{version}-%{release}-filelist

%defattr(-,root,root)

%pre


%changelog
* Tue Apr 16 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-8.sme
- fix python error in dnf plugin [SME: 12631]

* Mon Apr 08 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-7.sme
- fix python error in dnf plugin [SME: 12601]
- fix server error in old manager [SME: 12602]

* Thu Apr 04 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-6.sme
- rewrite smeserver.py plugin [SME: 12113]
- fix migrate template 39VisibleSmeContribs, 45RockyEOL [SME: 12549]

* Thu Apr 04 2024 Brian Read <brianr@koozali.org> 11.0.0-5.sme
- Set license file to GPL2.0  [SME: 12577]

* Mon Mar 25 2024 Jean-Philippe Pialasse <jpp@koozali.org> 11.0.0-4.sme
- initial release of smeserver-update based on smeserver-yum [SME: 12114]
  * tidy centos repos, add rocky repos, add support for metalinks
  * tidy most references to yum (except manager), tidy config and templates
  * rename yum_** esmith db, except yum_repositories 
  * renamed yum.service to dnf.service
- adapt dnf with available plugins and new config [SME: 12527]
  * moved yum.conf to dnf.conf with deltarpm , fastestmirror support
  * add requirement for dnf post-transaction-actions
  * adapt setting for priorities
- yum-cron moved to dnf-automatic [SME: 12528]
- TODO smeserver.py plugin

* Sat Mar 23 2024 Brian Read <brianr@koozali.org> 11.0.0-2.sme
- Change Requires: e-smith- to Requires:smeserver-

* Sat Mar 23 2024 Brian Read <brianr@koozali.org> 11.0.0-1.sme
- Update Release and Version to base version and 1st release for SME11 [SME: 12518]

* Fri Mar 15 2024 Jean-Philippe Pialasse <jpp@koozali.org> 2.6.2-8.sme
- disable brp-python-bytecompile [SME: 12511]

* Thu Mar 14 2024 Jean-Philippe Pialasse <jpp@koozali.org> 2.6.2-7.sme
- use python 3 to build and python 2, as needed for brp-python-bytecompile
  https://bugzilla.redhat.com/show_bug.cgi?id=1411588

* Thu Oct 26 2023 cvs2git.sh aka Brian Read <brianr@koozali.org> 2.6.2-5.sme
- Roll up patches and move to git repo [SME: 12338]

* Thu Oct 26 2023 BogusDateBot
- Eliminated rpmbuild "bogus date" warnings due to inconsistent weekday,
  by assuming the date is correct and changing the weekday.

* Wed Aug 16 2023 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.2-4.sme
- remove initialize-default-databases and navigation-conf from yum-* events [SME: 12172]
- fix warning readline() on closed filehandle YUM_STATUS [SME: 12170]
- fix warning on uninitialized value in concatenation [SME: 12173]
- fix CSRF time-out during yum update [SME: 10926]
  now 10 minutes for this panel updated on last generation of a page

* Mon Feb 27 2023 Michel Begue <mab974@misouk.com> 2.6.2-3.sme
- fix reconfigure asked when not needed [SME: 12171]
- do not show reconfigure button and message if not needed [SME: 12209]

* Tue Nov 22 2022 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.2-2.sme
- set smecontribs enabled on new install [SME: 12179]

* Mon Jul 11 2022 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.2-1.sme
- bump version number
- no reboot for dbus-glib [SME: 12091]

* Tue Jun 14 2022 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.0-64.sme
- rephrase contrib update message [SME: 11543]
- move mysqld to mariadb in smeserver plugin [SME: 11921]

* Sun Apr 24 2022 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.0-63.sme
- remove force AutoInstallUpdates to disabled [SME: 11961]

* Sun Apr 17 2022 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.0-61.sme
- fix rotate yum.log as not standard location [SME: 11951]
- remove yum_update_dbs from messages log [SME: 11952]

* Tue Mar 08 2022 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.0-60.sme
- restart cvm-unix on cvm or bglibs update [SME: 11886]

* Mon Dec 20 2021 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.0-59.sme
- remove pop3 and pop3s services from plugin [SME: 11808]

* Thu Dec 09 2021 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.0-58.sme
- fix restarting spamd instead of spamassassin [SME: 11803]

* Fri Dec 03 2021 Brian Read <brianr@bjsystems.co.uk> 2.6.0-57.sme
- Re-word-reboot-required-message.patch [SME: 11790]

* Sun Nov 21 2021 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.0-56.sme
- fix wrong qpsmtpd handling [SME: 11768]

* Mon Jun 07 2021 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.0-55.sme
- add elrepo GPG key [SME: 11625]

* Mon May 31 2021 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.0-54.sme
- no reboot needed for systemd-python [SME: 11609]

* Tue Mar 30 2021 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.0-53.sme
- fix services stop on removal [SME: 11510]

* Tue Mar 30 2021 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.0-52.sme
- run navigation-conf when a panel is installed [SME: 11507]

* Sun Mar 21 2021 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.0-51.sme
- migrate back to normal CentOS mirrors after el6 EOL  [SME: 11477]
- version 2 with 
  deleting yum{eolversion} if for previous release or not yet eol
  better handling of conditions

* Wed Mar 17 2021 Jean-Philippe Pialasse <tests@pialasse.com> 2.6.0-49.sme
- avoid reboot on removal of smeserver-* rpms [SME: 11458]
- navigation-conf when a panel is installed

* Wed Feb 24 2021 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-47.sme
- fix wrong path for rsyslog.conf [SME: 11364]

* Sun Feb 21 2021 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-46.sme
- remove noise in yum process "overriding all signals, forcing restart" [SME: 11372]

* Fri Feb 19 2021 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-45.sme
- packages installed logged both in yum.log and message [SME: 11364]
- set priority to 10 for remi-safe [SME: 11360]

* Mon Feb 15 2021 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-44.sme
- fix poor handling of service adjusting and action order [SME: 11300]
  now a temp event is created
  also better logging, better handling of update vs removal

* Wed Dec 09 2020 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-43.sme
- make yum dbs service fork [SME: 11243]
  now smeserver.py plugin call the service
  yum-modify can use the service restart
  yum.service is its own service, not called by local.service

* Tue Dec 08 2020 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-42.sme
- move yum upate db service to systemd [SME: 11180]

* Sun Dec 06 2020 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-41.sme
- fix -update events not runt on package upgrade [SME: 11184]
  lower noise on forced restart

* Thu Dec 03 2020 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-39.sme
- fix switch to vault BaseURL for CentOS [SME: 11227]

* Mon Nov 16 2020 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-38.sme
- add remi-safe as base repo [SME: 11179]
- smeserver-yum-update event created [SME: 11168]

* Sun Nov 15 2020 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-37.sme
- fix separate action before template, and after service [SME: 11175]
  run all actions with post-upgrade as default event

* Tue Nov 10 2020 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-36.sme
- fix some templates not expanded [SME: 11121]

* Tue Oct 20 2020 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-35.sme
- fix smeserver.py not executing action because of wrong path [SME: 11047]

* Mon Jun 22 2020 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-33.sme
- fix error when key absent of a dict of smeserver plugin at clean stage [SME: 10931]

* Thu Jan 30 2020 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-32.sme
- avoid missing template error after removal of a rpm [SME: 10846]

* Thu Jan 30 2020 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-30.sme
- restart php-fpm services when needed [SME: 10873]

* Mon Dec 09 2019 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-29.sme
- applying patch [SME: 10690]

* Sun Dec 08 2019 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-27.sme
- fix NameError: global name 'yum_update_dbs' is not defined [SME: 6940]

* Fri Dec 06 2019 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-26.sme
- use yum-cron with autoupdate feature [SME: 10690]
  * use yum-cron for download only or auto update 
  * yum-cron.conf templates
  * update lock path
  * settings in server-manager
  * remove yumdownloadonly script and crontab template

* Fri Dec 06 2019 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-25.sme
- fix typo on patch [SME: 10249]

* Wed Dec 04 2019 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-24.sme
- fix header detected as package [SME: 10843]
- avoid discrepancy between manager, cli and email [SME: 6940] 
  * force refresh of metadata before db generation 
  * add regeneration of db during check4updates, after yum update/install/remove 
- fix no installed groups file [SME: 118]
- switch to centos vault after EOL [SME: 10249]
- update http://mirrorlist.contribs.org/mirrorlist to https://mirrorlist.koozali.org/mirrorlist [SME: 9697]
- make smecontribs visible [SME: 10716]

* Mon Feb 18 2019 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-22.sme
- add openfusion gpg key [SME: 10742]

* Sat Jan 26 2019 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-21.sme
- updated EOL patch [SME: 10170]

* Wed Jan 23 2019 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-19.sme
- add yum-priority as requirement [SME: 6499]
  add support for plugin priority using property priority im yum_repositories db 
  initial priority to 10 for sme*, base and updates repos.
  property yum priority set as enabled as default
- avoid double check updates for contribs if smecontribs is set to enabled [SME: 9388]
- update check4contribs email format to match check4updates [SME: 8782]
- improve yum plugin to avoid reboot [SME: 8705]
  add nut support, add exclusions for -doc, -devel... subpackages

* Tue Jan 22 2019 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-18.sme
- add message to indicate EOL after Jun 30 2024 fix [SME: 10170]

* Mon Nov 06 2017 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-17.sme
- add yum-plugin-post-transaction-actions as requirement [SME: 1100]

* Tue May 02 2017 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-16.sme
- add rpmfusion free el7 RPM GPG KEY [SME: 10263]

* Mon Apr 10 2017 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-15.sme
- avoid reboot for smeserver-locale upgrade [SME: 8705]
- code by stefano zamboni <zamboni@mind-at-work.it>

* Wed Mar 29 2017 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-14.sme
- correct service names with plugin to avoid reboot [SME: 8705]
- code by stefano zamboni <zamboni@mind-at-work.it>

* Mon Mar 27 2017 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-13.sme
- fix KeyError with plugin to avoid reboot [SME: 8705]
- code by stefano zamboni <zamboni@mind-at-work.it>

* Mon Mar 20 2017 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-12.sme
- remove centos contrib repo [SME: 10156]

* Sat Feb 25 2017 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-11.sme
- added centos SCLo SIG gpg rpm signing key [SME: 10119]
- will allow to install SCL packages directly from smecontribs

* Sat Feb 18 2017 stephane de Labrusse <stephdl@de-labrusse.fr> 2.6.0-10.sme
- Added smeserver-yum-2.6.0.bz8705.avoidReboot.patch [SME: 8705]
- code by stefano zamboni <zamboni@mind-at-work.it>
- Avoid to reboot after the installation of a smeserver-* package

* Fri Jan 06 2017 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-8.sme
- add Remi Collet RPM GPG KEY [SME: 9903]

* Thu Aug 04 2016 stephane de Labrusse <stephdl@de-labrusse.fr> 2.6.0-7.sme
- Rpm updates can be downloaded during the night [SME: 1502]
- Added smeserver-yum-2.6.0.bz1502.DownloadOnly.patch

* Mon Aug 1 2016 stephane de Labrusse <stephdl@de-labrusse.fr> 2.6.0-6.sme
- Deltarpm is now a setting in the yum panel (disabled by default)
- Added smeserver-yum-2.6.0.bz8834.DeltaRpm.patch [SME: 8834]

* Fri May 27 2016 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-5.sme
- adding Koozali SME10, EPEL7 and Centos7 gpg keys [SME: 9533]

* Thu May 12 2016 Daniel Berteaud <daniel@firewall-services.com> 2.6.0-4.sme
- Rebuild [SME: 9393]

* Wed Mar 23 2016 Jean-Philipe Pialasse <tests@pialasse.com> 2.6.0-3.sme
- yum points now to SME10 mirrors [SME: 9377]
- moved changelog at the end of file
- Eliminated rpmbuild "bogus date" warnings due to inconsistent weekday,
  by assuming the date is correct and changing the weekday.
  Fri May 31 2005 --> Fri May 27 2005 or Tue May 31 2005 or Fri Jun 03 2005 or ....
  Fri Nov 16 2006 --> Fri Nov 10 2006 or Thu Nov 16 2006 or Fri Nov 17 2006 or ....
  Fri Nov 23 2006 --> Fri Nov 17 2006 or Thu Nov 23 2006 or Fri Nov 24 2006 or ....


* Sun Feb 7 2016 Daniel Berteaud <daniel@firewall-services.com> 2.6.0-2.sme
- Add python to BuildReq so brp-python-bytecode compiles sme yum plugin
  [SME: 9229]

* Sat Feb 06 2016 stephane de Labrusse <stephdl@de-labrusse.fr> 2.6.0-1.sme
- Initial release to sme10

* Wed Jan 13 2016 Daniel Berteaud <daniel@firewall-services.com> 2.4.0-12.sme
- Example to update contribs 1 by 1 [SME: 8850]

* Sat Feb 21 2015 Stephane de Labrusse <stephdl@de-labrusse.fr> 2.4.0-11.sme
- Set the check update frequency of smecontribs through the server-manager
- [SME: 8855]

* Sat Jan 10 2015 Stephane de Labrusse <stephdl@de-labrusse.fr> 2.4.0-10.sme
- Add a default Yum db property for check4contribsupdates [SME: 8790]

* Wed Nov 19 2014 Stephane de Labrusse <stephdl@de-labrusse.fr> 2.4.0-9.sme
- Added a check-update for the smecontribs repository [SME: 8672]

* Mon Jun 30 2014 Daniel Berteaud <daniel@firewall-services.com> 2.4.0-8.sme
- Move protected package list to the correct location [SME: 8476]

* Fri Mar 22 2013 Ian Wells <esmith@wellsi.com> 2.4.0-7.sme
- Change order of mail options in check4updates [SME: 7504]

* Sun Mar 17 2013 Ian Wells <esmith@wellsi.com> 2.4.0-6.sme
- Change wording of Software Update button [SME: 7499]

* Wed Mar 6 2013 Shad L. Lords <slords@mail.com> 2.4.0-5.sme
- Obsolete el5 yum-protect-packages, provided by yum [SME: 7273]

* Wed Mar 6 2013 Shad L. Lords <slords@mail.com> 2.4.0-4.sme
- Update GPG keys for sme9 [SME: 7465]

* Wed Feb 27 2013 Daniel Berteaud <daniel@firewall-services.com> 2.4.0-3.sme
- Add fasttrack and remove addons repo [SME: 7385]

* Tue Feb 5 2013 Shad L. Lords <slords@mail.com> 2.4.0-2.sme
- Add back in missing parts from new stream [SME: 7305]

* Thu Jan 31 2013 Shad L. Lords <slords@mail.com> 2.4.0-1.sme
- Roll new stream for sme9

* Fri Aug 31 2012 Shad L. Lords <slords@mail.com> 2.2.0-20.sme
- Point mirrorlist to mirrorlist.contribs.org [SME: 7087]

* Tue Mar 1 2011 Jonathan Martens <smeserver-contribs@snetram.nl> 2.2.0-19.sme
- Add random wait timer for check4updates script to distribute load on ibiblio [SME: 6534]

* Fri Oct 1 2010 Jonathan Martens <smeserver-contribs@snetram.nl> 2.2.0-18.sme
- Trigger post-upgrade and reboot on kernel updates [SME: 6166]

* Sat Jun 12 2010 Shad L. Lords <slords@mail.com> 2.2.0-17.sme
- Fix migrate fragment to not throw warnings [SME: 5705]

* Wed Jun 02 2010 Shad L. Lords <slords@mail.com> 2.2.0-16.sme
- Fix yum database removal (missing one) [SME: 5705]

* Wed Jun 02 2010 Shad L. Lords <slords@mail.com> 2.2.0-15.sme
- Migrate MirrorList properties to sme8 repos [SME: 5705]
- Remove BaseURL properties if migrating to sme8 repos [SME: 5949]
- Remove yum databases and repodata if migrating to sme8 repos [SME: 5998]

* Mon May 17 2010 Jonathan Martens <smeserver-contribs@snetram.nl> 2.2.0-14.sme
- Revert previous change [SME: 5962]

* Mon May 17 2010 Jonathan Martens <smeserver-contribs@snetram.nl> 2.2.0-13.sme
- Migrate CentOS Exclude property default values to smeserver-yum [SME: 5962]

* Thu Nov 5 2009 Shad L. Lords <slords@mail.com> 2.2.0-12.sme
- only unlink file if we created it [SME: 5476]

* Wed Oct 14 2009 Filipo Carletti <filippo.carletti@gmail.com> 2.2.0-11.sme
- Import only keys not already imported [SME: 5507]

* Tue Sep 15 2009 Shad L. Lords <slords@mail.com> 2.2.0-10.sme
- set unsaved changes in yum event [SME: 5475]
- move yum warming to sme yum plugin [SME: 5474]
- ensure file exists before unlinking [SME: 5476]
- remove semicolons from yum plugin

* Tue Sep 15 2009 Shad L. Lords <slords@mail.com> 2.2.0-9.sme
- Add frequency of updates toggle [SME: 3764]
- remove stray file

* Sat May 30 2009 Shad L. Lords <slords@mail.com> 2.2.0-8.sme
- Add /etc/yum.smerepos.d to package [SME: 5305]

* Mon May 18 2009 Shad L. Lords <slords@mail.com> 2.2.0-7.sme
- Change SME mirrorlists to point to ibiblio [SME: 5242]

* Fri Apr 10 2009 Jonathan Martens <smeserver-contribs@snetram.nl> 2.2.0-6.sme
- Require mailx [SME: 5131]

* Mon Nov 24 2008 Shad L. Lords <slords@mail.com> 2.2.0-5.sme
- Add yum-protect-packages support to prevent removal of 
  needed pacakges [SME: 3133]

* Tue Oct 28 2008 Shad L. Lords <slords@mail.com> 2.2.0-4.sme
- Make yum update unbuffered for web interface [SME: 4726]

* Mon Oct 13 2008 Shad L. Lords <slords@mail.com> 2.2.0-3.sme
- Move repos to repodir to fix yum bug [SME: 3676]

* Sun Oct 12 2008 Shad L. Lords <slords@mail.com> 2.2.0-2.sme
- Fix name for smeextras [SME: 4585]

* Tue Oct 7 2008 Shad L. Lords <slords@mail.com> 2.2.0-1.sme
- Roll new stream to separate sme7/sme8 trees [SME: 4633]

* Tue Oct 7 2008 Shad L. Lords <slords@mail.com> 1.2.0-58
- Fix mirrorlist for sme8 [SME: 4508]

* Fri Sep 19 2008 Shad L. Lords <slords@mail.com> 1.2.0-57
- Add smeextras repo database and information [SME: 4585]

* Sun Aug 10 2008 Shad L. Lords <slords@mail.com> 1.2.0-56
- Remove links to crontab in bootstrap-console-save [SME: 4494]

* Sat Jul 5 2008 Jonathan Martens <smeserver-contribs@snetram.nl> 1.2.0-55
- Add common <base> tags to e-smith-formmagick's general [SME: 4279]

* Sun Apr 27 2008 Jonathan Martens <smeserver-contribs@snetram.nl> 1.2.0-54
- Add common <base> tags to e-smith-formmagick's general [SME: 4290]

* Mon Mar 31 2008 Shad L. Lords <slords@mail.com> 1.2.0-53
- Include installonlyn plugin to manage kernels [SME: 2101]

* Mon Mar 31 2008 Stephen Noble <support@dungog.net> 1.2.0-52
- Delete dungog repository, reworked [SME: 4097]

* Fri Mar 14 2008 Shad L. Lords <slords@mail.com> 1.2.0-51
- Clean up "rpm -qa" warnings in yum wrapper [SME: 4052]

* Wed Feb 13 2008 Stephen Noble <support@dungog.net> 1.2.0-50
- Remove <base> tags now in general [SME: 3914]

* Sun Feb 10 2008 Stephen Noble <support@dungog.net> 1.2.0-49
- Remove duplicate <base> entries [SME: 3889]

* Fri Jan 11 2008 Shad L. Lords <slords@mail.com> 1.2.0-48
- Put check4updates obsoletes & provides in the right place [SME: 3250]

* Fri Jan 11 2008 Shad L. Lords <slords@mail.com> 1.2.0-47
- Add check4update script, make cronjob run same as scheduled dirs [SME: 3250]

* Wed Jan 09 2008 Stephen Noble <support@dungog.net> 1.2.0-46
- Add server is up to date message on panel [SME: 2512]

* Mon Jan 7 2008 Stephen Noble <support@dungog.net> 1.2.0-45
- remove BaseURL property for repos with mirrorlists [SME: 3275]

* Mon Jan 7 2008 Stephen Noble <support@dungog.net> 1.2.0-44
- safesymlink yum into local [SME: 3238]

* Mon Jan 7 2008 Stephen Noble <support@dungog.net> 1.2.0-43
- add check4updates cronjob, obsolete check4updates rpm [SME: 3250]

* Mon Jan 7 2008 Stephen Noble <support@dungog.net> 1.2.0-42
- yum-import-keys action to yum-update event [SME: 3196]

* Mon  Dec 24 2007 Stephen Noble <support@dungog.net> 1.2.0-41
- add smecontribs repo [SME: 3551]

* Tue Dec 11 2007 Gavin Weight <gweight@gmail.com> 1.2.0-40
- Remove bad mirror and add two new mirrors. [SME: 3636]

* Fri Nov 30 2007 Gavin Weight <gweight@gmail.com> 1.2.0-39
- Change EnableGroups value to no/yes instead of 0/1. [SME: 3607]

* Fri Nov 30 2007 Gavin Weight <gweight@gmail.com> 1.2.0-38
- Fix use of uninitialized value in migrate 10GPG_and_Groups. [SME: 2491]

* Sat Jul 14 2007 Shad L. Lords <slords@mail.com> 1.2.0-37
- Add GPG keys for CentOS 5 [SME: 3160]

* Sun Jun 10 2007 Stephen Noble <support@dungog.net> 1.2.0-36
- Refine matching of rpms or repos [SME: 2416]

* Sun Jun 10 2007 Stephen Noble <support@dungog.net> 1.2.0-35
- Add db values to restrict available rpms or repos [SME: 2416]

* Sun Jun 10 2007 Stephen Noble <support@dungog.net> 1.2.0-34
- remove restrictAvailable patch [SME: 2416]

* Fri Jun 08 2007 Stephen Noble <support@dungog.net> 1.2.0-33
- Add db value to restrict available rpms [SME: 2416]

* Fri May 25 2007 Shad L. Lords <slords@mail.com> 1.2.0-32
- Add rpm key for epel packages

* Wed May 9 2007 Shad L. Lords <slords@mail.com> 1.2.0-31
- Updates to support SME Server 8

* Sun Apr 29 2007 Shad L. Lords <slords@mail.com>
- Clean up spec so package can be built by koji/plague

* Mon Apr 09 2007 Stephen Noble <support@dungog.net> 1.2.0-30
- remove two of them, leaving pacific.net.au [SME: 2763]

* Mon Apr 09 2007 Stephen Noble <support@dungog.net> 1.2.0-29
- add three more repositories to yum.repos.d/mirrors-sme* files [SME: 2763]

* Fri Feb 16 2007 Shad L. Lords <slords@mail.com> 1.2.0-28
- Change runsvctrl to sv to support runit v1.7.x [SME: 2486]

* Wed Jan 17 2007 Shad L. Lords <slords@mail.com> 1.2.0-27
- Only import keys we don't already have [SME: 1174]

* Wed Jan 03 2007 Shad L. Lords <slords@mail.com> 1.2.0-26
- Only allow upstream proxies to cache packages not metadata.

* Thu Dec 07 2006 Shad L. Lords <slords@mail.com>
- Update to new release naming.  No functional changes.
- Make Packager generic

* Fri Dec 1 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-25
- Remove defaults for CentOS testing repository [SME: 2119]

* Thu Nov 30 2006 Greg Swallow <greg@runlevel7.ca> 1.2.0-24
- Change Includepkgs to IncludePkgs [SME: 2049]

* Thu Nov 30 2006 Greg Swallow <greg@runlevel7.ca> 1.2.0-23
- Add includepkgs option to repository configuration [SME: 2049]

* Thu Nov 30 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-22
- Correct typos in last patch [SME: 2050]

* Thu Nov 30 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-21
- Create local SME Server mirrorlists during build of package
- Refer to these mirrorlists from yum.conf
- Comment out baseurl if a MirrorList is defined [SME: 2050]

* Wed Nov 29 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-20
- Revert to 10s panel refresh [SME: 2097]

* Thu Nov 23 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-19
  Fri Nov 23 2006 --> Fri Nov 17 2006 or Thu Nov 23 2006 or Fri Nov 24 2006 or ....
- Make CentOS base and updates enabled/Visible by default [SME: 1849]
- Migrate CentOS base and updates to Visible, but leave status [SME: 1849]

* Thu Nov 23 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-18
  Fri Nov 23 2006 --> Fri Nov 17 2006 or Thu Nov 23 2006 or Fri Nov 24 2006 or ....
- Adjust wording on post-upgrade page [SME: 2076]

* Tue Nov 21 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-17
- Clean up post-upgrade page LogFile display [SME: 2077]

* Tue Nov 21 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-16
- Fix post-upgrade page handling [SME: 2077]
- TODO: Add persistent RebootRequired handling so that the reconfigure
  page is displayed from other sessions
- TODO: Re-add display of LogFile prior to reconfigure

* Thu Nov 16 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-15
  Fri Nov 16 2006 --> Fri Nov 10 2006 or Thu Nov 16 2006 or Fri Nov 17 2006 or ....
- Add dependency on yum-plugin-fastestmirror [SME: 1163]
- Alpha sort dependencies

* Thu Nov 16 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-14
  Fri Nov 16 2006 --> Fri Nov 10 2006 or Thu Nov 16 2006 or Fri Nov 17 2006 or ....
- Add MirrorList options to each of the SME repos [SME: 1163]

* Thu Nov 16 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-13
  Fri Nov 16 2006 --> Fri Nov 10 2006 or Thu Nov 16 2006 or Fri Nov 17 2006 or ....
- Put back missed patch for post-upgrade [SME: 2071]

* Thu Nov 16 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-12
  Fri Nov 16 2006 --> Fri Nov 10 2006 or Thu Nov 16 2006 or Fri Nov 17 2006 or ....
- Re-add post-upgrade handling [SME: 2071]
- Display yum output
- Lower refresh to 3 seconds from 10

* Thu Nov 16 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-11
- Add Federico Simoncelli's smeserver plugin for yum [SME: 59]
- TODO: Add post-upgrade page handling

* Tue Nov 14 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-10
- Add distroverpkg to set release version for CentOS packages [SME: 1163]

* Thu Nov  9 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-09
- Allow MirrorList property to be optional [SME: 1163]

* Thu Nov  9 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-08
- Add mirrorlist option to CentOS repos via MirrorList db property [SME: 1163]
- TODO: Create mirrorlist for SME repos.

* Thu Nov  9 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-07
- Explicitly unset reposdir so we ignore the CentOS repo files [SME: 1905]

* Fri Sep  1 2006 Charlie Brady <charlieb@e-smith.com> 1.2.0-06
- Fix quoting in yum wrapper script. [SME: 1894]

* Mon May  1 2006 Charlie Brady <charlieb@e-smith.com> 1.2.0-05
- Remove stray yum.pm.orig file. [SME: 1350]

* Tue Apr 18 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-04
- Also display yum output if the yum command fails, e.g. due to an
  existing yum lock. [SME: 1110]

* Tue Apr 18 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-03
- Update the yum dbs in yum-modify in case the repos have changed [SME: 1261]

* Tue Apr 18 2006 Gordon Rowell <gordonr@gormand.com.au> 1.2.0-02
- Capture and display yum output [SME: 1269]

* Wed Mar 15 2006 Charlie Brady <charlie_brady@mitel.com> 1.2.0-01
- Roll stable stream version. [SME: 1016]

* Mon Mar 6 2006 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-26
- And migrate old SME repo URLs to new paths [SME: 951]

* Mon Mar 6 2006 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-25
- Change SME Server repo URLs to match repo names so we avoid confusion
  with CentOS repos and can remove the symlinks [SME: 951]

* Mon Mar 6 2006 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-24
- Don't force the BaseURL properties - just set defaults [SME: 951]

* Wed Feb 22 2006 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-23
- Default smeupdates-testing repository to Visible, disabled [SME: 846]

* Thu Feb 16 2006 Charlie Brady <charlie_brady@mitel.com> 1.1.2-22
- Do not suggest post-upgrade/reboot if no rpms were installed or
  removed. [SME: 676]

* Thu Feb 16 2006 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-21
- Run post-upgrade and reboot in the background so that the front page
  can be displayed without the "Your system needs to be rebooted"
  warning - it's already getting one by then. [SME: 611]
- Adjust reconfiguration wording [SME: 611]

* Thu Feb 16 2006 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-20
- And add L10N for newly exposed unlocalised message [SME: 611]

* Thu Feb 16 2006 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-19
- Catch error return status from yum commands [SME: 611]

* Tue Feb 7 2006 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-18
- Adjust wording in yum wrapper [SME: 676]

* Tue Jan 24 2006 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-17
- And change "A reboot will be required" to 
  "A reboot will be initiated" in the post-upgrade panel [SME: 199]

* Tue Jan 24 2006 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-16
- Bring back post-upgrade page after performing updates [SME: 199]
- Force a reboot after the post-upgrade command [SME: 199]

* Tue Jan 24 2006 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-15
- Add wrapper /sbin/e-smith/yum to remind people to 
  post-upgrade/reboot [SME: 199]

* Tue Jan 24 2006 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-14
- Force yum{AutoInstallUpdates} to disabled and remove toggle from
  panel for now [SME: 525]

* Mon Nov 21 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-13
- And make them Visible=no by default [SF: 1362528]

* Mon Nov 21 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-12
- Disable centos base/updates/contrib repos by default [SF: 1362528]

* Mon Nov 21 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-11
- Show repositories which are either Visible or enabled [SF: 1362529]

* Mon Nov 21 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-10
- Disable automatic updates by default [SF: 1362526]

* Mon Nov 14 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-09
- Add Conflicts: centos-yumconf [SF: 1356006]

* Tue Nov 8 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-08
- Don't force a post-upgrade/reboot after changes. We don't need to
  do it in most cases [SF: 1304387, 1349946]

* Fri Oct 28 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-07
- Allow optional GPGKey property [SF: 1332624]

* Fri Oct 28 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-06
- Change CentOS BaseURL values back to /centos/4 [SF: 1334861]
- Generate all repositories in /etc/yum.conf with enabled=0/1 [SF: 1332624]
- Only display "Visible" repositories in the server-manager panel [SF: 1332624]

* Fri Oct 14 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-05
- Move all L10Ns to smeserver-locale [SF: 1309520]

* Mon Oct 10 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-04
- Fix up auto-selection of all updates [SF: 1321887]

* Mon Oct 10 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-03
- Remove navigation-conf-hidden [SF: 1315730]

* Fri Oct 7 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-02
- Require GPG signatures on all yum packages

* Fri Oct 7 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.2-01
- Roll new tarball, patches to 1.1.1-07

* Fri Sep 30 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.1-07
- And another [SF: 1301044]

* Fri Sep 30 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.1-06
- Correction to French L10N - Thanks Didier Rambeau [SF: 1301044]

* Fri Sep 30 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.1-05
- Added Italian L10N - Thanks Filippo Carletti [SF: 1309266]

* Fri Sep 30 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.1-04
- Added lots of RPM GPG keys [SF: 1309195]

* Thu Sep 29 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.1-03
- It's obsoletes=1 [SF: 1306265]

* Thu Sep 29 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.1-02
- Added obsoletes option to yum.conf  [SF: 1306265]

* Mon Sep 26 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.1-01
- Rolled patches up to 1.1.0-26
- Added German L10N

* Sun Sep 25 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.0-26
- Typo fix - add space between 'yum' and options

* Sun Sep 25 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.0-25
- Increase debug and error level so we at least capture yum output
  in the messages log [SF: 1218082]

* Sun Sep 25 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.0-24
- Need to return a hash, with key equal to package.arch [SF: 1298468]

* Sun Sep 25 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.0-23
- Display version and repository in picklists [SF: 1298468]

* Sun Sep 25 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.0-22
- Change 1/0 values for GPGCheck and EnableGroups to yes/no
  It's more readable in the DB and also works around a bug [SF: 1303885]

* Sun Sep 25 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.0-21
- Wrap HTML escapes in Fr lexicon in CDATA blocks [SF: 1302289]

* Fri Sep 23 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.0-20
- Remove XXX - FIXMEs from French lexicon [SF: 1301044]

* Fri Sep 23 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.0-19
- French L10N fix [SF: 1266152]

* Mon Sep 12 2005 chris burnat <cburnat@burnat.com> 1.1.0-18
- Fix equal greater than (=>) to (>=) in two instances in spec file.

* Mon Sep 5 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.0-17
- Change centos BaseURL entries from /centos/4/ to /centos/4.1/ as
  it appears that some mirrors aren't following the symlinks correctly
- Move BaseURL settings into force fragments as they will need to
  change as we update the base [SF: 1272438]

* Wed Aug 24 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.0-16
- Remove XXX entries from panel text [SF: 1267315]

* Wed Aug 24 2005 Gordon Rowell <gordonr@gormand.com.au> 1.1.0-15
- Fix status check in yum cron job - Thanks Filippo Carletti [SF: 1266967]

* Wed Aug 17 2005 Charlie Brady <charlieb@e-smith.com> 1.1.0-14
- Change dependency to rpmdb-CentOS

* Mon Aug 15 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-13]
- Add dependency on rpmdb package

* Mon Jul 18 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-12]
- And remove now unused action scripts

* Mon Jul 18 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-11]
- Removed the old pre-FM panels, which we haven't used or displayed for
  a while

* Mon Jul 18 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-10]
- Relocate dbs to /home/e-smith/db. Note yum_update_dbs avoids the
  ConfigDB interface for speed and to reduce log noise. Maybe it 
  shouldn't, which would give a record of nightly changes.

* Thu Jul 14 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-09]
- French localisation - Merci Didier Rambeau [SF: 1234929]

* Thu Jul 14 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-08]
- Fix cron.daily ordering so yum_update_dbs gets a chance to fix
  the yum flag file before the standard yum cron job runs [SF: 1237639]
- Clean up various old cron jobs which are no longer used
- Change cron job template into a shell script

* Thu Jul 14 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-07]
- Remove pid file check - yum leaves stale pid files when an action
  fails, but cleans up next time. Since we're calling yum, it can
  do the work. Death to pid files.

* Thu Jul 14 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-06]
- Adjusted repository names sme{addons,core,dev,test,updates} -> 
  addons,os,dev,test,updates
- Added updates-testing
- Changed BaseURL to use mirror.contribs.org/pub/smeserver for consistency
  across mirrors
- Drop /7.0alpha/ to /7/

* Sat Jul 2 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-05]
- Fix creation of event links

* Sat Jul 2 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-04]
- Remove all other instances of services2adjust once for yum, and use
  the action script instead to avoid an endless run of yum_update_dbs

* Sat Jul 2 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-03]
- Add exec to yum service run script
- Add action script to update DBs as required, including 'local' event
- TODO: Work out why services2adjust 'once' loops forever on this service

* Sat Jul 2 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-02]
- Add Provides: yumconf [SF: 1230970]
- Cater for new yum output format, and only pick package lines from
  output [SF: 1230971]

* Thu Jun 30 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr22]
- Change from CentOS 3 to CentOS 4
- Remove force fragment for stunnel since we now ship the CentOS RPM

* Fri Jun 10 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr21]
- Import keys in bootstrap-console-save rather than post-{install,upgrade}

* Fri Jun 10 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr20]
- Populate /usr/share/rpm-gpg-keys with various RPM-GPG-KEY files
  we might want to use
- Add script to import keys
- TODO: Clean out duplicate key copies

* Thu Jun 9 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr19]
- Comment out 'once' invocation in local event - it seems to loop
- Change cron job to do the 'runsvctrl once' invocation

* Thu Jun 9 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr18]
- Fix up exit status warning.

* Thu Jun 9 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr17]
- Don't bother checking the exit status of yum, since yum may
  return non-zero for failure or for "no matching groups/packages".
  TODO: We should probably work out how to tell between these.

* Thu Jun 9 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr16]
- Make it a supervised service, but one which we only run
  "once" when we need it [SF: 1216096]

* Thu Jun 9 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr15]
- Don't try to grab the yum.pid file with Proc::PID_File as then
  we can't actually run yum commands [SF: 1216097]

* Thu Jun 9 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr14]
- Add yum_update_dbs into a supervised service so we don't have 
  to wait for it at boot time [SF: 1216096]

* Thu Jun 9 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr13]
- Unlink tmp files if yum command fails and we exit early

* Thu Jun 9 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr12]
- Check for another running yum process [SF: 1216097]
- Don't update the databases if the yum command fails [SF: 1216097]

* Fri Jun 3 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr11]
- Use the dump RPM from CentOS [SF: 1214055]

* Fri Jun 3 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr10]
- Invert exit status of system()

* Fri Jun 3 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr09]
- Move management of /var/lock/subsys/yum into yum_updates_dbs action script
- Call yum_update_dbs in local event - after the system is up and running
- Remove commented out panel references

* Fri Jun 3 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr08]
- Default gpgcheck off, except for base/updates/smecore/smeupdates
- Default yum{AutoInstallUpdates} == enabled
- Add code to manage /var/lock/subsys/yum, which controls daily updates
  in /etc/cron.daily/yum

* Fri Jun 3 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr07]
- Deal with the case when the list of updates is empty
- Put a header on each of the yum_* dbs

* Fri Jun 3 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr06]
- Rename centos repositories to match the centos-yumcache names 
- Remove pkgpolicy=last and repository ordering. 
- Add Exclude= properties to CentOS base and updates for packages which
  are modified for the SMEServer releases
- INSTALL: Need to manually remove old version of yum_repositories DB

* Tue May 31 2005 Gordon Rowell <gordonr@gormand.com.au>
  Fri May 31 2005 --> Fri May 27 2005 or Tue May 31 2005 or Fri Jun 03 2005 or ....
- [1.1.0-01gr05]
- Add enable/disable repository support to configuration page

* Tue May 31 2005 Gordon Rowell <gordonr@gormand.com.au>
  Fri May 31 2005 --> Fri May 27 2005 or Tue May 31 2005 or Fri Jun 03 2005 or ....
- [1.1.0-01gr04]
- Hide empty group/package select boxes

* Tue May 31 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr03]
- Change BaseURLs for smeserver repositories to ..../7.0alpha/ until we
  add FollowSymlinks to httpd.conf

* Fri May 27 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr02]
- Add post-upgrade configuration page
- Hide Darrell's original panels
- Remove historical event directories
- TODO: Page for adding/deleting repositories
- TODO: yum-arch local repositories

* Fri May 27 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.1.0-01gr01]
- Roll to 1.1.0

* Fri May 27 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr30]
- Call yum_update_dbs during the actions so the db state is correct

* Fri May 27 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr29]
- Create empty yum_{available,installed,updates} dbs in SPEC file
- Display the available repositories, and provide a select box
  to allow them to be enabled/disabled.
- Add dependency on recent CGI::FormMagick so that the select options work

* Thu May 26 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr28]
- Introduce yum_repositories database and convert yum.conf template
- Introduce yum_repositories database and convert yum.conf template
- Set defaults, which can be overridden on a per-repository basis:
    yum{EnableGroups}==0
    yum{GPGCheck}==1

* Sat May 21 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr27]
- Add contrib group from CentOS and contribs.org repositories

* Fri May 20 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr26]
- Change configuration event to yum-modify since we need 
  yum-update for other purposes
- TODO: Need to update yum_* dbs after we perform an action
  so the panel status matches reality. For speed, we should
  probably delete the entries directly.
- TODO: Some yum comands take a long time, probably too long for
  the manager.
- TODO: Capture the yum output

* Fri May 20 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr25]
- Fix CGI parameter passing

* Fri May 20 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr24]
- Add actions for install/remove/update
- TODO: groupremove needs to pull apart the group and remove 
  packages individually

* Fri May 20 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr23]
- Major cleanup of yum.pm, refactoring lots of code
- Note: Depends on CGI::FormMagick patch from  [SF:1205448]

* Fri May 20 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr22]
- Changed yum{ShowPackages} to yum{PackageFunctions}
- Added enable/disable toggle to panel and fleshed out
  change_settings() so that the settings are saved
- TODO: Actually signal-event yum-update

* Fri May 20 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr21]
- Change button labels for consistency
- TODO: Deal with degenerate case where no groups exist

* Fri May 20 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr20]
- Show groups in the panel
- Hide the ability to install/remove individual packages by default
- To enable, set yum{ShowPackages}=yes
- Add a tst group, courtesy of Greg Swallow

* Fri May 20 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr19]
- List available/installed/updates for yum groups as well
- Create yum_installed db and use that instead of /var/log/rpmpkgs
  for orthogonality. We also update all three DBs with one action.

* Fri May 20 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr18]
- enablegroups for smeserver, but disable them for centos

* Fri May 20 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr17]
- For consistency, sort extras before os as well

* Fri May 20 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr16]
- Set pkgpolicy=last, put centos groups before smeserver groups, and
  ensure that the group labels are sortable

* Thu May 19 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr15]
- Comment out the smeserver parts of yum.conf for now

* Thu May 19 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr14]
- Fill in removable packages from /var/log/rpmpkgs, updated nightly
  by a cronjob in the rpm package. 
  TODO: We should probably run the cron job just before displaying 
  this panel

* Thu May 19 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr13]
- Rough in install/remove pages

* Thu May 19 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr12]
- Add configuration page to panel

* Thu May 19 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr11]
- Fix up conf-yum and /etc/yum.conf links

* Thu May 19 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr10]
- Clean up daily cronjobs, and check whether yum is enabled in each of them
- Remove /var/service/yum - we don't need to run all the time
- Make use of new templates.metadata to remove conf-yum script entirely

* Thu May 19 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr09]
- Rewrite yum.conf templates to depend on:
  sysconfig{ReleaseVersion}
  sysconfig{BaseDistro}
  sysconfig{BaseDistroVersion}

* Fri May 13 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr08]
- Initial FormMagick panel using new databases

* Fri May 13 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr07]
- And put yum_update_dbs in the right directory...

* Fri May 13 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr06]
- Add /sbin/e-smith/yum_update_dbs

* Fri May 13 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr05]
- Change db names and fix yum list updates command

* Fri May 13 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr04]
- Generate esmith::DB files from the yum output, as it's so much
  easier to deal with them later in panels, etc.

* Fri May 13 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr03]
- Change output path of yum list commands

* Fri May 13 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr02]
- Fix up init.d/supervise/yum symlink
- Create /service symlink
- Ensure correct permissions on supervise bits and pieces

* Fri May 13 2005 Gordon Rowell <gordonr@gormand.com.au>
- [1.0.0-04gr01]
- Change default type for yum to service
- Add yum{status}==enabled
- Create /var/log/yum in build
- Add yum service directory and startup

* Mon Mar 01 2004 Darrell May <dmay@myezserver.com>
- [1.0.0-03dmay]
- bugfix to yum-config missing db set {Arch,Check}Repository
* Sun Feb 29 2004 Darrell May <dmay@myezserver.com>

- [1.0.0-02dmay]
- major updates to yum panels, templates
* Sun Feb 08 2004 Darrell May <dmay@myezserver.com>

- [1.0.0-01_beta]
- initial beta release
- added yum-remove panel
- updated all panels, events, actions
* Sat Feb 07 2004 Darrell May <dmay@myezserver.com>

- [0.0.1a-09]
- added yum-post panel
- updated yum-{update,available} panels
- updated yum-install-{available,update} events & actions

* Tue Feb 03 2004 Darrell May <dmay@myezserver.com>
- [0.0.1a-08]
- added pre-alpha yum-{update,available} panels
- renamed all panels yum-panelname

* Mon Feb 02 2004 Darrell May <dmay@myezserver.com>
- [0.0.1a-07]
- updated yum-check-repository template and action to accept --nomail commandline option
- updated yumcheck panel to issue --nomail commandline option

* Sun Feb 01 2004 Darrell May <dmay@myezserver.com>
- [0.0.1a-06]
- added yumcheck server-manager panel
- updated cron.daily/yum-check-repository template
- change log file name to yum-check-repository.log

* Sat Jan 31 2004 Darrell May <dmay@myezserver.com>
- [0.0.1a-05]
- added yumconfig server-manager panel
- added yum-post-{install,remove} events
- added navigation-conf-hidden action

* Mon Jan 26 2004 Darrell May <dmay@myezserver.com>
- [0.0.1a-04]
- moved cron.hourly actions to cron.daily
- added yum-update event
- added yum-arch-repository yum-check-repository actions
- added yum-install-updates yum-install-available actions
- removed %post entries, created db defaults

* Sun Jan 25 2004 Darrell May <dmay@myezserver.com>
- [0.0.1a-03]
- yum-check-repository, changed to run 'yum list'
- yum-arch-repository, added support for multiple archive repositories

* Sat Jan 24 2004 Darrell May <dmay@myezserver.com>
- [0.0.1a-02]
- fix db typo UpdateURL to UpdatesUrl
- added cron.hourly/yum-check-repository & yum-arch-repository
- updated actions/conf-yum

* Thu Jan 22 2004 Darrell May <dmay@myezserver.com>
- [0.0.1a-01]
- Original version
