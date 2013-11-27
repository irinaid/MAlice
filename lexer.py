import keywords 
import lexerkeywords
'''
   The class instantiates with the filepath of the (MAlice) program. It holds a dictionary that maps all the strings
   and a global variable representing the file path. Although the lexer can be configured for MAlice, it can also be
   flexible for any programming language. 
'''
class Lexer:
   
   #This initializes the class
   def __init__(self):
      self.symbolTable = {}

   #Adds a token to the dictionary
   def addToken(self, toReplace, token):
      self.symbolTable[toReplace] = token

   #Looks up the symbol in the table. If the symbol is not found, the key is returned.
   #This is particularly helpful as it doesn't replace or throw exceptions when we
   #input expressions

   #Removes a token from the dictionary
   def deleteToken(self, toDelete):
      del self.symbolTable[toDelete]

   def hasDefinition(self, definition):
      return self.symbolTable.has_key(definition)

   def getToken(self, key):
      if self.hasDefinition(key):
         return self.symbolTable[key]
      return key

   #Adds all the tokens needed for MAlice
   def addMaliceTokens(self):
      
      self.symbolTable[keywords.ARRAYDECL] = lexerkeywords.ARRAY
      self.symbolTable[keywords.ARRAY] = lexerkeywords.ARRAY
      self.symbolTable[keywords.ASSIGN] = lexerkeywords.ASSIGN
      self.symbolTable[keywords.CHAR] = lexerkeywords.CHAR
      self.symbolTable[keywords.CHR] = lexerkeywords.CHR
      self.symbolTable[keywords.CLOSE] = lexerkeywords.CLOSE
      self.symbolTable[keywords.DEC] = lexerkeywords.DEC
      self.symbolTable[keywords.DECL] = lexerkeywords.DECL
      self.symbolTable[keywords.ELSE] = lexerkeywords.ELSE
      self.symbolTable[keywords.ELSE_IF] = lexerkeywords.ELSE_IF
      self.symbolTable[keywords.END_STATEMENT1] = lexerkeywords.END_STATEMENT
      self.symbolTable[keywords.END_STATEMENT2] = lexerkeywords.END_STATEMENT
      self.symbolTable[keywords.END_STATEMENT3] = lexerkeywords.END_STATEMENT
      self.symbolTable[keywords.ENDIF] = lexerkeywords.ENDIF
      self.symbolTable[keywords.ENDWHILE] = lexerkeywords.ENDWHILE
      self.symbolTable[keywords.FULLSTOP] = lexerkeywords.FULLSTOP
      self.symbolTable[keywords.IF1] = lexerkeywords.IF
      self.symbolTable[keywords.IF2] = lexerkeywords.IF
      self.symbolTable[keywords.INC] = lexerkeywords.INC
      self.symbolTable[keywords.INT] = lexerkeywords.INT
      self.symbolTable[keywords.LEFTOPEN] = lexerkeywords.LEFTOPEN
      self.symbolTable[keywords.LPAREN] = lexerkeywords.LPAREN
      self.symbolTable[keywords.MAINF] = lexerkeywords.MAINF
      self.symbolTable[keywords.OF] = lexerkeywords.OF
      self.symbolTable[keywords.OPEN] = lexerkeywords.OPEN
      self.symbolTable[keywords.PRINT1] = lexerkeywords.PRINT
      self.symbolTable[keywords.PRINT2] = lexerkeywords.PRINT
      self.symbolTable[keywords.READ] = lexerkeywords.READ
      self.symbolTable[keywords.RET] = lexerkeywords.RET
      self.symbolTable[keywords.RIGHTCLOSE] = lexerkeywords.RIGHTCLOSE 
      self.symbolTable[keywords.RPAREN] = lexerkeywords.RPAREN
      self.symbolTable[keywords.SAID] = lexerkeywords.SAID
      self.symbolTable[keywords.START_WHILE] = lexerkeywords.START_WHILE
      self.symbolTable[keywords.STRING] = lexerkeywords.STRING
      self.symbolTable[keywords.THEN] = lexerkeywords.THEN
      self.symbolTable[keywords.TYPE_OF_FUNCTION] = lexerkeywords.TYPE_OF_FUNCTION
      self.symbolTable[keywords.TYPEF] = lexerkeywords.TYPEF
      self.symbolTable[keywords.VOIDF] = lexerkeywords.VOIDF
      self.symbolTable[keywords.WHILE] = lexerkeywords.WHILE


   def replaceInTree(self, tree):
      for i in range(len(tree)):
         if type(tree[i]) is str:
            while (tree[i].find("  ") > -1):
               tree[i] = tree[i].replace("  "," ")
            tree[i] = tree[i].replace(tree[i], self.getToken(tree[i]))
         else:
            tree[i] = self.replaceInTree(tree[i])
      if(len(tree)>=2 and (type(tree[1]) is str) and (tree[1] in [lexerkeywords.PRINT, lexerkeywords.DECL, lexerkeywords.ASSIGN, lexerkeywords.ARRAY, lexerkeywords.INC, lexerkeywords.DEC  ]) ):
         aux = tree[0]
         tree[0] = tree[1]
         tree[1] = aux

         if(tree[0] == lexerkeywords.ARRAY):
            tree.insert(0, lexerkeywords.DECL)
      if(len(tree)>=5 and tree[4] == lexerkeywords.ASSIGN): #Handles assign case.
         i = 4
         while (i>0): 
            tree[i] = tree[i-1]
            i-=1
         tree[0] = lexerkeywords.ASSIGN
         
         
      return tree
         







