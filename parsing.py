from pyparsing import Word, alphas, ParseException, Literal, CaselessKeyword, \
     Combine, Optional, nums, Or, Forward, ZeroOrMore, StringEnd, alphanums, \
     Regex, Suppress, OneOrMore, printables, Group, replaceWith
from reservedwords import *

#Operators

# Bitwise operators
bitAnd = Combine(Literal( "&" ) + ~Literal("&"))
bitOr =  Combine(Literal( "|" ) + ~Literal("|"))
bitXor = Literal( "^" )
bitNot = Literal( "~" )

bitOp = (bitAnd | bitOr | bitXor | bitNot)

# Boolean operators
boolAnd = Literal( "&&" )
boolOr = Literal( "||" )
greater_op       = Combine( Literal( ">" ) + ~Literal( "=" ) )
greater_equal_op = Combine( Literal( ">" ) + Literal( "=" ) )
less_op          = Combine( Literal( "<" ) + ~Literal( "=" ) )
less_equal_op    = Combine( Literal( "<" ) + Literal( "=" ) )

boolNeq = Literal( "!=" )
boolEq = Literal( "==" )
boolNot = Literal("!")

boolAndOrOp = (boolAnd | boolOr)
boolEqNeqOp =  (boolEq | boolNeq)
relationalOp = (greater_op | greater_equal_op | less_op | less_equal_op | 
boolEqNeqOp)

# Arithmetic operators
plus  = Literal( "+" )
minus = Literal( "-" )
mult  = Literal( "*" )
mod = Literal( "%" )
div   = Literal( "/" )
artmOp = plus | minus | mult | mod | div

artmBitOp = artmOp | bitOp 
plusMinus = plus | minus
multDivMod = mult | div | mod
unOp = bitNot | minus | plus


#Defining all recursives
expression2 = Forward()
variable = Forward()
arrayElem = Forward()
fctCall = Forward()
term = Forward()
expression = Forward()
relationalExp = Forward()
boolExp1 = Forward()
boolExp = Forward()
declaration = Forward()
assignment = Forward()
ifSt1 = Forward()
ifSt2 = Forward()
whileSt = Forward()
sequence = Forward()
seqass = Forward()
voidFunction = Forward()
mainFunction = Forward()
typeFunction = Forward()
function = Forward()
program = Forward()
opcl = Forward()
statement = Forward()
anyFunction = Forward()
functionCall = Forward()

#MAlice elements
spaces = OneOrMore(" ")
lpar =  Literal(LPAR)
rpar =  Literal(RPAR)
opened = Literal(OPENED)
closed = Literal(CLOSED)
spoke = Literal(SPOKE)
saidAlice = Combine(Literal(SAID) + spaces + Literal(ALICE))
so = Literal(SO)

#Constants
integer = Word(nums)
char = Combine(Literal('\'') + Word((nums + alphas + 
'\#!$%&()*+,-./:;<=>?@[]^_`{|}~ '), max=1) + Literal('\''))
string = Combine(Literal('"') + Word(nums + alphas + 
"!$%&(')*+,-./:;<=>?@[]^_`{|}~ #" + "\\") 
+ Literal('"'))
constant = (integer ^ char ^ string)


#Variables
variable << ( Combine( Word(alphas) + ZeroOrMore( Word(alphas) | integer 
| Literal(UNDERSCORE) )))

#Array elements
arrayElem << ( (variable + Literal(S) + expression + Literal(PIECE)) )

#Identifiers
identifier = ( (arrayElem) ^ (variable) )

#Types
types = (Literal(LETTER) | Literal(NUMBER) | Literal(SENTENCE))

#Expressions
term << Group(functionCall ^ constant  ^ identifier ^ Group(lpar.suppress() 
+ expression + rpar.suppress())) 
notTerm = (ZeroOrMore(bitNot) + term)
unary = ZeroOrMore(plusMinus) + notTerm 
multiplication = Group(unary + (ZeroOrMore(multDivMod + unary )))
addition = Group(multiplication + (ZeroOrMore(plusMinus + multiplication)))
andExp = Group(addition + (ZeroOrMore(bitAnd + addition ))) 
xorExp = Group(andExp + (ZeroOrMore(bitXor + andExp ))) 
orExp = Group(xorExp + (ZeroOrMore(bitOr + xorExp ))) 
expression << Group(orExp)


#Boolean expressions
relationalExp << Group((expression + relationalOp + expression) | 
( ZeroOrMore(boolNot) + lpar.suppress() + relationalExp + rpar.suppress()))
boolAndExp = Group(relationalExp) + ZeroOrMore(boolAnd + Group(relationalExp)) 
boolOrExp = Group(boolAndExp) + ZeroOrMore(boolOr + Group(boolAndExp))
boolExp << Group(ZeroOrMore(boolNot) + Group(boolOrExp))

#Array definition
arrayDef = (identifier + (Literal(HAD) + (expression) + types ))

