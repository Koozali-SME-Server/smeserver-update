# vim: noexpandtab tabstop=4

import os
import shutil
import subprocess
import syslog
from yum.constants import *
from yum.plugins import PluginYumExit
from yum.plugins import TYPE_CORE
from yum.packages import parsePackages
from yum.packages import RpmBase

requires_api_version = '2.1'
plugin_type = (TYPE_CORE,)

events_path  = '/etc/e-smith/events'
initialize_database = events_path + '/actions/initialize-default-databases'
navigation_conf = events_path + '/actions/navigation-conf'
systemctl = "/usr/bin/systemctl"
dnf_update_dbs = events_path + '/actions/yum-update-dbs'
Conflicts=yum-cron.service dnf-automatic-notifyonly.service dnf-automatic.service
signal_event = '/sbin/e-smith/signal-event'
config_set = '/sbin/e-smith/config'
status_file  = '/var/run/yum.status'
expand_template = '/sbin/e-smith/expand-template'
service = '/sbin/e-smith/service'

eventlist = dict()
actionlist = dict()
templateslist = dict()
serviceslist = dict()


# list of packages that need a reboot
# if a package name starts with one these names, a reboot is needed
rebootpkgs = ['daemontools', 'dbus', 'glibc', 'gnutls', 'kernel', 'linux-firmware', 'lvm2', 'mdadm', 'openssl-libs', 'systemd']
# exclusions : 
rebootpkgsexclude = dict()
rebootpkgsexclude['dbus']='-python','-tests','-devel','-doc', 
rebootpkgsexclude['glibc']='-devel','-headers','-statics','-utils','-glib',
rebootpkgsexclude['gnutls']='-devel',
rebootpkgsexclude['kernel']='-doc','-debug','-devel','-abi-whitelists','tools',
rebootpkgsexclude['lvm2']='-devel','-python',
rebootpkgsexclude['systemd']='-devel','-python',


# list of packages that need a service restart
# if a package name starts with one of these values, a service restart is needed
# since, for example, httpd means httpd-admin and httpd-e-smith, we won't use these names directly but via serviceslist (see below)
restartpkgs = ['dovecot','bglibs','cvm','freeradius','httpd','iptables', 'mariadb' ,  'nut', 'openldap', 'openssh', 'php', 'pptpd', 'proftp', 'samba', 'spamassassin', 'squid', 'qmail', 'qpsmtpd']
servicenames = dict()
servicenames['bglibs']='cvm-unix',
servicenames['cvm']='cvm-unix',
servicenames['dovecot']='dovecot',
servicenames['freeradius']='radiusd',
servicenames['httpd']='httpd-admin','httpd-e-smith',
servicenames['iptables']='masq',
servicenames['mariadb']='mariadb',
servicenames['nut']='nut-server','nut-driver','nut-monitor',
servicenames['openldap']='ldap',
servicenames['openssh']='sshd',
servicenames['php']='httpd-e-smith', 'php-fpm', 'php55-php-fpm', 'php56-php-fpm', 'php70-php-fpm', 'php71-php-fpm', 'php72-php-fpm', 'php73-php-fpm', 'php74-php-fpm', 'php80-php-fpm', 'php81-php-fpm',
servicenames['proftp']='ftp',
servicenames['samba']='smb',
servicenames['spamassassin']='spamassassin',
servicenames['squid']='squid',
servicenames['qmail']='qmail',
servicenames['qpsmtpd']='qpsmtpd',

smechange = False
smechangelist = dict()
ourfile = False
erasing = False
DEBUG = False
smeEventPretrans = False
removenorebootok = dict()

def log(s):
    if DEBUG :
        print s
def createevent():
    if os.path.isdir('/etc/e-smith/events/temp'):
	shutil.rmtree('/etc/e-smith/events/temp')
    os.makedirs('/etc/e-smith/events/temp/services2adjust', 0o777)
    os.makedirs('/etc/e-smith/events/temp/templates2expand', 0o777)

