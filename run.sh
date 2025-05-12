#!/bin/bash

set -e

ANTLR_JAR="antlr-4.13.1-complete.jar"
INPUT_FILE="input.txt"
ANTLR_OUT="ANTLR_p1.txt"
SCANNER_OUT="tokens.txt"

echo "🔁 Cleaning old files..."
rm -f CMinus*.py $ANTLR_OUT $SCANNER_OUT

echo "⚙️ Running ANTLR on CMinus.g4..."
java -jar $ANTLR_JAR -Dlanguage=Python3 CMinus.g4

source ./venv/bin/activate

echo "📦 Running ANTLR-generated lexer..."
python3 run_antlr_lexer.py

echo "🧠 Running your custom scanner.py..."
python3 scanner.py

echo "🔍 Comparing outputs using check.py..."
python3 check.py
