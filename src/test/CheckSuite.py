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
            begin
                break
            end
        end
        """
        expect = str(MustInLoop(Break()))
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_4"))

        inp = """
        func main() begin
            begin
                continue
            end
        end
        """
        expect = str(MustInLoop(Continue()))
        self.assertTrue(TestChecker.test(inp, expect, "must_in_loop_5"))

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

    def test_type_mismatch_in_stateemnt(self):
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

            ## ensure that x is inferred as number
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

            ## ensure that x is inferred as number
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
