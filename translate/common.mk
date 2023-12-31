SCRIPTS  = $(TOPDIR)/scripts
SRCDIR   = $(TOPDIR)/it
OPTIONS ?=

run:
	python $(SCRIPTS)/translate.py $(OPTIONS) $(LANG) $(SRCDIR) .

check:
	python $(SCRIPTS)/pickup.py 1-error.xml */*.xml

fix:
	python $(SCRIPTS)/word-fix.py
