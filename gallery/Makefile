TOPDIR = ..
SCRDIR = $(TOPDIR)/scripts

define generate_gallery
	echo $$d; \
	mkdir -p $(1)/{inferno,purgatorio,paradiso}; \
	for f in inferno/{01..34} purgatorio/{01..33} paradiso/{01..33}; do \
		if [ -f $(TOPDIR)/word/$(1)/$$f.xml -a ! -f $(1)/$$f.md ]; then \
		  (python $(SCRDIR)/gallery.py -l $(1) -f $$f.xml $(TOPDIR) > $(1)/$$f.md); \
		fi; \
	done
endef

all:
	for d in `cd $(TOPDIR)/word; echo ?? ???`; do \
		$(call generate_gallery,$$d); \
	done

clean:
	rm -rf ??/ ???/
