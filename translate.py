from script.translate import Translate
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("language", help="language to translate to",default="French")
args = parser.parse_args()

if __name__ == '__main__':
    language = args.language
    translate = Translate()
    translate.read_md_files('pages',language=language,model='gpt-4')	
	