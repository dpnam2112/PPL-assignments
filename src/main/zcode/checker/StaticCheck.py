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
    def __init__(self, arg_types, return_type):
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

class IllegalArrayLiteral(Exception):
    def __init__(self, ast):
        self.ast = ast

    def __str__(self):
        return f"IllegalArrayLiteral({self.ast})"

class StaticChecker(BaseVisitor, Utils):
    """Static checker is used to check if the input program satisfies all semantic constraints
    defined by the ZCode programming language.

    While checking, it also has to infer types of all unknown-type variables. For instance:
    ========== Example snippet ==========
    dynamic x
    number y
    x <- y
    ========== Example snippet ==========
    In the above example, the static checker has to infer the type of 'x'. From the declaration of
    'y' and the assignment statement, so the checker can conclude that the type of 'x' must be
    number.

    The strategy used by the checker is as follows: It uses a stack represented by a list to
    store all the constraints for expressions. Whenever the checker visits an expression, it peeks
    the top constraint in the stack, and compare the return type of the expression (which can be deduced 
    from the operator, e.g, result of an addition expression must have return a number) with the 
    constraint. If the constraint is satisfied, it proceeds to add the constraints for the
    expression's operands and visit these operands. If all of the constraints for operands are
    satisfied, the visit function returns True to indicate that the expression satisfies the
    constraint.

    For example, in this expression:
    number x <- a + b
    In this context, types of a and b haven't been deduced yet. The visitor visits the declaration
    and add the type constraint:
    [number]
    This means that, the initialization expression must return a number.
    Next, it proceeds to visit the initialization expression. It compares the return type of '+'
    with the top constraint in the stack:
    number = number
    So, the return type constraint is satisfied. Note that, if the return type constraint were not
    satisfied in this case, then the visitor would return false.
    The operands' types of '+' must be numbers, so the checker pushes a constraint to the stack:
    [number, number]
    Then, it visits each operand. the type of x hasn't been inferred yet, so we use the return
    type constraint to infer its type. The type of 'x' must be number. The checker does the same thing
    for 'b', and it infers that b's type must be number too.

    For some cases, we cannot infer the type of a variable from the expression. For example:
    ========== Example snippet ==========
    dynamic x
    number y <- x[10]
    ========== Example snippet ==========
    This case is ambiguous. Although we know that x is an array of numbers, but what about its size?
    The checker raises an exception if it encounters such cases.
    """
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
        main_fn_type = self.typeEnv.getType('main')

#        if not (main_decl and main_decl.param == [] and main_decl.body and ):
#            raise NoEntryPoint()

        if not (main_fn_type and isinstance(main_fn_type, FnType) and
                isinstance(main_fn_type.returnType, VoidType) and main_fn_type.argTypes == []):
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

        if(prev_decl.body or not ast.body or len(prev_decl.param) != len(ast.param)):
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
        for param_decl in ast.param:
            try:
                param_decl.accept(self, None)
            except Redeclared as exception:
                exception.kind = Parameter()
                raise exception

        self.beginScope()
        if ast.body:
            ast.body.accept(self, None)
            if not fn_type.returnType:
                fn_type.returnType = VoidType()

        self.endScope()
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
                and not (isinstance(exception.stmt, Id)
                         or isinstance(exception.stmt, CallExpr))):
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
            try:
                ast.lhs.accept(self, None)
