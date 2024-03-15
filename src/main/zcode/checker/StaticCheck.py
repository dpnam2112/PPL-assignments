from AST import *
from Visitor import *
from Utils import Utils
from StaticError import *

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

def getOperandType(op):
    if op in ['+', '-', '*', '/', '%', '>', '<', '>=', '<=', '=', '!=']:
        return NumberType()
    if op in ['and', 'or', 'not']:
        return BoolType()
    return StringType()

def getResultType(op):
    if op in ['+', '-', '*', '/', '%']:
        return NumberType()
    if op in ['and', 'or', 'not', '=', '==', '!=', '>=', '<=', '>', '<']:
        return BoolType()
    return StringType()

class StaticChecker(BaseVisitor, Utils):
    def __init__(self, prog: Program):
        self.prog = prog
        self.typeEnv = TypeEnvironment()

        # Used to check the current position of the checker in the AST.
        self.inLoop = False
        self.inArray = 0

        # Used to check if there is a function without definition.
        self.funcDecls = {}
        self.currentFnName = ""
        self.typeConstraints = []

    def check(self):
        self.prog.accept(self, None)

        # Check for no-function-definition error
        for fn_name, fn_decl in self.funcDecls.items():
            if not fn_decl.body:
                raise NoDefinition(fn_name)

        if 'main' not in self.funcDecls:
            raise NoEntryPoint()

        main_decl = self.funcDecls['main']
        if not (main_decl and main_decl.param == [] and main_decl.body):
            raise NoEntryPoint()

    def setCurrentFnName(self, name: str):
        self.currentFnName = name

    def getCurrentFnName(self) -> str:
        return self.currentFnName

    def getFnType(self, name: str):
        pass

    def isFunctionRedeclaration(self, ast: FuncDecl):
        fn_name = ast.name.name

        # Check if there is any identifier declared.
        fn_type = self.typeEnv.getType(fn_name)
        if fn_type is not None and not isinstance(fn_type, FnType):
            return True
        
        if not fn_type: return False

        # we need to use function declaration instead of function type in this case because we
        # also need to check if the previous declaration has a body.
        prev_decl = self.funcDecls[fn_name]

        if(prev_decl.body or not ast.body
                             or len(prev_decl.param) != len(ast.param)):
            return True

        return not all([compatibleTypes(pair[0].varType, pair[1].varType)
                        for pair in zip(prev_decl.param, ast.param)])

    def beginScope(self):
        self.typeEnv.beginScope()

    def endScope(self):
        self.typeEnv.endScope()

    def visitProgram(self, ast: Program, param):
        for decl in ast.decl:
            decl.accept(self, None)

    def visitFuncDecl(self, ast: FuncDecl, param):
        fn_name = ast.name.name

        if self.isFunctionRedeclaration(ast):
            raise Redeclared(Function(), fn_name)
        
        self.funcDecls[fn_name] = ast
        fn_type = self.typeEnv.getType(fn_name)

        if not fn_type:
            fn_type = FnType(
                        arg_types=[decl.varType for decl in ast.param],
                        return_type=None
                    )
            self.typeEnv.declare(fn_name, fn_type)

        self.funcDecls[fn_name] = ast

        self.setCurrentFnName(fn_name)
        self.beginScope()
        if ast.body:
            ast.body.accept(self, None)
        self.endScope()

    def visitVarDecl(self, ast: VarDecl, param):
        var_name = ast.name.name

        if self.typeEnv.isInCurrentScope(var_name):
            raise Redeclared(Variable(), var_name)

        var_type = ast.varType if ast.varType else TypePlaceholder()
        self.typeConstraints.append(var_type)

        try:
            if ast.varInit:
                satisfied_constr = ast.varInit.accept(self, None)
                if not satisfied_constr:
                    raise TypeMismatchInStatement(ast)
        except TypeCannotBeInferred:
            raise TypeCannotBeInferred(ast)

        self.typeConstraints.pop()

        if isinstance(var_type, TypePlaceholder) and var_type.getType() is not None:
            var_type = var_type.getType()

        self.typeEnv.declare(var_name, var_type)

    def visitAssign(self, ast: Assign, param):
        self.typeConstraints.append(TypePlaceholder())

        try:
            ast.rhs.accept(self, None)
        except TypeCannotBeInferred as exception:
            if (exception.stmt == ast.rhs 
                and not isinstance(exception.stmt, Id)):
                raise TypeCannotBeInferred(ast)

        if self.typeConstraints[-1].getType():
            self.typeConstraints[-1] = self.typeConstraints[-1].getType()
            try:
                if not ast.lhs.accept(self, None):
                    raise TypeMismatchInStatement(ast)
            except TypeCannotBeInferred:
                raise TypeCannotBeInferred(ast)
        else:
            # rhs's type is not inferred. Proceed to infer the lhs's type.
            # if the type of lhs still cannot be inferred, raise the exception.
            ast.lhs.accept(self, None)
            if not self.typeConstraints[-1].getType():
                raise TypeCannotBeInferred(ast)

            self.typeConstraints[-1] = self.typeConstraints[-1].getType()
            try:
                if not ast.rhs.accept(self, None):
                    raise TypeMismatchInStatement(ast)
            except TypeCannotBeInferred:
                raise TypeCannotBeInferred(ast)

        self.typeConstraints.pop()

    def visitBinaryOp(self, ast: BinaryOp, param):
        type_constraint = self.typeConstraints[-1]

        if not compatibleTypes(type_constraint, getResultType(ast.op)):
            return False

        if isinstance(type_constraint, TypePlaceholder) and type_constraint.getType() is None:
            type_constraint.setType(getResultType(ast.op))

        self.typeConstraints.append(getOperandType(ast.op))

        if not (ast.left.accept(self, None) and ast.right.accept(self, None)):
            raise TypeMismatchInExpression(ast)

        self.typeConstraints.pop()

        return True

    def visitUnaryOp(self, ast: UnaryOp, param):
        type_constraint = self.typeConstraints[-1]

        if not compatibleTypes(type_constraint, getResultType(ast.op)):
            return False

        if isinstance(type_constraint, TypePlaceholder) and type_constraint.getType() is None:
            type_constraint.setType(getResultType(ast.op))

        self.typeConstraints.append(getOperandType(ast.op))

        visit_operand = ast.operand.accept(self, None)
        if not visit_operand:
            raise TypeMismatchInExpression(ast)

        self.typeConstraints.pop()

        return True

    def visitBreak(self, ast, param):
        if not self.inLoop:
            raise MustInLoop(ast)

    def visitContinue(self, ast, param):
        if not self.inLoop:
            raise MustInLoop(ast)

    def visitArrayCell(self, ast: ArrayCell, param):
        self.typeConstraints.append(NumberType())
        for idx in ast.idx:
            satisfied_constr = idx.accept(self, None)
            if not satisfied_constr:
                raise TypeMismatchInExpression(ast)
        self.typeConstraints.pop()

        self.typeConstraints.append(ArrayType(eleType=self.typeConstraints[-1], size=[]))
        ast.arr.accept(self, None)

        return True

    def visitCallStmt(self, ast: CallStmt, param):
        fn_name = ast.name.name

        fn_type = self.typeEnv.getType(fn_name)
        if not fn_type:
            raise Undeclared(Function(), fn_name)

        if (not isinstance(fn_type, FnType) 
            or len(ast.args) != len(fn_type.argTypes)
            or not (fn_type.returnType is None or isinstance(fn_type.returnType, VoidType))):
            raise TypeMismatchInExpression(ast)

        if not fn_type.returnType:
            fn_type.returnType = VoidType()

        for arg_type, arg_expr in zip(fn_type.argTypes, ast.args):
            self.typeConstraints.append(arg_type)
            if not arg_expr.accept(self, None):
                raise TypeMismatchInExpression(ast)
            self.typeConstraints.pop()

    def visitCallExpr(self, ast: CallExpr, param):
        fn_name = ast.name.name

        fn_type = self.typeEnv.getType(fn_name)
        if not fn_type:
            raise Undeclared(Function(), fn_name)

        if not isinstance(fn_type, FnType) or len(ast.args) != len(fn_type.argTypes):
            raise TypeMismatchInExpression(ast)

        for arg_type, arg_expr in zip(fn_type.argTypes, ast.args):
            self.typeConstraints.append(arg_type)
            if not arg_expr.accept(self, None):
                raise TypeMismatchInExpression(ast)
            self.typeConstraints.pop()

        return_type_constr = self.typeConstraints[-1]

        if isinstance(return_type_constr, ArrayType):
            if not fn_type.returnType:
                raise TypeCannotBeInferred(ast)

            return isinstance(fn_type.returnType, ArrayType)

        if isinstance(return_type_constr, TypePlaceholder):
            raise TypeCannotBeInferred(ast)

        if not fn_type.returnType:
            fn_type.returnType = return_type_constr

        return compatibleTypes(return_type_constr, fn_type)

    def visitBlock(self, ast: Block, param):
        self.beginScope()
        for stmt in ast.stmt:
            stmt.accept(self, None)
        self.endScope()

    def visitIf(self, ast: If, param):
        self.typeConstraints.append(BoolType())

        if not ast.expr.accept(self, None):
            raise TypeMismatchInStatement(ast)
        ast.thenStmt.accept(self, None)

        for cond, block in ast.elifStmt:
            if not cond.accept(self, None):
                raise TypeMismatchInStatement(ast)
            block.accept(self, None)

        if ast.elseStmt:
            ast.elseStmt.accept(self, None)
        
        self.typeConstraints.pop()

    def visitFor(self, ast: For, param):
        self.inLoop = True
        ast.body.accept(self, None)
        self.inLoop = False

    def visitReturn(self, ast: Return, param):
        pass

    def visitArrayLiteral(self, ast: ArrayLiteral, param):
        assert ast.value != []
        type_constr = self.typeConstraints[-1]

        if type_constr.__class__ not in [ArrayType, TypePlaceholder]:
            return False

        if (isinstance(type_constr, TypePlaceholder) 
            and type_constr.getType().__class__ not in [ArrayType, None.__class__]):
            return False

        if isinstance(type_constr, TypePlaceholder):
            type_constr_unwrapped = type_constr.getType()
            if isinstance(type_constr_unwrapped, ArrayType) and len(type_constr_unwrapped.size) > 1:
                type_var = TypePlaceholder()
                type_var.setType(ArrayType(eleType=type_constr_unwrapped.eleType,
                                        size=type_constr_unwrapped.size[1:]))
                self.typeConstraints.append(type_var)
            elif isinstance(type_constr_unwrapped, ArrayType):
                # the expressions in the array are subject to belonging to atomic type
                self.typeConstraints.append(type_constr_unwrapped.eleType)
            else:
                self.typeConstraints.append(TypePlaceholder())
            
            # Visit the first expression in the array to infer its element type.
            # If the element type is inferred by visiting another expression, this visiting is used
            # to check if the constraint put on the expression is satisfied.
            visit_head = ast.value[0].accept(self, None)
            if not visit_head:
                return False

            head_ele_type = self.typeConstraints[-1]

            # Unwrap the type variable if it is inferred to an atomic type
            # otherwise, keep it as it is because we arent sure that the size of other subarray is
            # the same as the first one.
            if (isinstance(head_ele_type, TypePlaceholder) 
                and not isinstance(head_ele_type.getType(), ArrayType)):
                head_ele_type = head_ele_type.getType()

            self.typeConstraints[-1] = head_ele_type

            for expr in ast.value[1:]:
                visit_expr = expr.accept(self, None)
                if not visit_expr:
                    return False

            ele_type = self.typeConstraints.pop()

            if isinstance(type_constr_unwrapped, ArrayType):
                if len(type_constr_unwrapped.size) == 1:
                    inferred_arr_size = [max(type_constr_unwrapped.size[0], len(ast.value))]
                else:
                    inferred_arr_size = list(map(lambda pair: max(pair),
                                   zip(type_constr_unwrapped.size, ele_type.size)))

                type_constr.setType(ArrayType(eleType=type_constr_unwrapped.eleType,
                                      size=inferred_arr_size))
            else:
                assert type_constr_unwrapped is None
                if isinstance(ele_type, TypePlaceholder):
                    ele_type = ele_type.getType()

                if isinstance(ele_type, ArrayType):
                    arr_type = ArrayType(eleType=ele_type.eleType,
                                    size=[len(ast.value)] + ele_type.size)
                else:
                    arr_type = ArrayType(eleType=ele_type,
                                         size=[len(ast.value)])

                type_constr.setType(arr_type)
        else:
            assert isinstance(type_constr, ArrayType)

            if len(ast.value) != type_constr.size[0]:
                return False

            ele_type_constr = None
            if len(type_constr.size) != 1:
                ele_type_constr = ArrayType(eleType=type_constr.eleType, size=type_constr.size[1:])
            else:
                ele_type_constr = type_constr.eleType

            self.typeConstraints.append(ele_type_constr)

            for expr in ast.value:
                satisfied_constr = expr.accept(self, None)
                if not satisfied_constr:
                    return False
            
            self.typeConstraints.pop()

        return True

    def visitId(self, ast: Id, param):
        id_name = ast.name

        # if identifier refers to a function, retrieve its return type
        id_type = self.typeEnv.getType(id_name)

        if not id_type:
            raise Undeclared(Identifier(), id_name)

        if isinstance(id_type, TypePlaceholder):
            # Infer type of the identifier
            # We cannot infer a variable to an array type.
            if (self.typeConstraints == [] or isinstance(self.typeConstraints[-1],
                                                         TypePlaceholder)):
                raise TypeCannotBeInferred(ast)

            if isinstance(self.typeConstraints[-1], ArrayType) and self.typeConstraints[-1].size == []:
                    raise TypeCannotBeInferred(ast)

            self.typeEnv.setType(id_name, self.typeConstraints[-1])
            return True

        if self.typeConstraints == []:
            return True

        type_constr = self.typeConstraints[-1]

        if isinstance(type_constr, ArrayType) and isinstance(id_type, ArrayType) and type_constr.size == []:
            # this code is used for cases that we only need to ensure that a function call or
            # identifier returns an array.
            return compatibleTypes(type_constr.eleType, id_type.eleType)

        if isinstance(type_constr, TypePlaceholder):
            type_constr.setType(id_type)
        
        return compatibleTypes(self.typeConstraints[-1], id_type)

    def visitNumberLiteral(self, ast, param):
        type_constraint = self.typeConstraints[-1]
        if isinstance(type_constraint, TypePlaceholder):
            type_constraint.setType(NumberType())
        return compatibleTypes(type_constraint, NumberType())

    def visitBooleanLiteral(self, ast, param):
        type_constraint = self.typeConstraints[-1]
        if isinstance(type_constraint, TypePlaceholder):
            type_constraint.setType(BoolType())
        return compatibleTypes(type_constraint, BoolType())

    def visitStringLiteral(self, ast, param):
        type_constraint = self.typeConstraints[-1]
        if isinstance(type_constraint, TypePlaceholder):
            type_constraint.setType(StringType())
        return compatibleTypes(type_constraint, StringType())
