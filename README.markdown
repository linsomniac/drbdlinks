DRBDLINKS README
================

Sean Reifschneider <jafo@tummy.com>  
Tuesday October 26, 2004  
drbdlinks is under the following license: GPLv2

Overview
--------

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