def addtemplate2expand(template):
    #check filename
    head_tail = os.path.split(template)
    head = head_tail[0];
    filename = head_tail[1];
    # create dir
    if not os.path.isdir('/etc/e-smith/events/temp/templates2expand' + head):
        os.makedirs('/etc/e-smith/events/temp/templates2expand' + head, 0o777)
    #touch file
    fname= '/etc/e-smith/events/temp/templates2expand'+ template
    fhandle = open(fname, 'a')
    try:
        os.utime(fname, None)
    finally:
        fhandle.close()

def report_yum_status(status):
    fileHandle = open(status_file, 'w')
    fileHandle.write(status)
    fileHandle.close()

def predownload_hook(conduit):
    report_yum_status('predownload')

def postdownload_hook(conduit):
    report_yum_status('postdownload')

def prereposetup_hook(conduit):
    global ourfile
    
    ourfile = True
    report_yum_status('prereposetup')

def postreposetup_hook(conduit):
    report_yum_status('postreposetup')

def exclude_hook(conduit):
    report_yum_status('exclude')

def preresolve_hook(conduit):
    report_yum_status('preresolve')

def postresolve_hook(conduit):
    report_yum_status('postresolve')

def pretrans_hook(conduit):
# we might need to change the strategy here to make a difference between update and removal.
#transaction set states
#TS_UPDATE = 10
#TS_INSTALL = 20
#TS_TRUEINSTALL = 30
#TS_ERASE = 40
#TS_OBSOLETED = 50
#TS_OBSOLETING = 60
#TS_AVAILABLE = 70
#TS_UPDATED = 90
#TS_FAILED = 100
#TS_INSTALL_STATES = [TS_INSTALL, TS_TRUEINSTALL, TS_UPDATE, TS_OBSOLETING]
#TS_REMOVE_STATES = [TS_ERASE, TS_OBSOLETED, TS_UPDATED]

    report_yum_status('pretrans')
    log("*******Pretrans********")
    # Prefetch filelist for packages to be removed,
    # otherwise for updated packages headers will not be available
    ts = conduit.getTsInfo()
    removes = ts.getMembersWithState(output_states=TS_REMOVE_STATES)
    rpmdb = conduit.getRpmDB()
    global smechange
    global eventlist 
    global actionlist
    global templateslist 
    global serviceslist 
    global erasing    
    global smeEventPretrans
    global removenorebootok


    # reinstall are not listed there so already skipped
    # downgrade are going there 
    # update are going there, we filter them out
    # real removal are the real deal there ; downgrade are played like if they were removal  
    for tsmem in removes:
        erasing = True
        (n, a, e, v, r) = tsmem.po.pkgtup
	if tsmem.output_state == TS_UPDATED :
		# if we are actually updating then we are not removing, and new package will do better... skipping
		log('skiping as updating ==> state ' + str(tsmem.po.state) + " RPM current state" + str(tsmem.current_state) + " RPM output state" + str(tsmem.output_state))
		continue
        log('**Package: ' + tsmem.name + ' to be removed')
        smeevent = tsmem.name + '-update'
        if os.path.isdir(events_path + os.sep + smeevent):
            tmppath = events_path + os.sep + smeevent + os.sep
            eventlist[tsmem.name] = smeevent

            if os.path.isdir(tmppath + "templates2expand" + os.sep):
                tmppathtmpl = tmppath + "templates2expand" + os.sep
                for subdir, dirs, files in os.walk(tmppathtmpl):
                    for file in files:
                        mytmptemplate = os.path.join(subdir, file).replace(tmppathtmpl,os.sep)
                        if not templateslist.has_key(mytmptemplate):
                            templateslist[mytmptemplate]=mytmptemplate
                        log(" template " + mytmptemplate)

	    # nothing for actions ???
	    tmppathsrv = tmppath +  os.sep
	    files = [f for f in os.listdir(tmppathsrv)]
            for f in files:
		if os.path.islink(tmppathsrv + f):
                        mytmpaction = os.path.realpath(os.readlink(tmppath + f).replace("..",events_path))
                        log(" link " + f + ": " + mytmpaction)
                        actionlist[f]=mytmpaction

            # end debug print
            if os.path.isdir(tmppath + "services2adjust" + os.sep):
                tmppathsrv = tmppath + "services2adjust" + os.sep
                files = [f for f in os.listdir(tmppathsrv)]
                for f in files:
                    if os.path.islink(tmppathsrv + f):
                        log(" service link " + f + ": " + (os.readlink(tmppathsrv + f)))
                        mytmpserv = os.readlink(tmppathsrv + f)
                        if not serviceslist.has_key(f):
                           	serviceslist[f]=mytmpserv
                        else:
                            if mytmpserv == "restart":
                                log("overriding all signals, forcing restart " + f )
                                serviceslist[f]="restart"
	    removenorebootok[n]=1;
            thispo = rpmdb.searchNevra(name=n, arch=a, epoch=e, ver=v, rel=r)[0]
            # thispo.dirlist thispo.ghostlist thispo.filelist
            if "/etc/e-smith/web/panels/manager/cgi-bin" in thispo.dirlist:
                log(" ==> pannel detected : adding navigation-conf")
                actionlist['S80navigation-conf']="/etc/e-smith/events/actions/navigation-conf"

        else:
            if (n.startswith('smeserver') or n.startswith('e-smith')) and not n.startswith('smeserver-locale'):
                smechange = True
		smechangelist[n]=str(tsmem.po.state) + " " + str(tsmem.current_state) + " " + str(tsmem.output_state)
		log("smechange set to True because of " + n + " with " + str(tsmem.po.state) + " " + str(tsmem.current_state) + " " + str(tsmem.output_state) )

    #only for debug
    log('## smechange: '+str(smechange))
    log('## eventlist: '+ str(eventlist))
    log('## templateslist: '+str(templateslist.keys()))
    log('## serviceslist: '+str(serviceslist.items()))
    log('## actions ALL: '  + str(actionlist.keys()))
    log('## smechangelist: ' + str(smechangelist.keys()))

    if len(serviceslist)>0:
    	# would it be a good idea to do some action/event there to stop service being removed ?
	# for the moment we do not, logic : if template still there at posttrans, we expand it after removal
	# probably the actions in some situations could be done before...
    	# create an empty temp event
    	print "Creating temporary event 'temp' and populating it..."
    	createevent()
        print " Adding services to adjust"
        for kservices in serviceslist:
            log("  " + kservices + ": " + serviceslist[kservices])
            os.symlink(serviceslist[kservices], '/etc/e-smith/events/temp/services2adjust/' + kservices)

    	# execute the event ; should we really wait ??
    	print "Executing signal-event temp before uninstalling ..........."
    	os.spawnl(os.P_WAIT,signal_event,signal_event, 'temp')
	smeEventPretrans = True;

