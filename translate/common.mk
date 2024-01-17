TOPDIR  ?= ../..
SCRIPTS  = $(TOPDIR)/scripts
SRCDIR   = $(TOPDIR)/it
DIRSM    = {inferno,purgatorio,paradiso}
OPTIONS ?=

all: run check

run:
	python $(SCRIPTS)/translate.py $(OPTIONS) "$(LANG)" $(SRCDIR) .

check:
	python $(SCRIPTS)/pickup.py 1-error.xml $(DIRSM)/*.xml

fix:
	python $(SCRIPTS)/word-fix.py

split:
	python $(SCRIPTS)/split3.py $(DIRSM)/*.xml

redo:
	python $(SCRIPTS)/redo.py 1-error.xml

redo1:
	python $(SCRIPTS)/redo.py -1 1-error.xml

replace:
	python $(SCRIPTS)/replace.py 1-error-ok.xml $(DIRSM)/*.xml
