test = nosetests --stop

.PHONY: check, checkpython, checkjava, clean

all:
	@python src/compile/compile.py -s src -i compile/importFile -f compile/fileOrder out.py

check:
	@$(test)

checkpython:
	@$(test) tests/pygen_test.py

checkjava:
	@$(test) tests/javagen_test.py

clean:
	@rm -rf tests/*.pyc src/*.pyc test_tmp out.py

