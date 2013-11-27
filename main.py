#!/usr/bin/python
import sys
import parsing
from lexer import *
import semantics
import preprocessing as PS
import code_generation as CG

def main(argv):
   malice_file = open(argv[1])
   malice_text = malice_file.read()
   alice_path = ""
   if(argv[1].find("/") != -1):
      alice_path = argv[1][:(argv[1].rindex("/")+1)]
   malice_text = PS.preprocess(malice_text, alice_path)


   parsingTree = parsing.getTree(malice_text).asList()
   lexer = Lexer()
   lexer.addMaliceTokens()
   parsingTree = lexer.replaceInTree(parsingTree)
   assemblyFile = argv[1][:(argv[1].rindex('.'))] + ".asm"
   if(semantics.check(parsingTree)):
      CG.generate(parsingTree, assemblyFile)

if __name__ == "__main__":
   main(sys.argv)
