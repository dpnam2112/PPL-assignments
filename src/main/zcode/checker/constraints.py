from type_env import FnType, TypePlaceholder, annotateType, getExpressionType
from AST import *
from StaticError import Function, Identifier, Redeclared, Undeclared
from Visitor import *
from type_env import TypeEnvironment, getTypeAnnotation
from heapq import heapify, heappop, heappush
from functools import reduce

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

def isType(t):
    return isinstance(t, Type)

def containTypeVar(t):
    if t.__class__ in [StringType, NumberType, BoolType, VoidType]:
        return False

    if isinstance(t, ArrayType):
        return containTypeVar(t.eleType)

    return True

class Constraint:
    def __init__(self, lhs, rhs, order):
        self.lhs = lhs
        self.rhs = rhs
        self.order = order

    def computeScore(self):
        score = 0
        
        score += not containTypeVar(self.lhs) and 1 or 0
        score += not containTypeVar(self.rhs) and 1 or 0

        return score

    def __eq__(self, other):
        return self.computeScore() == other.computeScore() and self.order == other.order

    def __gt__(self, other):
        # other is more prior than self
        lhs_score = self.computeScore()
        rhs_score = other.computeScore()

        if lhs_score != rhs_score:
            return lhs_score < rhs_score

        return self.order > other.order

    def __lt__(self, other):
        # self is more prior than other
        lhs_score = self.computeScore()
        rhs_score = other.computeScore()

        if lhs_score != rhs_score:
            return lhs_score > rhs_score

        return self.order < other.order 

    def __str__(self):
        return f"Constraint({str(self.lhs)} = {str(self.rhs)}, order = {self.order})"

class ConstraintResolver:
    def __init__(self, type_env: TypeEnvironment, constraints: list[Constraint]):
        self.typeEnv = type_env
        self.constraints = constraints

    def resolve(self):
        if not self.constraints:
            return

        heapify(self.constraints)
        unresolved = []

        while len(self.constraints) != 0:
            constraint = heappop(self.constraints)
            print(f"{constraint}")
            if not self.resolveConstraint(constraint):
                unresolved.append(constraint)

        unresolved_count = len(unresolved)
        prev_unresolved_count = len(unresolved)

        while unresolved_count != 0:
            for constraint in unresolved:
                if self.resolveConstraint(constraint):
                    unresolved_count -= 1

            if unresolved_count >= prev_unresolved_count:
                break

            prev_unresolved_count = unresolved_count

    def resolveConstraint(self, constraint: Constraint):
        lhs = constraint.lhs
        rhs = constraint.rhs

        for t in [lhs, rhs]:
            if isinstance(t, ArrayType):
                t = t.eleType
        

        if not (containTypeVar(lhs) or containTypeVar(rhs)):
            return

        if not containTypeVar(lhs):
            rhs_type_var = rhs if not isinstance(rhs, ArrayType) else rhs.eleType
            rhs_type_var.setType(lhs)
        elif not containTypeVar(rhs):
            lhs_type_var = lhs if not isinstance(lhs, ArrayType) else lhs.eleType
            lhs_type_var.setType(rhs)
        else:
            rhs_type_var = rhs if not isinstance(rhs, ArrayType) else rhs.eleType
            lhs_type_var = lhs if not isinstance(lhs, ArrayType) else lhs.eleType

            unified = rhs_type_var.getType() or lhs_type_var.getType()
            if not unified:
                return unified

            rhs_type_var.setType(unified)
            lhs_type_var.setType(unified)

        return True

