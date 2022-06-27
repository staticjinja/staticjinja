# Generic makefile for staticjinja supporting static folders

# Config vars
# directory to put the rendered site
OUTPATH = build

# directory containing template files
SRCPATH = templates
# directory containing static files
STATICPATH = static

# extra files that will trigger a template build when modified.
EXTRAS =

# command to run staticjinja build.
# Set to "./build.py" if you have a custom script
STATICJINJA = staticjinja build --srcpath $(SRCPATH) --outpath $(OUTPATH)

# End config vars

# This makefile starts by finding all the static files and resolving them to
# the proper output location. I use find here because $(wildcard $(D)/**/*)
# doesn't catch direct children.
#
# It then does the same for the templates. Not all the templates produce an
# output, so another list is created excluding those and is resolved to the
# proper output location.
#
# When a static file changes, it triggers rsync to copy everything to the
# output folder. When a template or defined extra file changes, it triggers
# staticjinja to run using the configured executable.

STATIC_INPUT := $(foreach D,$(STATICPATH),$(shell find $(D) -type f))
STATIC_OUTPUT := $(patsubst $(STATICPATH)/%,$(OUTPATH)/%,$(STATIC_INPUT))

# includes all files as input
TEMPLATE_INPUT := $(foreach D,$(SRCPATH),$(shell find $(D) -type f))
# only find renderable files
TEMPLATE_PUBLIC := $(foreach D,$(SRCPATH),$(shell find $(D) -type f -name "[^_.]*"))
TEMPLATE_OUTPUT := $(patsubst $(SRCPATH)/%,$(OUTPATH)/%,$(TEMPLATE_PUBLIC))

.PHONY: clean all

all: $(OUTPATH)

# the main target
$(OUTPATH): $(STATIC_OUTPUT) $(TEMPLATE_OUTPUT)
# Run something, otherwise it defaults to cat build.sh >build
	@echo

# copy static files
$(STATIC_OUTPUT): $(STATIC_INPUT)
	rsync -r $(STATICPATH)/* $(OUTPATH)/

# render the templates
$(TEMPLATE_OUTPUT): $(TEMPLATE_INPUT) $(EXTRAS)
	$(STATICJINJA)

# clean up after ourselves
clean:
	rm -r $(OUTPATH)
