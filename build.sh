#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"