
def importHandler(tree):
   filePath = tree[1]
   fileText = open(tree[1], "r")
   print fileText.read()


