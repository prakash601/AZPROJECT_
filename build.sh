#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"

# Pre-export ONNX model during build and persist it where search.py
# expects it (models/onnx-minilm-l6-v2), so runtime boots use the
# fast cached path instead of re-exporting PyTorch -> ONNX.
python -c "
from optimum.onnxruntime import ORTModelForFeatureExtraction
from transformers import AutoTokenizer

m = 'sentence-transformers/all-MiniLM-L6-v2'
tok = AutoTokenizer.from_pretrained(m)
model = ORTModelForFeatureExtraction.from_pretrained(m, export=True)
model.save_pretrained('models/onnx-minilm-l6-v2')
tok.save_pretrained('models/onnx-minilm-l6-v2')
print('ONNX model exported and saved.')
"
