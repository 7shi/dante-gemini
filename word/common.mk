SCRIPTS  = $(TOPDIR)/scripts
SRCDIR  ?= $(TOPDIR)/translate/$(LCODE)
COLUMNS ?=
OPTIONS ?=

init:
	python $(SCRIPTS)/init.py -n $(COLUMNS) $(LANG) $(SRCDIR)

test:
	python $(SCRIPTS)/init.py -t $(LANG) $(SRCDIR)

run:
	python $(SCRIPTS)/word.py $(OPTIONS) $(LANG) $(SRCDIR) .

check:
	python $(SCRIPTS)/pickup.py 1-error.xml */*.xml

fix:
	python $(SCRIPTS)/word-fix.py
