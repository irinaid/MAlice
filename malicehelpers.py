'''
   A list of helper functions useful throughout the compiler
'''
from reservedwords import RESTRICTED
# Checks if a variable name is valid
# TODO not in reserved keyword list
def checkIfVariable(var):
   return (var[0]>='a' and var[0]<='z' or var[0]>='A' and var[0]<='Z') and (not var in RESTRICTED) 

# Helper function to map a list changing function to a list of lists
def mapRemoveLast(subTree, index):
   if (len(subTree) == 0):
      return subTree
   return map(removeLast, subTree[index])


# Helper function to remove the last element of a list
def removeLast(subTree):
   return subTree[:len(subTree)-1]

# Prompts an error message and exits the script
def promptErrorMessage(*messages):
   errorMessage = ""
   for message in messages:
      errorMessage += str(message) + " "
   raise SystemExit(errorMessage)
