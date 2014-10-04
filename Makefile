test = nosetests --stop

.PHONY: check, checkpython, checkjava, clean

all:
	@echo Compilation unimplemented

check:
	@$(test)

checkpython:
	@$(test) test/pygen_test.py

checkjava:
	@$(test) test/javagen_test.py

clean:
	@rm -rf test/*.pyc src/*.pyc test_tmp out

