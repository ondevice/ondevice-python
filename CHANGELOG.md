ondevice client changelog
=========================

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
