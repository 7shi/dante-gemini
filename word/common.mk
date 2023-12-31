SCRIPTS  = $(TOPDIR)/scripts
SRCDIR  ?= $(TOPDIR)/translate/$(LCODE)
INIT    ?= init.xml
COLUMNS ?=
OPTIONS ?=

init:
	python $(SCRIPTS)/init.py -n $(COLUMNS) -i $(INIT) $(LANG) $(SRCDIR)

test:
	python $(SCRIPTS)/init.py -t -i $(INIT) $(LANG) $(SRCDIR)

run:
	python $(SCRIPTS)/word.py $(OPTIONS) $(LANG) $(SRCDIR) $(INIT) .

check:
	python $(SCRIPTS)/pickup.py 1-error.xml */*.xml

fix:
	python $(SCRIPTS)/word-fix.py $(INIT)
