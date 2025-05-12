#!/usr/bin/env fish

set -e

set ANTLR_JAR "antlr-4.13.1-complete.jar"
set INPUT_FILE "input.txt"
set ANTLR_OUT "ANTLR_p1.txt"
set SCANNER_OUT "tokens.txt"

echo "🔁 Cleaning old files..."
rm -f CMinus*.py $ANTLR_OUT $SCANNER_OUT

echo "⚙️ Running ANTLR on CMinus.g4..."
java -jar $ANTLR_JAR -Dlanguage=Python3 CMinus.g4

echo "📦 Activating virtual environment..."
source venv/bin/activate.fish

echo "📦 Running ANTLR-generated lexer..."
python3 run_antlr_lexer.py

echo "🧠 Running your custom scanner.py..."
python3 scanner.py

echo "🔍 Comparing outputs using check.py..."
python3 check.py
