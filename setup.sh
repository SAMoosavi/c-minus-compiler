#!/bin/bash

set -e

ANTLR_JAR="antlr-4.13.1-complete.jar"

echo "🔧 Creating virtual environment if not exists..."
python3 -m venv venv
source venv/bin/activate

echo "⬆️ Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing Python dependencies..."
pip install -r ./requirements.txt

if [ -f "$ANTLR_JAR" ]; then
  echo "✅ $ANTLR_JAR already exists, skipping download."
else
  echo "📥 Downloading ANTLR4 jar..."
  curl -O https://www.antlr.org/download/$ANTLR_JAR
fi

echo "🔧 Setting up aliases (will be added to ~/.bashrc if not present)..."
if ! grep -q "$ANTLR_JAR" ~/.bashrc; then
  echo "export CLASSPATH=\".:$(pwd)/$ANTLR_JAR:\$CLASSPATH\"" >>~/.bashrc
  echo "alias antlr4='java -jar $(pwd)/$ANTLR_JAR'" >>~/.bashrc
  echo "alias grun='java org.antlr.v4.gui.TestRig'" >>~/.bashrc
  echo "✅ Aliases added to ~/.bashrc"
else
  echo "✅ Aliases already configured in ~/.bashrc"
fi

echo "✅ Setup complete! Run 'source ~/.bashrc' to apply changes."
