'''
This module performs semantic analysis on the tree. Unlike the lexer, 
the code cannot be reused (it works only on MAlice) so we decided to 
not give it a proper class.
Roles of the global variables:

 - scopeId: increments and decrements as we enter and/or exit scopes. 
   This assures that each scope has a unique id (the id can be reused 
   once the scope terminates)

 - hashTable: of type {(scope, var_name) : type} - this assures that 
   if a key occurs, a variable is redeclared in the scope

 - funtionHashTable: to keep it all clean, we did a separate hash 
   table that will hold function names, scope in which they appear 
   and argument types
'''

from malicehelpers import *
import lexerkeywords
import imports

hashTable = {}
scopeId = 0
functionHashTable = {} 


# Checks if a variable is already declared
# Starts from the current scope and goes downwards
def isDeclared(varName):
     scope = scopeId
     while scope>=0:
          if(hashTable.has_key((scope, varName))):
               return True, hashTable[(scope, varName)]
          scope-=1
     return False, "nothing"


# Checks if the function name is valid to be called
def isFunctionDeclared(functionName):
     scope = scopeId
     while scope>=0:
          if(functionHashTable.has_key((scope, functionName))):
               return True, functionHashTable[(scope, functionName)]
          scope-=1
     return False, "nothing"


# Checks to see if what I have can be an array
def checkIfArray(array):
     return ( len(array)>=4 and checkIfVariable(array[0]) 
               and array[1] == "[" and checkExpr(array[2], 
               lexerkeywords.INT) )


# Checks to see if the given array is valid (right syntax + declared)
def checkDefinedArray(array):
     if(not checkIfArray(array)):
          return False, "nothing"
     ok, tup = isDeclared(array[0])
     if(ok):
          if(type(tup) is tuple):
               return True, tup[1]
          else:
               return False, "nothing"
     else:
          return False, "nothing"
     return False, "nothing"
     

# When exiting a scope, all the variables / functions defined
# in it must be emptied
def emptyScope(scope):
     global hashTable
     keys = hashTable.keys()
     for key in keys:
          if(key[0] == scope):
               del hashTable[key]

     keys = functionHashTable.keys()

     for key in keys:
          if(key[0] == scope):
               del functionHashTable[key]


# Checks if an expression is valid
def checkExpr(subTree, assertedType):
     i = 0
     ok = True
     if(len(subTree)>=2 and subTree[1]==lexerkeywords.LPAREN): 
          ok, dictInfo = isFunctionDeclared(subTree[0])
          
          if(not ok or not checkFunctionHashTable(subTree, scopeId)):
               return False
          functionType = dictInfo[0]
          return (functionType == assertedType)

     while (i<len(subTree) and ok):
          if ((subTree[i] in ['-', '+', '*', '&', '|', '%', '~', '^', '/']
               )):
               #If the current operator is just a sign, I'll skip it
               i+=1
               continue
          if isinstance(subTree[i], list):
               #As expressions are usually nested, this function needs 
               #to recurse sometimes
               ok = checkExpr(subTree[i], assertedType) 
               i+=1
               continue
          else:     
               ok2 = checkIfArray(subTree)
               if(ok2): #The current term is a valid array
                    ok2, the_type = checkDefinedArray(subTree)
                    if(not ok2):
                         return False
                    ok = (the_type == assertedType)
               elif(checkIfVariable(subTree[i])): 
                    #In case we have a variable, we need to do check 
                    #3 things:
                    # 1 - If it's defined
                    # 2 - If it has a value
                    # 3 - If it has the correct type 
                    #(the assertedType parameter)
                    j = scopeId
                    ok, the_type = isDeclared(subTree[i]) 
                    #Checks if the variable 
                    if (ok and the_type!=assertedType ):
                         ok = False
               if("'" in subTree[i] and not ('"' in subTree[i]) and 
                    assertedType!=lexerkeywords.CHAR): 
                    #If it's a char, make ok false
                    ok = False
               if('"' in subTree[i] and 
                    assertedType!=lexerkeywords.STRING):
                    ok = False
               if(subTree[i][0]>='0' and subTree[i][0]<='9' 
                    and assertedType!=lexerkeywords.INT):
                    ok = False
               #Otherwise it's an int(the parser guarantees this)
          i+=1 
     return ok


