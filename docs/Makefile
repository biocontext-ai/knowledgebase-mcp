# Minimal makefile for Sphinx documentation

.DEFAULT_GOAL := build-docs

# You can set these variables from the command line.
SPHINXOPTS    ?=
SPHINXBUILD   = python3 -m sphinx
SPHINXPROJ    = biocontext_kb
SOURCEDIR     = source
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

build-docs: clean

# Build html
	make html

.PHONY: help Makefile

clean:
	rm -rf "$(BUILDDIR)"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
