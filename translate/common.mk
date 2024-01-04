TOPDIR  ?= ../..
SCRIPTS  = $(TOPDIR)/scripts
SRCDIR   = $(TOPDIR)/it
OPTIONS ?=

all: run check

run:
	python $(SCRIPTS)/translate.py $(OPTIONS) "$(LANG)" $(SRCDIR) .

check:
	python $(SCRIPTS)/pickup.py 1-error.xml */*.xml

fix:
	python $(SCRIPTS)/word-fix.py
