from types import FunctionType
import unittest
from TestUtils import TestChecker
from constraints import *
from AST import *

def collect_constraint(ast):
    type_env = TypeEnvironment()
    collector = ConstraintCollector(prog=Program(decl=[]), type_env=type_env)
    ast.accept(collector, None)

def resolve_constraint(ast):
    type_env = TypeEnvironment()
    collector = ConstraintCollector(prog=Program(decl=[]), type_env=type_env)
    ast.accept(collector, None)
    constraints = collector.getConstraints()
    resolver = ConstraintResolver(type_env, constraints)
    resolver.resolve()

class TestTypeInference(unittest.TestCase):
        
    def _test_type_inference_simple_expr(self):
        stmts = [
            VarDecl(name=Id('x'), varType=NumberType(), varInit=NumberLiteral(1))
        ]

        block = Block(stmts)

        resolve_constraint(block)

        self.assertEqual(
                isinstance(getExpressionType(stmts[0].name), NumberType),
                True)

        self.assertEqual(
                isinstance(getExpressionType(stmts[0].varInit), NumberType),
                True
                )

    def _test_simple_decl_with_dynamic(self):
        stmts = [
            VarDecl(name=Id("x"), modifier="dynamic"),
            VarDecl(name=Id("y"), modifier="dynamic", varInit=Id("x")),
            VarDecl(name=Id("z"), varType=NumberType(), varInit=Id("y"))
        ]

        block = Block(stmts)
        resolve_constraint(block)

        self.assertEqual(isinstance(getExpressionType(stmts[0].name), NumberType), True)
        self.assertEqual(isinstance(getExpressionType(stmts[1].name), NumberType), True)
        self.assertEqual(isinstance(getExpressionType(stmts[2].name), NumberType), True)

    def _test_simple_one_dim_array(self):
        id_x = Id(name="x") # $0
        id_y = Id(name="y") # $1

        stmts = [
            VarDecl(name=id_x, modifier="dynamic"),
            VarDecl(name=id_y, modifier="dynamic"),
            VarDecl(name=Id("arr"),
                    varType=ArrayType(eleType=NumberType(), size=[3]),
                    varInit=ArrayLiteral(
                            value=[
                                id_x, id_y
                            ]
                        ))
        ]

        block = Block(stmts)

        resolve_constraint(block)

        self.assertEqual(isinstance(getExpressionType(id_x), NumberType), True)
        self.assertEqual(isinstance(getExpressionType(id_y), NumberType), True)

    def _test_simple_multi_dim_array(self):
        id_x = Id(name="x") # $0
        id_y = Id(name="y") # $1

        stmts = [
            VarDecl(name=id_x, modifier="dynamic"),
            VarDecl(name=id_y, modifier="dynamic"),
            VarDecl(name=Id("arr"),
                    varType=ArrayType(eleType=NumberType(), size=[2,3]),
                    varInit=ArrayLiteral(
                            value=[
                                ArrayLiteral(
                                    value=[id_x, id_y]
                                )
                            ]
                        ))
        ]

        block = Block(stmts)

        resolve_constraint(block)

        self.assertEqual(isinstance(getExpressionType(id_x), NumberType), True)
        self.assertEqual(isinstance(getExpressionType(id_y), NumberType), True)

    def _test_function_type_inference(self):
        id_x = Id(name="x")
        id_y = Id(name="y")
        stmts = [
            FuncDecl(name=id_x, param=[]),
            VarDecl(name=id_y, modifier="dynamic",
                        varInit=BinaryOp(
                                left=NumberLiteral(1),
                                right=CallExpr(
                                        name=Id("x"),
                                        args=[]
                                    ),
                                op='+'
                            ))
        ]

        resolve_constraint(Block(stmts))

        fn_type = getExpressionType(id_x)
        print(fn_type.returnType)
        print(fn_type.returnType.getType())
        
        self.assertEqual(isinstance(fn_type, FnType), True)
        self.assertEqual(isinstance(fn_type.returnType.getType(), NumberType), True)

    def test_param_type_inference(self):
        id_x = Id(name="x")
        id_y = Id(name="y")

        stmts = [
            VarDecl(name=id_x, modifier='dynamic'),
            VarDecl(name=id_y, modifier='dynamic'),
            FuncDecl(name=Id('f'), param=[
                    VarDecl(name=Id('x'), varType=NumberType()),
                    VarDecl(name=Id('y'), varType=StringType())
                ]),
            CallStmt(name=Id('f'), args=[Id('x'), Id('y')])
        ]

        resolve_constraint(Block(stmts))


        self.assertEqual(isinstance(getExpressionType(id_x), NumberType), True)
        self.assertEqual(isinstance(getExpressionType(id_y), StringType), True)

    
class CheckerSuite(unittest.TestCase):
    pass
