
all:
	echo '-- usage: make pypi-publish --'

pypi-publish: clean
	./setup.py sdist
	twine upload dist/*

clean:
	rm -rf build/ dist/
