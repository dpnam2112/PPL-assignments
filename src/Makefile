.PHONY:test clean

PROJ_DIR := ..
PYTHON_VENV := $(PROJ_DIR)/.env
TARGET_DIR := $(PROJ_DIR)/target
TEST_DIR := $(PROJ_DIR)/src/test
ANTLR_JAR := $(PROJ_DIR)/antlr-4.9.2-complete.jar
GRAM_FILE := $(PROJ_DIR)/src/main/zcode/parser/ZCode.g4

RECOGNIZER_SOLUTION_DIR := $(PROJ_DIR)/submit-recognizer
AST_GEN_SOLUTION_DIR := $(PROJ_DIR)/submit-ast-gen
CHECKER_SOLUTION_DIR := $(PROJ_DIR)/submit-checker
CODEGEN_SOLUTION_DIR := $(PROJ_DIR)/submit-codegen

PYTHON := python3

build-parser:
	$(MAKE) clean-target
	$(PYTHON) run.py gen

test: test-lexer test-parser test-ast-gen

test-lexer:
	$(PYTHON) run.py test LexerSuite

test-parser:
	$(PYTHON) run.py test ParserSuite

test-ast-gen:
	$(PYTHON) run.py test ASTGenSuite

test-static-checker:
	$(PYTHON) run.py test CheckerSuite

clean:
	rm -rf $(TARGET_DIR)/*
	rm -rf test/solutions/*
	rm -rf test/testcases/*

clean-target:
	rm -rf $(TARGET_DIR)/*

# These rules are used to gather all required files for submission.
submit-recognizer: build-parser
	mkdir -p $(RECOGNIZER_SOLUTION_DIR)
	cp $(PROJ_DIR)/src/main/zcode/parser/ZCode.g4 \
		$(PROJ_DIR)/src/test/LexerSuite.py \
		$(PROJ_DIR)/src/test/ParserSuite.py \
		$(TARGET_DIR)/main/zcode/parser/* \
		$(RECOGNIZER_SOLUTION_DIR)

submit-ast: build-parser
	mkdir -p $(AST_GEN_SOLUTION_DIR)
	cp $(PROJ_DIR)/src/main/zcode/parser/ZCode.g4 \
		$(PROJ_DIR)/src/main/zcode/astgen/ASTGeneration.py \
		$(PROJ_DIR)/src/test/ASTGenSuite.py \
		$(TARGET_DIR)/main/zcode/parser/* \
		$(AST_GEN_SOLUTION_DIR)
	
submit-checker:
	mkdir -p $(CHECKER_SOLUTION_DIR)
	cp $(PROJ_DIR)/src/main/zcode/checker/StaticCheck.py \
	$(PROJ_DIR)/src/test/CheckSuite.py \
	$(CHECKER_SOLUTION_DIR)

submit-codegen:
	mkdir -p $(CODEGEN_SOLUTION_DIR)
	cp $(PROJ_DIR)/src/main/zcode/codegen/CodeGenerator.py \
	$(PROJ_DIR)/src/main/zcode/codegen/Emitter.py \
	$(PROJ_DIR)/src/main/zcode/codegen/MachineCode.py \
	$(PROJ_DIR)/src/test/CodeGenSuite.py \
	$(CODEGEN_SOLUTION_DIR)
