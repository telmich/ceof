WEBDIR=~/www.nico.schottelius.org/software

pub:
	git push --mirror
web:
	cp README.mdwn $(WEBDIR)/ceof.mdwn
	cd $(WEBDIR) && git add ceof.mdwn && git commit -m "Update ceof" ceof.mdwn
