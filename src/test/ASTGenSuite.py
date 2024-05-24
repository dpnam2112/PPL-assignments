import unittest
from TestUtils import TestAST
from AST import *

class ASTGenSuite(unittest.TestCase):
    def test_simple_program(self):
        input = """number a
        """
        expect = str(Program([VarDecl(Id("a"), NumberType(), None, None)]))
        self.assertTrue(TestAST.test(input,expect,300))

    def create_program(self, stmts: list[tuple] = []):
        stmt_list, ast_list = zip(*stmts) if stmts else ([], [])

        prog = "func main()\nbegin\n"
        for stmt in stmt_list:
            prog += f"{stmt}"
        prog += "end\n\n"

        main_ast = FuncDecl(name=Id("main"), param=[], body=Block(stmt=ast_list))
        prog_ast = Program(decl=[main_ast])
        return (prog, prog_ast)

    def create_call_stmt(self, name, args: list[tuple]):
        expr_list, expr_ast_list = zip(*args) if args else ([], [])

        call_stmt = f"{name}(" + ','.join(expr_list) + ")\n\n"
        call_ast = CallStmt(name=Id(name), args=expr_ast_list)
        return (call_stmt, call_ast)

    def create_block_stmt(self, stmts: list[tuple]):
        stmt_list, ast_list = zip(*stmts) if stmts else ([], [])
        block_stmt = "begin\n" + "\n".join(stmt_list) + "\nend\n\n"
        block_ast = Block(stmt=ast_list)
        return (block_stmt, block_ast)

    def create_return_stmt(self, expr='', expr_ast=None):
        return_stmt = "return " + expr + "\n\n"
        return_ast = Return()
        if expr_ast:
            return_ast.expr = expr_ast
        return (return_stmt, return_ast)

    def create_if_stmt(self, conditions: list[tuple], cond_body: list[tuple], else_body=None):
        if_cond, if_body = conditions[0], cond_body[0]
        stmt = f"if ({if_cond[0]})\n{if_body[0]}"
        stmt_ast = If(expr=if_cond[1], thenStmt=if_body[1], elifStmt=[])

        for cond, body in zip(conditions[1:], cond_body[1:]):
            stmt += f"elif ({cond[0]})\n\t{body[0]}"
            stmt_ast.elifStmt.append((cond[1], body[1]))

        if else_body:
            stmt += f"else\n\t{else_body[0]}"
            stmt_ast.elseStmt = else_body[1]

        return (stmt, stmt_ast)

    def create_assignment_stmt(self, lhs: tuple, expr: tuple):
        lhs_text, lhs_ast = lhs
        expr_text, expr_ast = expr

        assignment_expr = f"{lhs_text} <- {expr_text}\n"
        assignment_ast = Assign(lhs=lhs_ast, rhs=expr_ast)

        return (assignment_expr, assignment_ast)

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

        expr_6 = f"{expr_3} + ({expr_4} - {expr_5})"
        ast_6 = BinaryOp(
                    op="+",
                    left=ast_3,
                    right=BinaryOp(
                            op="-",
                            left=ast_4,
                            right=ast_5
                        )
                )

        expr_7 = """ "abc"..."def" """
        ast_7 = BinaryOp(
                    op="...",
                    left=StringLiteral(value="abc"),
                    right=StringLiteral(value="def")
                    )

        expr_8 = f"[{expr_1}, {expr_2}, {expr_3}, {expr_4}]"
        ast_8 = ArrayLiteral(
                    value=[ast_1, ast_2, ast_3, ast_4]
                    )

        expr_9 = "not not false"
        ast_9 = UnaryOp(
                    op="not",
                    operand=UnaryOp(
                        op="not",
                        operand=BooleanLiteral(value=False)
                        ))

        expr_10 = f"true and ({expr_9})"
        ast_10 = BinaryOp(
                    op="and",
                    left=BooleanLiteral(True),
                    right=ast_9)

        expr_11 = f"{expr_9} or false"
        ast_11 = BinaryOp(
                    op="or",
                    left=ast_9,
                    right=BooleanLiteral(False))

        expr_12 = f"({expr_11}) or ({expr_11}) and ({expr_10})"
        ast_12 = BinaryOp(
                    op="and",
                    left=BinaryOp(
                        op="or",
                        left=ast_11,
                        right=ast_11),
                    right=ast_10)
    
        expr_13 = "a_variable and a_function()"
        ast_13 = BinaryOp(
                    op="and",
                    left=Id(name="a_variable"),
                    right=CallExpr(
                            name=Id("a_function"),
                            args=[])
                    )

        expr_14 = f"true and (({expr_13}) or false)"
        ast_14 = BinaryOp(
                    op="and",
                    left=BooleanLiteral(value=True),
                    right=BinaryOp(
                        op="or",
                        left=ast_13,
                        right=BooleanLiteral(value=False)
                        ))

        expr_15 = f"{expr_14} = {expr_13}"
        ast_15 = BinaryOp(
                    op="=",
                    left=ast_14,
                    right=ast_13
                    )

        expr_16 = f"{expr_1} < {expr_6}"
        ast_16 = BinaryOp(
                    op="<",
                    left=ast_1,
                    right=ast_6)

        expr_17 = f"{expr_1} > {expr_6}"
        ast_17 = BinaryOp(
                    op=">",
                    left=ast_1,
                    right=ast_6)

        expr_18 = f"{expr_14} == {expr_14}"
        ast_18 = BinaryOp(
                    op="==",
                    left=ast_14,
                    right=ast_14)

        expr_19 = f"{expr_18} ... {expr_18}"
        ast_19 = BinaryOp(
                    op="...",
                    left=ast_18,
                    right=ast_18)

        expr_20 = f"({expr_7}) == ({expr_7})"
        ast_20 = BinaryOp(
                    op="==",
                    left=ast_7,
                    right=ast_7)

        expr_21 = f"f({expr_7}, {expr_11}, {expr_17})"
        ast_21 = CallExpr(
                    name=Id(name="f"),
                    args=[ast_7, ast_11, ast_17])

        expr_22 = f"{expr_21}[{expr_7}, {expr_11}, {expr_17}]"
        ast_22 = ArrayCell(
                    arr=ast_21,
                    idx=[ast_7, ast_11, ast_17])

        expr_23 = f"arr[{expr_7}]"
        ast_23 = ArrayCell(
                    arr=Id(name="arr"),
                    idx=[ast_7])

        expr_24 = f"abc()"
        ast_24 = CallExpr(
                    name=Id(name="abc"),
                    args=[]
                )

        expr_25 = "true"
        ast_25 = BooleanLiteral(value=True)

        expr_26 = "false"
        ast_26 = BooleanLiteral(value=False)

        expr_27 = '"abc\\f\\n"'
        ast_27 = StringLiteral(value="abc\\f\\n")

        expr_28 = "23.281e-12"
        ast_28 = NumberLiteral(value=float("23.281e-12"))

        expr_29 = "true and true or false"
        ast_29 = BinaryOp(
                    op="or",
                    left=BinaryOp(
                            op="and",
                            left=BooleanLiteral(value=True),
                            right=BooleanLiteral(value=True)
                        ),
                    right=BooleanLiteral(value=False)
                )

        expr_30 = f"arr[{expr_6}, {expr_6}, {expr_6}, {expr_6}]"
        ast_30 = ArrayCell(
                    arr=Id(name="arr"),
                    idx=[ast_6, ast_6, ast_6, ast_6])

        expr_31 = f"{expr_1} != {expr_6}" 
        ast_31 = BinaryOp(
                    op="!=",
                    left=ast_1,
                    right=ast_6
                )

        expr_32 = f"{expr_1} <= {expr_6}"
        ast_32 = BinaryOp(
                    op="<=",
                    left=ast_1,
                    right=ast_6
                )

        expr_33 = f"{expr_1} >= {expr_6}"
        ast_33 = BinaryOp(
                    op=">=",
                    left=ast_1,
                    right=ast_6
                )



        return [
            (expr_1, ast_1),
            (expr_2, ast_2),
            (expr_3, ast_3),
            (expr_4, ast_4),
            (expr_5, ast_5),
            (expr_6, ast_6),
            (expr_7, ast_7),
            (expr_8, ast_8),
            (expr_9, ast_9),
            (expr_10, ast_10),
            (expr_11, ast_11),
            (expr_12, ast_12),
            (expr_13, ast_13),
            (expr_14, ast_14),
            (expr_15, ast_15),
            (expr_16, ast_16),
            (expr_17, ast_17),
            (expr_18, ast_18),
            (expr_19, ast_19),
            (expr_20, ast_20),
            (expr_21, ast_21),
            (expr_22, ast_22),
            (expr_23, ast_23),
            (expr_24, ast_24),
            (expr_25, ast_25),
            (expr_26, ast_26),
            (expr_27, ast_27),
            (expr_28, ast_28),
            (expr_29, ast_29),
            (expr_30, ast_30),
            (expr_31, ast_31),
            (expr_32, ast_32),
            (expr_33, ast_33)
        ]

    def tc_name_getter(self, prefix: str):
        i = 0
        def _tc_name_getter():
            nonlocal i
            i += 1
            return prefix + f"_{i}"
        return _tc_name_getter

    def test_variable_declaration(self):
        tc_name_getter = self.tc_name_getter("var_decl_ast")

        expr, ast = self.expressions_and_asts()[0]

        # Test declaration keyword
        var_decl = f"var x <- {expr}"
        var_decl_ast = VarDecl(
                            name=Id("x"),
                            modifier='var',
                            varInit=ast)


        number_decl = f"number a_num <- {expr}"
        number_decl_ast = VarDecl(
                            name=Id("a_num"),
                            varType=NumberType(),
                            varInit=ast)

        number_decl_no_init = f"number a_num"
        number_decl_no_init_ast = VarDecl(
                            name=Id("a_num"),
                            varType=NumberType())

        bool_decl = f"bool a_var <- {expr}"
        bool_decl_ast = VarDecl(
                        name=Id("a_var"),
                        varType=BoolType(),
                        varInit=ast)

        bool_decl_no_init = f"bool a_var"
        bool_decl_no_init_ast = VarDecl(
                        name=Id("a_var"),
                        varType=BoolType())

        string_decl = f"string a_str <- {expr}"
        string_decl_ast = VarDecl(
                        name=Id("a_str"),
                        varType=StringType(),
                        varInit=ast)

        string_decl_no_init = f"string a_str"
        string_decl_no_init_ast = VarDecl(
                        name=Id("a_str"),
                        varType=StringType())

        dynamic_decl = f"dynamic a_var <- {expr}"
        dynamic_decl_ast = VarDecl(
                        name=Id("a_var"),
                        modifier='dynamic',
                        varInit=ast)

        dynamic_decl_no_init = f"dynamic a_var"
        dynamic_decl_no_init_ast = VarDecl(
                        modifier='dynamic',
                        name=Id("a_var"))

        number_arr_decl = f"number x[1, 2, 3] <- {expr}"
        number_arr_decl_ast = VarDecl(
                            name=Id("x"),
                            varType=ArrayType(eleType=NumberType(), size=[1.0, 2.0, 3.0]),
                            varInit=ast)

        bool_arr_decl = f"bool x[4, 5, 6] <- {expr}"
        bool_arr_decl_ast = VarDecl(
                            name=Id("x"),
                            varType=ArrayType(eleType=BoolType(), size=[4.0, 5.0, 6.0]),
                            varInit=ast)

        string_arr_decl = f"string x[1, 2, 3] <- {expr}"
        string_arr_decl_ast = VarDecl(
                            name=Id("x"),
                            varType=ArrayType(eleType=StringType(), size=[1.0, 2.0, 3.0]),
                            varInit=ast)

        number_arr_decl_no_init = f"number x[1, 2, 3]"
        number_arr_decl_no_init_ast = VarDecl(
                    name=Id("x"),
                    varType=ArrayType(eleType=NumberType(), size=[1.0, 2.0, 3.0])
                )

        prog = f"""
        {var_decl}
        {number_decl}
        {number_decl_no_init}
        {bool_decl}
        {bool_decl_no_init}
        {string_decl}
        {string_decl_no_init}
        {dynamic_decl}
        {dynamic_decl_no_init}
        {number_arr_decl}
        {bool_arr_decl}
        {string_arr_decl}
        {number_arr_decl_no_init}
        """

        prog_ast = Program(
                decl=[var_decl_ast,
                      number_decl_ast,
                      number_decl_no_init_ast,
                      bool_decl_ast,
                      bool_decl_no_init_ast,
                      string_decl_ast,
                      string_decl_no_init_ast,
                      dynamic_decl_ast,
                      dynamic_decl_no_init_ast,
                      number_arr_decl_ast,
                      bool_arr_decl_ast,
                      string_arr_decl_ast,
                      number_arr_decl_no_init_ast
                      ])
        res = TestAST.test(prog, str(prog_ast), tc_name_getter())
        self.assertTrue(res)

    def test_expressions(self):
        tc_name_getter = self.tc_name_getter("test_expr_ast")
        expr_and_asts = self.expressions_and_asts()

        for expr, ast in expr_and_asts:
            decl_stmt = f"var x <- {expr}\n"
            decl_ast = VarDecl(name=Id("x"), varInit=ast, modifier="var")
            prog_ast = Program(decl=[decl_ast])
            tc_name = tc_name_getter()

            res = TestAST.test(decl_stmt, str(prog_ast), tc_name)

            if not res:
                print(f"failed testcase: {tc_name}")

            self.assertTrue(res)

    def create_function_declaration(self, name, param_decl: list[tuple], body=None):
        decl_ast = FuncDecl(name=Id(name), param=[])

        param_decl_txt, decl_ast.param = zip(*param_decl)
        decl_txt = f"func {name}(" + ','.join(param_decl_txt) + ")\n\n"

        if body:
            body_txt, body_ast = body
            decl_txt += body_txt
            decl_ast.body = body_ast

        return (decl_txt, decl_ast)

    def test_function_declaration(self):
        expr, ast = self.expressions_and_asts()[11]

        func_decl_with_no_body = "func main()\n"
        func_decl_with_no_body_ast = FuncDecl(name=Id("main"), param=[])
        self.assertTrue(TestAST.test(func_decl_with_no_body,
                        str(Program(decl=[func_decl_with_no_body_ast])),
                        "func_decl_with_no_body"))

        func_decl_with_a_return = f"func main() return {expr}\n"
        return_stmt_ast = Return(expr=ast)
        func_decl_with_a_return_ast = FuncDecl(name=Id("main"), param=[], body=return_stmt_ast)
        self.assertTrue(TestAST.test(func_decl_with_a_return,
                                     str(Program(decl=[func_decl_with_a_return_ast])),
                                             "func_decl_with_a_return"))

        empty_prog, empty_prog_ast = self.create_program()
        self.assertTrue(TestAST.test(empty_prog, str(empty_prog_ast), "func_decl_with_a_block"))

        # functions with parameter declarations
        param_decl = [
            ("number x", VarDecl(name=Id("x"), varType=NumberType())),

            ("bool x", VarDecl(name=Id("x"), varType=BoolType())),

            ("string x", VarDecl(name=Id("x"), varType=StringType())),

            ("number x[1]", VarDecl(name=Id("x"), varType=ArrayType(eleType=NumberType(),
                                                                    size=[1.0]))),
            ("string x[1, 2]", VarDecl(name=Id("x"),
                                       varType=ArrayType(eleType=StringType(),
                                                                    size=[1.0, 2.0]))),
            ("bool x[1, 2, 3]", VarDecl(name=Id("x"), varType=ArrayType(eleType=BoolType(),
                                                                    size=[1.0, 2.0, 3.0]))),
        ]

        decl, decl_ast = self.create_function_declaration(name="f", param_decl=param_decl)
        self.assertTrue(TestAST.test(decl, str(Program(decl=[decl_ast])), "decl_with_param"))

        block_txt, block_ast = self.create_block_stmt(param_decl[:3])

        decl, decl_ast = self.create_function_declaration(name="abc", param_decl=param_decl,
                                                        body=(block_txt, block_ast))

        self.assertTrue(TestAST.test(decl, str(Program(decl=[decl_ast])), "decl_with_param_2"))

    def test_function_call_stmt(self):
        call_no_args = self.create_call_stmt("f", args=[])

        args = self.expressions_and_asts()[10:13]

        call_with_args = self.create_call_stmt("abc", args)

        prog, prog_ast = self.create_program([call_no_args, call_with_args])

        self.assertTrue(TestAST.test(prog, str(prog_ast), "test_call_stmt"))

    def test_for_loop_stmt(self):
        cond = self.expressions_and_asts()[13]
        update = self.expressions_and_asts()[2]

        loop_body = self.create_call_stmt(name="f", args=[])
        loop_stmt = f"for i until {cond[0]} by {update[0]}\n{loop_body[0]}"

        loop_ast = For(name=Id("i"), condExpr=cond[1],
                       updExpr=update[1], body=loop_body[1])

        prog, prog_ast = self.create_program([loop_body, (loop_stmt, loop_ast)])
        
        self.assertTrue(TestAST.test(prog, str(prog_ast), "test_for_loop_ast"))

        block, block_ast = self.create_block_stmt([loop_body, (loop_stmt, loop_ast)])

        loop_with_block = f"for i until {cond[0]} by {update[0]}\n{block}"

        loop_with_block_ast = For(name=Id("i"), condExpr=cond[1],
                       updExpr=update[1], body=block_ast)

        prog_2, prog_ast_2 = self.create_program([(loop_with_block, loop_with_block_ast)])

        self.assertTrue(TestAST.test(prog_2, str(prog_ast_2), "loop_with_block_ast"))

    def test_if_stmt(self):
        exprs = self.expressions_and_asts()[:3]

        stmts = []
        for i in range(3):
            stmts.append(self.create_call_stmt(name="f", args=exprs))

        # if statement without elif and else parts
        if_stmt_0 = self.create_if_stmt(conditions=[exprs[0]], cond_body=[stmts[0]])
        
        # if statement that has elif parts but no else part
        if_stmt_1 = self.create_if_stmt(conditions=exprs, cond_body=stmts)

        # if statement that has elif parts and else part
        if_stmt_2 = self.create_if_stmt(conditions=exprs, cond_body=stmts, else_body=stmts[0])

        # if statement that have else part but no elif parts
        if_stmt_3 = self.create_if_stmt(conditions=[exprs[0]], cond_body=[stmts[0]],
                                        else_body=stmts[1])

        prog, prog_ast = self.create_program(stmts=[if_stmt_0, if_stmt_1, if_stmt_2, if_stmt_3])

        self.assertTrue(TestAST.test(prog, str(prog_ast), "test_if_stmt_ast"))

        # Ambiguous if statement
        if_stmt_4 = self.create_if_stmt(conditions=[exprs[0], exprs[1]], cond_body=[if_stmt_2,
                                                                                   if_stmt_3])

        prog, prog_ast = self.create_program(stmts=[if_stmt_4])
        self.assertTrue(TestAST.test(prog, str(prog_ast), "test_amb_if_stmt"))


    def test_loop_ctrl_stmt(self):
        prog, prog_ast = self.create_program(stmts=[('break\n', Break()), ('continue\n', Continue())])
        self.assertTrue(TestAST.test(prog, str(prog_ast), "loop_ctrl_ast"))

    def test_assignment_stmt(self):
        expr, expr_ast = self.expressions_and_asts()[10]

        # left-hand side may be an identifier or an array element
        lhs = [("x", Id("x")), self.expressions_and_asts()[29]]

        stmts = []

        for lhs_tup in lhs:
            assignment = self.create_assignment_stmt(lhs=lhs_tup, expr=(expr, expr_ast))
            stmts.append(assignment)

        prog, prog_ast = self.create_program(stmts=stmts)

        self.assertTrue(TestAST.test(prog, str(prog_ast), "test_assignment_ast"))

    def test_block_stmt(self):
        exprs = self.expressions_and_asts()[:3]

        stmts = []
        for i in range(3):
            stmts.append(self.create_call_stmt(name="f", args=exprs))

        if_stmt = self.create_if_stmt(conditions=[exprs[0]], cond_body=[stmts[0]],
                                        else_body=stmts[1])

        stmts.append(if_stmt)
        stmts.append(('break\n', Break()))

        block, block_ast = self.create_block_stmt(stmts)

        prog, prog_ast = self.create_program(stmts=stmts + [(block, block_ast)])

        self.assertTrue(TestAST.test(prog, str(prog_ast), "test_block"))
