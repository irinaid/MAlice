"""
   This extenssion provides preprocessing functionality to the compiler. The following 
   instructions:

   define X Y - replaces the occurances of X with Ys. This can be very efficient in defining
   constants

   import x - imports the file located at the path x

"""
from malicehelpers import promptErrorMessage
from re import sub
import sys
#Takes the file 
'''
   Returns a list of all the imports from a file
'''
def __getImports(lines):
   
   i = 0
   importedFiles = []
   while(i<len(lines) and lines[i].count("import")>0):
      if(lines[i].startswith("import")):
         aux = lines[i].split(" ")
         importedFiles.append(aux[1])
      i+=1

   return importedFiles

'''
   Returns a list of all the definitions from a file
'''

def __getDefinitions(lines):
   i = 0
   definitionsDict = {}
   while(i<len(lines)):
      if(lines[i].startswith("define")):
         aux = lines[i].split(" ")
         if definitionsDict.has_key(aux[1]):
            promptErrorMessage("Preprocessing error:",aux[1], "defined twice")
         definitionsDict.update({aux[1]:aux[2]})
      i+=1
   return definitionsDict

'''
   Clears the file from 'imports' and 'defines'
'''

def __clearFile(malice_file):
   malice_text = malice_file
   while(malice_text.count("import") or malice_text.count("define")):
      malice_text = malice_text[malice_text.index("\n")+1:]
   return malice_text

'''
   Checks (using the DFS algorithm) if the file has cyclic imports:
'''
def has_cyclic_imports(imp, file_path, viz):
   for i in imp:
      if viz.count(i) > 0:
         return True
      viz.append(i)
      iFile = open(file_path + i, "r").read()
      lines = iFile.split("\n")
      im = __getImports(lines)
      for j in im:
         imp.append(j)
   return False

'''
   The function where the whole preprocessing is done:
'''

def preprocess(malice_file, file_path):

   lines = malice_file.split("\n")
   imp  = __getImports(lines)
   defs = __getDefinitions(lines)
   
   malice_text = __clearFile(malice_file)
   for definition in defs:
      malice_text = sub("(?<![A-Za-z0-9_])" + definition + "(?![A-Za-z0-9_])", defs[definition], malice_text)
   if(has_cyclic_imports(imp, file_path, [])):
      promptErrorMessage("Preprocessing error: cyclic dependencies in imports detected")
   
   for imported_file in imp:
      myFile = open(file_path + imported_file, "r")
      file_text = myFile.read()
      file_text = preprocess(file_text, file_path)
      print "INDEX:", malice_file.index("The")
      print malice_text
      index = malice_text.index("The") - 1
      malice_text = malice_text[:index] + '\n' + file_text + '\n' + malice_text[index:]
      
   return malice_text

   
