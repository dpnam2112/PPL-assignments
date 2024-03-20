from os import walk
import unittest
from StaticError import *
from TestUtils import TestAST, TestChecker
from AST import *

class CheckSuite(unittest.TestCase):
    def test_no_entry_point(self):
        input_0  = """
        func main(number a)
        func main(number a) return a
        """

        expect_0 = str(NoEntryPoint())
        self.assertTrue(TestChecker.test(input_0, expect_0, "no_entry_point_0"))

        input_1 = """
        number x
        """
        expect_1 = str(NoEntryPoint())
        self.assertTrue(TestChecker.test(input_1, expect_1, "no_entry_point_1"))

        input_2 = """
        func main(number x) begin
        end
        """
        expect_2 = str(NoEntryPoint())
        self.assertTrue(TestChecker.test(input_2, expect_2, "no_entry_point_2"))

        input_3 = """
        func main() return
        """
        expect_3 = ""
        self.assertTrue(TestChecker.test(input_3, expect_3, "no_entry_point_3"))

        input_4 = """
        func main() return 1
        """
        expect_4 = str(NoEntryPoint())
        self.assertTrue(TestChecker.test(input_4, expect_4, "no_entry_point_4"))

        input_5 = """
        func main()
        func main() begin
            return 1 + 2
        end
        """
        expect_5 = str(NoEntryPoint())
        self.assertTrue(TestChecker.test(input_5, expect_5, "no_entry_point_5"))

        input_6 = """
        func main() begin
            dynamic x
            x <- [[1, 2], [3, 4], [5, 6]]
        end
        """
        expect_6 = ""
        self.assertTrue(TestChecker.test(input_6, expect_6, "no_entry_point_6"))

        input_7 = """
        func main() begin
            var x <- 1
            return
            x <- 2
        end
        """
        expect_7 = ""
        self.assertTrue(TestChecker.test(input_7, expect_7, "no_entry_point_7"))

        input_8 = """
        var main <- 1
        """
        expect_8 = str(NoEntryPoint())
        self.assertTrue(TestChecker.test(input_8, expect_8, "no_entry_point_8"))
        
        input_9 = Program([])
        expect = str(NoEntryPoint())
        self.assertTrue(TestChecker.test(input_9, expect, "no_entry_point_9"))

    def test_no_definition(self):
        inp = """
        func f()
        func main() return
        """
        expect = str(NoDefinition('f'))
        self.assertTrue(TestChecker.test(inp, expect, "no_def_0"))

        inp = """
        func f(number x, number y)
        func main() return
        """
        expect = str(NoDefinition('f'))
        self.assertTrue(TestChecker.test(inp, expect, "no_def_1"))

        inp = """
        func f(number x, number y) return x + y
        func main() return
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "no_def_2"))

        inp = """
        func f(number x, number y)
        func f(number x, number y) return x + y
        func main() return
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "no_def_3"))

    def test_redeclared_function(self):
        inp = """
        func f() return
        func f(number x) return
        """
        expect = str(Redeclared(Function(), 'f'))
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_fn_0"))

        inp = """
        var f <- 1
        func f()
        """
        expect = str(Redeclared(Function(), 'f'))
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_fn_1"))

        inp = """
        func f() return
        func f()
        """
        expect = str(Redeclared(Function(), 'f'))
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_fn_2"))

        inp = """
        func f(number x, number y) return x + y
        func f()
        """
        expect = str(Redeclared(Function(), 'f'))
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_fn_3"))

        inp = """
        func f()
        func f(number x)
        """
        expect = str(Redeclared(Function(), 'f'))
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_fn_4"))

        inp = """
        func f() return
        func f() return
        """
        expect = str(Redeclared(Function(), 'f'))
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_fn_5"))

    def test_redeclared_builtin_function(self):
        builtin_fn = ["readNumber", "writeNumber", "readBool", "writeBool", "readString", "writeString"]
        for fn_name in builtin_fn:
            inp = f"func {fn_name}()\n func main() return\n"
            expect = str(Redeclared(Function(), fn_name))
            self.assertTrue(TestChecker.test(inp, expect, f"redeclared_buildin_{fn_name}_0"))

            inp = f"var {fn_name} <- 1\n func main() return\n"
            expect = str(Redeclared(Variable(), fn_name))
            self.assertTrue(TestChecker.test(inp, expect, f"redeclared_buildin_{fn_name}_1"))

    def test_loop_ctrl(self):
        inp = """
        func main() begin
            break
        end
        """
        expect = str(MustInLoop(Break()))
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_0"))

        inp = """
        func main() begin
            continue
        end
        """
        expect = str(MustInLoop(Continue()))
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_1"))

        inp = """
        func main() begin
            var i <- 1
            for i until i > 1 by 1 begin
                break
            end
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_2"))

        inp = """
        func main() begin
            var i <- 1
            for i until i > 1 by 1 begin
                continue
            end
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_3"))

        inp = """
        func main() begin
            var i <- 1
            for i until i > 1 by 1 begin
                for i until i > 1 by 1 begin
                    break
                    for i until i > 1 by 1 begin
                        continue
                    end
                    continue
                end
                continue
                break
            end
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_4"))

        inp = """
        func main() begin
            var i <- 1
            for i until i > 1 by 1
                if (true)
                    break
                else
                    continue
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_5"))

        inp = """
        func main() begin
            var i <- 1
            for i until i > 1 by 1
                if (true)
                    break
                else
                    continue
            continue

        end
        """
        expect = str(MustInLoop(Continue())) 
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_6"))

        inp = """
        func main() begin
            begin
                begin
                break
                end
            end
        end
        """
        expect = str(MustInLoop(Break()))
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_7"))

        inp = """
        func main() begin
            begin
                begin
                continue
                end
            end
        end
        """
        expect = str(MustInLoop(Continue()))
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_8"))

        inp = """
        func main() begin
            number i
            for i until i > 10 by 1 break
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_9"))

        inp = """
        func main() begin
            number i
            for i until i > 10 by 1 continue
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_10"))

        inp = """
        func main() begin
            number i
            for i until true by 1 begin
                begin
                    begin
                        break
                    end
                    continue
                end
            end
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_11"))

    def test_redeclared_variable(self):
        inp = """
        func main() begin
            var x <- 1
            var x <- 2
        end
        """
        expect = str(Redeclared(Variable(), 'x'))
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_var_0"))

        inp = """
        var x <- 1

        func main() begin
            var x <- 2
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_var_1"))

        inp = """
        func main() begin
            var x <- 1
            begin
                var x <- 2
            end
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_var_2"))

        inp = """
        func main() begin
            var x <- 1
            begin
                var x <- 2
                var x <- 3
            end
        end
        """
        expect = str(Redeclared(Variable(), 'x'))
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_var_3"))

        inp = """
        func main() begin
            var main <- 1
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_var_4"))

        inp = """
        func f(number x) begin
            dynamic x <- 1
        end
        func main() return
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_var_5"))

        inp = """
        func f() return
        dynamic f <- 1
        func main() return
        """
        expect = str(Redeclared(Variable(), 'f'))
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_var_6"))


    def test_undeclared_identifier(self):
        inp = """
        func main() begin
            begin
                number x <- y + 1
            end
        end
        """
        expect = str(Undeclared(Identifier(), 'y'))
        self.assertTrue(TestChecker.test(inp, expect, "undeclared_id_0"))

        inp = """
        func main() begin
            number x <- x + 1
        end
        """
        expect = str(Undeclared(Identifier(), 'x'))
        self.assertTrue(TestChecker.test(inp, expect, "undeclared_id_1"))

        inp = """
        func main() begin
            begin
                begin
                    number x <- y + 1
                end
            end
        end
        """
        expect = str(Undeclared(Identifier(), 'y'))
        self.assertTrue(TestChecker.test(inp, expect, "undeclared_id_2"))

        inp = """
        func f() return x
        func main() begin
            number x <- f()
        end
        """
        expect = str(Undeclared(Identifier(), 'x'))
        self.assertTrue(TestChecker.test(inp, expect, "undeclared_id_3"))

        inp = """
        func main() begin
            var x <- 1
            begin
                var y <- x
            end
            var z <- y
        end
        """
        expect = str(Undeclared(Identifier(), 'y'))
        self.assertTrue(TestChecker.test(inp, expect, "undeclared_id_4"))

        inp = """
        func main() begin
            begin
                var x <- 1
            end
            x[100] <- 2
        end
        """
        expect = str(Undeclared(Identifier(), 'x'))
        self.assertTrue(TestChecker.test(inp, expect, "undeclared_id_5"))

        inp = """
        func main() begin
            begin
                dynamic x
                x <- 1
            end
        x[1, 2, 3] <- 12
        end
        """
        expect = str(Undeclared(Identifier(), 'x'))
        self.assertTrue(TestChecker.test(inp, expect, "undeclared_id_6"))

        inp = """
        func main() begin
            if (true) var x <- 1
            elif (false) var x <- 2
            else dynamic x <- 3
            x <- 1
        end
        """
        expect = str(Undeclared(Identifier(), 'x'))
        self.assertTrue(TestChecker.test(inp, expect, "undeclared_id_7"))

        inp = """
        var x <- y + 1
        func main() return
        """
        expect = str(Undeclared(Identifier(), 'y'))
        self.assertTrue(TestChecker.test(inp, expect, "undeclared_id_8"))

    def test_undeclared_function(self):
        inp = """
        func main() begin
            number x <- f()
        end
        """
        expect = str(Undeclared(Function(), 'f'))
        self.assertTrue(TestChecker.test(inp, expect, "undeclared_function_0"))

        inp = """
        func f() return g()
        func main() return
        """
        expect = str(Undeclared(Function(), 'g'))
        self.assertTrue(TestChecker.test(inp, expect, "undeclared_function_1"))

        inp = """
        func main() begin
            var x <- 1
            begin
                var y <- 2
            end
            var z <- y()
        end
        """
        expect = str(Undeclared(Function(), 'y'))
        self.assertTrue(TestChecker.test(inp, expect, "undeclared_function_2"))

    def test_simple_var_declaration(self):
        inp = """
        func main() begin
            var x <- (1 + 2) * 3 - 4
            dynamic y <- (1 + 2) * 3 - 4
            ## var z <- [1, 2, 3, 4, 1 + 2]
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "var_decl_0"))

        inp = """
        func main() begin
            number x <- (1 + 2) * 3
            bool y <- true and false and false or true
            string z <- ("abc" ... "abc") ... "abc"
            bool h <- (1 = 1) and (2 != 2) or not ("abc" == "abc")
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "var_decl_1"))

    def test_local_type_inference(self):
        inp = """
        func main() begin
            dynamic x
            var y <- x + 1
            bool z <- not x
        end
        """
        expect = str(TypeMismatchInExpression(UnaryOp(op='not', operand=Id('x'))))
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_0"))

        inp = """
        func main() begin
            dynamic x
            var y <- (x and true) or (x == "abc")
        end
        """
        expect = str(TypeMismatchInExpression(BinaryOp('==', Id('x'), StringLiteral("abc"))))
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_1"))

        inp = """
        func main() begin
            dynamic x
            bool y <- x
            string z <- x
        end
        """
        expect = str(TypeMismatchInStatement(VarDecl(Id('z'), varType=StringType(),
                                                     varInit=Id('x'))))
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_2"))

        inp = """
        func main() begin
            dynamic x
            dynamic y
            number z <- x + y
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_3"))

        inp = """
        func main() begin
            dynamic x
            dynamic y
            number z <- x - y
            bool h <- x
        end
        """
        expect = str(TypeMismatchInStatement(VarDecl(Id('h'), BoolType(), varInit=Id('x'))))
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_4"))

        inp = """
        func main() begin
            dynamic x
            dynamic y
            bool z <- (x != y) and (x = y) or (x + y = x * y % y)
            number h <- x
            number g <- y
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_5"))

        inp = """
        func main() begin
            dynamic x
            dynamic y
            dynamic z <- x ... y
            string abc <- x
            string xyz <- y
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_6"))

        inp = """
        func main() begin
            dynamic x
            dynamic y
            dynamic abc <- (x ... y) == (x ... y)
            bool _abc <- abc
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_7"))

        inp = """
        func main() begin
            dynamic x
            dynamic y
            dynamic abc <- ((x ... y) == (x ... y)) and (x or true)
        end
        """
        expect = str(TypeMismatchInExpression(BinaryOp('or', Id('x'), BooleanLiteral(True))))
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_8"))

        inp = """
        func main() begin
            dynamic x
            dynamic y <- x
        end
        """
        expect = str(TypeCannotBeInferred(VarDecl(Id('y'), None, 'dynamic', Id('x'))))
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_9"))

        inp = """
        func main() begin
            dynamic x <- 1 + 2 + 3
            var y <- x
            dynamic z <- x + y
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_10"))

        inp = """
        func main() begin
            dynamic x
            begin
                dynamic x
                dynamic y <- x + 1
                number aaa <- x
            end
            bool z <- x
            bool h <- x and true
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_11"))

        inp = """
        func main() begin
            dynamic x
            bool y <- x
            begin
                dynamic z <- x + 1
            end
        end
        """
        expect = str(TypeMismatchInExpression(BinaryOp('+', Id('x'), NumberLiteral(1.0))))

        self.assertTrue(TestChecker.test(inp, expect, "type_inference_12"))

    
    def test_simple_array_inference(self):
        inp = """
        func main() begin
            var x <- [1, 2, 3, 4, 5]
            number y[5] <- x 
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "array_type_inference_0"))

        inp = """
        func main() begin
            var x <- [1, 2, 3, 4 * 2 - 1, 6, 7, 19 * 2 - 2]
            number y[5] <- x
        end
        """
        expect = str(TypeMismatchInStatement(
                    VarDecl(Id('y'), ArrayType([5.0], NumberType()), None, Id('x'))))
        self.assertTrue(TestChecker.test(inp, expect, "array_type_inference_1"))

        inp = """
        func main() begin
            var x <- [[1, 2], [1, 2, 3], [1, 2, 3, 4]]
            number y[3, 4] <- x
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "array_type_inference_2"))

        inp = """
        func main() begin
            var x <- [[1, 2], [2, 1]]
            bool y[2, 2] <- x
        end
        """
        expect = str(TypeMismatchInStatement(VarDecl(Id('y'), ArrayType([2.0, 2.0], BoolType()), None,
                                                                    Id('x'))))
        self.assertTrue(TestChecker.test(inp, expect, "array_type_inference_3"))

        inp = """
        func main() begin
            number x[2, 3] <- [[1, 2, 3 * 3 % 3], [(4 - 5 * 7) / 2, 3.12, 1.1]]
            number y[2, 3] <- x
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "array_type_inference_4"))

        inp = """
        func main() begin
            number x[2, 3] <- [[1, 2, 3, 4], [1, 2, 3]]
        end
        """
        expect = str(TypeMismatchInStatement(VarDecl(Id('x'), ArrayType([2.0, 3.0], NumberType()), None,
                                         ArrayLiteral([ArrayLiteral([NumberLiteral(1.0), NumberLiteral(2.0), NumberLiteral(3.0),
                                                                     NumberLiteral(4.0)]),
                                                       ArrayLiteral([NumberLiteral(1.0), NumberLiteral(2.0),
                                                                     NumberLiteral(3.0)])]))))
        self.assertTrue(TestChecker.test(inp, expect, "array_type_inference_4"))

        inp = """
        func main() begin
            dynamic x
            number x1
            number x2
            number x3
            var y <- [[[1, 2], x, [x1, x2 , x3]]]
        end
        """
        arr_lit = ArrayLiteral([ArrayLiteral([ArrayLiteral([NumberLiteral(1.0),
                                                            NumberLiteral(2.0)]), Id('x'),
                                              ArrayLiteral([Id('x1'), Id('x2'), Id('x3')])])])
        expect = str(TypeCannotBeInferred(VarDecl(Id('y'), None, 'var', arr_lit)))
        self.assertTrue(TestChecker.test(inp, expect, "array_type_inference_5"))

        inp = """
        func main() begin
            dynamic x
            number x1
            number x2
            number x3
            dynamic y
            y <- [[[1, 2], x, [x1, x2 , x3]]]
        end
        """
        arr_lit = ArrayLiteral([ArrayLiteral([ArrayLiteral([NumberLiteral(1.0),
                                                            NumberLiteral(2.0)]), Id('x'),
                                              ArrayLiteral([Id('x1'), Id('x2'), Id('x3')])])])
        expect = str(TypeCannotBeInferred(Assign(Id('y'), arr_lit)))
        self.assertTrue(TestChecker.test(inp, expect, "array_type_inference_6"))


    def test_type_mismatch_in_statement(self):
        inp = """
        func main() begin
            number x
            string y
            x <- y
        end
        """
        expect = str(TypeMismatchInStatement(Assign(Id('x'), Id('y'))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_stmt_0"))

        inp = """
        func main() begin
            dynamic x
            x <- 1 + (2 * 3 + 4 * (5 + 6))
            x <- true
        end
        """
        expect = str(TypeMismatchInStatement(Assign(Id('x'), BooleanLiteral(True))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_stmt_1"))

        inp = """
        func main() begin
            dynamic x
            x <- ("abc" ... "def") ... "ghi"
            x <- 1
        end
        """
        expect = str(TypeMismatchInStatement(Assign(Id('x'), NumberLiteral(1.0))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_stmt_2"))

        inp = """
        func main() begin
            var x <- 1 + 2 - 3
            dynamic y
            y <- x
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_stmt_3"))

        inp = """
        func main() begin
            number x[3, 2, 1]
            string y[3, 2, 1]
            y <- x
        end
        """
        expect = str(TypeMismatchInStatement(Assign(Id('y'), Id('x'))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_stmt_4"))

        inp = """
        func main() begin
            dynamic x
            var y <- x == x 

            ## x's type must be string
            ## y's type must be bool
            y <- x
        end
        """
        expect = str(TypeMismatchInStatement(Assign(Id('y'), Id('x'))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_stmt_5"))

    def test_type_inference_from_assignment(self):
        inp = """
        func main() begin
            dynamic x
            number y
            y <- x

            ## ensure that x's type is inferred to be number type
            number z <- x
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "assign_type_inference_0"))

        inp = """
        func main() begin
            dynamic x
            number y
            x <- y

            ## ensure that x's type is inferred to be number type
            number z <- x
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "assign_type_inference_1"))

        inp = """
        func main() begin
            dynamic x
            bool y

            x <- y
            y <- x

            dynamic z
            string h

            z <- h
            string g <- h ... z
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "assign_type_inference_2"))

        inp = """
        func main() begin
            dynamic x
            x <- [1, 2, 3, 4, 5]

            number y[5] <- x
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "assign_type_inference_3"))

        inp = """
        func main() begin
            dynamic x
            x <- [[1, 2], [1, 2, 3], [1, 2, 3]]
            number y[3, 3] <- x
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "assign_type_inference_4"))

        inp = """
        func main() begin
            dynamic x
            x <- [1, 2, 3, 4, 5]
            number y[2] <- x
        end
        """
        expect = TypeMismatchInStatement(VarDecl(Id('y'), ArrayType([2.0], NumberType()), None,
                                                 Id('x')))
        expect = str(expect)
        self.assertTrue(TestChecker.test(inp, expect, "assign_type_inference_5"))

    def test_redeclared_parameter(self):
        inp = """
        func f(number x, bool x) begin
            return x
        end

        func main() begin
        end
        """
        expect = str(Redeclared(Parameter(), 'x'))
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_parameter_0"))

        inp = """
        func f(number x, bool y, number y[10]) begin
            return x
        end

        func main() begin
        end
        """
        expect = str(Redeclared(Parameter(), 'y'))
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_parameter_1"))

        inp = """
        func f(number f, number f1) return f + f1
        func main() return
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_parameter_2"))

        inp = """
        func f(number f1, number f, number f) return f
        func main() return
        """
        expect = str(Redeclared(Parameter(), 'f'))
        self.assertTrue(TestChecker.test(inp, expect, "redeclared_parameter_3"))

    def test_type_inference_from_param_types(self):
        inp = """
        func f(number a, number b)
        func main() begin
            dynamic x
            dynamic y
            var z <- f(x, y) + (x * y)
        end
        func f(number a, number b) return a + b
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inf_from_param_0"))

        inp = """
        func f(string x, number y)
        func main() begin
            dynamic x
            dynamic y
            var z <- f(x, y) and (y = 1) or (x == "abc")
        end
        func f(string a, number b) return (a == "...") and (b = (1 + 2))
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inf_from_param_1"))

    def test_function_type_inference(self):
        inp = """
        func f() return 1
        func main() begin
            number x <- f()
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_0"))

        inp = """
        func f(number x, number y, string z)
            return (x = y) and (z == "abc")

        func main() begin
            bool x <- f(1, 2, "abc")
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_1"))

        inp = """
        func f()
        func main() begin
            bool x <- f()
        end

        func f() return true
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_2"))

        inp = """
        func f()
        func main() begin
            number x[5] <- f()
            number y[5] <- f()
        end
        func f() return [1, 2, 3, 4 ,5]
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_3"))

        inp = """
        func f()
        func main() begin
            f()
            string x <- f()
        end
        func f() return
        """
        expect = str(TypeMismatchInExpression(CallExpr(Id('f'), [])))
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_4"))

        inp = """
        func f()
        func main() begin
            f()
            var x <- f()
        end
        func f() return
        """
        expect = str(TypeMismatchInExpression(CallExpr(Id('f'), [])))
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_5"))

        inp = """
        func f()
        func main() begin
            bool x <- f() and true and (1 != f())
        end

        func f() return true
        """
        expect = str(TypeMismatchInExpression(BinaryOp('!=', NumberLiteral(1.0), CallExpr(Id('f'), []))))
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_6"))

        inp = """
        func f() return [1, 2, 3, 4, 5]
        func main() begin
            number x <- f()[0]
            number y <- f()[2]
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_7"))

        inp = """
        func f(number arr[100]) return arr
        func main() begin
            number a[100]
            number x[100] <- f(a)
            bool y <- f(a)
        end
        """
        expect = str(TypeMismatchInStatement(VarDecl(Id('y'), BoolType(), None, CallExpr(Id('f'),
                                                                                         [Id('a')]))))
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_8"))

        inp = """
        func f(number x)
        func main() begin
            number a1
            number a2 <- f(a1)
        end

        func f(number y) return y
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_9"))

        inp = """
        func f(bool x)
        func main() begin
            bool x
            number y <- f(x)
        end
        func f(bool x) return x
        """
        expect = str(TypeMismatchInStatement(Return(Id('x'))))
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_10"))

        inp = """
        func f() begin
            number x[10]
            bool y[10]
            return x
            return y
        end

        func main() return
        """
        expect = str(TypeMismatchInStatement(Return(Id('y'))))
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_11"))

        inp = """
        func f()
        func main() begin
            var x <- f()
        end

        func f() return 1
        """
        expect = str(TypeCannotBeInferred(VarDecl(Id('x'), None, 'var', CallExpr(Id('f'), []))))
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_12"))

        inp = """
        func f()
        func main() begin
            string x
            x <- f()
        end
        func f() return "abc"
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_13"))

        inp = """
        func f(number x, number y)
        func main() begin
            number x
            dynamic a
            dynamic b
            x <- f(a, b)
        end
        func f(number a1, number a2) return a1 + a2
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "fn_type_inference_14"))

    def test_type_mismatch_in_expression(self):
        inp = """
        func main() begin
            dynamic x
            dynamic y
            var z <- (x + y = 0) and (x == "")
        end
        """
        expect = str(TypeMismatchInExpression(BinaryOp('==', Id('x'), StringLiteral(""))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr"))

        inp = """
        func main() begin
            var x <- 1
            var y <- x[1]
        end
        """
        expect = str(TypeMismatchInExpression(ArrayCell(Id('x'), [NumberLiteral(1.0)])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_1"))

        inp = """
        func main() begin
            number x[10]
            bool y <- x[0] and true
        end
        """
        expect = str(TypeMismatchInExpression(BinaryOp('and', ArrayCell(Id('x'), [NumberLiteral(0.0)]), BooleanLiteral(True))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_2"))

        inp = """
        func main() begin
            string names[10]
            bool match <- names[0] == "Harry"
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_3"))

        inp = """
        func main() begin
            bool x[100]
            bool x1 <- x[0] and x[1] or x[2] and not x[3]
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_4"))
        
        inp = """
        func main() begin
            bool x[10, 5]
            bool y <- x[0, 0] and x[0, 1] or x[0, 2] and not x[1, 2] and not x[2, 1]
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_5"))

        inp = """
        func main() begin
            string s[3, 2, 1]
            number n[10]
            bool y <- s[0, 0, 0] == n[0]
        end
        """
        expect = TypeMismatchInExpression(BinaryOp('==', ArrayCell(Id('s'), [NumberLiteral(0.0), NumberLiteral(0.0), NumberLiteral(0.0)]),
                                                                   ArrayCell(Id('n'), [NumberLiteral(0.0)])))
        expect = str(expect)
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_6"))

        inp = """
        func main() begin
            string names[10]
            string x <- names[""]
        end
        """
        expect = str(TypeMismatchInExpression(ArrayCell(Id('names'), [StringLiteral("")])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_7"))

        inp = """
        func f() return "abc" == "def"

        func main() begin
            var x <- [1, 2, 3, 4, 5]
            var y <- x[f()]
        end
        """
        expect = str(TypeMismatchInExpression(ArrayCell(Id('x'), [CallExpr(Id('f'), [])])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_8"))

        inp = """
        func f() return [1, 2, 3, 4, 5]
        func main() begin
            var x <- [1, 2, 3]
            var y <- x[f()]
        end
        """
        expect = str(TypeMismatchInExpression(ArrayCell(Id('x'), [CallExpr(Id('f'), [])])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_9"))

        inp = """
        func main() begin
            var x <- [1, 2, 3, 4, 5]
            var y <- x[[1]]
        end
        """
        expect = str(TypeMismatchInExpression(ArrayCell(Id('x'), [ArrayLiteral([NumberLiteral(1.0)])])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_10"))

        inp = """
        func f() return 1
        func main() begin
            var x <- f()[0]
        end
        """
        expect = str(TypeMismatchInExpression(ArrayCell(CallExpr(Id('f'), []), [NumberLiteral(0.0)])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_11"))

        inp = """
        func f() return [1, 2, 3, 4, 5]
        func main() begin
            var x <- f()[0] = 1
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_12"))

        inp = """
        func f() return "abc"
        func main() begin
            var x <- [1, 2, 3, 4, 5]
            string s <- f()
            var y <- x[1 + (2 * 3 % 4 - 5 + (-f() * 6))]
        end
        """
        expect = str(TypeMismatchInExpression(UnaryOp('-', CallExpr(Id('f'), []))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_13"))

        inp = """
        func main() begin
            number x
            bool y
            var z <- x or y
        end
        """
        expect = str(TypeMismatchInExpression(BinaryOp('or', Id('x'), Id('y'))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_14"))

        inp = """
        func main() begin
            var z <- not (1 + 2)
        end
        """
        expect = str(TypeMismatchInExpression(UnaryOp('not', BinaryOp('+', NumberLiteral(1.0), NumberLiteral(2.0)))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_15"))

        inp = """
        func main() begin
            var x <- [1, 2] + 1
        end
        """
        expect = str(TypeMismatchInExpression(BinaryOp('+', ArrayLiteral([NumberLiteral(1.0), NumberLiteral(2.0)]), NumberLiteral(1.0))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_16"))

        inp = """
        func main() begin
            var x <- not [1, 2]
        end
        """
        expect = str(TypeMismatchInExpression(UnaryOp('not', ArrayLiteral([NumberLiteral(1.0), NumberLiteral(2.0)]))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_17"))

        inp = """
        func f(number x, string y[10]) return x
        func main() begin
            dynamic x
            dynamic y <- ["abc", "abcd", "123"]
            var z <- f(x, y)
        end
        """
        expect = str(TypeMismatchInExpression(CallExpr(Id('f'), [Id('x'), Id('y')])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_18"))

        inp = """
        func f() return
        func main() begin
            var x <- f()
        end
        """
        expect = str(TypeMismatchInExpression(CallExpr(Id('f'), [])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_19"))

        inp = """
        func f(number x, number y) return x + y
        func main() begin
            dynamic y
            var x <- f(y)
        end
        """
        expect = str(TypeMismatchInExpression(CallExpr(Id('f'), [Id('y')])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_20"))

        inp = """
        func f(number x, number y) return x + y
        func main() begin
            dynamic x1
            dynamic x2
            dynamic x3
            var x <- f(x1, x2, x3)
        end
        """
        expect = str(TypeMismatchInExpression(CallExpr(Id('f'), [Id('x1'), Id('x2'), Id('x3')])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_21"))

        inp = """
        func main() begin
            var x <- [1, 2, 3]
            var x1 <- "a"
            var x2 <- "b"
            var y <- x[x1]
        end
        """
        expect = str(TypeMismatchInExpression(ArrayCell(Id('x'), [Id('x1')])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_22"))

        inp = """
        func main() begin
            var x <- [[1, 2], [3, 4]]
            var x1 <- 0
            var x2 <- "a" 
            var y <- x[x1, x2]
        end
        """
        expect = str(TypeMismatchInExpression(ArrayCell(Id('x'), [Id('x1'), Id('x2')])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_23"))

        inp = """
        func main() begin
            var x <- 1
            var x1 <- 1
            var y <- x[x1]
        end
        """
        expect = str(TypeMismatchInExpression(ArrayCell(Id('x'), [Id('x1')])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_expr_24"))

    def test_type_mismatch_in_stmt(self):
        inp = """
        func f() return
        func main() begin
            dynamic x
            var y <- x and true
            dynamic z
            z <- y and x

            if (x) f()
            if (y) f()
            if (z) f()
            else f()
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_0"))

        inp = """
        func f(number a, bool b, number c) return
        func main() begin
            dynamic x
            dynamic y
            dynamic z
            f(x, y, z)
            for x until y by z begin
                f(x, y, z)
            end
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_1"))

        inp = """
        func main() begin
            dynamic x
            x <- "abc"
            for x until true by 1 begin
            end
        end
        """
        expect = str(TypeMismatchInStatement(For(Id('x'), BooleanLiteral(True), NumberLiteral(1.0), Block([]))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_2"))

        inp = """
        func f() return "abc"
        func g() return
        func main() begin
            if (f()) begin
                g()
            end
        end
        """
        if_stmt = If(CallExpr(Id('f'), []), Block([CallStmt(Id('g'), [])]))
        expect = str(TypeMismatchInStatement(if_stmt))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_3"))

        inp = """
        func f() return "abc"
        func g() return
        func main() begin
            dynamic x
            if (x) g()
            elif(f()) g()
        end
        """
        if_stmt = If(Id('x'), CallStmt(Id('g'), []), [(CallExpr(Id('f'), []), CallStmt(Id('g'), []))])
        expect = str(TypeMismatchInStatement(if_stmt))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_4"))

        inp = """
        func f1() return true
        func f() return false and false or f1()
        func g() return
        func main() begin
            dynamic x
            if (x) g()
            elif (f()) g()
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_5"))

        inp = """
        func f(bool x) return [1, 2, 3, 4, 5]
        func g() return
        func main() begin
            dynamic x
            if (x) g()
            elif (f(x)) g()
        end
        """
        if_stmt = If(Id('x'), CallStmt(Id('g'), []), [(CallExpr(Id('f'), [Id('x')]), CallStmt(Id('g'), []))])
        expect = str(TypeMismatchInStatement(if_stmt))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_6"))

        inp = """
        func f(bool x) return [x, x, x]
        func g() return
        func main() begin
            dynamic arr <- f(true)
            dynamic x
            if (arr[0]) g()
            elif (arr[1]) g()
            elif (arr[x + x] and arr[x - x]) g()
            else g()

            for x until arr[0] and arr[1] or arr[x * x] by x
                g()
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_7"))

        inp = """
        func f(string x) return [x, x, x]
        func main() begin
            var arr <- f("abc")
            dynamic x
            for x until arr[0] by 1
            begin
            end
        end
        """
        for_stmt = For(Id('x'), ArrayCell(Id('arr'), [NumberLiteral(0.0)]), NumberLiteral(1.0), Block([]))
        expect = str(TypeMismatchInStatement(for_stmt))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_8"))


        inp = """
        func f(string x) return [x, x, x]
        func g(number x) return [x, x, x]
        func main() begin
            var arr <- f("abc")
            dynamic x
            for x until g(x)[x * 2] by arr[0]
            begin
            end
        end
        """
        stop_cond = ArrayCell(CallExpr(Id('g'), [Id('x')]), [BinaryOp('*', Id('x'), NumberLiteral(2.0))])
        for_stmt = For(Id('x'), stop_cond, ArrayCell(Id('arr'), [NumberLiteral(0.0)]), Block([]))
        expect = str(TypeMismatchInStatement(for_stmt))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_9"))

        inp = """
        func f(number x, number y, number z) return x + y * z
        func main() begin
            dynamic x
            dynamic y
            dynamic z

            f(x, y, z)
        end
        """
        expect = str(TypeMismatchInStatement(CallStmt(Id('f'), [Id('x'), Id('y'), Id('z')])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_10"))

        inp = """
        func f(number x[100]) return x
        func main() begin
            number x[100]
            x <- f(x)
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_11"))

        inp = """
        func f() begin
            number x[100]
            return x
        end

        func g() return 1

        func main() begin
            number y
            y <- f()[f()[0] + 1 * g() / f()[2]]
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_12"))

        inp = """
        func main() begin
            number x[100]
            bool y[100]
            x[2] <- y[1] 
        end
        """
        expect = str(TypeMismatchInStatement(Assign(ArrayCell(Id('x'), [NumberLiteral(2.0)]), ArrayCell(Id('y'), [NumberLiteral(1.0)]))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_13"))

        inp = """
        func f() return [1, 2, 3, 4, 5]
        func main() begin
            bool x[100]
            x[0] <- f()[1]
        end
        """
        expect = str(TypeMismatchInStatement(Assign(ArrayCell(Id('x'), [NumberLiteral(0.0)]), ArrayCell(CallExpr(Id('f'), []), [NumberLiteral(1.0)]))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_14"))

        inp = """
        func f() return [1, 2, 3, 4, 5]
        func main() begin
            dynamic x
            x <- f()[1]
            bool y
            x <- y
        end
        """
        expect = str(TypeMismatchInStatement(Assign(Id('x'), Id('y'))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_15"))

        inp = """
        func f() return [[1, 2], [1, 2], [3 * 2 - 5, 4 * 1 + 4]]
        func main() begin
            dynamic x
            x <- f()
            dynamic y
            y <- x[0, 1 * 2 + 3]
            bool z
            z <- y
        end
        """
        expect = str(TypeMismatchInStatement(Assign(Id('z'), Id('y'))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_16"))

        inp = """
        func f() return [[1, 2], [3, 4]]
        func main() begin
            number y[2, 2] <- f()
            number x[3, 4, 5] <- f()
        end
        """
        expect = str(TypeMismatchInStatement(VarDecl(Id('x'), ArrayType([3.0, 4.0, 5.0], NumberType()), None, CallExpr(Id('f'), []))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_17"))

        inp = """
        func f() return [[1, 2], [3 * 2 - 1, 1], [4 / 6 % 6, 3 - 3]]
        func main() begin
            bool x[1] <- f()
        end
        """
        expect = str(TypeMismatchInStatement(VarDecl(Id('x'), ArrayType([1.0], BoolType()), None, CallExpr(Id('f'), []))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_18"))

        inp = """
        func f(bool x, bool y) return [[[x, y], [x, y]], [[x and y, x or y], [not x, not y and x]]]
        func main() begin
            bool x[2, 2, 2] <- f(true, false)
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_19"))

        inp = """
        func f() begin
            var x <- "abc"
            var y <- "def"
            return [x, y, x ... y, (x ... y) ... (x ... y)]
        end
        func main() begin
            string arr[1] <- f()
        end
        """
        expect = str(TypeMismatchInStatement(VarDecl(Id('arr'), ArrayType([1.0], StringType()), None, CallExpr(Id('f'), []))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_19"))

        inp = """
        func f(number x, bool y) return x
        func main() begin
            number x
            bool y
            number z <- f(y, x)
        end
        """
        expect = str(TypeMismatchInExpression(CallExpr(Id('f'), [Id('y'), Id('x')])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_20"))

        inp = """
        func f(number x, bool y) return x
        func main() begin
            number x <- f(not false, 1)
        end
        """
        expect = str(TypeMismatchInExpression(CallExpr(Id('f'), [UnaryOp('not', BooleanLiteral(False)), NumberLiteral(1.0)])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_21"))

        inp = """
        func f(number x, bool y[10]) return
        func main() begin
            var x <- [true, false, false]
            f(1, x)
        end
        """
        expect = str(TypeMismatchInStatement(CallStmt(Id('f'), [NumberLiteral(1.0), Id('x')])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_22"))

        inp = """
        func main() begin
            string s[2] <- ["R", "o", "n"]
        end
        """
        expect = str(TypeMismatchInStatement(VarDecl(Id('s'), ArrayType([2.0], StringType()), None,
                                                     ArrayLiteral([StringLiteral('R'),
                                                                   StringLiteral('o'),
                                                                   StringLiteral('n')]))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_23"))

        inp = """
        func main() begin
            number n[1, 2, 1] <- [[[1], [2], [3]]]
        end
        """
        expect = TypeMismatchInStatement(VarDecl(Id('n'), ArrayType([1.0, 2.0, 1.0], NumberType()),None,
                                 ArrayLiteral([ArrayLiteral([ArrayLiteral([NumberLiteral(1.0)]),
                                                             ArrayLiteral([NumberLiteral(2.0)]),
                                                             ArrayLiteral([NumberLiteral(3.0)])])])))
        expect = str(expect)
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_24"))

        inp = """
        func main() begin
            return
            return 1
        end
        """
        expect = str(TypeMismatchInStatement(Return(NumberLiteral(1.0))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_25"))

        inp = """
        func f() begin
            dynamic x
            if (false)
                return x + 1
            begin
                dynamic x
                x <- false
                begin
                    return x
                end
            end
        end
        func main() return
        """
        expect = str(TypeMismatchInStatement(Return(Id('x'))))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_26"))

        inp = """
        func f()
        func main() begin
            number x <- f()
            f()
        end
        func f() return 1
        """
        expect = str(TypeMismatchInStatement(CallStmt(Id('f'), [])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_27"))

        inp = """
        func f(number x, number y) return
        func main() begin
            f(1)
        end
        """
        expect = str(TypeMismatchInStatement(CallStmt(Id('f'), [NumberLiteral(1.0)])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_28"))

        inp = """
        func f(number x, number y) return
        func main() begin
            f(1, 2, 3)
        end
        """
        expect = str(TypeMismatchInStatement(CallStmt(Id('f'), [NumberLiteral(1.0),
                                                                NumberLiteral(2.0),
                                                                NumberLiteral(3.0)])))
        self.assertTrue(TestChecker.test(inp, expect, "type_mismatch_in_stmt_29"))

    def test_type_inference_from_expression(self):
        inp = """
        func main() begin
            dynamic x
            dynamic y

            var z <- x % y + (x * y) - (x / y)
            dynamic y1
            dynamic y2

            var y3 <- not y2 and not y1 and (y1 or y2) and (x != y)

            dynamic x1
            dynamic x2
            dynamic x3

            var x4 <- ((x1 ... x2) == "abc") and (x2 == "def") or (x1 == "ghi")
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_from_expression"))

    def test_type_inference_in_array(self):
        inp = """
        func main() begin
            dynamic x
            dynamic y
            number arr[2] <- [x, y]
            number z <- x + y
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_in_array_0"))

        inp = """
        func main() begin
            dynamic x
            dynamic y
            number arr[2, 2] <- [x, y]
            number x1[2] <- x
            number y1[2] <- y
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_in_array_1"))

        inp = """
        func main() begin
            dynamic x
            var y <- [x]
        end
        """
        expect = str(TypeCannotBeInferred(VarDecl(Id('y'), None, 'var', ArrayLiteral([Id('x')]))))
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_in_array_2"))

        inp = """
        func main() begin
            dynamic x1
            dynamic x2
            dynamic x3
            var y <- [[1, x1], [2, x2], [3, x3]]
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_in_array_3"))

        inp = """
        func main() begin 
            dynamic x
            dynamic y <- [[1], x]
        end
        """
        expect = str(TypeCannotBeInferred(VarDecl(Id('y'), None, 'dynamic', ArrayLiteral([ArrayLiteral([NumberLiteral(1.0)]), Id('x')]))))
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_in_array_4"))

        inp = """
        func f(number x, number y, number z)
        func main() begin
            dynamic x
            dynamic y 
            dynamic z
            number arr[10] <- [f(x, y, z), x, y, z]
            number sum <- f(x, y, z) + x + y + z
        end
        func f(number a, number b, number c) return a + b + c
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_in_array_5"))

    def test_hardcore(self):
        inp = """
        func f() return 1

        func g(number x, number y[100]) begin
            dynamic i
            for i until i >= 100 by f() begin
                i <- i + f() * x
            end
            
            dynamic z
            if (i > 100)
                return i + 1
            elif (z and (i = f() * x) or ("abc" == "abc"))
                return i + 2
            return i
        end 

        func main() begin
            number x[100]
            dynamic t <- g(1, x)
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "hardcore_test_0"))

    def _test_single_tc(self):
        inp = """
        """
        expect = str(TypeMismatchInStatement(Return(BinaryOp('+', Id('a'), NumberLiteral(1.0)))))
        self.assertTrue(TestChecker.test(inp, expect, "test"))

    def test_type_inference_inside_scope(self):
        inp = """
        func main() begin
            dynamic x
            begin
                x <- 1
                dynamic x
                x <- true
            end
            dynamic y <- not x
        end
        """
        expect = str(TypeMismatchInExpression(UnaryOp('not', Id('x'))))
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_inside_scope_0"))

        inp = """
        func f(number x, bool y, string z) return
        func main() begin
            dynamic x
            dynamic y
            dynamic z
            begin
                dynamic x
                dynamic y
                f(x, y, z)
            end
            ## z is string, x and y is not type-determined
            x <- 1
            y <- "abc"
            var g <- ((y ... z) == z) and (x = 1)
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "type_inference_inside_scope_1"))

    def test_builtin_fn_return_type(self):
        inp = """
        number x <- readNumber()
        bool y <- readBool()
        string z <- readString()

        func main() begin
            writeNumber(x)
            writeBool(y)
            writeString(z)
        end
        """
        expect = ""
        self.assertTrue(TestChecker.test(inp, expect, "test_builtin_fn_0"))

        inp = """
        func f() return readNumber()

        func main() begin
            return writeNumber()
        end
        """
        expect = str(TypeMismatchInExpression(CallExpr(Id('writeNumber'), [])))
        self.assertTrue(TestChecker.test(inp, expect, "test_builtin_fn_1"))

    def test_single_tc(self):
        inp = """
        func main() begin
            dynamic x
            number x1
            number x2
            number x3
            dynamic y
            y <- [[[1, 2], x, [x1, x2 , x3]]]
        end
        """
        arr_lit = ArrayLiteral([ArrayLiteral([ArrayLiteral([NumberLiteral(1.0),
                                                            NumberLiteral(2.0)]), Id('x'),
                                              ArrayLiteral([Id('x1'), Id('x2'), Id('x3')])])])
        expect = str(TypeCannotBeInferred(Assign(Id('y'), arr_lit)))
        self.assertTrue(TestChecker.test(inp, expect, "array_type_inference_6"))
