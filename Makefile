PYLINT = pylint
PYLINTFLAGS = -rn
PYTHONFILES := $(shell find . -name '*.py' -type f -print)

all: pylint

pylint: Makefile $(patsubst %.py,%.pylint,$(PYTHONFILES))

%.pylint:
	$(PYLINT) $(PYLINTFLAGS) $*.py

.PHONY: all pylint