# Checks a declaration is valid in terms of scope 
def checkDecl(subTree):
     global hashTable
     if(subTree[1] != lexerkeywords.ARRAY):
          if(hashTable.has_key((scopeId, subTree[1]))):
               promptErrorMessage("Variable", subTree[1], 
               "declared twice in the same scope.")
               return False
          if( len(subTree)>3 and subTree[3] == lexerkeywords.OF ):
               if(not checkExpr(subTree[4], subTree[2])):
                    promptErrorMessage("Variable", subTree[1],
                    "cannot be assigned a type other than", 
                    subTree[2])
                    return False
          hashTable.update({(scopeId, subTree[1]):subTree[2]})
     else:
          if(hashTable.has_key((scopeId, subTree[1]))):
               promptErrorMessage("Array", subTree[1], 
               "already declared.")
               return False

          if((not checkExpr(subTree[3], lexerkeywords.INT))):
               promptErrorMessage("Array size has to be an integer.")
               return False
          hashTable.update({(scopeId, subTree[2]):("ARRAY", subTree[4])})
     return True


# Checks if the variable assign is valid
def checkAssign(subTree):
     if(subTree[2] == "["):
          ok, the_type =checkDefinedArray(subTree[1:5])
          if(ok):
               if(not checkExpr(subTree[5], the_type)):
                    ok = False
                    promptErrorMessage(
                    "Type mismatch in array assignment.")
          else:
               
               promptErrorMessage("Array", subTree[1], "not defined.")
     else:
          ok, var = isDeclared(subTree[1])
          if(not ok):
               promptErrorMessage("Variable", subTree[1], 
               "not declared.")
               return False
          ok = ok and checkExpr(subTree[2], var)
          if(not ok):
               promptErrorMessage(
               "Type mismatch in variable assignment.")
               return False
     return ok


# Checks if the print statement is valid
def checkPrint(subTree):
     arg = subTree[1]
     ok = checkExpr(arg,lexerkeywords.INT) or checkExpr(arg, lexerkeywords.STRING) or checkExpr(arg,lexerkeywords.CHAR)
     if (len(arg[0]) == 4 and arg[0][1] == '[' and arg[0][3] == ']'):
          var = arg[0]
          index = arg[0][2]
          ok = ok or checkDefinedArray(var)[0] and checkExpr(index, 
          lexerkeywords.INT)     
     if(not ok):
          while (isinstance(arg, list)):
               arg = arg[0]
          ok = arg[0] == "\"" and arg[len(arg)-1] == "\""
          if (not ok):          
               promptErrorMessage(
               "Invalid expression in spoke / said Alice.")
     return ok


# Checks if the return type 
def checkRet(subTree, retType):
     return checkExpr(subTree[1], retType)


# Checks the given variable is healthy to be eaten or drunk
def checkIncDec(subTree):
     var = subTree
     ok = True
     if(len(var)>1 and var[1] == "["):
          ok, k = isDeclared(var[0])
          if(ok):
               if(type(hashTable[var]) is tuple):
                    if (hashTable[var][1] != lexerkeywords.INT):
                         promptErrorMessage(     
                         "Increment and decrement require an integer argument.")
                    return True
               else:
                    promptErrorMessage("Invalid expression in ate / drank.")
                    ok = False
          else:
               ok = False
     else:     
          while (isinstance(var[1], list)):
               var[1] = var[1][0]
          ok, the_type = isDeclared(var[1])
          if(not ok or the_type != lexerkeywords.INT):
               promptErrorMessage("Increment and decrement require an integer argument.")
               return False
          if (not ok):
               promptErrorMessage("Invalid expression in ate / drank.")
               return False
     return True


# Checks that the variable given to "what was" is valid
def checkWhatWas(subTree): 
     
     ok, the_type = isDeclared(subTree[1])
     if (not ok or the_type == "Nothing"):
     #Case 1: Did you try and read an undefined variable?
          promptErrorMessage("Variable in what was is not declared.")
          return False
     elif (not (type(the_type) is tuple) and subTree[2] == '['):
     #Case 2: Did you try and read a number as if it was an array?
          promptErrorMessage("Invalid read.",subTree[1], "is not an array.")
          return False
     elif (the_type[0] == lexerkeywords.ARRAY and len(subTree) == 3):
     #Case 3: Did you just try to read an ENTIRE array?
          promptErrorMessage("Invalid (array) variable call in what was.")
          return False
     else:
     #Case 4: Congratualtions! You've done well!
          #updateAssignments(subTree[1])
          return True

