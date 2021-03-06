DRBDLINKS README
================

Sean Reifschneider <jafo00@gmail.com>  
Homepage: [http://www.tummy.com/Community/software/drbdlinks/](http://www.tummy.com/Community/software/drbdlinks/)  
Code/bugfixes: [https://github.com/linsomniac/drbdlinks](https://github.com/linsomniac/drbdlinks)  
drbdlinks is under the following license: GPLv2

Status
------

drbdlinks is stable and in maintenance mode.  It is included in many
distributions (Debian, Ubuntu, Fedora, CentOS and variants).

Overview
--------

drbdlinks is a program that will manage creation and removal of symbolic
links.  It is primarily used with clusters of machines using either shared
storage or the "DRBD" replicated block device.  It has the ability to fix
SELinux contexts and restart cron and syslog as part of the linking
process.

While the name of the program is "drbdlinks", it can be used in any
shared-storage sort of environment where the shared storage is only mounted
on the active node.  In cases like NFS where the shared storage is always
mounted on all nodes, drbdlinks is not necessary.

The advantage over creating static symbolic links is that package updates
often require that directories point at real files, so updates can often
fail if you do not have the shared storage mounted.

drbdlinks also supports multiple instances of links, in the case of
active/active clusters.  For example, if you have MySQL running in one
resource group, and Apache running in another, you can use the "-c"
switch to specify a configuration file for each resource group.

A simple configuration file, "/etc/drbdlinks.conf", specifies the links.
This can be used to manage links for /etc/httpd, /var/lib/pgsql, and other
system directories that need to appear as if they are local to the system
when running applications after a drbd shared partition has been mounted.

Optionally, configuration directives can also be written to files in
"/etc/drbdlinks.d" with the suffix ".conf", which are loaded after the
"/etc/drbdlinks.conf" file, in sorted order.

When run with "start" as the mode, drbdlinks will rename the existing
files/directories, and then make symbolic links into the DRBD partition.
"stop" does the reverse.  By default, the rename appends ".drbdlinks" to
the name, but this can be overridden.

An init script is included which runs "stop" before heartbeat starts, and
after heartbeat stops.  This is done to try to ensure that when the shared
partition isn't mounted, the links are in their normal state.

Getting Started
---------------

The first thing you need to do is create a "/etc/drbdlinks.conf" file.  The
package ships with an example, primarily you will need to uncomment and
modify the "mountpoint" and "link" directives.  The "mountpoint" directive
tells drbdlinks the root of where your shared storage for this resource
group is mounted.

Next, you will need to set up the shared storage.

Automatic population: drbdlinks now includes an "initialize_shared_storage"
mode that will look at the links in the config file, and if they don't
exist in the shared storage it will populate them from the root
file-system.  Parent paths that do not exist will be set to the same
ownership and mode as the same directory from the source file-system, if
they share the same name.  So for example, if you have a
"link('/etc/apache2', '/shared/etc/apache2')", it will create "/shared/etc"
and "/shared/etc/apache2" with the same permissions/ownership.

Manual population: Create the directories specified by the "link" directives
in the configuration file and copy the appropriate files into them.


Now run "drbdlinks checklinks".  This will test the configuration file and
make sure all the specified links exist in the shared storage.

Now you just need to list "drbdlinks" in your resources, it needs to be
after the shared storage is mounted, but before any references to it are
used.  I usually bring it up immediately after the resource that mounts the
shared storage.

About Apache
------------

The easy route is to just set up all of "/etc/apache2" or "/etc/httpd" as
the directory that is linked.  However, this contains many sub-directories
or links that may best be left on the root file-system, so that updates
don't get the shared storage and the root file-system out of sync.

In particular, the links to Apache modules may become out of sync.

However, it also requires some discipline to ensure that all of the
configuration changes you make are not in system directories or files.  For
example, ideally you would customize the configuration only in the
"conf.d", "sites-available", "sites-enabled", and "mods-enabled"
directories.

I haven't yet tested these, but I'd propose you'd need to use the
following.

For RHEL/CentOS/Fedora:

    link('/etc/httpd/conf.d')
    link('/etc/httpd/conf/httpd.conf')
    link('/var/log/httpd')

For Debian/Ubuntu:

    link('/etc/apache2/mods-enabled')
    link('/etc/apache2/sites-enabled')
    link('/etc/apache2/sites-available')
    link('/etc/apache2/conf.d')
    link('/etc/apache2/ports.conf')
    link('/etc/apache2/envvars')
    link('/etc/apache2/apache2.conf')
    link('/var/log/apache2')

Please let me know if these values work or do not work for you.

OCF Resource
------------

drbdlinks can also be used as an OCF resource.  Following example could
contain RHEL/CentOS/Fedora specific paths and names, but should give an
impression how drbdlinks could be used in a Pacemaker cluster setup.  It
of course requires Corosync and Pacemaker configuration before, see the
ClusterLabs documentation for details.

Create a Pacemaker resource for DRBD resource "data", assumes existing
DRBD configuration:

    pcs cluster cib data_drbd_cfg
    pcs -f data_drbd_cfg resource create data_drbd ocf:linbit:drbd drbd_resource=data
    pcs -f data_drbd_cfg resource op add data_drbd start interval=0 timeout=120s
    pcs -f data_drbd_cfg resource op add data_drbd stop interval=0 timeout=60s
    pcs -f data_drbd_cfg resource op add data_drbd monitor role=Master interval=59s timeout=30s
    pcs -f data_drbd_cfg resource op add data_drbd monitor role=Slave interval=60s timeout=30s
    pcs -f data_drbd_cfg resource master data_clone data_drbd master-max=1 master-node-max=1 clone-max=2 clone-node-max=1 notify=true
    pcs cluster cib-push data_drbd_cfg

Filesystem resource to mount ext4 filesystem on /dev/drbd0 to /data (after
DRBD device got primary), assumes existing ext4 filesystem on DRBD device:

    pcs cluster cib data_fs_cfg
    pcs -f data_fs_cfg resource create data_fs ocf:heartbeat:Filesystem device="/dev/drbd0" directory="/data" fstype="ext4" op monitor interval=60s
    pcs -f data_fs_cfg constraint colocation add data_fs data_clone INFINITY with-rsc-role=Master
    pcs -f data_fs_cfg constraint order promote data_clone then start data_fs
    pcs cluster cib-push data_fs_cfg

Resource for drbdlinks to create symbolic links as per /etc/drbdlinks.conf;
on same node but after the filesystem was mounted, assumes proper drbdlinks
configuration before:
 
    pcs cluster cib drbdlinks_cfg
    pcs -f drbdlinks_cfg resource create drbdlinks ocf:tummy:drbdlinks op monitor interval=60s
    pcs -f drbdlinks_cfg constraint colocation add drbdlinks data_fs INFINITY
    pcs -f drbdlinks_cfg constraint order data_fs then drbdlinks
    pcs cluster cib-push drbdlinks_cfg

Apache resource that shall handle its configuration and log files on DRBD
partition (after drbdlinks was started):

    pcs cluster cib httpd_cfg
    pcs -f httpd_cfg resource create httpd systemd:httpd
    pcs -f httpd_cfg resource op add httpd monitor interval=60s timeout=30s
    pcs -f httpd_cfg resource op add httpd start interval=0 timeout=120s
    pcs -f httpd_cfg resource op add httpd stop interval=0 timeout=120s
    pcs -f httpd_cfg constraint colocation add httpd drbdlinks INFINITY
    pcs -f httpd_cfg constraint order drbdlinks then httpd
    pcs cluster cib-push httpd_cfg