def posttrans_hook(conduit):
    report_yum_status('posttrans')
    log("*******Postrans********")
    ts = conduit.getTsInfo()
    rpmdb = conduit.getRpmDB()

    global smechange
    global eventlist 
    global actionlist
    global templateslist 
    global serviceslist 
    global erasing
    global smeEventPretrans
    global removenorebootok

   
    for tsmem in ts.getMembers():
        (n, a, e, v, r) = tsmem.po.pkgtup
	# n: name ; a : arch; e: epoch ; v: version, r: release
	#if tsmem.output_state in TS_INSTALL_STATES:	
	#  thispo = rpmdb.searchNevra(name=n, arch=a, epoch=e, ver=v, rel=r)[0]

        # we're upgrading/installing/removing a rebootpkgs package.. a reboot is required
        for pkg in rebootpkgs:
            if n.startswith(pkg):
                log('**Package: ' + tsmem.name + ' triggers reboot')
		# we do some exclusions -devel -doc ...
                if  pkg in rebootpkgsexclude:
		    cont=False
                    for name in rebootpkgsexclude[pkg]:
                        if n.startswith(pkg + name):
			    cont=True
		    if cont:
			# this is an exception we do not need reboot : -devel, -doc ...
			continue
		# either no exception or does not fit exceptions: we need reboot
		smechange = True
                smechangelist[n]=str(tsmem.po.state) + " " + str(tsmem.current_state) + " " + str(tsmem.output_state)
                log("smechange set to True because of " + n + " with " + str(tsmem.po.state) + " " + str(tsmem.current_state) + " " + str(tsmem.output_state))
		#log("smechange set to True because of " + pkg)

        # check if we're upgrading a restartpkgs rpm
        for pkg in restartpkgs:
            if n.startswith(pkg):
                if pkg in servicenames:
                    for name in servicenames[pkg]:
                        if not serviceslist.has_key(name):
                            serviceslist[name] = 'restart'
                else:
                    if not serviceslist.has_key(pkg):
                        serviceslist[pkg] = 'restart'


        #if smechange is true we can ignore the following part
	# wondering  if we reallly do want to ignore that : let's say we want to delay kernel reboot, 
	# could we at least configure httpd cleanly until next week ?
	# also when updating a package the erasing flag was on and prevented to do this ....
        # if not smechange and not erasing:
        if True:

            smeevent = tsmem.name + '-update'
            if os.path.isdir(events_path + os.sep + smeevent):
                tmppath = events_path + os.sep + smeevent + os.sep
                eventlist[tsmem.name] = smeevent

                files = [f for f in os.listdir(tmppath)]
                for f in files:
                    if os.path.islink(tmppath + f):

                        mytmpaction = os.path.realpath(os.readlink(tmppath + f).replace("..",events_path))
                        #log(" link " + f + ": " + mytmpaction)
			actionlist[f]=mytmpaction


                if os.path.isdir(tmppath + "templates2expand" + os.sep):
                    tmppathtmpl = tmppath + "templates2expand" + os.sep
                    for subdir, dirs, files in os.walk(tmppathtmpl):
                        for file in files:
                            mytmptemplate = os.path.join(subdir, file).replace(tmppathtmpl,os.sep)
                            if not templateslist.has_key(mytmptemplate):
                                templateslist[mytmptemplate]=mytmptemplate
                            log(" template " + mytmptemplate)

                if os.path.isdir(tmppath + "services2adjust" + os.sep):
                    tmppathsrv = tmppath + "services2adjust" + os.sep
                    files = [f for f in os.listdir(tmppathsrv)]
                    for f in files:
                        if os.path.islink(tmppathsrv + f):
                            log(" service link " + f + ": " + (os.readlink(tmppathsrv + f)))
                            mytmpserv = os.readlink(tmppathsrv + f)
                            if not serviceslist.has_key(f):
                                serviceslist[f]=mytmpserv
                            else:
                                if mytmpserv == "restart":
                                    #only for debug
                                    log("overriding all signals, forcing restart " + f)
                                    serviceslist[f]="restart"
		if tsmem.output_state in TS_INSTALL_STATES:
          	    thispo = rpmdb.searchNevra(name=n, arch=a, epoch=e, ver=v, rel=r)[0]
          	    # thispo.dirlist thispo.ghostlist thispo.filelist
		    if "/etc/e-smith/web/panels/manager/cgi-bin" in thispo.dirlist:
		        log(" ==> pannel detected : adding navigation-conf")
			actionlist['S80navigation-conf']="/etc/e-smith/events/actions/navigation-conf"

            else:
                if (n.startswith('smeserver') or n.startswith('e-smith')) and not n.startswith('smeserver-locale') and not (n in removenorebootok):
                    smechange = True
		    smechangelist[n]=str(tsmem.po.state) + " " + str(tsmem.current_state) + " " + str(tsmem.output_state)
		    log("smechange set to True because of " + n + " with " + str(tsmem.po.state) + " " + str(tsmem.current_state) + " " + str(tsmem.output_state) )
    
    #only for debug
    log('## smechange: '+str(smechange))
    log('## eventlist: '+ str(eventlist))
    log('## templateslist: '+str(templateslist.keys()))
    log('## serviceslist: '+str(serviceslist.items()))
    log('## actions ALL: '  + str(actionlist.keys()))
    log('## smechangelist: ' + str(smechangelist.keys()))

    # check if smechange is true or if eventlist has items.. in both cases we must initialize databases
    if smechange == True or len(eventlist)>0:
        print 'Initializing databases'
        os.spawnl(os.P_WAIT, initialize_database, initialize_database)

    # just in case we add systemd-default and systemd-reload
    if not actionlist.has_key('S88systemd-default'):
        actionlist['S88systemd-default'] = '/etc/e-smith/events/actions/systemd-default'
    if not actionlist.has_key('S89systemd-reload'):
        actionlist['S89systemd-reload'] = '/etc/e-smith/events/actions/systemd-reload'

    # here we would like to remove duplicates
    # those are potential : S??navigation-conf S??systemd-reload S??systemd-default
    for act in ('navigation-conf','systemd-reload','systemd-default'):
    	global iter 
	iter = 0
    	for key in actionlist.keys():
		if key.endswith(act):
		    iter += 1
		    if iter>1:
		        del actionlist[key]
		        log("removing duplicate action " + key + " iter " + str(iter))
    

    # now, if smechange is false (no reboot needed), we can execute actions, expand templates and adjust services

    # create an empty temp event
    print "Creating temporary event 'temp' and populating it..."
    createevent()

    # fill it with our list of actions
    if len(actionlist)>0:
	print " Adding actions to execute"
	for kactions in actionlist:
            if os.path.isfile(actionlist[kactions]):
		log("  " + kactions)
		os.symlink(actionlist[kactions],'/etc/e-smith/events/temp/' + kactions)

    # fill it with our list of templates to expand
    if len(templateslist)>0:
        print " Adding templates to expand"
        for ktemplates in templateslist:
            mytemplatedir = '/etc/e-smith/templates/' + ktemplates
            mytemplatemeta = '/etc/e-smith/templates.metadata/' + ktemplates
            if os.path.exists(mytemplatedir) or  os.path.exists(mytemplatemeta):
		log("  " + ktemplates)
                addtemplate2expand(ktemplates)

    if len(serviceslist)>0:
        print " Adding services to adjust"
        for kservices in serviceslist:
            log("  " + kservices + ": " + serviceslist[kservices])
	    os.symlink(serviceslist[kservices], '/etc/e-smith/events/temp/services2adjust/' + kservices)

    # execute the event ; should we really wait ??
    print "Executing signal-event temp ..........."
    os.spawnl(os.P_WAIT,signal_event,signal_event, 'temp')

    if smechange:
        os.spawnl(os.P_WAIT, config_set, config_set, 'set', 'UnsavedChanges', 'yes')
        os.spawnl(os.P_WAIT, navigation_conf, navigation_conf)
	syslog.syslog('Needs signal-event post-upgrade; signal-event reboot because of: ' + str(smechangelist.keys()) )
    print "Reload yum db for server-manager"
    os.spawnl(os.P_WAIT, systemctl, systemctl, 'restart', 'yum')

def close_hook(conduit):
    if ourfile and os.path.isfile('/var/run/yum.status'):
        os.unlink('/var/run/yum.status')

    if smechange:
	print "\nThe following updates require a server reboot:\n" + str(smechangelist.keys()) 
        print "\n=============================================================="
        print "WARNING: You now need to run BOTH of the following commands"
        print "to ensure consistent system state:\n"
        print "signal-event post-upgrade; signal-event reboot\n"
        print "You should run these commands unless you are certain that"
        print "yum made no changes to your system."
        print "=============================================================="

