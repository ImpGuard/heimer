.PHONY: check, clean

check:
	@nosetests

clean:
	@rm -rf test/*.pyc src/*.pyc test_tmp out