#Declarations
declarationWithoutEnd = ( arrayDef | ( variable + Combine(Literal(WAS) + spaces 
+ Literal(A)) + types 
+ Optional( Literal(TOO).suppress() | (Literal(OF) + expression )) ))
declaration << ( OneOrMore(Group( declarationWithoutEnd + 
( Literal(BUT).suppress() | Literal(AND).suppress() |
 Literal(THEN).suppress() | Literal(COMMA).suppress() | Literal(DOT).suppress() 
)))  )



#If
elseLiterals  = (Literal(OR) + spaces + ~Literal(MAYBE))
maybeLiterals = (Literal(OR) + spaces + Literal(MAYBE))
endif = Combine(Literal(BECAUSE) + spaces + Literal(ALICE) + spaces + 
Literal(WAS) + spaces 
+ Literal(UNSURE) + spaces + Literal(WHICH))
orMaybe = (Combine(maybeLiterals) + lpar + boolExp + rpar + so + seqass)
orSimple = (Literal(OR) + seqass)
conditionBlock = (lpar  + boolExp + rpar + so + seqass)
ifSt1 << ( Literal(PERHAPS) + conditionBlock + ZeroOrMore(orMaybe) + 
Optional(orSimple) + endif )
ifSt2 << ( Literal(EITHER) + conditionBlock + orSimple + endif )
ifSt = Group(ifSt2 | ifSt1)


#While
endWhile = Combine( Literal(ENOUGH) + spaces + Literal(TIMES) )
whileSt << Group(Literal(EVENTUALLY) + lpar + Group(boolExp) + rpar + 
Literal(BECAUSE) + Group(seqass) + endWhile)

#Assignment, statement and sequence
read = Group(Combine(Literal(WHAT) + spaces + Literal(WAS)) + identifier 
+ Literal(QUESTION))
aliceFound = Combine(Literal(ALICE) + spaces + Literal(FOUND)) + (constant | 
expression | identifier)
assignment << (identifier + Literal(BECAME) + (expression|char|string))
statement << (aliceFound | assignment |  (Group(identifier) + Literal(ATE)) | 
(identifier + Literal(DRANK)) |
 (expression + (saidAlice|Literal(SPOKE))) | 
( (functionCall ^ constant  ^ identifier) + (saidAlice|Literal(SPOKE))) | 
functionCall ) 
sequence << (( OneOrMore(Group(statement  + (Literal(BUT).suppress() | 
Literal(AND).suppress() | Literal(THEN).suppress() 
| Literal(COMMA).suppress() | (Literal(DOT)).suppress()))) ) | opcl | fctCall | 
ifSt | whileSt |  Group(Literal(DOT))  | read )
seqass << OneOrMore(sequence)

#Arguments
containedA = Combine(Literal(CONTAINED) + spaces + Literal(A))
args = ZeroOrMore(types + identifier)
argument = Group((Optional(Literal(SPIDER)))  + (Literal(NUMBER) | 
Literal(LETTER)  | Literal(SENTENCE)) + identifier)
argsDeff = Group(Optional(argument + ZeroOrMore(Literal(COMMA).suppress() + 
argument) ))
argsCall = Optional(expression + ZeroOrMore(Literal(COMMA).suppress() 
+ expression))

#Function call 
functionCall << (identifier + lpar + Group(argsCall) + rpar)

#Function definitions

voidF = Combine(Literal(THE) + spaces + Literal(LOOKING_GLASS) + 
spaces.suppress() + ~Literal(HATTA))
mainF = Combine(Literal(THE) + spaces + Literal(LOOKING_GLASS) 
+ spaces + Literal(HATTA))
typeF = Combine(Literal(THE) + spaces + Literal(ROOM))
block = Group(opened + Group(Optional(ZeroOrMore(anyFunction | declaration) + 
OneOrMore(sequence))) + closed)
opcl <<  block
mainFunction = Group(mainF + lpar + argsDeff + rpar + block)
voidFunction = Group(voidF + identifier + lpar + argsDeff + rpar + block)
typeFunction = Group(typeF + identifier + lpar + argsDeff + rpar + containedA 
+ types + block)
function << (voidFunction | typeFunction)
anyFunction << (function | mainFunction)

# Import extension
filePath = Word(nums + alphas + "!$%&(')*+,-./:;<=>?@[]^_`{|}~ #" + "\\")
malice_import = Group(Literal("import") + Literal("\"").suppress() + filePath + 
Literal("\"").suppress())

#Program
program << (ZeroOrMore(malice_import) + ZeroOrMore(declaration) + 
ZeroOrMore(function) + mainFunction )
bnf =   program + StringEnd()


def notInString(index, code): 
     code = code[0:index]
     counter = 0     
     for c in code: 
          if (c == '"'): counter +=1
     if (counter%2): return False
     return True

#Ignore comments
def stripComments(text): 
     code = text
     while "###" in code and notInString(code.index("###"), code):
          code1 = code[0:code.index("###")]
          endl_index = code.index("###")+3
          while code[endl_index] != '\n':
               endl_index+=1
          code = code1 + code[endl_index+1:code.__len__()]
     return code

def getTree(fileText):
     tokens = bnf.parseString(stripComments(fileText))
     return tokens

