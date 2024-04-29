import unittest
from CodeGenerator import TypeInferenceVisitor
from StaticError import *
from antlr4 import *
from TestUtils import TestCodeGen
from ASTGeneration import ASTGeneration
from ZCodeLexer import ZCodeLexer as Lexer
from ZCodeParser import ZCodeParser as Parser
from lexererr import *
from ASTGeneration import ASTGeneration
from AST import *
from TestUtils import TestUtil
import os

class CheckCodeGenSuite(unittest.TestCase):
    def check_codegen_var_type_infernece(self, inp, expect, num):
        inputfile = TestUtil.makeSource(inp, num)
        lexer = Lexer(inputfile)
        tokens = CommonTokenStream(lexer)
        parser = Parser(tokens)
        tree = parser.program()
        asttree = ASTGeneration().visit(tree)
        typeInference = TypeInferenceVisitor(asttree)
        types, fnTypes = typeInference.infer()

        for pair in types:
            pair[1] = str(pair[1])

        for pair in expect:
            pair[1] = str(pair[1])
        
        self.assertTrue(str(expect) == str(types))

    def _test_codegen_type_inference(self):
        inp = """
        var x <- 1
        func main() begin
            var y <- true
        end
        """
        expect = [['x', NumberType()], ['y', BoolType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_0")

        inp = """
        dynamic x
        dynamic y
        func main() begin
            y <- 2
            x <- 1
            var z <- x
        end
        """
        expect = [['x', NumberType()], ['y', NumberType()], ['z', NumberType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_1")

        inp = """
        dynamic x
        func main() begin
            x <- [1, 2, 3, 4, 5]
            dynamic y
            begin
                y <- 1
            end
        end
        """
        expect = [['x', ArrayType([5.0], NumberType())], ['y', NumberType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_2")

        inp = """
        dynamic x
        func f() return x + 1
        func main() begin
            dynamic x
            if (x) return
        end
        """
        expect = [['x', NumberType()], ['x', BoolType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_3")

        inp = """
        dynamic x
        func f() return 1
        func g() return false
        func main() begin
            x <- f()
            dynamic y
            dynamic z
            begin
                z <- x
                y <- g()
            end
        end
        var y <- f() * f()
        """
        expect = [['x', NumberType()], ['y', BoolType()], ['z', NumberType()], ['y', NumberType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_4")

        inp = """
        func f(number x, bool y, string z, number g[1, 2]) return
        dynamic x
        func main() begin
            dynamic y
            dynamic z
            begin
                dynamic g
                f(x, y, z, g)
            end
        end
        """
        expect = [['x', NumberType()], ['y', BoolType()], ['z', StringType()], ['g', ArrayType([1.0, 2.0], NumberType())]]
        expect += expect
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_5")

        inp = """
        dynamic x
        func f(string s) begin
            return s
            return x
        end
        
        func main() return
        """
        expect = [['x', StringType()], ['s', StringType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_6")

        inp = """
        dynamic x
        func main() begin
            dynamic y <- 1
            x <- y
        end
        """
        expect = [['x', NumberType()], ['y', NumberType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_7")

        inp = """
        func f() return 1
        dynamic x <- f()
        func main() return
        """
        expect = [['x', NumberType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_8")

        inp = """
        func f() return [[1, 2], [3, 4]]
        dynamic x <- f()
        func main() return
        """
        expect = [['x', ArrayType([2.0, 2.0], NumberType())]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_9")

        inp = """
        func f() return [["abc", "def" ... "ghi"], ["abc", "a"]]
        dynamic x <- f()
        dynamic y <- x[1, 1]
        func main() return
        """
        expect = [['x', ArrayType([2.0, 2.0], StringType())],['y', StringType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_10")

        inp = """
        func f() return [[1 + 2 = 1, "abc" == "abc"], [true, false]]
        var x <- f()
        dynamic y <- x[1, 1]
        func main() return
        """
        expect = [['x', ArrayType([2.0, 2.0], BoolType())], ['y', BoolType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_11")

        inp = """
        func f(number x, bool y, string z) return x
        var x <- f(1, true, "abc")
        func main() begin
            dynamic y
            dynamic z
            dynamic z1 <- f(x, y, z)
        end
        """
        expect = [['x', NumberType()], ['y', BoolType()], ['z', StringType()], ['x', NumberType()], ['y', BoolType()], ['z', StringType()], ['z1', NumberType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_12")

        inp = """
        func f() return [[1, 2], [3, 4]]
        var x <- f()[0, 1]
        func main() return
        """
        expect = [['x', NumberType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_13")

        inp = """
        func f() return [[1, 2], [3, 4]]
        func main() begin
            dynamic x
            x <- f()[0]
        end
        """
        expect = [['x', NumberType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_14")

        inp = """
        func f() return [[1, 2], [3, 4]]
        func g() return [true, false]
        func main() begin
            dynamic x
            begin
                dynamic x
                x <- f()[0, 1]
            end
            x <- g()[0]
        end
        """
        expect = [['x', BoolType()], ['x', NumberType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_15")

        inp = """
        func f1() return 1
        func f2() return true
        func f3() return "abc"
        dynamic x
        func main() begin
            begin
                dynamic x
                begin
                    dynamic x
                    x <- f3()
                end
                x <- f2()
            end
            x <- f1()
        end
        """
        expect = [['x', NumberType()], ['x', BoolType()], ['x', StringType()]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_16")

        inp = """
        dynamic x
        dynamic y
        dynamic z
        number a[3] <- [x, y, z]
        func main() return
        """
        expect = [['x', NumberType()], ['y', NumberType()], ['z', NumberType()], ['a', ArrayType([3.0], NumberType())]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_17")

        inp = """
        dynamic x
        dynamic y
        dynamic z
        number a[2, 2, 2] <- [[[x, y], z], [[x, y], [x, y]]]
        func main() return
        """
        expect = [['x', NumberType()], ['y', NumberType()], ['z', ArrayType([2.0], NumberType())], ['a', ArrayType([2.0, 2.0, 2.0], NumberType())]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_18")

    def _test_simple_codegen(self):
        inp = """
        func main() return
        """
        expect = ""
        self.assertTrue(TestCodeGen.test(inp, expect, "__test_simple_codegen"))

    def _test_global_declaration(self):
        inp = """
        var x <- 1
        func main() return
        """
        expect = ""
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_global_decl_0"))

    def _test_simple_fn_call(self):
        inp = """
        func main() begin
            writeNumber(1)
            writeBool(true)
            writeString("abc")
        end
        """
        expect = "1.0trueabc"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_simple_fn_call"))
    
    def _test_var_decl(self):
        inp = """
        var x <- 1
        func main() begin
            var y <- true
            var z <- "abc"
            writeNumber(x)
            writeBool(y)
            writeString(z)
        end
        """
        expect = "1.0trueabc"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen__test_var_decl"))

        inp = """
        func main() begin
            var x <- 1
            begin
                var x <- true
                begin
                    var x <- "abc7"
                    writeString(x)
                end
                writeBool(x)
            end
            writeNumber(x)
        end
        """
        expect = "abc7true1.0"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen__test_var_decl_2"))

    def _test_func_decl(self):
        inp = """
        number x

        func f() begin
            x <- 1
        end

        func main() begin
            f()
            writeNumber(x)
        end
        """
        expect = "1.0"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_test_func_decl_1"))

        inp = """
        func f(number x) return x
        func main() begin
            var x <- f(1)
            writeNumber(x)
        end
        """
        expect = "1.0"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_test_func_decl_2"))

    def _test_assignment(self):
        inp = """
        func main() begin
            dynamic x
            begin
                dynamic x
                begin
                    dynamic x
                    x <- 1
                    writeNumber(x)
                end
                x <- true
                writeBool(x)
            end
            x <- "abc"
            writeString(x)
        end
        """
        expect = "1.0trueabc"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen__test_assignment_0"))

    def _test_unary_expr(self):
        inp = """
        func main() begin
            dynamic x
            begin
                dynamic x
                begin
                    dynamic x
                    x <- not true
                    writeBool(x)
                end
                x <- not false
                writeBool(x)
            end
            x <- -1
            writeNumber(x)
        end
        """
        expect = "falsetrue-1.0"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen__test_simple_unary_0"))

    def _test_relational_expr(self):
        inp = """
        func main() begin
            var x <- 1 + 1
            writeNumber(x)
            x <- 1 - 1
            writeNumber(x)
            x <- 2 * 3
            writeNumber(x)
            x <- 6 / (-2)
            writeNumber(x)
        end
        """
        expect = "2.00.06.0-3.0"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_test_simple_arithmetic_0"))

        inp = """
        func main() begin
            dynamic x
            x <- 1 = 1
            writeBool(x)
            x <- 2 < 3
            writeBool(x)
            x <- 2 <= 3
            writeBool(x)
            x <- 2 >= 1
            writeBool(x)
            x <- 2 != 1
            writeBool(x)
            x <- 2 >= 2
            writeBool(x)
            x <- 2 <= 2
            writeBool(x)
            x <- "abc" == "abc"
            writeBool(x)
        end
        """
        expect = "true" * 8
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_test_simple_relational_expr"))

        inp = """
        func main() begin
            dynamic x
            x <- 2 > 3
            writeBool(x)
            x <- 3 < 2
            writeBool(x)
            x <- 1 != 1
            writeBool(x)
            x <- 2 = 1
            writeBool(x)
            x <- 3 <= 2
            writeBool(x)
            x <- 2 >= 3
            writeBool(x)
            x <- 1 > 1
            writeBool(x)
            x <- "abc" == "ab"
            writeBool(x)
        end
        """
        expect = "false" * 8
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_test_simple_relational_expr_2"))
    
    def _test_arithmetic_expr(self):
        inp = """
        func main() begin
            dynamic x
            x <- 3.3 - 2.3
            writeNumber(x)
            x <- -1.0 + 2.0
            writeNumber(x)
            x <- 0.5 * 2
            writeNumber(x)
            x <- 3 / 3
            writeNumber(x)
            x <- 5 % 4
            writeNumber(x)
        end
        """
        expect = "1.0" * 5
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_test_simple_arithmetic"))

        inp = """
        func main() begin
            dynamic x
            x <- (10 * 3) - (4 / 2)
            writeNumber(x)
            x <- (12 + 8) / 2 * 5
            writeNumber(x)
            x <- (7 + 2) * (4 - 1) 
            writeNumber(x)
            x <- 15 - (4 * 2) + 6
            writeNumber(x)
            x <- (10 * (6 - 3)) / 2
            writeNumber(x)
        end
        """
        expect = "28.0" + "50.0" + "27.0" + "13.0" + "15.0"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_test_simple_arithmetic_2"))

    def _test_bool_expr(self):
        inp = """
        func main() begin
            var x <- true and true
            writeBool(x)
            x <- true and false
            writeBool(x)
            x <- false and true
            writeBool(x)
            x <- false and false
            writeBool(x)

            x <- true or true
            writeBool(x)
            x <- true or false
            writeBool(x)
            x <- false or true
            writeBool(x)
            x <- false or false
            writeBool(x)
        end
        """
        expect = "true" + "false" * 3 + "true" * 3 + "false"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_bool_expr_0"))

        inp = """
        func main() begin
            var x <- false and false and true
            writeBool(x)
            x <- true and false and true
            writeBool(x)
            x <- true and true and true
            writeBool(x)
            x <- false and false and false
            writeBool(x)

            x <- true or false or false
            writeBool(x)
            x <- false or true or false
            writeBool(x)
            x <- false or false or true
            writeBool(x)
            x <- false or false or false
            writeBool(x)
        end
        """
        expect = "falsefalsetruefalse" + "truetruetruefalse"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_bool_expr_1"))

        inp = """
        number x

        func f(number _x, bool Ret)

        bool y <- f(1.0, true) and f(2.0, false) and f(3.0, true) or f(4.0, false) or f(5.0, false) and f(6.0, false)

        func main() begin
            writeBool(y)
            writeNumber(x)
        end

        func f(number _x, bool Ret) begin
            x <- _x
            return Ret
        end
        """
        expect = "false5.0"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_bool_expr_2"))

    def _test_branch_stmt(self):
        inp = """
        func main() begin
            if (true) begin
                writeString("hello")
            end
        end
        """
        expect = "hello"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_branch_stmt"))

        inp = """
        func main() begin
            if (false) begin
                writeString("hello")
            end
            else begin
                writeString("world")
            end
        end
        """
        expect = "world"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_branch_stmt_2"))

        inp = """
        func main() begin
            if (false)
                writeString("hello")
            elif (1 <= 2)
                writeString("world")
        end
        """
        expect = "world"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_branch_stmt_3"))

        inp = """
        func main() begin
            if (true and false and true)
                writeString("hello")
            elif (false or false or true)
                writeString("world")
        end
        """
        expect = "world"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_branch_stmt_4"))

        inp = """
        func main() begin
            if (false or false or false)
                writeString("hello")
            elif (true and true and false)
                writeString("world")
            else
                writeString("...")
        end
        """
        expect = "..."
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_branch_stmt_5"))

    def _test_concat(self):
        inp = """
        func firstName() return "Harry "
        func lastName() return "Potter"
        func main() begin
            writeString((firstName() ... lastName()) ... ".")
        end
        """
        expect = "Harry Potter."
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen__test_concat"))

    def _test_array(self):
        inp = """
        func main() begin
            dynamic x
            x <- [[1, 2], [3, 4]]
            writeNumber(x[0, 1])
            writeNumber(x[1, 1])
        end
        """
        expect = "2.04.0"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen__test_array_1"))

        inp = """
        func main() begin
            dynamic x
            dynamic y
            x <- [[true, y], [y, true]]
            writeBool(x[0, 1])
            writeBool(x[1, 1])
        end
        """
        expect = "falsetrue"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen__test_array_2"))

        inp = """
        func main() begin
            dynamic x
            x <- [[["a"], ["b"]]]
            writeString(x[0, 1, 0])
        end
        """
        expect = "b"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen__test_array_3"))

        inp = """
        number x[3, 3, 3]
        func main() begin
            writeNumber(x[0, 1, 1])
            writeNumber(x[1, 0, 1])
            writeNumber(x[2, 2, 2])
        end
        """
        expect = "0.0" * 3
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen__test_array_4"))

        inp = """
        string s[3, 3, 3]
        func main() begin
            writeString(s[0, 1, 1])
            writeString(s[1, 0, 1])
            writeString(s[2, 2, 2])
        end
        """
        expect = ""
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen__test_array_5"))

    def test_array_item_assignment(self):
        inp = """
        func main() begin
            bool x[1, 2, 3]
            x[0, 1, 1] <- false and false and false or false or false or true and true
            writeBool(x[0, 1, 1])
            writeBool(x[0, 1, 2])
        end
        """
        expect = "truefalse"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_arr_item_assignment_0"))

        inp = """
        func main() begin
            string names[3] <- ["hArry", "Ron", "Hermione"]
            names[0] <- "Harry" ... " Potter"
            writeString("Harry Potter")
        end
        """
        expect = "Harry Potter"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_arr_item_assignment_1"))

        inp = """
        func main() begin
            string s[2, 2] <- [["a", "b"], ["c", "d"]]
            s[0, 0] <- "A"
            s[0, 1] <- "B"
            s[1, 0] <- s[0, 0] ... s[0, 1]
            writeString(s[1, 0])
        end
        """
        expect = "AB"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_arr_item_assignment_2"))

        inp = """
        number s[2, 2] <- [[1, 2 + 3 * (-5)], [3, 4]]
        func f()
        func main() begin
            dynamic x <- f()
            writeNumber(x)
            s[0, 0] <- s[1, 1] % s[0, 1] + 100
            writeNumber(f())
        end
        func f() return s[0, 0]
        """
        expect = "1.0" + "100.0"
        self.assertTrue(TestCodeGen.test(inp, expect, "codegen_arr_item_assignment_3"))

    def test_single_tc(self):
        pass