#                if not self.typeConstraints[-1].getType():
#                    raise TypeCannotBeInferred(ast)
            except TypeCannotBeInferred as e:
                e.stmt = ast
                raise e

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

        # We cannot conclude that a variable of unknown type is an array if the variable is used
        # in an index expression.
        # for example, this case is ambiguous:
        # ======================================
        # dynamic x
        # number y <- x[1, 2, 3]
        # ======================================
        # Although we can infer the type of x[1, 2, 3], but what about x? It is for sure an array of
        # number, but what is its size? [4, 4, 4]? [10, 10, 10]?
        #
        # So, we cannot infer the type of the array in this case. The 'invalid array' (its size is
        # empty) is pushed to the list of constraints so the checker can use it to determine if it
        # is able to infer the type of a variable or the return type of a function.

        self.typeConstraints.append(ArrayType(eleType=self.typeConstraints[-1], size=[]))
        if not ast.arr.accept(self, None):
            # Determine whether the type mismatch occurred in the index expression, or in the
            # upper expression
            if isinstance(ast.arr, Id):
                arr_name = ast.arr.name
                if not isinstance(self.typeEnv.getType(arr_name), ArrayType):
                    raise TypeMismatchInExpression(ast)
            elif isinstance(ast.arr, CallExpr):
                fn_name = ast.arr.name.name
                fn_type = self.typeEnv.getType(fn_name)
                if not isinstance(fn_type.returnType, ArrayType):
                    raise TypeMismatchInExpression(ast)

            self.typeConstraints.pop()
            return False
        self.typeConstraints.pop()

        return True

    def visitCallStmt(self, ast: CallStmt, param):
        fn_name = ast.name.name

        fn_type = self.typeEnv.getType(fn_name)
        if not fn_type:
            raise Undeclared(Function(), fn_name)

        if (not isinstance(fn_type, FnType) 
            or len(ast.args) != len(fn_type.argTypes)
            or not (fn_type.returnType is None or isinstance(fn_type.returnType, VoidType))):
            raise TypeMismatchInStatement(ast)

        if not fn_type.returnType:
            fn_type.returnType = VoidType()

        for arg_type, arg_expr in zip(fn_type.argTypes, ast.args):
            if not isinstance(arg_type, ArrayType):
                self.typeConstraints.append(arg_type)
                if not arg_expr.accept(self, None):
                    raise TypeMismatchInStatement(ast)
                self.typeConstraints.pop()
            else:
                self.typeConstraints.append(TypePlaceholder())
                arg_expr.accept(self, None)
                passed_param_type = self.typeConstraints.pop().getType()
                if not isinstance(passed_param_type, ArrayType) or passed_param_type.size != arg_type.size:
                    raise TypeMismatchInStatement(ast)

    def visitCallExpr(self, ast: CallExpr, param):
        fn_name = ast.name.name

        fn_type = self.typeEnv.getType(fn_name)
        if not fn_type:
            raise Undeclared(Function(), fn_name)

        if (not isinstance(fn_type, FnType) 
            or len(ast.args) != len(fn_type.argTypes) 
            or isinstance(fn_type.returnType, VoidType)):
            raise TypeMismatchInExpression(ast)

        for arg_type, arg_expr in zip(fn_type.argTypes, ast.args):
            if not isinstance(arg_type, ArrayType):
                self.typeConstraints.append(arg_type)
                if not arg_expr.accept(self, None):
                    raise TypeMismatchInExpression(ast)
                self.typeConstraints.pop()
            else:
                self.typeConstraints.append(TypePlaceholder())
                arg_expr.accept(self, None)
                passed_param_type = self.typeConstraints.pop().getType()
                if not isinstance(passed_param_type, ArrayType) or passed_param_type.size != arg_type.size:
                    raise TypeMismatchInExpression(ast)

        return_type_constr = self.typeConstraints[-1]

        if not fn_type.returnType:
            # infer function's return type
            if (isinstance(return_type_constr, ArrayType) and return_type_constr.size == []):
                raise TypeCannotBeInferred(ast)

            if isinstance(return_type_constr, TypePlaceholder) and not return_type_constr.getType():
                raise TypeCannotBeInferred(ast)

            fn_type.returnType = return_type_constr

        if isinstance(return_type_constr, TypePlaceholder):
            return_type_constr.setType(fn_type.returnType)

        if isinstance(return_type_constr, ArrayType) and return_type_constr.size == [] and isinstance(fn_type.returnType, ArrayType):

            if isinstance(return_type_constr.eleType, TypePlaceholder):
                return_type_constr.eleType.setType(fn_type.returnType.eleType)

            return compatibleTypes(return_type_constr.eleType, fn_type.returnType.eleType)
        
        return compatibleTypes(return_type_constr, fn_type.returnType)

    def visitBlock(self, ast: Block, param):
        self.beginScope()
        for stmt in ast.stmt:
            stmt.accept(self, None)
        self.endScope()

    def visitIf(self, ast: If, param):
        self.typeConstraints.append(BoolType())

        try:
            if not ast.expr.accept(self, None):
                raise TypeMismatchInStatement(ast)
        except TypeCannotBeInferred:
            raise TypeCannotBeInferred(ast)

        ast.thenStmt.accept(self, None)

        for cond, block in ast.elifStmt:
            try:
                if not cond.accept(self, None):
                    raise TypeMismatchInStatement(ast)
            except TypeCannotBeInferred:
                raise TypeCannotBeInferred(ast)

            block.accept(self, None)

        if ast.elseStmt:
            ast.elseStmt.accept(self, None)
        
        self.typeConstraints.pop()

    def visitFor(self, ast: For, param):
        self.inLoop = True
        try:
            self.typeConstraints.append(NumberType())
            if not ast.name.accept(self, None):
                raise TypeMismatchInStatement(ast)
            self.typeConstraints.append(BoolType())
            if not ast.condExpr.accept(self, None):
                raise TypeMismatchInStatement(ast)
            self.typeConstraints.append(NumberType())
            if not ast.updExpr.accept(self, None):
                raise TypeMismatchInStatement(ast)
        except TypeCannotBeInferred:
            raise TypeCannotBeInferred(ast)

        self.typeConstraints = self.typeConstraints[:-3]
        ast.body.accept(self, None)
        self.inLoop = False

    def visitReturn(self, ast: Return, param):
        fn_name = self.getCurrentFnName()
        fn_type = self.typeEnv.getType(fn_name)

        assert isinstance(fn_type, FnType)

        if not ast.expr:
            if not fn_type.returnType:
                fn_type.returnType = VoidType()
            elif not isinstance(fn_type, VoidType):
                raise TypeMismatchInStatement(ast)
        else:
            self.typeConstraints.append(fn_type.returnType or TypePlaceholder())

            try:
                if not ast.expr.accept(self, None):
                    raise TypeMismatchInStatement(ast)
            except TypeCannotBeInferred:
                raise TypeCannotBeInferred(ast)

            return_type = self.typeConstraints.pop()
            if isinstance(return_type, TypePlaceholder):
                fn_type.returnType = return_type.getType()

    def visitArrayLiteral(self, ast: ArrayLiteral, param):
        assert ast.value != []
        type_constr = self.typeConstraints[-1]

        if type_constr.__class__ not in [ArrayType, TypePlaceholder]:
            return False

        if (isinstance(type_constr, TypePlaceholder) 
            and type_constr.getType().__class__ not in [ArrayType, None.__class__]):
            return False

        if isinstance(type_constr, TypePlaceholder):
            return self.visitUnknownTypeArrLit(ast, None)
        else:
            return self.visitKnownTypeArrLit(ast, None)

    def visitUnknownTypeArrLit(self, ast: ArrayLiteral, param):
        assert isinstance(self.typeConstraints[-1], TypePlaceholder)

        # constraint applied for this array
        arr_type_constr = self.typeConstraints[-1]

        self.typeConstraints.append(TypePlaceholder())
        ast.value[0].accept(self, None)

        first_ele_type = self.typeConstraints.pop()
        if not isinstance(first_ele_type.getType(), ArrayType):
            first_ele_type = first_ele_type.getType()

        self.typeConstraints.append(first_ele_type)
        for expr in ast.value[1:]:
            if not expr.accept(self, None):
                return False
        ele_type_constr = self.typeConstraints.pop()

        if isinstance(ele_type_constr, TypePlaceholder):
            ele_type_constr = ele_type_constr.getType()

        arr_type = None
        if isinstance(ele_type_constr, ArrayType):
            arr_type = ArrayType([len(ast.value)] + ele_type_constr.size, ele_type_constr.eleType)
        else:
            # element type must be scalar type in this case
            arr_type = ArrayType([len(ast.value)], ele_type_constr)

        if not arr_type_constr.getType():
            arr_type_constr.setType(arr_type)
        else:
            # If this array has an constraint applied to it
            # this case can happen for subarrays
            arr_type_constr = arr_type_constr.getType()
            assert isinstance(arr_type_constr, ArrayType)
            if len(arr_type_constr.size) != len(arr_type.size) or not compatibleTypes(arr_type_constr.eleType, arr_type.eleType):
                return False

            inferred_size = list(map(lambda pair: max(pair), zip(arr_type_constr.size, arr_type.size)))
            arr_type_constr.size = inferred_size

        return True

    def visitKnownTypeArrLit(self, ast: ArrayLiteral, param):
        assert isinstance(self.typeConstraints[-1], ArrayType)
        type_constr = self.typeConstraints[-1]

        if len(ast.value) > type_constr.size[0]:
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
            if (self.typeConstraints == [] or isinstance(self.typeConstraints[-1],
                                                         TypePlaceholder)):
                raise TypeCannotBeInferred(ast)

            # Invalid array constraint is pushed when the index expression is visited.
            if isinstance(self.typeConstraints[-1], ArrayType) and self.typeConstraints[-1].size == []:
                    raise TypeCannotBeInferred(ast)

            self.typeEnv.setType(id_name, self.typeConstraints[-1])
            return True

        if self.typeConstraints == []:
            return True

        type_constr = self.typeConstraints[-1]

        if isinstance(type_constr, ArrayType) and isinstance(id_type, ArrayType) and type_constr.size == []:
            # this code is used for cases that we only need to ensure that a function call or
            # identifier just returns an array, regardless of its size.
            if isinstance(type_constr.eleType, TypePlaceholder):
                # resolve the type constraint of the index expression
                type_constr.eleType.setType(id_type.eleType)

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
