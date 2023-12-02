#!/bin/bash

PYTHON_SCRIPT_URL="https://raw.githubusercontent.com/knowl-doc/knowl-cli-temp/master/gen_apidocs.py"
ALIAS_NAME="knowl"

mkdir -p "$HOME/.knowl"
LOCAL_SCRIPT_PATH="$HOME/.knowl/gen_apidocs.py"

echo "Downloading the script..."
curl -o "$LOCAL_SCRIPT_PATH" "$PYTHON_SCRIPT_URL"

chmod +x "$LOCAL_SCRIPT_PATH"

echo "Adding alias to .bashrc..."
if [ -f "$HOME/.bashrc" ]; then
    echo "alias $ALIAS_NAME='python3 $LOCAL_SCRIPT_PATH'" >> $HOME/.bashrc
    echo "Alias $ALIAS_NAME added to .bashrc"
elif [ -f "$HOME/.bash_profile" ]; then
    echo "alias $ALIAS_NAME='python3 $LOCAL_SCRIPT_PATH'" >> $HOME/.bash_profile
    echo "Alias $ALIAS_NAME added to .bash_profile"
else
    echo "No .bashrc or .bash_profile found. Please manually add the alias."
fi

source $HOME/.bashrc

echo "Installation completed. You can now use 'knowl' to generate docs."
