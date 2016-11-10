ondevice client changelog
=========================

## v0.3.1 (2016-11-10)

Bugfix release:
- fixed some system-wide config issues
- fixed issue with overwriting the control socket (was set up outside the FileLock)
- explicitly calling chmod after writing to the various config files

## v0.3 (2016-11-10)

- added `ondevice.sock` UNIX socket
- added `/state` socket endpoint (shows info about the device daemon, current connections, etc.)
- reimplemented `ondevice status` to query `ondevice.sock` instead of making guesses about the daemon state
- we're sending ping messages through tunnels too
- added `--foreground` and `--configDir` arguments to `ondevice daemon`
- added support for setting the device authentiction using environment variables (in preparation of the ondevice-daemon debian package)

## v0.2.6

Bugfix release:
- fixed command line parsing issue in `ondevice list`

## v0.2.5
- improved `ondevice ssh`'s command line argument parsing
- added `ondevice rsync` (see #26)
- added `--props` option to `ondevice list`
- minor error handling improvements

## v0.2.4
- fixed issue with missing `~/.config/` directory (fixes #19)
- improved error and exception handling
- added `ondevice ssh` (replaces `ondevice :ssh`)
- deprecated `ondevice connecct` (at least for now, might come back once there's official support for custom modules)
- fixed missing user-agent header on REST requests
- hiding some of the not fully implemented and legacy commands from the `ondevice help` listing (for now)
- added `ondevice stop` to stop a running daemon
- added `ondevice status` to query the status of the ondevice daemon

## v0.2.3
- propagating the exit code of the ssh client in `ondevice :ssh` (fixes #18)

## v0.2.2
- setting the user-agent header on REST and websocket requests (fixes #17)
- fixed the tunnel not being closed properly (see #12)

## v0.2.1

Bugfix release:

- fixed issue in `ondevice setup` (see #15)
- fixed authentication issue (see #14)

## v0.2
- initial tracked release
