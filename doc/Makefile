SPHINXOPTS    ?= -W -E
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = ../generated/website/doc

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)