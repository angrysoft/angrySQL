PREFIX = /usr

install:
	#python3 setup.py -v sdist
	python3 setup.py -v install --prefix=$(PREFIX) --record files.txt

clean:
	python3 setup.py clean
	rm -rf build
	rm -rf dist
	rm -rf angrySQL.egg-info
	rm -rf angrysql/__pycache__
