.PHONY: check, clean

check:
	nosetests --no-byte-compile

clean:
	@rm -rf test/*.pyc src/*.pyc out

