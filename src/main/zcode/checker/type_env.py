from AST import ArrayType, Type


class TypePlaceholder:
    count = 0

    def __init__(self):
        self.t = None
        self.type_id = TypePlaceholder.count
        TypePlaceholder.count += 1

    def setType(self, t):
        self.t = t

    def getType(self):
        return self.t

    def __str__(self):
        return f"${self.type_id}"

class FnType(Type):
    def __init__(self, arg_types: list[Type], return_type: Type | TypePlaceholder):
        self.argTypes = arg_types
        self.returnType = return_type

class TypeEnvironment:
    def __init__(self):
        self.scopes = []
        self.beginScope()

    def declare(self, name, var_type):
        scope = self.getCurrentScope()
        scope[name] = var_type

    def isDeclared(self, name):
        return self.getType(name) != None

    def getType(self, name):
        for scope in reversed(self.scopes):
            try:
                return scope[name]
            except KeyError:
                continue
        return None

    def beginScope(self):
        self.scopes.append(dict())

    def endScope(self):
        self.scopes.pop()

    def getCurrentScope(self):
        return self.scopes[-1]

def annotateType(ast, exprType):
    ast.exprType = exprType

def getTypeAnnotation(ast):
    if hasattr(ast, 'exprType'):
        return ast.exprType
    return None

def getExpressionType(ast):
    expr_type = getTypeAnnotation(ast)
    if isinstance(expr_type, ArrayType) and isinstance(expr_type.eleType, TypePlaceholder):
        return ArrayType(eleType=expr_type.eleType.getType(), size=expr_type.size)
    if isinstance(expr_type, Type):
        return expr_type
    if isinstance(expr_type, TypePlaceholder):
        return expr_type.getType()


def isValidArrayType(t):
    return isinstance(t, ArrayType) and t.size != []

def compatibleTypes(lhs_type, rhs_type):
    if lhs_type.__class__ != rhs_type.__class__:
        return False

    if isinstance(lhs_type, ArrayType):
        return (lhs_type.eleType.__class__ == rhs_type.eleType.__class__
                and len(lhs_type.size) == len(rhs_type.size)
                and all([i == j for i, j in zip(lhs_type.size, rhs_type.size)]))

    return True
