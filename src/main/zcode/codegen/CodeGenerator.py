from Emitter import Emitter
from functools import reduce
from Frame import Frame
from abc import ABC
from Visitor import *
from AST import *

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

class MType:
    def __init__(self, partype, rettype):
        self.partype = partype
        self.rettype = rettype

class Symbol:
    def __init__(self, name, mtype, value=None):
        self.name = name
        self.mtype = mtype
        self.value = value

    def __str__(self):
        return "Symbol("+self.name+","+str(self.mtype)+")"

class CodeGenerator:
    def __init__(self):
        self.libName = "io"

    def init(self):
        return [Symbol("readInt", MType(list(), IntType()), CName(self.libName)),
                Symbol("writeInt", MType([IntType()], VoidType()), CName(self.libName)),
                Symbol("writeIntLn", MType([IntType()], VoidType()), CName(self.libName)),
                Symbol("writeFloat", MType([FloatType()], VoidType()), CName(self.libName))]

    def gen(self, ast, path):
        # ast: AST
        # dir_: String

        gl = self.init()
        gc = CodeGenVisitor(ast, gl, path)
        gc.visit(ast, None)


class SubBody():
    def __init__(self, frame, sym):
        self.frame = frame
        self.sym = sym


class Access():
    def __init__(self, frame, sym, isLeft, isFirst=False):
        self.frame = frame
        self.sym = sym
        self.isLeft = isLeft
        self.isFirst = isFirst

class Val(ABC):
    pass

class Index(Val):
    def __init__(self, value):
        self.value = value


class CName(Val):
    def __init__(self, value):
        self.value = value

class TypeInferenceVisitor(BaseVisitor):
    def __init__(self, ast):
        self.ast = ast

        # a list of tuples, each one includes variable's name and its corresponding type.
        # if the variable type is not inferred yet, the second item of the pair is None.
        self.varTypePairs = []

        # key: function's name
        # value: [<list of parameter types>, <return type>]
        self.funcType = {}

        # name of the function whose body the visitor is in
        self.currentFuncName = None

    def infer(self):
        self.ast.accept(self, None)
        return self.varTypePairs, self.funcType

    def visitProgram(self, ast: Program, param):
        for decl in ast.decl:
            decl.accept(self, None)

    def visitVarDecl(self, ast: VarDecl, param):
        if ast.varType:
            self.varTypePairs.append([ast.name.name, ast.varType])
            return

        exprType = ast.varInit.accept(self, param) if ast.varInit is not None else None
        self.varTypePairs.append([ast.name.name, exprType])

    def visitFuncDecl(self, ast: FuncDecl, param):
        self.currentFuncName = ast.name.name
        params = tuple(map(lambda decl: decl.varType, ast.param))
        self.funcType[self.currentFuncName] = [params, None]
        for paramDecl in ast.param:
            paramDecl.accept(self, None)
        if ast.body is not None:
            ast.body.accept(self, param)
        self.currentFuncName = None

    def visitBlock(self, ast: Block, param):
        for stmt in ast.stmt:
            stmt.accept(self, param)

    def visitReturn(self, ast: Return, param):
        resolvedReturnType = self.funcType[self.currentFuncName][1]
        returnType = VoidType() if ast.expr is None else ast.expr.accept(self, resolvedReturnType)
        self.funcType[self.currentFuncName][1] = returnType 

    def visitCallStmt(self, ast: CallStmt, param):
        funcType = self.funcType[ast.name.name]
        paramTypes, returnType = funcType[0], funcType[1]
        for arg, paramType in zip(ast.args, paramTypes):
            arg.accept(self, paramType)
        if returnType is None:
            funcType[1] = VoidType()
        return funcType[1]
    
    def visitBreak(self, ast: Break, vmState: Access):
        pass

    def visitContinue(self, ast: Continue, vmState: Access):
        pass

    def visitIf(self, ast: If, param):
        ast.expr.accept(self, BoolType())
        ast.thenStmt.accept(self, param)
        if ast.elifStmt is not None:
            for expr, stmt in ast.elifStmt:
                expr.accept(self, BoolType())
                stmt.accept(self, param)
        if ast.elseStmt:
            ast.elseStmt.accept(self, param)
    
    def visitFor(self, ast: For, param):
        ast.name.accept(self, NumberType())
        ast.condExpr.accept(self, BoolType())
        ast.updExpr.accept(self, NumberType())
        ast.body.accept(self, param)

    def visitAssign(self, ast: Assign, param):
        leftType = ast.lhs.accept(self, param)
        if leftType is None:
            rightType = ast.rhs.accept(self, param)
            ast.lhs.accept(self, rightType)
        else:
            ast.rhs.accept(self, leftType)

    def visitNumberLiteral(self, ast: NumberLiteral, param):
        return NumberType()

    def visitBooleanLiteral(self, ast: BooleanLiteral, param):
        return BoolType()

    def visitStringType(self, ast: StringType, param):
        return StringType()

    def visitArrayLiteral(self, ast: ArrayLiteral, param):
        # get type constraint of array's elements
        if param is None:
            eleType = ast.value[0].accept(self, None)
            for expr in ast.value[1:]:
                expr.accept(self, eleType)
        else:
            assert type(param) is ArrayType
            eleType = param.eleType
            for expr in ast.value:
                expr.accept(self, eleType)

        if type(eleType) is ArrayType:
            arrType = ArrayType(eleType=eleType.eleType, size=[float(len(ast.value))] + eleType.size)
        else:
            arrType = ArrayType(eleType=eleType, size=[float(len(ast.value))])

        return arrType

    def visitId(self, ast: Id, typeConstr):
        varTypePair = next(filter(lambda pair: pair[0] == ast.name, reversed(self.varTypePairs)), None)
        assert varTypePair is not None

        if varTypePair[1] is None:
            varTypePair[1] = typeConstr

        return varTypePair[1]

    def visitCallExpr(self, ast: CallExpr, param):
        funcType = self.funcType[ast.name.name]
        paramTypes, returnType = funcType
        for arg, paramType in zip(ast.args, paramTypes):
            arg.accept(self, paramType)
        if returnType is None:
            funcType[1] = param
        return funcType[1]

    def visitArrayCell(self, ast: ArrayCell, param):
        arrType = ast.arr.accept(self, param)
        assert type(arrType) is ArrayType
        for expr in ast.idx:
            expr.accept(self, NumberType())
        return arrType.eleType

    def visitUnaryOp(self, ast: UnaryOp, param):
        ast.operand.accept(self, getOperandType(ast.op))
        return getResultType(ast.op)

    def visitBinaryOp(self, ast: BinaryOp, param):
        operandType = getOperandType(ast.op)
        ast.left.accept(self, operandType)
        ast.right.accept(self, operandType)
        return getResultType(ast.op)

