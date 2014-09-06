.PHONY: check, clean

check:
	@cd src; nosetests ../test

clean:
	@rm -rf test/*.pyc src/*.pyc out

