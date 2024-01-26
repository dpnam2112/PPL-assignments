.PHONY: build test clean

build:
	python3 run.py gen

test:
	python3 run.py test LexerSuite
	python3 run.py test ParserSuite

clean:
	rm -r test/solutions/*
	rm -r test/testcases/*
