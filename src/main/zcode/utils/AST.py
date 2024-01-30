from abc import ABC, abstractmethod, ABCMeta
#from Visitor import Visitor
from dataclasses import dataclass
from typing import List, Tuple


class AST(ABC):
    def __eq__(self, other): 
        return self.__dict__ == other.__dict__

    def accept(self, v, param):
        method_name = 'visit{}'.format(self.__class__.__name__)
        visit = getattr(v, method_name)
        return visit(self,param)

class Stmt(AST):
    __metaclass__ = ABCMeta
    pass

class Expr(AST):
    __metaclass__ = ABCMeta
    pass

class LHS(Expr):
    __metaclass__ = ABCMeta
    pass

class Type(AST):
    __metaclass__ = ABCMeta
    pass

class Decl(AST):
    __metaclass__ = ABCMeta
    pass

@dataclass
class Id(LHS):
    name:str
    def __str__(self):
        return "Id(" + self.name + ")"
        

# used for binary expression
@dataclass
class BinaryOp(Expr):
    op:str
    left:Expr
    right:Expr
    def __str__(self):
        return "BinaryOp(" + self.op + "," + str(self.left) + "," + str(self.right) + ")"

#used for unary expression with orerand like !,+,-
@dataclass
class UnaryOp(Expr):
    op:str
    operand:Expr
    def __str__(self):
        return "UnaryOp(" + self.op + "," + str(self.operand) + ")"

@dataclass
class CallExpr(Expr):
    name:Id
    args:List[Expr]
    def __str__(self):
        return "CallExpr(" + str(self.name) + ",[" +  ','.join(str(i) for i in self.args) + "])"


@dataclass
class ArrayCell(LHS):
    arr:Expr
    idx:List[Expr]
    def __str__(self):
        return "ArrayCell(" + str(self.arr) + ",[" + ','.join(str(i) for i in self.idx) + "])"

class Literal(Expr):
    __metaclass__ = ABCMeta
    pass

@dataclass
class NumberLiteral(Literal):
    value:float
    def __str__(self):
        return "NumLit(" + str(self.value) + ")"

@dataclass
class StringLiteral(Literal):
    value:str
    def __str__(self):
        return "StringLit(" + self.value + ")"

@dataclass
class BooleanLiteral(Literal):
    value:bool
    def __str__(self):
        return "BooleanLit(" + str(self.value) + ")"

@dataclass
class ArrayLiteral(Literal):
    value: List[Expr]
    def __str__(self):
        return '[' + ','.join(str(i) for i in self.value)+ ']'

@dataclass
class Assign(Stmt):
    lhs:Expr
    exp:Expr
    def __str__(self):
        return "AssignStmt(" + str(self.lhs) + "," +  str(self.exp) + ")"

@dataclass
class If(Stmt):
    expr:Expr
    thenStmt:Stmt
    elifStmt:List[Tuple[Expr,Stmt]] # empty list if there is no elif statement
    elseStmt:Stmt = None # None if there is no else branch
    def __str__(self):
        return "If("+str(self.expr)+","+str(self.thenStmt)+("," if len(self.elifStmt) > 0 else "") + ','.join((str(i[0])+","+str(i[1])) for i in self.elifStmt)+(("," +  str(self.elseStmt)) if self.elseStmt else "")  + ")"

@dataclass
class For(Stmt):
    name:Id
    condExpr:Expr
    updpExpr:Expr
    body:Stmt  
    def __str__(self):
        return "For(" + str(self.name) + "," + str(self.condExpr) + "," + str(self.updpExpr) + ',' + str(self.body)  + "])"

class Break(Stmt):
    def __str__(self):
        return "Break"

class Continue(Stmt):
    def __str__(self):
        return "Continue"

@dataclass
class Return(Stmt):
    expr:Expr = None # None if there is no expression after return
    def __str__(self):
        return "Return(" + (str(self.expr)  if  self.expr else "") + ")"

@dataclass
class CallStmt(Stmt):
    name:Id
    args:List[Expr]  # empty list if there is no argument
    def __str__(self):
        return "Call(" + str(self.name) + ",[" +  ','.join(str(i) for i in self.args) + "])"

@dataclass
class Block(Stmt):
    stmt:List[Stmt] # empty list if there is no statement in block
    def __str__(self):
        return "Block([" + ','.join(str(i) for i in self.stmt) + "])"

# used for variable or parameter declaration 
@dataclass
class VarDecl(Decl,Stmt):
    name : Id
    varType : Type = None # None if there is no type
    modifier: str = None # None if there is no modifier
    varInit : Expr = None # None if there is no initial
    def __str__(self):
        return "VarDecl(" + (self.modifier+"," if self.modifier else "")+ (str(self.varType)+"," if self.varType else "") + str(self.name) + (","+ str(self.varInit) if self.varInit else "") + ")"
    
# used for a function declaration. 
@dataclass
class FuncDecl(Decl):
    name: Id
    param: List[VarDecl] # empty list if there is no parameter
    body: Stmt = None # None if this is just a declaration-part
    def __str__(self):
        return "FuncDecl(" + str(self.name) +  ",[" +  ','.join(str(i) for i in self.param) + "]"+ (", "+ str(self.body) if self.body else "") + ")"

class NumberType(Type):
    def __str__(self):
        return "NumberType"

class BoolType(Type):
    def __str__(self):
        return "BoolType"

class StringType(Type):
    def __str__(self):
        return "StringType"

@dataclass
class ArrayType(Type):
    size : List[int]
    eleType:Type
    def __str__(self):
        return "ArrayType([" + ','.join(str(i) for i in self.size) +  "]," + str(self.eleType) + ")"

# used for whole program
@dataclass
class Program(AST):
    decl : List[Decl]
    def __str__(self):
        return "Program([" + ','.join(str(i) for i in self.decl) + "])"
