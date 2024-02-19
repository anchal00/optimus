# !/usr/bin/bash
echo -e "Packaging optimus :) ...\n\n"
python -m build .
echo -e "Installing optimus...\n\n"
pip install dist/optimus-1.0.tar.gz
echo "optimus installed successfully..."
