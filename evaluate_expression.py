
def can_evaluate(tree):
	if(len(tree) == 3):
		return can_evaluate(tree[0]) and can_evaluate(tree[2])
	if(type(tree) is list):
		return can_evaluate(tree[0])
	if(tree[0] >='0' and tree[0] <='9'):
		return True
	return False

def evaluate(tree):
	if(len(tree) == 3):
		op = tree[1]
		if(op == "+"):
			return evaluate(tree[0]) + evaluate(tree[2])
		elif(op == "*"):
			return evaluate(tree[0]) * evaluate(tree[2])
		elif(op == "/"):
			return evaluate(tree[0]) / evaluate(tree[2])
		elif(op == "%"):
			return evaluate(tree[0]) % evaluate(tree[2])
		elif(op == "-"):
			return evaluate(tree[0]) - evaluate(tree[2])
		elif(op == "&"):
			return evaluate(tree[0]) & evaluate(tree[2])
		elif(op == "|"):
			return evaluate(tree[0]) | evaluate(tree[2])
		elif(op == "^"):
			return evaluate(tree[0]) ^ evaluate(tree[2])
	elif(len(tree) == 1 and (type(tree) is list)):
		return evaluate(tree[0])
	else:
		return int(tree)


