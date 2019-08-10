DRBDLINKS=python ../drbdlinks

test:
	$(DRBDLINKS) meta-data | grep -iq '<shortdesc lang="en">Configuration Filename</shortdesc>'
	mkdir shared
	echo 'Shared file' >shared/testlink
	echo 'Local file' >testlink
	$(DRBDLINKS) -c drbdlinks.conf list
	$(DRBDLINKS) -c drbdlinks.conf start
	$(DRBDLINKS) -c drbdlinks.conf status
	$(DRBDLINKS) -c drbdlinks.conf checklinks
	grep -q 'Shared file' testlink
	$(DRBDLINKS) -c drbdlinks.conf stop
	grep -q 'Local file' testlink
	rm -f testlink
	rm -rf shared
