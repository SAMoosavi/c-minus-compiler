#!/usr/bin/env fish

set -e

set ANTLR_JAR "antlr-4.13.1-complete.jar"

echo "🔧 Creating virtual environment if not exists..."
python3 -m venv venv
source venv/bin/activate.fish

echo "⬆️ Upgrading pip..."
pip install --upgrade pip

echo "📦 Installing Python dependencies..."
pip install -r ./requirements.txt

if test -f $ANTLR_JAR
    echo "✅ $ANTLR_JAR already exists, skipping download."
else
    echo "📥 Downloading ANTLR4 jar..."
    curl -O https://www.antlr.org/download/$ANTLR_JAR
end

set CONFIG_PATH ~/.config/fish/config.fish

echo "🔧 Setting up aliases in $CONFIG_PATH..."
if not grep -q $ANTLR_JAR $CONFIG_PATH
    echo "set -gx CLASSPATH \".:(pwd)/$ANTLR_JAR:\$CLASSPATH\"" >>$CONFIG_PATH
    echo "alias antlr4='java -jar (pwd)/$ANTLR_JAR'" >>$CONFIG_PATH
    echo "alias grun='java org.antlr.v4.gui.TestRig'" >>$CONFIG_PATH
    echo "✅ Aliases added to $CONFIG_PATH"
else
    echo "✅ Aliases already configured in $CONFIG_PATH"
end

echo "✅ Setup complete! Run 'source ~/.config/fish/config.fish' to apply changes."
