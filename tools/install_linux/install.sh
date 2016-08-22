#!/bin/bash -e
#
# ondevice linux installer
#

_findCmd() {
	while (( "$#" )); do
		p="$(command -v "$1" 2>/dev/null)"
		if [ -n "$p" ]; then
			echo "$p"
			return 0
		fi
		shift
	done
	return 1
}

_isDistro() {
	grep -qis "$1"
}

_hasCmd() {
	command -v "$1" &>/dev/null
}

_aptHasPkg() {
	[ "$(apt-cache pkgnames "$pkgName" |grep "^$pkgName$"|wc -l)" -eq 1 ]
}

detectPython() {
	if [ -z "$PYTHON" ]; then
		PYTHON="$(_findCmd python3 python)"
	fi
	if [ -z "$PYTHON" ]; then
		return 1
	fi

	if [ -z "$PIP" ]; then
		PIP="$(_findCmd pip3 pip)"
	fi
	if [ -z "$PIP" ]; then
		return 1
	fi

	if [ -z "$VIRTUALENV" ]; then
		VIRTUALENV="$(_findCmd virtualenv)"
	fi
	if [ -z "$VIRTUALENV" ]; then
		return 1
	fi

	return 0
}

installPython_apt() {
	echo '== installing python using apt-get ==' >&2
	if _aptHasPkg python3-pip && _aptHasPkg python3-virtualenv; then
		apt-get -y install python3-pip python3-virtualenv
	else
		apt-get -y install python-pip python-virtualenv
	fi
}

installPython() {
	if detectPython; then
		echo "~~ found $PYTHON, $PIP ~~" >&2
		return
	fi

	if _isDistro "Debian GNU/Linux"; then
		installPython_apt "$@"
	elif _isDistro "Ubuntu"; then
		installPython_apt "$@"
	elif _hasCmd "apt-get"; then
		installPython_apt "$@"
	else
		echo "Error: Your linux distribution isn't supported (yet). Try installing using pip directly" >&2
		echo "(and file an issue report if there isn't any)" >&2
		exit 1
	fi

	if ! detectPython; then
		echo "!! Failed to detect python/pip !!" >&2
		exit 1
	fi
}

installOndevice() {
	if ! detectPython; then
		echo "python/pip/virtualenv missing!!!" >&2
		exit 1
	fi

	"$VIRTUALENV" -p "$PYTHON" /usr/local/lib/ondevice
	. /usr/local/lib/ondevice/bin/activate

	if [ "python3" = "$(basename "$PYTHON")" ]; then
		pip install --upgrade ondevice
	else
		# if we're still on python2, use python-daemon==1.5.5 (since the current version isn't compatible to py2.6)
		pip install --upgrade ondevice python-daemon==1.5.5
	fi

	deactivate

	# create wrapper script in /usr/local/bin/
	WRAPPER=/usr/local/bin/ondevice
	if [ -x "$WRAPPER" ]; then
		echo "~~ Not creating '$WRAPPER', already exists ~~" >&2
		return
	fi

	cat >> "$WRAPPER" <<EOF
#!/bin/bash -e

/usr/local/lib/ondevice/bin/ondevice "\$@"
EOF
	chmod +x "$WRAPPER"
}

installPython
installOndevice