class CodeGenVisitor(BaseVisitor):
    def __init__(self, astTree, env, path, typeArr, funcReturnType):
        self.astTree = astTree
        self.env = env
        self.path = path
        self.emitter = Emitter(self.path)
        self.typeArr = typeArr
        self.typeIter = iter(self.typeArr)
        self.funcReturnType = funcReturnType
        self.globalFrame = Frame("<clinit>", VoidType())
        self.globalVarGen = []
        self.className = "ZCodeClass"

    def getVarTypePair(self):
        return next(self.typeIter, None)

    def gen(self):
        vmState = Access(self.globalFrame, [], False)
        self.astTree.accept(self, vmState)

    def visitProgram(self, ast, vmState: Access):
        for decl in ast.decl:
            decl.accept(self, vmState)

        self.writeClinitMethod()

    def genInitMethod(self):
        pass

    def writeClinitMethod(self):
        """write out generated code for global variable initialization to the buffer.
        All of the code is inside <clinit> function.
        The associated frame to <clinit> is self.globalFrame.
        The generated code for declaration expressions is in self.globalVarGen. 
        This method should be invoked after all of the declarations are visited.
        """
        self.writeoutMethod(''.join(self.globalVarGen), self.globalFrame)

    def writeoutMethod(self, bodyGen: str, frame: Frame):
        """Write out generated code for a static method to the buffer.
        This should be called after the function's body is visited.

        Args:
            bodyGen (str): generated code for the parameter declaration and function body.
            frame (Frame): frame object associated with the function.
        """
        fname = frame.name
        returnType = frame.returnType

        self.emitter.printout(self.emitter.emitMETHOD(fname, returnType, True, frame))
        self.emitter.printout(self.emitter.emitLIMITLOCAL(frame.getMaxIndex() + 1))
        self.emitter.printout(self.emitter.emitLIMITSTACK(frame.getMaxOpStackSize()))
        self.emitter.printout(bodyGen)
        self.emitter.printout(self.emitter.emitENDMETHOD(frame))


    def visitFuncDecl(self, ast: FuncDecl, vmState: Access):
        if ast.body is None:
            return

        fname = ast.name.name

        # new frame associated with the function.
        vmState.frame = Frame(fname, self.funcReturnType[fname])

        # generate code for parameter's declaration and body.
        vmState.frame.enterScope(True)

        paramDecl = ''.join([decl.accept(self, vmState) for decl in ast.param])

        # function's body can be a block or a return statement.
        bodyGen = ''.join(ast.body.accept(self, vmState)) if type(ast.body) is Block else ast.body.accept(self, vmState)

        vmState.frame.exitScope()
        
        # emit the generated code to the emitter's buffer.
        self.writeoutMethod(paramDecl + bodyGen, vmState.frame)

        vmState.frame = self.globalFrame

    def visitBlock(self, ast: Block, vmState: Access):
        vmState.frame.enterScope(False)
        gen = [stmt.accept(self, vmState) for stmt in ast.stmt]
        vmState.frame.exitScope()
        return gen

    def visitVarDecl(self, ast: VarDecl, vmState: Access):
        iden = ast.name

        # a tuple: (variable name, variable type)
        varTypePair = self.getVarTypePair()
        assert varTypePair is not None and type(varTypePair) is tuple and varTypePair[0] == iden.name
        varName, varType = varTypePair

        # generate directive and create symbol
        if vmState.frame.name == "<clinit>":
            # global variable
            directive = self.emitter.emitATTRIBUTE(iden.name, varType, False, None)
            varSym = Symbol(name=varName, mtype=varType, value=CName(self.className))
        else:
            # local variable
            startLabel = vmState.frame.getStartLabel()
            endLabel = vmState.frame.getEndLabel()
            directive = self.emitter.emitVAR(varType, varName, startLabel, startLabel, endLabel, vmState.frame)
            varSym = Symbol(name=varName, mtype=varName, value=Index(vmState.frame.getNewIndex()))

        self.emitter.printout(directive)
        if ast.varInit is not None:
            # generate code for variable initialization
            exprCode, exprType = ast.varInit.accept(self, vmState)
            assert type(varType) is type(exprType)
            if vmState.frame.name == "<clinit>":
                # global variable
                writeVarGen = self.emitter.emitPUTSTATIC(varName, varType, vmState.frame)
                self.globalVarGen.append(writeVarGen)
            else:
                # local variable
                writeVarGen = self.emitter.emitWRITEVAR(varName, varType, varSym.value.value, vmState.frame)
                self.emitter.printout(exprCode + writeVarGen)

        return varSym

    def visitBinaryOp(self, ast: BinaryOp, vmState: Access):
        leftOperandGen, leftType = ast.left.accept(self, vmState)
        rightOperandGen, rightType = ast.right.accept(self, vmState)

        if ast.op in ['+', '-']:
            opGen = self.emitter.emitADDOP(ast.op, leftType, vmState.frame)
        elif ast.op in ['*', '/']:
            opGen = self.emitter.emitMULOP(ast.op, leftType, vmState.frame)
        elif ast.op == '%':
            opGen = self.emitter.emitMOD(ast.op, vmState.frame)
        elif ast.op in ['>', '<', '=', '<=', '>=', '==', '=', '!=']:
            opGen = self.emitter.emitREOP(ast.op, leftType, vmState.frame)
        elif ast.op in ['and', 'or']:
            opGen = None
        elif ast.op == 'not':
            opGen = None
        else:
            opGen = None

        assert opGen is not None
        return (leftOperandGen + rightOperandGen + opGen), getResultType(ast.op)

    def visitUnaryOp(self, ast: UnaryOp, vmState: Access):
        operandCode, operandType = ast.operand.accept(self, vmState)
        if ast.operand == 'not':
            operatorCode = self.emitter.emitNOT(operandType, vmState)
        else:
            # ast.op == '-', use ineg
            operatorCode = self.emitter.emitNEGOP(ast.operand, vmState.frame)
        return operandCode + operatorCode, operandType

    def visitArrayCell(self, ast: ArrayCell, vmState: Access):
        pass

    def visitArrayLiteral(self, ast: ArrayLiteral, vmState: Access):
        assert ast.value != []

        codeGen = []

        exprGen, eleType = ast.value[0].accept(self, vmState)

        arrGen = self.emitter.emitARRAY(eleType, vmState.frame)
        codeGen.append(arrGen)

        # load the result of the first expression into the array
        codeGen.append(self.emitter.emitDUP(vmState.frame))
        codeGen.append(exprGen)
        codeGen.append(self.emitter.emitLOADARRITEM(eleType=eleType, idx=0, frame=vmState.frame))

        for i, expr in enumerate(ast.value, 1):
            # load the result of the ith expression into the array
            exprGen, exprType = expr.accept(self, vmState)
            codeGen.append(self.emitter.emitDUP(vmState.frame))
            codeGen.append(exprGen)
            codeGen.append(self.emitter.emitLOADARRITEM(eleType=eleType, idx=i, frame=vmState.frame))
        if type(eleType) is ArrayType:
            arrType = ArrayType(eleType=eleType.eleType, size=[float(len(ast.value))] + eleType.size)
        else:
            arrType = ArrayType(eleType=eleType, size=[float(len(ast.value))])
        return ''.join(codeGen), arrType

    def visitNumberLiteral(self, ast: NumberLiteral, vmState: Access):
        return self.emitter.emitPUSHFCONST(ast.value, vmState), NumberType()

    def visitBooleanLiteral(self, ast: BooleanLiteral, vmState: Access):
        return self.emitter.emitPUSHICONST(1 if ast.value else 0, vmState.frame), BoolType()

    def visitStringLiteral(self, ast: StringLiteral, vmState: Access):
        return self.emitter.emitPUSHFCONST(ast.value, vmState.frame), StringType()
