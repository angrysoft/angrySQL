PREFIX = /usr

install:
	python3 setup.py -v sdist
	#python3 setup.py -v install --prefix=$(PREFIX) --record files.txt
