#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"

# Pre-download and convert ONNX model during build
python -c "from optimum.onnxruntime import ORTModelForFeatureExtraction; from transformers import AutoTokenizer; m='sentence-transformers/all-MiniLM-L6-v2'; AutoTokenizer.from_pretrained(m); ORTModelForFeatureExtraction.from_pretrained(m, export=True)"