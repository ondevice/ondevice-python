FROM debian:jessie

WORKDIR /tmp/build/

RUN apt-get update && apt-get -y install devscripts

# create ondevice meta package
RUN mkdir -p /tmp/build/ondevice/
WORKDIR /tmp/build/ondevice/
COPY debian /tmp/build/ondevice/debian

RUN dpkg-buildpackage -us -uc

RUN tar cfz /tmp/build.tgz ../ondevice_*.deb
