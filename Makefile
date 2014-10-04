.PHONY: check, clean

check:
	@nosetests --stop

clean:
	@rm -rf test/*.pyc src/*.pyc test_tmp out

