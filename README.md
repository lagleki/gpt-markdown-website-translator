# FreeGPT Markdown Website Translator


## Install
Run the following command to clone the repository:  

```
git clone https://github.com/lagleki/gpt-markdown-website-translator.git
cd gpt-markdown-website-translator
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Create `.env` file and input `OPENAI_API_KEY=` value of your OpenAI key there.

## Prepare your book or website

* Put your markdown files into `pages/` folder. you may have subfolders inside it recursively.

## Run
* Run `python3 translate.py Russian` or put the name of any other language.
* The files will be translated, the original will be put into `.md!` files.

## Features from freegpt-webui

* Still available but might no longer work, see docs at https://github.com/ramonvc/freegpt-webui
