#!/usr/bin/env just --justfile
set dotenv-load
set dotenv-filename := ".env.local"
default:
    just --list
venv:
    ./widgets/venv/Scripts/activate_nu.bat
srt2txt:
    cd tools
    python -c "from srt_to_txt import srt2txt;srt2txt('.tmp/Shape of You.srt')"
txt2lines:
    cd tools
    python -c "from txt_to_lines import txt2lines;txt2lines('.tmp/3.txt')"
pytest:
    pytest forread/tests

venv-install:
    echo "venv.... uv pip install inflect pytest pytest-asyncio textual-dev"
