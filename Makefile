.PHONY: all assemble test clean

all: assemble test

assemble:
	python assembler.py test_all.asm test_all.bin
	python assembler.py vector_shift.asm vector_shift.bin
	python assembler.py arithmetic.asm arithmetic.bin

test:
	@echo "Running all tests..."
	python run_tests.py

run_test_all:
	python interpreter.py test_all.bin test_dump.csv 0-50

run_vector_shift:
	python interpreter.py vector_shift.bin vector_dump.csv 500-2010

run_arithmetic:
	python interpreter.py arithmetic.bin arithmetic_dump.csv 1000-1010

clean:
	rm -f *.bin *.csv *.pyc __pycache__/*

help:
	@echo "Available commands:"
	@echo "  make assemble   - Assemble all test programs"
	@echo "  make test       - Run all tests"
	@echo "  make clean      - Clean generated files"
