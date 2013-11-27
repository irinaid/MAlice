#This file provides the functions for writing instructions to a file or strings
import code_generation
from sys import stdout

global assemblyFile
dataSection = "extern printf\nextern scanf\n\nsection .data\n\twriteInt db \"%d\", 0\n\twriteString db \"%s\", 0\n\twriteChar db \"%c\", 0\n\n\tscanInt db \"%d\", 0\n\tscanString db \"%s\", 0\n\tscanChar db \"%c\", 0\n"
mainSection = ""
textSection = "\nsection .text\n\tglobal main\n"
functionsSection = ""

#Writes strings into our assembly file.
def writeToFile(filePath):
   global assemblyFile
   global functionsSection
   global mainSection
   global dataSection
   global textSection
   assemblyFile = open(filePath, "w")
   assemblyFile.write(str(dataSection + textSection + mainSection + functionsSection))

#writes to the program section
def write(*strings):
   global functionsSection
   global mainSection
   for string in strings:
      string = str(string)
      if (getPart() == 0):
         mainSection += string
      if (getPart() == 1):
         functionsSection += string

#writes to the data section
def writeToDataSection(string):
   global dataSection
   dataSection += str(string)

def writeToTextSection(string):
   global textSection
   textSection += str(string)

#Writes the mov command into assembly code.
def writeMov(t1, t2):
   write("\tmov ", t1, ", ", t2, "\n")

def writeMovStart(t1, t2):
   global mainSection
   mov = "\tmov " + str(t1) + ", " + str(t2) + "\n"
   mainSection = mov + mainSection

def getMainSection():
   global mainSection
   return mainSection

def getFunctionSection():
   global functionsSection
   return functionsSection

def getDataSection():
   global dataSection
   return dataSection

def getPart():
   return code_generation.PART
