from AST import *
from Visitor import *
from Utils import Utils
from StaticError import *
from constraints import *
from type_env import *

class StaticChecker(BaseVisitor, Utils):
    def __init__(self):
        pass

    def init(self, prog: Program):
        self.prog = prog
        self.typeEnv = TypeEnvironment()

        # Used to check if there is a break/continue statement outside loop.
        self.in_loop = False

        # Used to check if there is a function without definition.
        self.funcDefs = {}
        self.currentFnName = ""

    def check(self, prog: Program):
        self.init(prog)

        # Resolve type constraints
        constr_collector = ConstraintCollector(prog=self.prog, type_env=self.typeEnv)
        constraints = constr_collector.collect()
        constr_resolver = ConstraintResolver(type_env=self.typeEnv, constraints=constraints)
        constr_resolver.resolve()

        # Start checking semantic errors
        self.prog.accept(self, None)

    def visitProgram(self, ast: Program, param):
        for decl in ast.decl:
            decl.accept(self, None)

        for fname, fdef in self.funcDefs.items():
            if not fdef:
                raise NoDefinition(fname)

    def setCurrentFnName(self, name: str):
        self.currentFnName = name

    def getCurrentFnName(self) -> str:
        return self.currentFnName

    def getFnType(self, name: str):
        return getExpressionType(self.funcDefs[name])

    def visitFuncDecl(self, ast: FuncDecl, param):
        if ast.name.name not in self.funcDefs:
            self.funcDefs[ast.name.name] = None
        elif not self.funcDefs[ast.name.name]:
            raise Redeclared(Function(), ast.name.name)

        if ast.body:
            self.funcDefs[ast.name.name] = ast.body
            self.setCurrentFnName(ast.name.name)
            ast.body.accept(self, None)

    def visitVarDecl(self, ast: VarDecl, param):
        if not (ast.varType or ast.varInit):
            return

        if ast.varInit:
            ast.varInit.accept(self, None)

        if ast.varType and ast.varInit:
            var_type = ast.varType
            expr_type = getExpressionType(ast.varInit)
            if not compatibleTypes(var_type, expr_type):
                raise TypeMismatchInStatement(ast)

    def visitAssign(self, ast: Assign, param):
        ast.lhs.accept(self, None)
        ast.rhs.accept(self, None)

        lhs_type = getExpressionType(ast.lhs)
        rhs_type = getExpressionType(ast.rhs)

        if not compatibleTypes(lhs_type, rhs_type):
            raise TypeMismatchInStatement(ast)

    def visitBinaryOp(self, ast: BinaryOp, param):
        lhs_type = getExpressionType(ast.left)
        rhs_type = getExpressionType(ast.right)

        required_type = getOperandType(ast.op)

        if lhs_type.__class__ != required_type.__class__ or rhs_type.__class__ != required_type.__class__:
            raise TypeMismatchInExpression(ast)

    def visitUnaryOp(self, ast: UnaryOp, param):
        operand_type = getExpressionType(ast.operand)
        if operand_type.__class__ != getOperandType(ast.op).__class__:
            raise TypeMismatchInExpression(ast)
        ast.accept(self, None)

    def visitBreak(self, ast, param):
        if not self.in_loop:
            raise MustInLoop(stmt=ast)

    def visitContinue(self, ast, param):
        if not self.in_loop:
            raise MustInLoop(stmt=ast)

    def visitArrayCell(self, ast: ArrayCell, param):
        lhs_type = getExpressionType(ast.arr)

        if not isinstance(lhs_type, ArrayType):
            raise TypeMismatchInExpression(lhs_type)
        if not isValidArrayType(lhs_type):
            raise TypeCannotBeInferred(lhs_type)

        if len(ast.idx) != len(lhs_type.size):
            raise TypeMismatchInExpression(ast)

        for index_operand in ast.idx:
            index_type = getExpressionType(index_operand)
            if not isinstance(index_type, NumberType):
                raise TypeMismatchInExpression(ast)
            index_operand.accept(self, None)

        annotateType(ast, lhs_type.eleType)
    
    def visitCallStmt(self, ast: CallStmt, param):
        fn_type = getExpressionType(ast.name)

        if (not isinstance(fn_type, FnType)
            or not isinstance(fn_type.returnType, VoidType)
            or len(ast.args) != len(fn_type.argTypes)):
            raise TypeMismatchInExpression(ast)

        param_types = list(map(lambda expr: getExpressionType(expr), ast.args))

        for arg_type, expr_type in zip(fn_type.argTypes, param_types):
            if not expr_type or expr_type.__class__ != arg_type.__class__:
                raise TypeMismatchInExpression(ast)

    def visitCallExpr(self, ast: CallExpr, param):
        fn_type = getExpressionType(ast.name)

        if (not isinstance(fn_type, FnType)
            or isinstance(fn_type.returnType, VoidType)
            or len(ast.args) != len(fn_type.argTypes)):
            raise TypeMismatchInExpression(ast)

        param_types = list(map(lambda expr: getExpressionType(expr), ast.args))

        for arg_type, expr_type in zip(fn_type.argTypes, param_types):
            if not expr_type or expr_type.__class__ != arg_type.__class__:
                raise TypeMismatchInExpression(ast)

    def visitBlock(self, ast: Block, param):
        for stmt in ast.stmt:
            stmt.accept(self, None)

    def visitIf(self, ast: If, param):
        if not isinstance(getExpressionType(ast.expr), BoolType):
            raise TypeMismatchInStatement(ast)
        for condition, stmt in ast.elifStmt:
            if not isinstance(getExpressionType(condition), BoolType):
                raise TypeMismatchInStatement(ast)
            condition.accept(self, None)
            stmt.accept(self, None)
        if ast.elseStmt:
            ast.elseStmt.accept(self, None)

    def visitFor(self, ast: For, param):
        if not (isinstance(getExpressionType(ast.name), NumberType)
                and isinstance(getExpressionType(ast.condExpr), BoolType)
                and isinstance(getExpressionType(ast.updExpr), NumberType)):
            raise TypeMismatchInStatement(ast)

        ast.condExpr.accept(self, None)
        ast.updExpr.accept(self, None)
        ast.body.accept(self, None)

    def visitReturn(self, ast: Return, param):
        return_type = VoidType()
        if ast.expr:
            ast.expr.accept(self, None)
            expr_type = getExpressionType(ast.expr)
            if isinstance(expr_type, VoidType):
                raise TypeMismatchInStatement(ast)

        fn_type = self.getFnType(self.getCurrentFnName())
        assert isinstance(fn_type, FnType)

        if compatibleTypes(fn_type.returnType, return_type):
            raise TypeMismatchInStatement(ast)

    def visitArrayLiteral(self, ast: ArrayLiteral, param):
        arr_type = getExpressionType(ast)

        assert isinstance(arr_type, ArrayType)

        for expr in ast.value:
            expr.accept(self, None)
            expr_type = getExpressionType(expr)
            if (expr_type.__class__ != arr_type.eleType.__class
                or isinstance(expr_type, ArrayType) 
                and expr_type.eleType.__class__ != arr_type.eleType.__class__):
                raise TypeMismatchInExpression(ast)

    def visitId(self, ast, param):
        return

    def visitNumberLiteral(self, ast, param):
        return

    def visitBooleanLiteral(self, ast, param):
        return

    def visitStringLiteral(self, ast, param):
        return
