FROM vicamo/debian:jessie-i386

WORKDIR /tmp/build/

RUN apt-get update && apt-get -y install devscripts python-virtualenv python3-virtualenv git equivs python3-dev

# build and install dh-virtualenv
# TODO use the prepackaged version
RUN git clone https://github.com/spotify/dh-virtualenv.git
WORKDIR /tmp/build/dh-virtualenv/
RUN mk-build-deps -r -i -t 'apt-get -y'
RUN dpkg-buildpackage -us -uc -b
RUN dpkg -i ../dh-virtualenv_*.deb

# build and package ondevice (install to /opt/ondevice/)
RUN git clone https://github.com/ondevice/ondevice-client.git /tmp/build/ondevice/
WORKDIR /tmp/build/ondevice/
ENV DH_VIRTUALENV_INSTALL_ROOT=/opt/
COPY debian /tmp/build/ondevice/debian

RUN dpkg-buildpackage -us -uc

RUN tar cfz /tmp/build.tgz ../ondevice_*.deb
