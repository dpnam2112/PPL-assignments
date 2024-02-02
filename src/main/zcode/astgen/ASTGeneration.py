from ZCodeVisitor import ZCodeVisitor
from ZCodeParser import ZCodeParser
from ZCodeLexer import ZCodeLexer
from AST import *

class ASTGeneration(ZCodeVisitor):
    # Each visit method's return value belongs to only three types: AST, List of ASTs or None

    def visitProgram(self,ctx:ZCodeParser.ProgramContext):
        decls = []
        for decl in ctx.getChildren():
            declAst = decl.accept(self)
            decls.append(declAst) if declAst else None
        return Program(decl=decls)

    def visitStmt(self, ctx: ZCodeParser.StmtContext):
        return ctx.getChild(0).accept(self)

    def visitBlockStmt(self, ctx: ZCodeParser.BlockStmtContext):
        stmtListAst = ctx.stmtList() and ctx.stmtList().accept(self) or []
        return Block(stmt=stmtListAst)

    def visitReturnStmt(self, ctx: ZCodeParser.ReturnStmtContext):
        exprAst = ctx.expr() and ctx.expr().accept(self)
        return Return(expr=exprAst)

    def visitStmtList(self, ctx: ZCodeParser.StmtListContext):
            return [stmt.accept(self) for stmt in ctx.stmt()] if ctx.stmt() else []

    def visitFuncDecl(self, ctx: ZCodeParser.FuncDeclContext):
        iden = Id(name=ctx.ID().getText())
        paramListAst = ctx.paramListDecl() and ctx.paramListDecl().accept(self) or []
        body = ctx.blockStmt() or ctx.returnStmt()

        # function declaration may not have a body
        bodyAst = body and body.accept(self)
        return FuncDecl(name=iden, param=paramListAst, body=bodyAst)

    def visitParamListDecl(self, ctx: ZCodeParser.ParamListDeclContext):
        return [paramDecl.accept(self) for paramDecl in ctx.paramDecl()]

    def visitParamDecl(self, ctx: ZCodeParser.ParamDeclContext):
        iden = Id(name=ctx.ID().getText())
        # string, bool or number
        atomicType = ctx.getChild(0).accept(self)

        if ctx.arrayDim():
            arrSize = ctx.arrayDim().accept(self)
            paramType = ArrayType(eleType=atomicType, size=arrSize)
        else:
            paramType = atomicType
        return VarDecl(name=iden, varType=paramType)

    def visitVariableDecl(self, ctx: ZCodeParser.VariableDeclContext):
        iden = Id(name=ctx.ID().getText())
        exprAst = ctx.expr() and ctx.expr().accept(self)

        # atomicType is number, string, bool or None if the
        # declaration keyword is dynamic or var
        atomicType = ctx.getChild(0).accept(self)   
        declType = atomicType if not ctx.arrayDim() else ArrayType(size=ctx.arrayDim().accept(self), eleType=atomicType)
        return VarDecl(name=iden, varType=declType, varInit=exprAst)

    def visitArrayDim(self, ctx: ZCodeParser.ArrayDimContext):
        return [float(dimLit.getText()) for dimLit in ctx.NUM_LIT()]

    def visitLoopCtrlStmt(self, ctx: ZCodeParser.LoopCtrlStmtContext):
        return ctx.getChild(0).accept(self)

    def visitAssignmentStmt(self, ctx: ZCodeParser.AssignmentStmtContext):
        lhs = ctx.ID() or ctx.idIndex()
        expr = ctx.expr()
        return Assign(lhs=lhs.accept(self), exp=expr.accept(self))

    def visitExpr(self, ctx: ZCodeParser.ExprContext):
        leftOp = ctx.relationalExpr(0).accept(self)
        op = ctx.TRIP_DOT()
        if not op:
            return leftOp
        rightOp = ctx.relationalExpr(1).accept(self)
        return BinaryOp(op=op.getText(), left=leftOp, right=rightOp)

    def visitRelationalExpr(self, ctx: ZCodeParser.RelationalExprContext):
        leftOpAst = ctx.boolExpr(0).accept(self)
        op = ctx.LT() or ctx.GT() or ctx.LT_EQ() or ctx.GT_EQ() or ctx.EQ() or ctx.EQ_EQ()
        if not op:
            return leftOpAst
        rightOpAst = ctx.boolExpr(1).accept(self)
        return BinaryOp(op=op.getText(), left=leftOpAst, right=rightOpAst)

    def visitBoolExpr(self, ctx: ZCodeParser.BoolExprContext):
        rightOpAst = ctx.additionExpr().accept(self)
        op = ctx.AND() or ctx.OR()
        if not op:
            return rightOpAst
        leftOpAst = ctx.boolExpr().accept(self)
        return BinaryOp(op=op.getText(), left=leftOpAst, right=rightOpAst)

    def visitAdditionExpr(self, ctx: ZCodeParser.AdditionExprContext):
        rightOpAst = ctx.termExpr().accept(self)
        op = ctx.PLUS() or ctx.MINUS()
        if not op:
            return rightOpAst
        leftOpAst = ctx.additionExpr().accept(self)
        return BinaryOp(op=op.getText(), left=leftOpAst, right=rightOpAst)

    def visitTermExpr(self, ctx: ZCodeParser.TermExprContext):
        rightOpAst = ctx.negationExpr().accept(self)
        op = ctx.STAR() or ctx.SLASH() or ctx.PERCENT()
        if not op:
            return rightOpAst
        leftOpAst = ctx.termExpr().accept(self)
        return BinaryOp(op=op.getText(), left=leftOpAst, right=rightOpAst)

    def visitNegationExpr(self, ctx: ZCodeParser.NegationExprContext):
        if ctx.signExpr():
            return ctx.signExpr().accept(self)

        operandAst = ctx.negationExpr().accept(self)
        return UnaryOp(op=ctx.NOT().getText(), operand=operandAst)

    def visitSignExpr(self, ctx: ZCodeParser.SignExprContext):
        opAst  = ctx.indexExpr().accept(self)
        if not ctx.MINUS():
            return opAst
        return UnaryOp(op=ctx.MINUS().getText(), operand=opAst)

    def visitIndexExpr(self, ctx: ZCodeParser.IndexExprContext):
        if ctx.primary():
            return ctx.primary().accept(self)
        arrExprAST = (ctx.ID() or ctx.functionCall()).accept(self)
        indexAST = ctx.index().accept(self)
        return ArrayCell(arr=arrExprAST, idx=indexAST)
        

    def visitIndex(self, ctx: ZCodeParser.IndexContext):
        return ctx.exprList().accept(self)

    def visitIdIndex(self, ctx: ZCodeParser.IdIndexContext):
        iden = Id(name=ctx.ID().getText())
        indexExprList = ctx.index().accept(self)
        return ArrayCell(arr=iden, idx=indexExprList)

    def visitPrimary(self, ctx: ZCodeParser.PrimaryContext):
        childExpr = ctx.array() or ctx.functionCall() or ctx.expr() or ctx.getChild(0)
        return childExpr.accept(self)

    def visitTerminal(self, node):
        symtype = node.getSymbol().type
        match symtype:
            case ZCodeLexer.STR_LIT:
                return StringLiteral(value=node.getText())
            case ZCodeLexer.NUM_LIT:
                return NumberLiteral(value=float(node.getText()))
            case ZCodeLexer.TRUE:
                return BooleanLiteral(value=True)
            case ZCodeLexer.FALSE:
                return BooleanLiteral(value=False)
            case ZCodeLexer.ID:
                return Id(name=node.getText())
            case ZCodeLexer.BREAK:
                return Break()
            case ZCodeLexer.CONTINUE:
                return Continue()
            case ZCodeLexer.NUMBER:
                return NumberType()
            case ZCodeLexer.BOOL:
                return BoolType()
            case ZCodeLexer.STRING:
                return StringType()
        return None

    def visitExprList(self, ctx: ZCodeParser.ExprListContext):
        exprAsts = []
        for expr in ctx.getChildren():
            exprAst = expr.accept(self)
            exprAsts.append(exprAst) if exprAst else None
        return exprAsts


    def visitArray(self, ctx: ZCodeParser.ArrayContext):
        exprList = [] if not ctx.exprList() else ctx.exprList().accept(self)
        return ArrayLiteral(value=exprList)

    def visitCallStmt(self, ctx: ZCodeParser.CallStmtContext):
        callAst = ctx.functionCall().accept(self)
        return CallStmt(name=callAst.name, args=callAst.args)

    def visitFunctionCall(self, ctx: ZCodeParser.FunctionCallContext):
        iden = Id(name=ctx.ID().getText())
        exprListAst = ctx.exprList().accept(self) if ctx.exprList() else []
        return CallExpr(name=iden, args=exprListAst)

    def visitNlList(self, ctx: ZCodeParser.NlListContext):
        return None

    def visitForStmt(self, ctx: ZCodeParser.ForStmtContext):
        iden = Id(name=ctx.ID().getText())
        condExprAst = ctx.expr(0).accept(self)
        updateExprAst = ctx.expr(1).accept(self)
        bodyAst = ctx.stmt().accept(self)
        return For(name=iden, condExpr=condExprAst, updpExpr=updateExprAst, body=bodyAst)

    def visitIfStmt(self, ctx: ZCodeParser.IfStmtContext):
        condAst = ctx.expr().accept(self)
        stmtAst = ctx.stmt().accept(self)
        elifList, elseStmt = ctx.elsePart().accept(self) if ctx.elsePart() else ([], None)
        return If(expr=condAst, thenStmt=stmtAst, elifStmt=elifList, elseStmt=elseStmt)

    def visitElsePart(self, ctx: ZCodeParser.ElsePartContext):
        # if there are one or more elif statements, return a list of pair (condition, body) that represents
        # the elif statements and a statement corresponding to the 'else' body.
        if not ctx.ELIF():
            return [], ctx.stmt() and ctx.stmt().accept(self)

        elifExpr = ctx.expr().accept(self)
        elifBody = ctx.stmt().accept(self)
        remainingElif, elsePart = ctx.elsePart().accept(self) if ctx.elsePart() else ([], None)
        return [(elifExpr, elifBody)] + remainingElif, elsePart
