SCRIPTS  = $(TOPDIR)/scripts
SRCDIR  ?= $(TOPDIR)/translate/$(LCODE)
INITOPT ?=
OPTIONS ?=

init:
	python $(SCRIPTS)/init.py $(INITOPT) $(LANG) $(SRCDIR)

test:
	python $(SCRIPTS)/init.py -t $(LANG) $(SRCDIR)

run:
	python $(SCRIPTS)/word.py $(OPTIONS) $(LANG) $(SRCDIR) .

check:
	python $(SCRIPTS)/pickup.py 1-error.xml */*.xml

fix:
	python $(SCRIPTS)/word-fix.py
