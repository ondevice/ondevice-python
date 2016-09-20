FROM vicamo/debian:squeeze-i386

WORKDIR /tmp/build/

# squeeze isn't officially supported anymore, so not all mirrors have it
#RUN echo 'deb http://archive.debian.org/debian squeeze main' > /etc/apt/sources.list
RUN sed -i s/httpredir/archive/ /etc/apt/sources.list

RUN apt-get -o Acquire::Check-Valid-Until=false update || true
RUN apt-get -y install devscripts python-virtualenv git equivs python-dev


# build and install dh-virtualenv
RUN git clone https://github.com/mreithub/dh-virtualenv.git dh-virtualenv/
WORKDIR /tmp/build/dh-virtualenv/

RUN mk-build-deps -r -i -t 'apt-get -y'
RUN dpkg-buildpackage -us -uc -b
RUN dpkg -i ../dh-virtualenv_*.deb


# build and package ondevice
RUN git clone https://github.com/ondevice/ondevice-client.git /tmp/build/ondevice
WORKDIR /tmp/build/ondevice/
ENV DH_VIRTUALENV_INSTALL_ROOT=/opt/
COPY debian /tmp/build/ondevice/debian

RUN dpkg-buildpackage -us -uc

RUN tar cfz /tmp/build.tgz ../ondevice_*.deb
