LANG    = Italian
TOPDIR  = ../..
SCRIPTS = $(TOPDIR)/scripts
SRCDIR  = $(TOPDIR)/it
INIT    = $(TOPDIR)/init/it.xml

all:

init:
	python $(SCRIPTS)/init.py -i $(INIT) $(LANG) $(SRCDIR)

test:
	python $(SCRIPTS)/init.py -t -i $(INIT) $(LANG) $(SRCDIR)

run:
	python $(SCRIPTS)/word.py $(LANG) $(SRCDIR) $(INIT) .

check:
	python $(SCRIPTS)/pickup.py 1-error.xml */*.xml

fix:
	python $(SCRIPTS)/word-fix.py $(INIT)
