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
    def __init__(self, arg_types: list[Type], return_type: Type | TypePlaceholder | None):
        self.argTypes = arg_types
        self.returnType = return_type

class TypeEnvironment:
    def __init__(self):
        self.scopes = []
        self.beginScope()

    def declare(self, name, var_type):
        scope = self.getCurrentScope()
        scope[name] = var_type

    def isInCurrentScope(self, name):
        return name in self.scopes[-1]

    def getType(self, name):
        for scope in reversed(self.scopes):
            try:
                return scope[name]
            except KeyError:
                continue
        return None

    def setType(self, name, var_type):
        scope = self.getCurrentScope()
        assert name in scope
        scope[name] = var_type

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
    return unwrapTypeVar(expr_type)

def unwrapTypeVar(t):
    if isinstance(t, ArrayType) and isinstance(t.eleType, TypePlaceholder):
        return ArrayType(eleType=unwrapTypeVar(t.eleType), size=t.size)
    if isinstance(t, Type):
        return t
    if isinstance(t, TypePlaceholder):
        return unwrapTypeVar(t.getType())


def isValidArrayType(t):
    return isinstance(t, ArrayType) and t.size != []

def compatibleTypes(lhs_type, rhs_type):
    # Type variable can be any type
    if isinstance(lhs_type, TypePlaceholder):
        return True if lhs_type.getType() is None else compatibleTypes(lhs_type.getType(), rhs_type)

    if lhs_type.__class__ != rhs_type.__class__:
        return False

    if isinstance(lhs_type, ArrayType):
        return (lhs_type.eleType.__class__ == rhs_type.eleType.__class__
                and len(lhs_type.size) == len(rhs_type.size)
                and all([i >= j for i, j in zip(lhs_type.size, rhs_type.size)]))

    return True
