ondevice.io client
==================

This is the official ondevice.io client.

``ondevice`` allows you to connect to all your devices from pretty much anywhere.


Installation
------------

You can install the client via python's ``pip`` command:

.. code::

    sudo pip3 install ondevice

**Important:** At the time of this writing ``ondevice connect`` doesn't fully work in python2, so make sure you install ``ondevice`` in python3 (e.g. using the ``pip3`` command (or similar).

Also make sure to install it as root.


After that you should be able to use it (note that you need an account on
https://ondevice.io/ though).

.. code::

  $ ondevice help
  USAGE: /usr/local/bin/ondevice <command> [args]

  - Device commands:
      daemon 
          Run the ondevice daemon
      service [add/rm] [args...]
          Manages services

  - Client commands:
      connect <module> <dev> [svcName]
          Connects to a service on the specified device (shorthand: `:<module>`)
      dev <devName> props/set/rm [args]
          Fetch/Manage a device's information
      list 
          Displays detailed information on your devices

  - Other commands:
      help [cmd]
          lists available commands or prints detailed help for one
      module 
          Lists installed modules
      setup 
          Set up the API keys for communicating with the ondevice.io service


Key setup
---------

After you've set up your ondevice.io account, you have to set up your API keys:

.. code::

  $ ondevice setup
  User: ondevUser
  API key: **********
  INFO:root:Updated client key (user: 'ondevUser')

After that you're good to go


Running the device daemon
-------------------------

simply run ``ondevice daemon``


List your devices (on the client)
---------------------------------

.. code::

  $ ondevice list|head
  ID                   State      IP              Version    Name
  ondevUser/abcdefghi  offline    127.0.0.1       0.1dev11   Raspberry Pi
  ondevUser/foobar123  online     10.0.0.2        0.1dev11   Home router
  ...


Connect to a device
-------------------

.. code::

  $ ondevice :ssh ondevUser/abcdefghi -l manuel
  manuel@ondevice:ondevUser/abcdefghi's password: 
  Linux raspberrypi 3.10.33+ #654 PREEMPT Fri Mar 7 16:32:08 GMT 2014 armv6l

  The programs included with the Debian GNU/Linux system are free software;
  the exact distribution terms for each program are described in the
  individual files in /usr/share/doc/*/copyright.

  Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
  permitted by applicable law.
  Last login: Mon Jul 25 17:08:43 2016 from localhost
  manuel@raspberrypi ~ $ 


Device properties
-----------------

For automation purposes, you can set custom properties for your devices.

.. code::

  $ ondevice device abcdefghi set foo=bar abc=123
  abc=123
  foo=bar

  $ ondevice device abcdefghi rm abc
  foo=bar

  $ ondevice device abcdefghi props
  foo=bar

  $ ondevice device abcdefghi set hello=world
  hello=world
  foo=bar

Each invocation returns the resulting property list; You can query the list using ``ondevice device <devId> props``

There's currently one special property:

- ``:desc``: set the device's description (will be shown online and in ``ondevice list``)


Requirements
------------

- python (with pip; the full functionality is currently only available on Python 3,
  but the device side should work on python2 as well)
- see requirements.txt for the actual list of python modules