class ConstraintCollector(BaseVisitor):
    """This phase has two roles:

    Firstly, the compiler reads the program from the beginning to the end
    and perform type inference. It collects all constraints and when the compiler's done
    reading, it would resolve constraints at once.

    Secondly, in the course of the process, the compiler annotates type variables
    on the syntax tree. The type variables are used for type-checking phase.

    Thirdly, Check if there are any constraints that cannot be resolved.
    For example, we cannot perform type inference based on index operator, because
    we cannot determine the size of the array. If there is, throw TypeCannotBeInferred
    exception.

    Type variables are created if the compiler encounters variable or function declarations.
    """

    def __init__(self, prog: Program, type_env: TypeEnvironment):
        self.typeEnv = type_env
        self.currentFn: str | None = None
        self.prog = prog
        self.constraints = []
        self.defs = set() 
        self.constraintCount = 0

    def getConstraints(self):
        return self.constraints
    
    def defined(self, name: str):
        """Check if a function is defined."""
        return name in self.defs

    def defineFunction(self, name: str):
        """Mark a function as defined."""
        self.defs.add(name)

    def collect(self):
        self.prog.accept(self, None)
        return self.constraints

    def visitProgram(self, ast: Program, param):
        for decl in ast.decl:
            decl.accept(self, None)

    def visitVarDecl(self, ast: VarDecl, param):
        # we need to visit expression before identifier because there are some cases like this:
        # var a <- a
        if ast.varInit:
            ast.varInit.accept(self, None)

        var_type = ast.varType or TypePlaceholder()
        self.typeEnv.declare(ast.name.name, var_type)
        annotateType(ast.name, var_type)

        if ast.varInit:
            expr_type = getTypeAnnotation(ast.varInit)
            self.addConstraint(var_type, expr_type)
            if ast.varType and isinstance(expr_type, ArrayType) and isinstance(ast.varType, ArrayType):
                self.addConstraint(expr_type.eleType, ast.varType.eleType)

    def visitAssign(self, ast: Assign, param):
        ast.rhs.accept(self, None)
        ast.lhs.accept(self, None)

        iden = ast.rhs.arr if isinstance(ast.rhs, ArrayCell) else ast.rhs

        iden_type_var = self.typeEnv.getType(iden.name)
        lhs_type = getTypeAnnotation(ast.rhs)

        if not iden_type_var:
            raise Undeclared(Identifier(), iden.name)

        self.addConstraint(iden_type_var, lhs_type)

    def visitIf(self, ast: If, param):
        ast.expr.accept(self, None)
        self.addConstraint(getTypeAnnotation(ast), BoolType())

        ast.thenStmt.accept(self, None)
        for condition, body in ast.elifStmt:
            condition.accept(self, None)
            self.addConstraint(getTypeAnnotation(condition), BoolType())
            body.accept(self, None)

        if ast.elseStmt:
            ast.elseStmt.accept(self, None)

    def visitFor(self, ast: For, param):
        ast.name.accept(self, None)
        self.addConstraint(getTypeAnnotation(ast.name), NumberType())
        ast.condExpr.accept(self, None)
        self.addConstraint(getTypeAnnotation(ast.condExpr), BoolType())
        ast.updExpr.accept(self, None)
        self.addConstraint(getTypeAnnotation(ast.updExpr), NumberType())
        ast.body.accept(self, None)


    def visitCallStmt(self, ast: CallStmt, param):
        fn_type = self.typeEnv.getType(ast.name.name)

        if not fn_type:
            raise Undeclared(Function(), ast)

        for expr, param_type in zip(ast.args, fn_type.argTypes):
            expr.accept(self, None)
            self.addConstraint(getTypeAnnotation(expr), param_type)

        self.addConstraint(fn_type.returnType, VoidType())

    def visitFuncDecl(self, ast: FuncDecl, param):
        if self.defined(ast.name.name):
            raise Redeclared(Function(), ast.name)

        arg_types = []


        for param_decl in ast.param:
            arg_types.append(param_decl.varType)


        fn_type = self.typeEnv.getType(ast.name.name)
        if not fn_type:
            fn_type = FnType(arg_types=arg_types, 
                             return_type=TypePlaceholder())

        if ast.name.name == "main":
            self.addConstraint(fn_type.returnType, VoidType())

        self.typeEnv.declare(ast.name.name, fn_type)
        annotateType(ast.name, fn_type)

        self.typeEnv.beginScope()
        for decl in ast.param:
            decl.accept(self, None)

        if ast.body:
            ast.body.accept(self, None)
            self.defineFunction(ast.name.name)

        self.typeEnv.endScope()


    def visitBlock(self, ast: Block, param):
        self.typeEnv.beginScope()
        for stmt in ast.stmt:
            stmt.accept(self, None)
        self.typeEnv.endScope()

    def visitReturn(self, ast: Return, param):
        current_func = self.currentFn
        fn_type = self.typeEnv.getType(current_func)

        if not fn_type:
            return

        self.addConstraint(fn_type.returnType, getTypeAnnotation(ast.expr))

    def visitBinaryOp(self, ast: BinaryOp, param):
        ast.left.accept(self, ast.op)
        ast.right.accept(self, ast.op)


        self.addConstraint(getTypeAnnotation(ast.left), getOperandType(ast.op))
        self.addConstraint(getTypeAnnotation(ast.right), getOperandType(ast.op))

        annotateType(ast, getResultType(ast.op))

    def visitUnaryOp(self, ast: UnaryOp, param):
        ast.accept(self, param=ast.op)
        annotateType(ast, getResultType(ast.op))

    def visitCallExpr(self, ast: CallExpr, param):
        # Return type of the call expression is annotated on the ast

        fn_name: str = ast.name.name
        fn_type = self.typeEnv.getType(fn_name)

        if not fn_type:
            raise Undeclared(Function(), fn_name)

        for param_ast in ast.args:
            param_ast.accept(self, None)

        annotateType(ast, fn_type.returnType)

    def visitArrayCell(self, ast: ArrayCell, param):
        ast.arr.accept(self, None)

        iden_type = getTypeAnnotation(ast.arr)

        # we cannot infer the type of the array using index expression
        self.addConstraint(getTypeAnnotation(ast.arr), ArrayType(size=[], eleType=Type()))

        for idx_op in ast.idx:
            idx_op.accept(self, None)
            self.addConstraint(getTypeAnnotation(idx_op), NumberType())

    def visitId(self, ast: Id, param):
        id_name = ast.name
        # id_type could be a type variable or an instance of Type.
        id_type = self.typeEnv.getType(id_name)

        if not id_type:
            # idenfier is used before being declared
            raise Undeclared(Identifier(), id_name)

        # Annotate type variable on the AST node
        annotateType(ast, id_type)

    def visitArrayLiteral(self, ast: ArrayLiteral, param):
        # We don't do type checking in this pass, so we assume that all elements in the array are in
        # the same type.
        ele_type_var = TypePlaceholder()
        arr_type = ArrayType(eleType=ele_type_var, size=[len(ast.value)])

        # Used to resolve array's size
        subarr_sizes = []

        for expr in ast.value:
            expr.accept(self, None)
            expr_type = getTypeAnnotation(expr)

            if isinstance(expr_type, ArrayType):
                self.addConstraint(ele_type_var, expr_type.eleType)
                subarr_sizes.append(expr_type.size)
            else:
                self.addConstraint(ele_type_var, getTypeAnnotation(expr))

        # TODO: Resolve array size
        max_dimension_len = reduce(lambda max_l, arr_size: max(len(arr_size), max_l), subarr_sizes, 0)

        max_subarr_size = subarr_sizes and reduce(
                    lambda acc, size: list(map(lambda pair: max(pair), zip(size, acc))),
                    list(filter(lambda arr_size: len(arr_size) == max_dimension_len, subarr_sizes))
                )

        if max_subarr_size:
            arr_type.size += max_subarr_size
        annotateType(ast, arr_type)

    def visitNumberLiteral(self, ast, param):
        annotateType(ast, NumberType())

    def visitBooleanLiteral(self, ast, param):
        annotateType(ast, BoolType())

    def visitStringLiteral(self, ast, param):
        annotateType(ast, StringType())

    def addConstraint(self, lhs, rhs):
        constraint = Constraint(lhs, rhs, self.constraintCount) 
        self.constraints.append(constraint)
        self.constraintCount += 1
        return constraint