def addArgsToHash(args):
     for arg in args:
          arg.insert(0,lexerkeywords.DECL)
          aux = arg[len(arg)-1]
          arg[len(arg)-1] = arg[len(arg)-2]
          arg[len(arg)-2] = aux
          if(arg[1] == lexerkeywords.ARRAY):
               arg.insert(3,[['0']])
          global scopeId
          scopeId+=1
          checkDecl(arg)
          scopeId-=1
     

# Checks a function of type 'The looking-glass'          
def checkFunction(subTree):
     global functionHashTable     
     if (subTree[0] == lexerkeywords.MAINF):
          fst =(scopeId, "hatta")
          snd = ("VOID", mapRemoveLast(subTree, 2))
          args = subTree[2]
     elif (subTree[0] == lexerkeywords.VOIDF):
          fst = (scopeId, subTree[1])
          snd = ("VOID", mapRemoveLast(subTree, 3))
          args = subTree[3]
     addArgsToHash(args)
     functionHashTable.update({fst:snd})
     return checkBlock(subTree[len(subTree)-1][1], "", True)


# Checks the return type function 'The room'
def checkTypeFunction(subTree):
     global functionHashTable
     
     fst = (scopeId, subTree[1])
     snd = (subTree[6], mapRemoveLast(subTree, 3))
     functionHashTable.update({fst:snd})
     functionType = subTree[6]
     args = subTree[3]
     addArgsToHash(args)
     if (not checkBlock(subTree[len(subTree)-1][1], functionType, True)):
          promptErrorMessage("Wrong return type in function", subTree[1])
          return False
     return True


# Checks a 'perhaps' statement
# If it's block is between 'opened' and 'closed' it will be 
#evaluated by checkBlock, otherwise it should not contain 
#function or variable declarations
def checkIf(subTree):
     i = 0
     while (i < len(subTree)):
          if (subTree[i] == lexerkeywords.IF or subTree[i] == 
               lexerkeywords.ELSE_IF):
               if (not checkCondition(subTree[i+2])):
                    return False
               elif (subTree[i+5][0] == lexerkeywords.OPEN and 
                         (not checkBlock(subTree[i+5][1], "", True))):
                    
                    return False
               elif (not checkIfSimpleBlock(subTree, i+5)):
                    return False
               else:
                    i+=6
          elif (subTree[i] == lexerkeywords.ELSE):
               if (subTree[i+1][0] == lexerkeywords.OPEN and 
                    (not checkBlock(subTree[i+1][1], "", True))):
                    return False               
               elif (not checkIfSimpleBlock(subTree, i+1)):
                    return False
               else:
                    i = len(subTree)
          else: i+=1
     return True


# Checks blocks of code after 'perhaps' that are not put 
# between 'opened' and 'closed'
def checkIfSimpleBlock(subTree, index):
     while (not (subTree[index] in [lexerkeywords.ELSE, 
          lexerkeywords.ELSE_IF, lexerkeywords.ENDIF])):
          checkBlock([subTree[index]], "", False)
          index += 1
     return True


# Checks a boolean condition from a 'perhaps' or 
# 'or maybe' statement
def checkCondition(subTree): 
     ok = True
     for t in subTree:
          if t in ['==', '&&', '||', '>', '<', '>=', '<=']:
               continue
          if type(t) is list:
               ok = ok and checkExpr(t,lexerkeywords.INT) 
     if (not ok):
          promptErrorMessage("Invalid boolean condition", subTree)
     return ok


