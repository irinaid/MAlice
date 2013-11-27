from sys import stdout
from evaluate_expression import *
from operations_and_expressions import *
from write import *

regs = ["r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]
relational_ops = [ ">", ">=", "<", "<=", "!=", "=="]

allocationTable = {}
globalTable = {}
stack = []
BYTE_SIZE = 8
IF_NUMBER = 0
WHILE_NUMBER = 0
program = []
functions = []
PART = 0 
STRING_COUNT = 0


# Starts generating the assembly code.
def generate(tree, filePath):
   global stack
   global program
   global regs
   global printf 
   global scanf
   global PART
   tree = cleanList(tree)
   stopPoint = 0 
   while (tree[stopPoint][0] == "DECL"):
      globalDecl(tree[stopPoint])
      stopPoint += 1
   if (tree[0] == "MAINF"):
      tree = [tree]
   for i in range(stopPoint, len(tree)):
      branch = tree[i]
      key = branch[0]
      if (key == "MAINF"):
         PART = 0
         genMain(branch)
      elif (key == "VOIDF"):
         PART = 1
         genVoid(branch)
      elif (key == "TYPEF"):
         PART = 1
         genType(branch)
   writeToFile(filePath)


# Generates the main function.
def genMain(tree):
   global PART
   PART = 0 
   block = tree[4][1]
   stack.append("__main_")
   write("main:\n")
   genBlock(block)
   PART = 0 
   write("\tret\n")
   stack.pop()


#Generates the code for a void function or an inner void/main (hatta) function
def genVoid(tree):
   global PART
   PART = 1
   if (tree[0] == "MAINF"):
      block = tree[4][1]
      args = tree[2]
      name = "hatta"
   else:
      block = tree[5][1]
      args = tree[3]
      name = tree[1]
   stack.append("__" + name + "_")
   write("\n_" + name + ":\n")
   write("\tpush rbp\n")
   write("\tmov rbp, rsp\n")
   if (len(args) > 0):
      getFunctionArgs(tree)
   genBlock(block)   
   stack.pop()
   write("\tpop rbp\n")
   write("\tret\n")
   PART = 0


# Generates instructions equivalent to a type function
def genType(tree):
   global PART
   global BYTE_SIZE
   global regs
   PART = 1
   stack.append("__" + tree[1] + "_")
   write("_"+tree[1]+":\n")
   args = tree[3]
   if (len(args) > 0):
      getFunctionArgs(tree)
   block = tree[7][1]
   genBlock(block)
   write("\tpop rbp\n")
   write("\tret\n")
   stack.pop()
   PART = 0


# Gets the arguments of a function and places them in registers
def getFunctionArgs(tree):
   args = tree[3]
   if (not type(args[0]) is list):
      args = [(args)]
   write("\tpush rbp\n")
   write("\tmov rbp, rsp\n")
   rbp_count = len(args)*BYTE_SIZE + BYTE_SIZE
   prefix = "__" + tree[1] + "_"
   for arg in args:
      aux_reg = regs.pop()
      var = prefix + arg[1]
      allocationTable.update({var:("[rbp+"+
            str(rbp_count)+"]", arg[2])})
      rbp_count -= BYTE_SIZE


# Assigns a value to a local variable. 
def genAssign(tree):
   global stack
   global allocationTable
   global regs 
   global STRING_COUNT
   # If it's a global variable, we need an extra mov
   if (tree[1] in globalTable and
         getScopePlusVar(tree[1]) == tree[1]):
      reg = regs.pop()
      writeMov(reg, 
         genExpr(tree[2], getRegisterInScope(tree[1])))     
      writeMov(getRegisterInScope(tree[1]), reg)
   else: 
      # If the value is a string, declare it in the data section
      if (isString(cleanToFirstValue(tree[2]))):
         comp = getRegisterInScope(tree[1])
         if (not comp in allocationTable or comp != comp.__getitem__(0)):
               value = cleanToFirstValue(tree[2])[1:-1]
               writeToDataSection("\t"+tree[1]+" dd `"+
                        str(value)+"`,0\n")
               writeMov(getRegisterInScope(tree[1]), tree[1])
               return
         value = cleanToFirstValue(tree[2])[1:-1]
         writeToDataSection("\t"+tree[1]+" dd `"+
                        str(value)+"`,0\n")
         if (getRegisterInScope(tree[1]) == ""):
            reg = tree[1]
            writeMov(regs.pop(), tree[1])
         else:
            reg = getRegisterInScope(tree[1])
         writeMov(regs.pop(), getRegisterInScope(tree[1]))
      # If it's a char or int, just put it in a register directly
      else:
         reg = getRegisterInScope(tree[1])
         value = genExpr(tree[2], reg)
         if (reg != value):
            writeMov(reg, value)


# Allocates a register to the new variable by inserting it in the
# table with the given name in scope.
# If the declaration also includes assignment, evaluate the
# expression and assign it. 
def genDecl(tree):
   global stack
   global allocationTable
   global regs
   varName = getAllStack() + tree[1]
   regName = regs.pop()
   typeVar = tree[2]
   allocationTable.update({varName:(regName, typeVar)})
   if (len(tree) == 5):
      genAssign(["ASSIGN", tree[1], tree[4]])
   return regName


# Global variables
def globalDecl(tree):
   global allocationTable
   global globalTable
   if (tree[2] == "STRING"):
      allocationTable.update({tree[1]:(tree[1], tree[2])})
      if (len(tree) == 3):
         if (not tree[1] in allocationTable and
            tree[1] != allocationTable[tree[1]].__getitem__(0)):        
            genAssign(["ASSIGN", tree[1], "0"])
      else:
         genAssign(["ASSIGN", tree[1], tree[4]])
      return
   writeToDataSection("\t" + tree[1] + " dd")
   writeToDataSection(" 0\n")
   allocationTable.update({tree[1]:("["+tree[1]+"]", tree[2])})
   globalTable.update({tree[1]:(0, tree[2])})
   if (len(tree) > 3):
      genAssign(["ASSIGN", tree[1], tree[4]])


# Generates a block of code into assembly code.
def genBlock(tree):
   global regs
   global stack
   global allocationTable
   if (not type(tree[0]) is list):
      tree = [tree]
   for t in tree:
      if(t[0] == "OPEN"):
         stack.append("_scope_")
         genBlock(t[1])
         stack.pop()
      if(t[0] == "DECL"):
         genDecl(t)
      elif(t[0] == "ASSIGN"):
         genAssign(t)
      elif(t[0] == "IF"):
         genIf(t)
      elif(t[0] == "WHILE"):
         genWhile(t)
      elif(t[0] == "PRINT"):
         genPrint(t) 
      elif(t[0] == "RET"):
         genRet(t)
      elif(t[0] == "DEC" or t[0] == "INC"):
         genIncDec(t)
      elif(t[0] == "READ"):
         genRead(t)
      elif(t[0] == "FULLSTOP"):
         continue
      elif(t[0] == "MAINF"):
         stack.append("__hatta_")
         genVoid(t)
         stack.pop()
      elif(t[0] == "TYPEF"):
         stack.append("__" + t[1] + "_")
         genType(t)
         stack.pop()
      elif(t[0] == "VOIDF"):
         stack.append("__" + t[1] + "_")
         genVoid(t)
         stack.pop()
      elif(t[1] == "LPAREN" and type(t[2]) is list and 
            t[3] == "RPAREN" and (not (t[0] == "IF"))
            and (not (t[0] == "WHILE"))):
         genFunctionCall(t)


# Print function in assembly.
def genPrint(tree):
   global allocationTable
   global regs
   global stack
   global STRING_COUNT
   value = tree[1]
   varStart = ""
   printType = ""
   # If we want to print a function call
   if (type(tree[1]) is list and len(tree[1]) == 4 and 
      tree[1][1] == "LPAREN" and tree[1][3] == "RPAREN"):
      genFunctionCall(tree[1])
      reg = regs.pop()
      writeMov(reg, "rax")
      varStart = reg
      printType = "writeInt"
      regs.append(reg)
   # If we want to print a value directly
   elif (getRegisterInScope(cleanToFirstValue(value)) == "" 
         and isValue(value)):
      # Special case for printing a string
      if (isString(cleanToFirstValue(value))):
         value = cleanToFirstValue(tree[1])[1:-1]
         writeToDataSection("\ts"+str(STRING_COUNT)+" dd `"+
                        str(value)+"`, 0\n")
         allocationTable.update({"s"+str(STRING_COUNT):(value, "STRING")})
         varStart = "s"+str(STRING_COUNT)
         printType = getPrintType("STRING")
         STRING_COUNT += 1
      else:
         varStart = cleanToFirstValue(value)
         printType = getPrintType(value)
   # If we want to print a variable content
   elif (len(value) == 1 and 
         getRegisterInScope(cleanToFirstValue(value)) != ""):
      value = getScopePlusVar(value)
      printType = allocationTable[value].__getitem__(1)
      printType = getPrintType(printType)
      varStart = getRegisterInScope(value)
   elif (len(value) > 1):
      # Multiple cases, should use genExpr
      varStart = genExpr(value, varStart)
      printType = "writeInt"
   writeMov("rax", "0")
   writeMov("rsi", varStart)
   writeMov("rdi", printType)
   write("\tcall printf\n")


def genRet(tree):
   global regs
   # If the function returns a negative variable
   if (type(tree[1]) is list and tree[1][0] == "-"):
      tree[1] = genExpr(tree[1], "rax")
      negate(tree[1], "rax")
   # If the function returns not value
   elif (type(tree[1]) is list and tree[1][0] == "~"):
      reg = regs.pop()
      writeMov(reg, getRegisterInScope(tree[1][1]))
      write("\tnot " + reg + "\n")
      writeMov("rax", reg)
      regs.append(reg)
   else:
      tree = cleanList(tree)
      # If the function returns 
      if (len(tree) > 1):     
         to_return = getScopePlusVar(tree[1])
         if (to_return != ""):
            to_return = allocationTable[to_return]       
            to_return = to_return.__getitem__(0)
            if (to_return[0] == "["):
               aux_reg = regs.pop()
               writeMov(aux_reg,to_return)
               to_return = aux_reg
               regs.append(aux_reg)
         else:
            to_return = tree[1]
         writeMov("rax", to_return)


# Reads input using gcc function scanf
def genRead(tree):
   global STRING_COUNT
   var = getScopePlusVar(tree[1])
   scanType = allocationTable[var].__getitem__(1)
   reg = allocationTable[var].__getitem__(0)
   write("\txor rax, rax\n")
   writeMov("rdi", getPrintType(scanType))
   pointer = "s" + str(STRING_COUNT)
   writeToDataSection("\t" + pointer + " db 0\n")
   writeMov("rsi", pointer)
   write("\tcall scanf\n")
   writeMov("rbx", "[" + pointer + "]")
   writeMov(reg, "rbx")
   STRING_COUNT += 1


# Generates the operations to calculate the value of an expression
def genExpr(tree, startVar):
   global regs
   if (startVar == ""):
      startVar = regs.pop()
   if (len(tree) == 1):
      if (isValue(tree)):
         return cleanToFirstValue(tree)
   elif (len(tree) == 2):
      reg = getRegisterInScope(cleanToFirstValue(tree[1]))
      if (reg == ""):
         reg = cleanToFirstValue(tree[1])
      if (tree[0] == "~"):
         writeMov(startVar, reg)
         write("\tnot ", startVar, "\n")
         return startVar
      elif(tree[0] == "-"):
         writeMov(startVar, reg)
         write("\tneg ", startVar, "\n")
         return startVar
   #solve subExpressions of current expression
   #and replace the variables with their values
   for i in range(len(tree)):
      if (len(tree[i]) > 1):
         newStartVar = regs.pop()
         tree[i] = genExpr(tree[i], newStartVar)
      else:
         #!!This if below might cause trouble, it should actually
         #check that tree[i] is not an operand
         if (i%2 == 0):
            #If I have a value in my expression, e.g. x + 2
            if (isValue(tree[i])):
               tree[i] = cleanToFirstValue(tree[i])
            else:

               tree[i] = getRegisterInScope(tree[i])
   #solve this expression
   writeMov(startVar, tree[0])
   while (len(tree) >= 3):
      writeOp(startVar, tree[1], tree[2])
      tree = tree[2:]
   return startVar


# Inc, Dec
def genIncDec(tree):
   global allocationTable
   if(tree[0] == "DEC"):
      op = "dec"
   else: 
      op = "inc"
   write("\t", op, " ", 
         allocationTable[getScopePlusVar(tree[1])].__getitem__(0), "\n")


# Generates a function call
def genFunctionCall(tree):
   global BYTE_SIZE
   args = tree[2]
   if (len(args) == 1):
      args = [args]
   if (len(args) == 0):
      write("\tcall _" + tree[0] + "\n") 
   else:
      for arg in args:
         var = getScopePlusVar(arg)
         # If argument is a variable
         if (var != ""):
            var = allocationTable[var].__getitem__(0)
         # If it's a value
         else:
            arg = cleanToFirstValue(arg)
            declTree = ["DECL", cleanToFirstValue(arg)]
            if (isString(arg)):
               declTree.append('STRING')
            elif (isChar(arg)):
               declTree.append('CHAR')
            else:
               declTree.append('INT')
            var = genDecl(declTree)
         write("\tpush " + var + "\n")
      write("\tcall _" + tree[0] + "\n")
      write("\tadd rsp, " + str(BYTE_SIZE*len(args)) + "\n") 
      

#Put in a variable the negative value of it
def negate(tree, startVar):
   #Check tree is well formed
   if (len(tree) == 2 and tree[0] == '-'):
      sign = tree[0]
      variable = tree[1][0]
      #If the value is already in a register
      reg = getScopePlusVar(tree[1])
      if (reg != ""):
         writeMov(startVar, reg)
         write("\tneg ", startVar, "\n")
      #Else put the value in the register and negate it
      else:
         writeMov(startVar, tree[1][0])
         write("\tneg ", startVar, "\n")


################# IF, WHILE ######################

#Generates a while loop in assembly.
def genWhile(tree):
   global WHILENUMBER
   WHILENUMBER += 1
   whileNumber = str(WHILENUMBER)
   write("while",whileNumber, ":\n")
   #Genetars the condition.
   genBoolExpr(tree[2])
   #Jumps at the end of while is it doesn't
   write("endWhile",whileNumber,"\n")
   #Generates the body of the while loop.
   genBlock(tree[4])
   #Writes the label for the end of the loop.
   write("\nendWhile",whileNumber,":\n")


#IF 1 1
def genIf2(tree, ifNumber):
   global regs
   global IF_NUMBER
   IF_NUMBER += 1
   y = str(IF_NUMBER)
   write("\nif", y, ":\n")    
   if(tree[0] == "ELSE"):
      genBlock(tree[1])
   elif(tree[0] == "ELSE_IF"):
      genBoolExpr(tree[2])
      if(tree[6] != "ENDIF"):
      #IF NOT TRUE. JUMP NEXT IF
         y = str(IF_NUMBER + 1)
         write("if", y , "\n")   
      else:
      #If not true, jump endIf
         write("endIf", ifNumber)      
      genBlock(tree[5])
      #IF TRUE, JUMP ENDIF
      write("\n\tjmp endIf", ifNumber, "\n") 
      if(tree[6] != "ENDIF"):
         genIf2(tree[7:], ifNumber)


#Generates boolean expressions if the initial condition is too complex. 
def genBoolExpr2(tree):
   global relational_ops
   global IF_NUMBER
   global regs
   ifNumber = str(IF_NUMBER)
   IF_NUMBER += IF_NUMBER
   write("\ncond", ifNumber, ":\n")
   #If the three has length 3 and the second element is a relational operator
   if(len(tree) == 3 and tree[1] in relational_ops):
      varStart1 = regs.pop()
      genExpr(tree[0], getAllStack(), varStart1)
      varStart2 = regs.pop()
      genExpr(tree[2], getAllStack(), varStart2)
      write("\n\tcmp ",varStart1, ", ", varStart2,"\n")  
      write("\tset",getSet(tree[1]), " al")
      #Restore the registers used
      regs.append(varStart1)
      regs.append(varStart2)
   elif(len(tree) > 1):  
      if(tree[1] == "&&"):
         genBoolExpr2(tree[0])
         register = regs.pop()
         write("\n\tmovzx ",register ,", al\n")
         write("\tcmp ", register, ", 1\n")
         #If the condition is false, then jump at the end of 
         #the condition with al = 0. 
         write("\n\tjne endCond", ifNumber , "\n")
         #Restore the register used
         regs.append(register)
         genBoolExpr2(tree[2:])
      elif(tree[1] == "||"):
         genBoolExpr2(tree[0])
         register = regs.pop()
         write("\n\tmovzx ",register, ", al\n")
         write("\tcmp ", register, ", 1\n")
         #If the condition is true, then jump at the end of 
         #the condition with al = 1. 
         write("\n\tje endCond", ifNumber, "\n")
         #Restore the register used
         regs.append(register)
         genBoolExpr2(tree[2:])  
      elif(tree[0] == "!"):
         genBoolExpr2(tree[1:])
         register = regs.pop()
         write("\n\tmovzx ",register, ", al\n")
         write("not ", register)
         write("cmp ", register, ", 1")
         write("\n\tjne endCond", ifNumber , "\n")
         #Restore the register used
         regs.append(register)
   write("\nendCond",ifNumber, ":\n")


#Generates a boolean expression.
def genBoolExpr(tree):
   global relational_ops
   global IF_NUMBER
   global regs
   #If the three has length 3 and the second element is a relational operator
   if(len(tree) == 3 and tree[1] in relational_ops):
      varStart1 = regs.pop()
      genExpr(tree[0],  varStart1)
      varStart2 = regs.pop()
      genExpr(tree[2],  varStart2)  
      write("\n\tcmp ",varStart1, ", ", varStart2,"\n")  
      write("\t", getJump(tree[1]), " ")
      #Restore the registers used
      regs.append(varStart1)
      regs.append(varStart2)
   #If the expression is of type !=, etc
   elif(len(tree)==2 and tree[0] == "!"):
      genBoolExpr2(tree[1])
      register = regs.pop()
      write("\n\tmovzx ",register, ", al\n")
      write("not ", register)
      write("cmp ", register, ", 1")
      write("\n\tjne ")
      #Restore the register used
      regs.append(register)
   else:
      genBoolExpr2(tree)
      register = regs.pop()
      write("\n\tmovzx ",register, ", al\n")
      write("cmp ", register, ", 1")
      write("\n\tjne ")
      #Restore the registers used
      regs.append(register)

   
#IF 1
def genIf(tree):
   global regs
   global IF_NUMBER
   IF_NUMBER += 1
   ifNumber = str(IF_NUMBER)
   #IF 1
   write("\nif", ifNumber, ":\n")
   genBoolExpr(tree[2])
   #If the condition doesn't hold, JUMP 
   if(tree[6] == "ENDIF"):
      write("endIf", ifNumber,  "\n")
   else:
      innerIf = (IF_NUMBER + 1)
      y = str(innerIf)
      write("if", y , "\n")
   genBlock(tree[5])
   #JUMP TO ENDIF 1
   write("\n\tjmp endIf", ifNumber)
   #Else and else_if
   if(tree[6] != "ENDIF"):
      genIf2(tree[6:], ifNumber)
   #ENDIF
   write("\nendIf", ifNumber,":\n" )


##########Auxiliary functions#############
# Auxiliary functions using the global variables, mainly for type checking 
# and handling lists

# Gets current scope on stack.
def getAllStack():
   st = ""
   for s in stack:
      st+=s
   return st

# Gets the inner most scope a variable is being found in + the variable
# or an empty string if the variable is not in any scope, e.g. global variables
def getScopePlusVar(tree):
   global stack
   global allocationTable
   potentialVarNames = []
   aux = list(stack)
   #If negative case
   if (type(tree) is list and len(tree) > 1):
      var = tree[1]
   elif (type(tree) is list):
      var = tree[0]
   else:
      var = tree
   while (len(stack) > 0):
      potentialVarNames.append(getAllStack()+var)
      stack.pop()
   potentialVarNames.append(var)
   stack = list(aux)
   # Finds if varname is in any scope of the allocation table
   for p in potentialVarNames:
      if (p in allocationTable):
         return p
   return ""

# Gets register associated with a variable in the inner most scope found
def getRegisterInScope(tree):
   global allocationTable
   if (getScopePlusVar(tree) != ""):
         return allocationTable[getScopePlusVar(tree)].__getitem__(0)
   return ""

# Cleans extra brackets from lists with one element.
def cleanList(tree):
   if (len(tree) == 1 and type(tree[0]) is list):
      tree = cleanList(tree[0])
   elif (len(tree) > 1 and type(tree) is list):
      for i in range (len(tree)):
         tree[i] = cleanList(tree[i])
   return tree

# Verifies if a tree contains an expression, function call, negation, etc
# or a simple value int/char value like 42 or 'a'
def isValue(tree):
   while (type(tree) is list):
      if (len(tree) == 1):
         tree = tree[0]
      else: 
         break
   if (type(tree) is list):
      return False
   elif (isInteger(tree)):
      return True
   elif (isChar(tree)):
      return True
   elif (isString(tree)):
      return True
   return False


def isChar(tree):
   return tree[0] == "\'" and tree[len(tree)-1] == "\'"


def isString(tree):
   return tree[0] == "\"" and tree[len(tree)-1] == "\""


def isInteger(tree):
   for digit in tree:
      if (not (digit.isdigit())):
         return False
   return True


def cleanToFirstValue(tree):
   while (type(tree) is list):
      tree = tree[0]
   return tree
