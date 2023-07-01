from script.line import Translate
import argparse

if __name__ == '__main__':
    translate = Translate()
    translate.read_md_files('pages',model='gpt-4')	
	
