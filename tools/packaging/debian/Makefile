DIRS=$(subst /,,$(wildcard */))

all:


phony:
	@true

build-%:
	cd '$*'; docker build -t 'ondevice/build-$*' .
	mkdir -p 'target/$*'
	cd 'target/$*'; docker run --rm -ti 'ondevice/build-$*' base64 /tmp/build.tgz | base64 -D | tar x

.PHONY: phony
