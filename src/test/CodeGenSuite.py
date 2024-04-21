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


    def test_single_tc(self):
        inp = """
        dynamic x
        dynamic y
        dynamic z
        number a[2, 2, 2] <- [[[x, y], z], [[x, y], [x, y]]]
        func main() return
        """
        expect = [['x', NumberType()], ['y', NumberType()], ['z', ArrayType([2.0], NumberType())], ['a', ArrayType([2.0, 2.0, 2.0], NumberType())]]
        self.check_codegen_var_type_infernece(inp, expect, "codegen_type_inference_17")
