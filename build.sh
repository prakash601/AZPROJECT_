#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

# Download NLTK punkt data into a private, writable project-local dir
# (/opt/render/nltk_data is world-writable and rejected by the downloader)
export NLTK_DATA="$PWD/nltk_data"
mkdir -p "$NLTK_DATA"
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"

# Fetch the prebuilt ONNX graph + tokenizer of all-MiniLM-L6-v2 so the
# app never needs torch/transformers at runtime. Cached into models/.
python -c "
import os, shutil
from huggingface_hub import hf_hub_download

m = 'sentence-transformers/all-MiniLM-L6-v2'
out = 'models/onnx-minilm-l6-v2'
os.makedirs(out, exist_ok=True)
for src, dest in [('onnx/model.onnx', 'model.onnx'), ('tokenizer.json', 'tokenizer.json')]:
    f = hf_hub_download(m, src)
    shutil.copyfile(f, os.path.join(out, dest))
print('ONNX model + tokenizer cached.')
"

# Serve the SPA from the API if a frontend build exists
mkdir -p static
if [ -d frontend/dist ]; then cp -r frontend/dist/* static/; fi
