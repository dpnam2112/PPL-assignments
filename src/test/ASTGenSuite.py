import unittest
from TestUtils import TestAST
from AST import *

class ASTGenSuite(unittest.TestCase):
    def test_simple_program(self):
        input = """number a
        """
        expect = str(Program([VarDecl(Id("a"),NumberType())]))
        self.assertTrue(TestAST.test(input,expect,300))

    def expressions_and_asts(self):
        expr_1 = "1e2 + 1"
        ast_1 = BinaryOp(op="+",
                        left=NumberLiteral(float("1e2")),
                        right=NumberLiteral(float("1")))

        expr_2 = "1e2 - 1.2"
        ast_2 = BinaryOp(op="-",
                         left=NumberLiteral(float("1e2")),
                         right=NumberLiteral(float("1.2")))

        expr_3 = "-123.e23"
        ast_3 = UnaryOp(op="-",
                        operand=NumberLiteral(float("123.e23")))

        expr_4 = "-123.e23 * 2.1"
        ast_4 = BinaryOp(
                    op="*",
                    left=UnaryOp(
                        op="-",
                        operand=NumberLiteral(float("123.e23"))),
                    right=NumberLiteral(float("2.1")))

        expr_5 = "-1.3e2 / -2.3 % 3"
        ast_5 = BinaryOp(
                    op="%",
                    left=BinaryOp(op="/",
                                  left=UnaryOp(
                                      op="-",
                                      operand=NumberLiteral(float("1.3e2"))),
                                  right=UnaryOp(
                                      op="-",
                                      operand=NumberLiteral(float("2.3")))),
                    right=NumberLiteral(float("3")))

        return [
            (expr_1, ast_1),
            (expr_2, ast_2),
            (expr_3, ast_3),
            (expr_4, ast_4),
            (expr_5, ast_5),
        ]

    def tc_name_getter(self, prefix: str):
        i = 0
        def _tc_name_getter():
            nonlocal i
            i += 1
            return prefix + f"_{i}"
        return _tc_name_getter

    def test_variable_declaration(self):
        tc_name_getter = self.tc_name_getter("decl_with_var")

        decl_with_var = """
        var x <- 1
        dynamic y <- 1 + 2.3 * 3E5
        number x <- f(1, 2)
        bool x <- true and false or f(1, 2)
        number x <- (1 + 2.3 * 3E5) - 1 + f(1, 2)
        """

        f"""
        {123}
        """
        
        exprAst1 = NumberLiteral(value=float(1))
        exprAst2 = BinaryOp(op='+', 
                            left=NumberLiteral(float(1)), 
                            right=BinaryOp(op='*',
                                           left=NumberLiteral(2.3),
                                           right=NumberLiteral(3E5)))

        exprAst3 = CallExpr(name=Id("f"),
                            args=[NumberLiteral(value=float(1)), NumberLiteral(value=float(2))])

        exprAst4 = BinaryOp(op='or',
                            left=BinaryOp(op="and",
                                          left=BooleanLiteral(True),
                                          right=BooleanLiteral(False)),
                            right=exprAst3)

        exprAst5 = BinaryOp(op='+',
                            left=BinaryOp(op='-',
                                          left=exprAst2,
                                          right=NumberLiteral(float(1))),
                            right=exprAst3)

        expected_decl_asts: List[Decl] =  [
                VarDecl(name=Id("x"), varInit=exprAst1),
                VarDecl(name=Id("y"), varInit=exprAst2),
                VarDecl(name=Id("x"), varInit=exprAst3, varType=NumberType()),
                VarDecl(name=Id("x"), varInit=exprAst4, varType=BoolType()),
                VarDecl(name=Id("x"), varInit=exprAst5, varType=NumberType())
        ]

        prog_ast = Program(decl=expected_decl_asts)

        self.assertTrue(TestAST.test(decl_with_var, str(prog_ast), tc_name_getter()))

        decl_with_var_2 = """
        number x[10] <- [(1 + 2.3 * 3E5) - 1 + f(1, 2), 1 + 2.3 * 3e5, f(1, 2), f(1, 2)]
        bool x[2] <- [true and false or f(1, 2), true and false or f(1, 2)]
        """

        expected_decl_asts_2: List[Decl] = [

        ]
