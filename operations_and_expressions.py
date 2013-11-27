#This file provides auxiliary functions used in the code generation
from write import *

# Writes arithmetic operations in assembly code. 
def writeOp(t1, op, t2):
   if (op == "*"):
      writeMov("rax", t2)
      write("\tmul ", t1, "\n")
      writeMov(t1, "rax")
   elif (op == "/"):
      writeMov("rax", t1)
      writeMov("rdx", "0")
      write("\tidiv ", t2, "\n")
      writeMov(t1, "rax")
   elif (op == "%"):
      writeMov("rax", t1)
      writeMov("rdx", "0")
      write("\tidiv ", t2, "\n")
      writeMov(t1, "rdx")
   else:
      write("\t", getOp(op), " ", t1, ", ", t2, "\n")

#Returns the jump to the end of condition according to the operator. 
def getJump(op):
   if(op == ">"):
      return "jle"
   elif(op == "<"):
      return "jge"
   elif(op == "<="):
      return "jg"
   elif(op == ">="):
      return "jl"
   elif(op == "=="):
      return "jne"
   elif(op == "!="):
      return "je"


#Returns the condition for the set command.
def getSet(op):
   if(op == ">"):
      return "l"
   elif(op == "<"):
      return "g"
   elif(op == "<="):
      return "le"
   elif(op == ">="):
      return "ge"
   elif(op == "=="):
      return "e"
   elif(op == "!="):
      return "ne"

#Generates the function corresponding to an operator.
def getOp(op):
   if(op == "+"):
      return "add"
   elif(op == "-"):
      return "sub"
   elif(op == "&"):
      return "and"
   elif(op == "*"):
      return "mul"
   elif(op == "%"):
      return "idiv"
   elif(op == "/"):
      return "idiv"
   elif(op == "|"):
      return "or"
   elif(op == "^"):
      return "xor"
   else:
      return op

#Tells what type it should print
def getPrintType(t):
   if (t == "INT"):
      return "writeInt"
   elif (t == "CHAR"):
      return "writeChar"
   elif (t == "STRING"):
      return "writeString"
   elif (t[0] == "\"" and t[len(t)-1] == "\""):
      return "writeInt"
   else:
      return "writeInt"
