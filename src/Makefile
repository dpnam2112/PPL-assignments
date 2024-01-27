.PHONY:test clean

PROJ_DIR := ..
PYTHON_VENV := $(PROJ_DIR)/.env
TARGET_DIR := $(PROJ_DIR)/target
TEST_DIR := $(PROJ_DIR)/src/test
ANTLR_JAR := $(PROJ_DIR)/antlr-4.9.2-complete.jar
GRAM_FILE := $(PROJ_DIR)/src/main/zcode/parser/ZCode.g4

RECOGNIZER_SOLUTION_DIR := $(PROJ_DIR)/submit-recognizer

PYTHON := python3

build-parser:
	$(MAKE) clean-target
	$(PYTHON) run.py gen

test-recognizer:
	$(PYTHON) run.py test LexerSuite
	$(PYTHON) run.py test ParserSuite

test-lexer:
	$(PYTHON) run.py test LexerSuite

test-parser:
	$(PYTHON) run.py test ParserSuite

clean:
	rm -r $(TARGET_DIR)/*
	rm -r test/solutions/*
	rm -r test/testcases/*

clean-target:
	rm -r $(TARGET_DIR)/*

# These rules are used to gather all required files for submission.
submit-recognizer: build-parser
	mkdir -p $(RECOGNIZER_SOLUTION_DIR)
	$(PYTHON) run.py gen
	cp $(PROJ_DIR)/src/main/zcode/parser/ZCode.g4 \
		$(PROJ_DIR)/src/test/LexerSuite.py \
		$(PROJ_DIR)/src/test/ParserSuite.py \
		$(TARGET_DIR)/main/zcode/parser/* \
		$(RECOGNIZER_SOLUTION_DIR)

submit-ast:
	
submit-static-checking:

submit-bytecode-gen:
