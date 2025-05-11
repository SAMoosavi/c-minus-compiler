#!/bin/bash

source venv/bin/activate

java -jar antlr-4.13.1-complete.jar -Dlanguage=Python3 CMinus.g4
python3 scanner.py
