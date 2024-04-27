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

    def __str__(self):
        return str((self.partype, self.rettype))

class Symbol:
    def __init__(self, name, mtype, value=None):
        self.name = name
        self.mtype = mtype
        self.value = value

    def __str__(self):
        return "Symbol("+self.name+","+str(self.mtype)+")"

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
        self.falseLabel = None

        # label ids used for 'and' expressions.
        self.andLoadBoolLabel = None
        self.andExitLabel = None

        # label ids used for 'or' expressions.
        self.orLoadBoolLabel = None
        self.orExitLabel = None

        # label used for conditional expression in if statement.
        self.ifFalseLabel = None
        self.ifTrueLabel = None

        self.requireBoolResult = None

    def __cloneAccess(self):
        access = Access(self.frame, self.sym, self.isLeft, self.isFirst)
        access.andLoadBoolLabel = self.andLoadBoolLabel
        access.andExitLabel = self.andExitLabel
        access.orLoadBoolLabel = self.orLoadBoolLabel
        access.orExitLabel = self.orExitLabel
        access.ifFalseLabel = self.ifFalseLabel
        access.ifTrueLabel = self.ifTrueLabel
        access.requireBoolResult = self.requireBoolResult
        return access

    def withLogicalLabel(self, op, loadBoolLabel, exitLabel):
        newVmState = self.__cloneAccess()
        if op == 'and':
            newVmState.andExitLabel = exitLabel
            newVmState.andLoadBoolLabel = loadBoolLabel
            newVmState.orLoadBoolLabel = None
            newVmState.orExitLabel = None
        else:
            newVmState.orExitLabel = exitLabel
            newVmState.orLoadBoolLabel = loadBoolLabel
            newVmState.andLoadBoolLabel = None
            newVmState.andExitLabel = None
        return newVmState

    def withIfLabel(self, ifTrueLabel, ifFalseLabel):
        newVmState = self.__cloneAccess()
        newVmState.ifTrueLabel = ifTrueLabel
        newVmState.ifFalseLabel = ifFalseLabel
        return newVmState

    def withRequireBoolResult(self):
        newVmState = self.__cloneAccess()
        newVmState.requireBoolResult = True
        return newVmState

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

        # key: function's name
        # value: [<list of parameter types>, <return type>]
        self.funcType = {
            "readNumber": MType([], NumberType()),
            "readBool": MType([], BoolType()),
            "readString": MType([], StringType()),
            "writeNumber": MType([NumberType()], VoidType()),
            "writeBool": MType([BoolType()], VoidType()),
            "writeString": MType([StringType()], VoidType())
        }


        # name of the function whose body the visitor is in
        self.currentFuncName = None
        self.vars = []

        # indicate
        self.fnStart = None
        self.scopeLevel = 0

    def infer(self):
        self.ast.accept(self, None)
        return list(map(lambda t: t[:2], self.vars)), self.funcType

    def beginScope(self):
        self.scopeLevel += 1

    def endScope(self):
        self.scopeLevel -= 1

    def visitProgram(self, ast: Program, param):
        for decl in ast.decl:
            decl.accept(self, None)

    def visitVarDecl(self, ast: VarDecl, param):
        if ast.varType:
            varType = ast.varType
            if ast.varInit:
                ast.varInit.accept(self, varType)
        else:
            varType = ast.varInit.accept(self, param) if ast.varInit is not None else None
        self.vars.append([ast.name.name, varType, self.scopeLevel])

    def visitFuncDecl(self, ast: FuncDecl, param):
        self.currentFuncName = ast.name.name
        params = tuple(map(lambda decl: decl.varType, ast.param))
        self.funcType[self.currentFuncName] = MType(params, None)
        for paramDecl in ast.param:
            paramDecl.accept(self, None)
        if ast.body is not None:
            ast.body.accept(self, param)
        self.currentFuncName = None

    def visitBlock(self, ast: Block, vmState: Access):
        self.beginScope()
        for stmt in ast.stmt:
            vmState = stmt.accept(self, vmState)
        self.endScope()

    def visitReturn(self, ast: Return, param):
        resolvedReturnType = self.funcType[self.currentFuncName].rettype
        returnType = VoidType() if ast.expr is None else ast.expr.accept(self, resolvedReturnType)
        self.funcType[self.currentFuncName].rettype = returnType 

    def visitCallStmt(self, ast: CallStmt, param):
        funcType = self.funcType[ast.name.name]
        paramTypes, returnType = funcType.partype, funcType.rettype
        for arg, paramType in zip(ast.args, paramTypes):
            arg.accept(self, paramType)
        if returnType is None:
            funcType.rettype = VoidType()
        return funcType.rettype
    
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

    def visitAssign(self, ast: Assign, vmState: Access):
        leftType = ast.lhs.accept(self, vmState)
        if leftType is None:
            rightType = ast.rhs.accept(self, vmState)
            ast.lhs.accept(self, rightType)
        else:
            ast.rhs.accept(self, leftType)

    def visitNumberLiteral(self, ast: NumberLiteral, param):
        return NumberType()

    def visitBooleanLiteral(self, ast: BooleanLiteral, param):
        return BoolType()

    def visitStringLiteral(self, ast: StringLiteral, param):
        return StringType()

    def visitArrayLiteral(self, ast: ArrayLiteral, param):
        # get type constraint of array's elements
        if param is None:
            eleType = ast.value[0].accept(self, None)
            for expr in ast.value[1:]:
                expr.accept(self, eleType)
        else:
            assert type(param) is ArrayType
            if len(param.size) == 1:
                eleType = param.eleType
            else:
                eleType = ArrayType(param.size[1:], param.eleType)
            for expr in ast.value:
                expr.accept(self, eleType)

        if type(eleType) is ArrayType:
            arrType = ArrayType(eleType=eleType.eleType, size=[float(len(ast.value))] + eleType.size)
        else:
            arrType = ArrayType(eleType=eleType, size=[float(len(ast.value))])

        return arrType

    def visitId(self, ast: Id, typeConstr):
        var = next(filter(lambda var: var[0] == ast.name and (var[2] in range(0, self.scopeLevel + 1)), reversed(self.vars)), None)
        assert var is not None
        if var[1] is None:
            var[1] = typeConstr
        return var[1]

    def visitCallExpr(self, ast: CallExpr, param):
        funcType = self.funcType[ast.name.name]
        paramTypes, returnType = funcType.partype, funcType.rettype
        for arg, paramType in zip(ast.args, paramTypes):
            arg.accept(self, paramType)
        if returnType is None:
            funcType.rettype = param
        return funcType.rettype

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
    """The job of this visitor is to emit bytecodes to the buffer.

    Anytime the visitor visits a statement or declaration, it will return 'vmState', which is an
    instance of Access class (Remind that the Access class is used to represent the virtual machine
    state in this context).

    Anytime the visitor visits an expression, it will return generated code, which is a string, and
    the expression's return type, which is an instance of Type.

    The visitor only emits code when it visits a statement or a declaration.
    """
    def __init__(self, astTree, path, typeArr, fnTypes, className):
        self.astTree = astTree
        self.path = path
        self.typeArr = typeArr
        self.typeIter = iter(self.typeArr)
        self.fnTypes = fnTypes
        self.globalFrame = Frame("<clinit>", VoidType())
        self.globalVarGen = []
        self.className = className
        self.emitter = Emitter(self.path + f"/{self.className}.j")
        self.fnTypes["main"] = MType([ArrayType([1], StringType())], VoidType())

    def getVarTypePair(self):
        return next(self.typeIter, None)

    def resolveFnType(self, fname):
        pass

    def convertName(self, name: str):
        if name in ["readNumber", "writeNumber", "readBool", "writeBool", "readString", "writeString"]:
            return "io/" + name
        return self.className + "/" + name

    def gen(self):
        vmState = Access(self.globalFrame, [], False)
        self.astTree.accept(self, vmState)
        self.emitter.emitPROGRAM(self.className, "")

    def visitProgram(self, ast, vmState: Access):
        for decl in ast.decl:
            vmState = decl.accept(self, vmState)
        self.genClinitMethod()

    def genInitMethod(self):
        initFrame = Frame("<init>", VoidType())
        self.emitter.printout(self.emitter.emitMETHOD("<init>()", VoidType(), False, initFrame))
        self.emitter.printout(self.emitter.emitLIMITSTACK(1))
        self.emitter.printout(self.emitter.emitLIMITLOCAL(1))
        initFrame.push()
        self.emitter.printout(self.emitter.emitALOAD(StringType(), initFrame))
        self.emitter.printout(self.emitter.emitRETURN(VoidType(), initFrame))
        self.emitter.printout(self.emitter.jvm.emitENDMETHOD())

    def genClinitMethod(self):
        """generate code for global variable initialization.
        All of the code is inside <clinit> function.
        The associated frame to <clinit> is self.globalFrame.
        The generated code for declaration expressions is in self.globalVarGen. 
        This method should be invoked after all of the declarations are visited.
        """
        self.emitter.printout(self.emitter.emitMETHOD(self.globalFrame.name + "()", self.globalFrame.returnType, True, self.globalFrame))
        self.emitter.printout(''.join(self.globalVarGen))
        self.emitter.printout(self.emitter.emitRETURN(self.globalFrame.returnType, self.globalFrame))
        self.emitter.printout(self.emitter.emitENDMETHOD(self.globalFrame))

    def visitFuncDecl(self, ast: FuncDecl, vmState: Access):
        if ast.body is None: return
        fname = ast.name.name
        fnType = self.fnTypes[fname]
        # new Access object to avoid side effect.
        fnVmState = Access(Frame(fname, fnType.rettype), vmState.sym, False)

        self.emitter.printout(self.emitter.emitMETHOD(fname, fnType, True, fnVmState.frame))
        fnVmState.frame.enterScope(True)
        startLabel, endLabel = fnVmState.frame.getStartLabel(), fnVmState.frame.getEndLabel()
        self.emitter.printout(self.emitter.emitLABEL(startLabel, fnVmState.frame))
        if fname == "main":
            # slot for string argument
            fnVmState.frame.getNewIndex()
        for paramDecl in ast.param:
             fnVmState = paramDecl.accept(self, fnVmState)
        # generate code for function's body.
        fnVmState = ast.body.accept(self, fnVmState)
        if type(fnType.rettype) is VoidType:
            self.emitter.printout(self.emitter.emitRETURN(VoidType(), fnVmState.frame))
        self.emitter.printout(self.emitter.emitLABEL(endLabel, fnVmState.frame))
        self.emitter.printout(self.emitter.emitENDMETHOD(fnVmState.frame))
        fnVmState.frame.exitScope()
        return vmState

    def visitBlock(self, ast: Block, vmState: Access):
        currentSymLen = len(vmState.sym)
        vmState.frame.enterScope(False)
        startLabel, endLabel = vmState.frame.getStartLabel(), vmState.frame.getEndLabel()
        self.emitter.printout(self.emitter.emitLABEL(startLabel, vmState.frame))
        for stmt in ast.stmt:
            vmState = stmt.accept(self, vmState)
        vmState.frame.exitScope()
        self.emitter.printout(self.emitter.emitLABEL(endLabel, vmState.frame))
        vmState.sym = vmState.sym[:currentSymLen]
        return vmState

    def visitAssign(self, ast: Assign, vmState: Access):
        rightGen, rightType = ast.rhs.accept(self, Access(vmState.frame, vmState.sym, False).withRequireBoolResult())
        leftGen, leftType = ast.lhs.accept(self, Access(vmState.frame, vmState.sym, True))
        self.emitter.printout(rightGen)
        self.emitter.printout(leftGen)
        return vmState

    def visitCallStmt(self, ast: CallStmt, vmState: Access):
        code = []
        code += [expr.accept(self, vmState)[0] for expr in ast.args]
        fname = ast.name.name
        fnType = self.fnTypes[fname]
        code.append(self.emitter.emitINVOKESTATIC(self.convertName(fname), fnType, vmState.frame))
        self.emitter.printout(''.join(code))
        return vmState

    def visitIf(self, ast: If, vmState: Access):
        ifParts = [(ast.expr, ast.thenStmt)] + ast.elifStmt

        for expr, stmt in ifParts:
            ifTrueLabelId, ifFalseLabelId = vmState.frame.getNewLabel(), vmState.frame.getNewLabel()
            _vmState = vmState.withIfLabel(ifTrueLabelId, ifFalseLabelId)
            exprGen, _ = expr.accept(self, _vmState)
            self.emitter.printout(exprGen)
            self.emitter.printout(self.emitter.emitIFFALSE(ifFalseLabelId, vmState.frame))
            self.emitter.printout(self.emitter.emitLABEL(ifTrueLabelId, vmState.frame))
            stmt.accept(self, vmState)
            self.emitter.printout(self.emitter.emitLABEL(ifFalseLabelId, vmState.frame))

        if ast.elseStmt is not None:
            ast.elseStmt.accept(self, vmState)

        return vmState

    def visitFor(self, ast: For, vmState: Access):
        pass

    def visitBreak(self, ast: Break, vmState: Access):
        pass

    def visitContinue(self, ast: Continue, vmState: Access):
        pass

    def visitReturn(self, ast: Return, vmState: Access):
        if ast.expr is None:
            self.emitter.printout(self.emitter.emitRETURN(VoidType(), vmState.frame))
        else:
            exprGen, exprType = ast.expr.accept(self, vmState)
            self.emitter.printout(exprGen)
            self.emitter.printout(self.emitter.emitRETURN(exprType, vmState.frame))
        return vmState

    def visitVarDecl(self, ast: VarDecl, vmState: Access):
        """Emit codes for variable declaration.

        Returns:
            vmState (Access): represents the state of the virtual machine after a variable is
            declared.
        """
        iden = ast.name

        # a tuple: (variable name, variable type)
        varTypePair = self.getVarTypePair()
        assert varTypePair is not None and varTypePair[0] == iden.name
        varName, varType = varTypePair

        # generate directive and create symbol
        if vmState.frame.name == "<clinit>":
            # global variable
            directive = self.emitter.emitATTRIBUTE(iden.name, varType, False, None)
            varSym = Symbol(name=varName, mtype=varType, value=CName(self.className))
            self.emitter.printoutGlobalDirective(directive)
        else:
            # local variable
            startLabel = vmState.frame.getStartLabel()
            endLabel = vmState.frame.getEndLabel()
            newSlot = vmState.frame.getNewIndex()
            directive = self.emitter.emitVAR(newSlot, varName, varType, startLabel, endLabel, vmState.frame)
            varSym = Symbol(name=varName, mtype=varType, value=Index(newSlot))
            self.emitter.printout(directive)

        if ast.varInit is not None:
            # generate code for variable initialization
            exprCode, exprType = ast.varInit.accept(self, vmState.withRequireBoolResult())
            assert type(varType) is type(exprType)
            if vmState.frame.name == "<clinit>":
                # global variable
                writeVarGen = self.emitter.emitPUTSTATIC(self.convertName(varName), varType, vmState.frame)
                self.globalVarGen.append(exprCode + writeVarGen)
            else:
                # local variable
                writeVarGen = self.emitter.emitWRITEVAR(varName, varType, varSym.value.value, vmState.frame)
                self.emitter.printout(exprCode + writeVarGen)
    
        vmState.sym.append(varSym)
        return vmState

    def visitBinaryOp(self, ast: BinaryOp, vmState: Access):
        if ast.op not in ['and', 'or']:
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
            else:
                opGen = None

            return (leftOperandGen + rightOperandGen + opGen), getResultType(ast.op)
        elif ast.op in ['and', 'or'] and not vmState.requireBoolResult:
            # if the expression's result is not required, e.g, conditional expressions,
            # then just check the result of the operands and perform the jump.
            trueLabel, falseLabel = vmState.ifTrueLabel, vmState.ifFalseLabel

            # create new Access object, with some additional metadata
            # the result of each operand are required.
            _vmState = vmState.withRequireBoolResult().withLogicalLabel(ast.op, trueLabel, falseLabel)

            leftGen, leftType = ast.left.accept(self, _vmState)
            rightGen, rightType = ast.right.accept(self, _vmState)


            if ast.op == 'and':
                jmpIfFalse = self.emitter.emitIFFALSE(falseLabel, vmState.frame)
                codegen = [leftGen, jmpIfFalse, rightGen]
            else:
                jmpIfTrue = self.emitter.emitIFTRUE(trueLabel, vmState.frame)
                codegen = [leftGen, jmpIfTrue, rightGen]
            return ''.join(codegen), BoolType()
        elif ast.op == 'and' or ast.op == 'or':
            # TODO: Implement code generation in the case that the result is required
            loadBoolLabelId, exitLabelId = None, None

            if ast.op == 'and':
                if not (vmState.andLoadBoolLabel and vmState.andExitLabel):
                    loadBoolLabelId, exitLabelId = vmState.frame.getNewLabel(), vmState.frame.getNewLabel()
                else:
                    loadBoolLabelId, exitLabelId = vmState.andLoadBoolLabel, vmState.andExitLabel
            else:
                if not (vmState.orLoadBoolLabel or vmState.orExitLabel):
                    loadBoolLabelId, exitLabelId = vmState.frame.getNewLabel(), vmState.frame.getNewLabel()
                else:
                    loadBoolLabelId, exitLabelId = vmState.orLoadBoolLabel, vmState.orExitLabel

            # create new Access object, with some additional metadata
            # the result of each operand are required.
            _vmState = vmState.withLogicalLabel(ast.op, loadBoolLabelId, exitLabelId).withRequireBoolResult()

            # generate code for operands
            # the result of lhs is always loaded onto the stack
            leftGen, leftType = ast.left.accept(self, _vmState)
            rightGen, rightType = ast.right.accept(self, _vmState)

            if ast.op == 'and':
                jmpToLoadBool = self.emitter.emitIFFALSE(loadBoolLabelId, vmState.frame)
            else:
                jmpToLoadBool = self.emitter.emitIFTRUE(loadBoolLabelId, vmState.frame)


            codegen = [leftGen, jmpToLoadBool, rightGen]

            if vmState.andLoadBoolLabel is None and vmState.andExitLabel is None and ast.op == 'and':
                jmpToExit = self.emitter.emitGOTO(exitLabelId, vmState.frame)
                loadBoolLabel = self.emitter.emitLABEL(loadBoolLabelId, vmState.frame)
                loadBoolGen = self.emitter.emitPUSHCONST("false", BoolType(), vmState.frame)
                exitLabel = self.emitter.emitLABEL(exitLabelId, vmState.frame)

                codegen += [jmpToExit, loadBoolLabel, loadBoolGen, exitLabel]
            elif vmState.orLoadBoolLabel is None and vmState.orLoadBoolLabel is None and ast.op == 'or':
                jmpToExit = self.emitter.emitGOTO(exitLabelId, vmState.frame)
                loadBoolLabel = self.emitter.emitLABEL(loadBoolLabelId, vmState.frame)
                loadBoolGen = self.emitter.emitPUSHCONST("true", BoolType(), vmState.frame)
                exitLabel = self.emitter.emitLABEL(exitLabelId, vmState.frame)

                codegen += [jmpToExit, loadBoolLabel, loadBoolGen, exitLabel]

            return ''.join(codegen), BoolType()

    def visitUnaryOp(self, ast: UnaryOp, vmState: Access):
        operandCode, operandType = ast.operand.accept(self, vmState)
        if ast.op == 'not':
            operatorCode = self.emitter.emitNOT(operandType, vmState.frame)
        else:
            # ast.op == '-', use ineg
            operatorCode = self.emitter.emitNEGOP(ast.op, vmState.frame)
        return operandCode + operatorCode, operandType

    def visitArrayCell(self, ast: ArrayCell, vmState: Access):
        code = []
        idxGens = [expr.accept(self, vmState)[0] + self.emitter.emitF2I(vmState) for expr in ast.idx]
        varGen, varType = ast.arr.accept(self, vmState)
        assert type(varType) is ArrayType

        code += varGen

        # generate code for loading array's item onto the stack
        for i, idxGen in enumerate(idxGens):
            eleType = varType if i < len(idxGens) else varType.eleType
            code.append(idxGen)
            code.append(self.emitter.emitALOAD(eleType, vmState.frame))

        return ''.join(code), varType.eleType
    
    def visitCallExpr(self, ast: CallExpr, vmState: Access):
        code = []
        code += [expr.accept(self, vmState)[0] for expr in ast.args]
        fname = ast.name.name
        fnType = self.fnTypes[fname]
        code.append(self.emitter.emitINVOKESTATIC(self.convertName(fname), fnType, vmState.frame))
        return ''.join(code), fnType.rettype

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

    def visitId(self, ast: Id, vmState: Access):
        sym = next(filter(lambda sym: sym.name == ast.name, reversed(vmState.sym)), None)
        assert sym is not None
        if vmState.isLeft:
            if type(sym.value) is Index:
                # store value into local variable
                gen = self.emitter.emitWRITEVAR(sym.name, sym.mtype, sym.value.value, vmState.frame)
            else:
                # store value into global variable
                gen = self.emitter.emitPUTSTATIC(self.convertName(sym.name), sym.mtype, vmState.frame)
        else:
            if type(sym.value) is Index:
                # read local variable
                gen = self.emitter.emitREADVAR(sym.name, sym.mtype, sym.value.value, vmState.frame)
            else:
                # read global variable a.k.a static field 
                gen = self.emitter.emitGETSTATIC(self.convertName(sym.name), sym.mtype, vmState.frame)
        return gen, sym.mtype

    def visitNumberLiteral(self, ast: NumberLiteral, vmState: Access):
        return self.emitter.emitPUSHCONST(str(ast.value), NumberType(), vmState.frame), NumberType()

    def visitBooleanLiteral(self, ast: BooleanLiteral, vmState: Access):
        return self.emitter.emitPUSHICONST(1 if ast.value else 0, vmState.frame), BoolType()

    def visitStringLiteral(self, ast: StringLiteral, vmState: Access):
        return self.emitter.emitPUSHCONST(ast.value, StringType(), vmState.frame), StringType()

class CodeGenerator:
    def __init__(self):
        self.libName = "io"

    def gen(self, ast, path):
        # ast: AST
        # dir_: String

        typeInference = TypeInferenceVisitor(ast)
        typeVarPairs, fnTypes = typeInference.infer()

        gc = CodeGenVisitor(ast, path, typeVarPairs, fnTypes, "ZCodeClass")
        gc.gen()