# Checks a block of code put between 'opened' and 'closed',
# by identifying each statement and calling the apropriate 
# check function
def checkBlock(subTree, potentialRetType, mustChangeScope): 
     global scopeId
     global functionHashTable
     if(mustChangeScope):
          scopeId += 1
     i = 0
     while i < len(subTree):
          instructionKey = subTree[i][0]
          if (instructionKey == lexerkeywords.DECL):
               if (not checkDecl(subTree[i])):
                    return False
          elif (instructionKey == lexerkeywords.OPEN):
               if (not checkBlock(subTree[i][1], "", True)):
                    return False
          elif (instructionKey == lexerkeywords.VOIDF 
               or subTree[i][0] == lexerkeywords.MAINF):
               if (not checkFunction(subTree[i])):
                    return False
          elif (instructionKey == lexerkeywords.TYPEF):
               if (not checkTypeFunction(subTree[i])):
                    return False
          elif (instructionKey == lexerkeywords.ASSIGN):
               if (not checkAssign(subTree[i])):
                    return False
          elif (instructionKey == lexerkeywords.PRINT): 
               if (not checkPrint(subTree[i])):
                    return False
          elif (instructionKey == lexerkeywords.IF): 
               if (not checkIf(subTree[i])): 
                    return False
          elif (instructionKey == lexerkeywords.WHILE): 
               if (not checkWhile(subTree[i])): 
                    return False
          elif (instructionKey == lexerkeywords.READ): 
               if (not checkWhatWas(subTree[i])):
                    return False
          elif (instructionKey == lexerkeywords.DEC 
               or instructionKey == lexerkeywords.INC): 
               if (not checkIncDec(subTree[i])):
                    return False
          elif (instructionKey == lexerkeywords.FULLSTOP):
               pass
          elif (instructionKey == lexerkeywords.RET):
               return checkExpr(subTree[i][1], potentialRetType)
          elif (checkIfVariable(instructionKey)):
               if (not checkFunctionHashTable(subTree[i], scopeId)):
                    return False
          i+=1
     if(mustChangeScope):
          emptyScope(scopeId)
          scopeId -= 1
     return True


# Helper function to check variable in scope of the function hash table
def checkFunctionHashTable(subTree, scope):
     global functionHashTable     
     global hashTable
     variable = subTree[0]
     args = subTree[2]
     while (scope >= 0):
          if (functionHashTable.has_key((scope, variable))):
               i = 0
               if (len(functionHashTable[(scope, variable)][1]) != len(subTree[2])):
                    promptErrorMessage("Wrong number of arguments in function call.")
                    return False
               count_vars = 0
               for var_type in functionHashTable[(scope, variable)][1]:
                    if (var_type[0] == lexerkeywords.ARRAY):
                         arrayName = subTree[2][count_vars][0][0]
                         ok, the_type = isDeclared(arrayName)
                         if(not ok):
                              promptErrorMessage("Undefined array", arrayName)
                              return False
                         elif(the_type[1] != var_type[1]):
                              promptErrorMessage(
                              "Type mismatch in function call. Array", 
                              arrayName, "must be of type", var_type[1])
                              return False
                    elif (not checkExpr(subTree[2][count_vars][0], var_type[0])):
                         promptErrorMessage("Wrong types in function call.")
                         return False
                    count_vars += 1
               return True
          scope -=1
     promptErrorMessage("Invalid function call in scope")
     return False


# Checks if all the components of a while loop are valid
def checkWhile(subTree):
     global scopeId
     if (not checkCondition(subTree[2])):
          return False
     if(subTree[4] == lexerkeywords.START_WHILE):
          whileBlock = subTree[5][0]
          if  (whileBlock[0] == lexerkeywords.OPEN):
               if (not checkBlock(whileBlock[1], "", True)):
                    return False
          else:
               
               if(not checkBlock(subTree[5], "", False)):
                    return False
     return True


# Checks the whole program for semantic errors
def check(parsingTree):
     ok = True
     for block in parsingTree:
          instructionKey = block[0]
          if (instructionKey == lexerkeywords.MAINF or 
               instructionKey == lexerkeywords.VOIDF):
               ok = checkFunction(block)
          elif (ok and instructionKey == lexerkeywords.TYPEF):
               ok = checkTypeFunction(block)
          elif (ok and instructionKey == lexerkeywords.DECL):
               ok = checkDecl(block)
          elif (ok and instructionKey == "IMPORT"):
               imports.importHandler(block)
          else:
               return False
     return ok

