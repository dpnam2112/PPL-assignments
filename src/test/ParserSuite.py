# Student's name: Nam Do Phuong
# Student's id: 2114111

import unittest
from TestUtils import TestParser

class ParserSuite(unittest.TestCase):
    def test_function_declaration(self):
        function_decl = """
        func f()

        func g() begin
            print("Hello world")
        end

        func h()
        begin
            print("Hello world")
        end

        func foo(number x, string y, number z[100, 10, 10])
        begin
            return 123
        end

        func bar(number x, number y) return x + y

        func f()
        begin
            print("Hello world")
        end

        func f() begin
        end

        func f()

            return 1


        func g()


            ## hello world
        begin
            return 1
        end
        """
        self.assertTrue(TestParser.test(function_decl, "successful", "simple_func_declarations"))

        func_decl_syntax_err_0 = """
        func f(x)
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_0, "successful", "func_decl_syntax_err_0"))

        func_decl_syntax_err_1 = """
        func f(number x, y)
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_1, "successful", "func_decl_syntax_err_1"))

        func_decl_syntax_err_2 = """
        func f(var x)
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_2, "successful", "func_decl_syntax_err_2"))

        func_decl_syntax_err_3 = """
        func f(number x, var y)
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_3, "successful", "func_decl_syntax_err_3"))

        func_decl_syntax_err_4 = """
        func f(dynamic x)
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_4, "successful", "func_decl_syntax_err_4"))

        func_decl_syntax_err_5 = """
        func f(number x, dynamic y)
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_5, "successful", "func_decl_syntax_err_5"))

        func_decl_syntax_err_6 = """
        func f(number x[100], number y[])
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_6, "successful", "func_decl_syntax_err_6"))

        func_decl_syntax_err_7 = """
        func f(number x[100, true])
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_7, "successful", "func_decl_syntax_err_7"))

        func_decl_syntax_err_8 = """
        func f(number x[100, 2, true])
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_8, "successful", "func_decl_syntax_err_8"))

        func_decl_syntax_err_9 = """
        func f(number x[10, 2, a])
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_9, "successful", "func_decl_syntax_err_9"))

        func_decl_syntax_err_10 = """
        func f(number x[100], number y[1,2,])
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_10, "successful", "func_decl_syntax_err_10"))

        func_decl_syntax_err_11 = """
        func f(number x, number y) print(x + y)
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_11, "successful", "func_decl_syntax_err_11"))

        func_decl_syntax_err_12 = """
        func f(number x, number y print(x + y)
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_12, "successful", "func_decl_syntax_err_12"))

        func_decl_syntax_err_13 = """
        func f(number x, number y, z)
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_13, "successful", "func_decl_syntax_err_13"))

        func_decl_syntax_err_14 = """
        func f(number x, number y, number z[100, 10)
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_14, "successful", "func_decl_syntax_err_14"))

        func_decl_syntax_err_15 = """
        func f(number x, number y, number z[100)
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_15, "successful", "func_decl_syntax_err_15"))

        func_decl_syntax_err_16 = """
        func f(number bool, number y, number z[100])
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_16, "successful", "func_decl_syntax_err_16"))

        func_decl_syntax_err_17 = """
        func f(number string, number y, number z[100])
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_17, "successful", "func_decl_syntax_err_17"))

        func_decl_syntax_err_18 = """
        func f(number string, number y, number z[100], )
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_18, "successful", "func_decl_syntax_err_18"))

        func_decl_syntax_err_19 = """
        funC f(number string, number y, number z[100])
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_19, "successful", "func_decl_syntax_err_19"))

        func_decl_syntax_err_20 = """
        func 123(number string)
        """
        self.assertFalse(TestParser.test(func_decl_syntax_err_20, "successful", "func_decl_syntax_err_20"))

        variable_decl_outside_func_body = """
        func main()
        begin
            print("Hello world")
        end

        var x <- 1
        """
        self.assertTrue(TestParser.test(variable_decl_outside_func_body, "successful", "variable_decl_outside_func_body"))

        ifstmt_outside_func_body = """
        func main()
        begin
        end

        if (x > 10) print("Hello world")

        func g()
        """
        self.assertFalse(TestParser.test(ifstmt_outside_func_body, "successful", "ifstmt_outside_func_body"))

    def test_variable_declaration(self):

        invalid_var_decl = """
        func main()
        begin
            var x


        end
        """
        self.assertFalse(TestParser.test(invalid_var_decl, "successful", "invalid_decl_with_var"))

        valid_dynamic_decl = """
        func main()
        begin
            dynamic x


        end
        """
        self.assertTrue(TestParser.test(valid_dynamic_decl, "successful", "valid_dynamic_decl"))

        valid_arr_decl = """
        func main()
        begin
            number matrix[1,2,3]
            number matrix[10] <- [1 + 2 * (5 - 8 * 3 + 1), 1e5 - 3e4 * 3.45e3 * f(), 1, 2, 3]
            bool matrix[10] <- [true, false, false and f(), "abc" == "abc", "false and (false or true) and false"]
        end
        """
        self.assertTrue(TestParser.test(valid_arr_decl, "successful", "valid_arr_dim"))

        invalid_arr_decl = """
        var x[1, 2, 3] <- [1, 2, 3]
        """
        self.assertFalse(TestParser.test(invalid_arr_decl, "successful", "invalid_arr_decl"))

        invalid_arr_decl_2 = """
        number x["abc", "def", 2] <- [1, 2, 3]
        """
        self.assertFalse(TestParser.test(invalid_arr_decl_2, "successful", "invalid_arr_decl_2"))

        invalid_arr_decl_3 = """
        dynamic x[1, 2, 3] <- [1, 2, 3]
        """
        self.assertFalse(TestParser.test(invalid_arr_decl_3, "successful", "invalid_arr_decl_3"))

        multidim_arr_decl = """
        func main()
        begin
            number matrix[2,3] <- [[1,2,3], [1,2,3]]
        end
        """
        self.assertTrue(TestParser.test(multidim_arr_decl, "successful", "multidim_arr_decl"))

        variable_decl = """
        func main()
        begin
            var x <- 1
            number y <- 23
            string z <- "Hello world"
            string z_ <- "'\"Hello world'\""
            number y[10] <- [1,2,3,4,5]
            number matrix[4, 3]
            string names[10] <- ["Harry", "Ron", "Hermione", "Fred"]
            dynamic x <- 2 * 3 - 1 + 4
            bool __is_true__ <- true
            string my_name_is <- "Na" ... "m"
        end
        """
        self.assertTrue(TestParser.test(variable_decl, "successful", "simple_var_decl"))

        variable_decl_2 = """
        var x <- 1
        dynamic y <- 1 + 2.3 * 3E5
        number x <- f(1, 2)
        bool x <- true and false or f(1, 2)
        """
        self.assertTrue(TestParser.test(variable_decl, "successful", "simple_var_decl_2"))

        dynamic_with_dimensions = """
        func main()
        begin
            dynamic x[1,2] <- [1,2,3,4,5]
        end
        """
        self.assertFalse(TestParser.test(dynamic_with_dimensions, "successful",
                                        "dynamic_with_dimensions"))

        var_with_dimensions = """
        func main()
        begin
            var x[1,2] <- [1,2,3,4,5]
        end
        """
        self.assertFalse(TestParser.test(var_with_dimensions, "successful",
                                        "var_with_dimensions"))
        
        decl_at_top_level_code = """
        var x <- 1
        number x[10] <- [1,2,3,4,5,6,7]

        func main()
        begin

        end

        bool a <- true
        bool b
        bool c

        string x
        string y
        string z

        string z[10]

        dynamic z
        """


    def test_expression(self):
        string_concat = """
        func main()
        begin
            var x <- "abc" ... "abc"
            var y <- ("abc" ... "abc") ... "abc"
            var z <- "abc" ... ("abc" ... "abc")
            var z <- (f() ... (g() ... (h() ... y))) ... "abc"
        end
        """
        self.assertTrue(TestParser.test(string_concat, "successful", "string_concat"))

        invalid_str_concat_1 = """
        func main()
        begin
            var x <- "abc" ... "abc" ... "abc"
        end
        """
        self.assertFalse(TestParser.test(invalid_str_concat_1, "successful", "invalid_str_concat_1"))

        invalid_str_concat_2 = """
        func main()
        begin
            var x <- abc ... ("abc" ... "abc" ... "abc")
        end
        """
        self.assertFalse(TestParser.test(invalid_str_concat_2, "successful", "invalid_str_concat_2"))

        invalid_comparison_1 = """
        func main() begin
            var x <- 1 + 2 > 1 >= 2
        end
        """
        self.assertFalse(TestParser.test(invalid_comparison_1, "successful", "invalid_comparison_1"))

        invalid_comparison_2 = """
        func main()
        begin
            ## comparison operators have no associative property
            var x <- 1 + 2 < 1 <= 2
        end
        """
        self.assertFalse(TestParser.test(invalid_comparison_2, "successful", "invalid_comparison_2"))

        invalid_comparison_3 = """
        func main()
        begin
            var x <- "abc" == "abc" == "def"

        end
        """
        self.assertFalse(TestParser.test(invalid_comparison_3, "successful", "invalid_comparison_3"))

        simple_math = """
        func main()
        begin
            var x <- 1 + 1 + 1 + 1

            var x <- 1 + 1 - 1 + 1 - 1

            var z <- 2e5 * 4 - 1 + 2.4e-3 / 3 % 6

            dynamic x <- -(1 + 1e-3) * 5 - 4 / 6

            var x <- 5 * f() + 4 - g(3) * 6 / 7 + h(3, 2)

            var x <- a[4] * f(3) - a[3] * f(2)

            dynamic x <- a[1,2,3] * g[1, 2] - 4

            var x <- a[i1, (i1 + i2 * 2e1) * 0] * g[i2] - h(1, 2, 3, 4, 5) 

            var x <- 4 - (4 - (4 + 4 * (4 / (f(4, a[4], a[4, 4, 4], b[4,4+4-4+g()])))))
        end
        """

        self.assertTrue(TestParser.test(simple_math, "successful", "simple_math"))

        simple_logical_expr = """
        func main()
        begin
            var x <- (true or false) and true and true
            var x <- not (not true or false and not(false and true)) and false
            var x <- not f() and g or h(1, 2, false)
           var x <- not not not not false
        end
        """
        self.assertTrue(TestParser.test(simple_logical_expr, "successful", "simple_logical_expr"))

        missing_parentheses_0 = """
        func main()
        begin
            var x <- f(
        end
        """
        self.assertFalse(TestParser.test(missing_parentheses_0, "successful", "missing_parentheses_0"))

        missing_parentheses_1 = """
        func main()
        begin
            var x <- (1 + 2 + 3
        end
        """
        self.assertFalse(TestParser.test(missing_parentheses_1, "successful", "missing_parentheses_1"))

        missing_parentheses_2 = """
        func main()
        begin
            var x <- 1e3 + 5 / 6 + ( 123 -  11 / (1 + 5 - 6)
        end
        """
        self.assertFalse(TestParser.test(missing_parentheses_2, "successful", "missing_parentheses_2"))

        missing_parentheses_3 = """
        func main()
        begin
            var x <- 1e3 + 5 / 6 + ( 123 -  11 / (1 + 5 - 6)
        end
        """
        self.assertFalse(TestParser.test(missing_parentheses_2, "successful", "missing_parentheses_2"))

        missing_operator = """
        func main()
        begin
            dynamic x <- 1 +
        end
        """
        self.assertFalse(TestParser.test(missing_operator, "successful", "missing_operator"))

        missing_operator_2 = """
        func main()
        begin
            dynamic x <- 2 + 3 * / 4
        end
        """
        self.assertFalse(TestParser.test(missing_operator_2, "successful", "missing_operator_2"))

        missing_operator_3 = """
        func main()
        begin
            var x <- 2e5 -
        end
        """
        self.assertFalse(TestParser.test(missing_operator_3, "successful", "missing_operator_3"))

        missing_operator_4 = """
        func main()
        begin
            var x <- 2e5[]
        end
        """
        self.assertFalse(TestParser.test(missing_operator_4, "successful", "missing_operator_4"))

        missing_operator_5 = """
        func main()
        begin
            var x <- ... "abc"
        end
        """
        self.assertFalse(TestParser.test(missing_operator_5, "successful", "missing_operator_5"))

        missing_operator_6 = """
        func main()
        begin
            var x <- true and
        end
        """
        self.assertFalse(TestParser.test(missing_operator_6, "successful", "missing_operator_6"))

        missing_operator_7 = """
        func main()
        begin
            var x <- true or
        end
        """
        self.assertFalse(TestParser.test(missing_operator_7, "successful", "missing_operator_7"))

        index_expr_test = """
        func main()
        begin
            var x <- x[1, 2, 3]
            var x <- x[1]
            var x <- f(1,2,3)[1,2,3]
            var x <- f()[1,2,3]
            var x <- f(1)[1]
        end
        """
        self.assertTrue(TestParser.test(index_expr_test, "successful", "index_expr_test"))

    def test_case_sensitivity(self):
        case_sensitivity_test_1 = """
        func main()
        begin
            number Number <- 1
            bool Begin <- true
            bool False <- false
            number eNd <- 100
        end
        """
        self.assertTrue(TestParser.test(case_sensitivity_test_1, "successful", "case_sensitivity_test_1"))

        case_sensitivity_test_2 = """
        func main()
        begin
            number number <- 2
        end
        """
        self.assertFalse(TestParser.test(case_sensitivity_test_2, "successful", "case_sensitivity_test_2"))

        case_sensitivity_test_3 = """
        func main()
        begin
            bool bOOl <- true
        end
        """
        self.assertTrue(TestParser.test(case_sensitivity_test_3, "successful", "case_sensitivity_test_3"))

        case_sensitivity_test_4 = """
        func main()
        begin
            string sTrIng <- "a string"
        end
        """
        self.assertTrue(TestParser.test(case_sensitivity_test_4, "successful", "case_sensitivity_test_4"))

        case_sensitivity_test_5 = """
        func main()
        begin
            bool bool <- true
        end
        """
        self.assertFalse(TestParser.test(case_sensitivity_test_5, "successful", "case_sensitivity_test_5"))

        case_sensitivity_test_6 = """
        func main()
        begin
            string string <- "a string"
        end
        """
        self.assertFalse(TestParser.test(case_sensitivity_test_6, "successful", "case_sensitivity_test_6"))

        case_sensitivity_test_7 = """
        func main()
        begin
            print("Hello world")
        enD
        """
        self.assertFalse(TestParser.test(case_sensitivity_test_7, "successful", "case_sensitivity_test_7"))

        case_sensitivity_test_8 = """
        func main()
        bEgin
            print("Hello world")
        end
        """
        self.assertFalse(TestParser.test(case_sensitivity_test_8, "successful", "case_sensitivity_test_8"))

    def test_assignment(self):
        assignment = """
        func main()
        begin
            ## simple assignment statements
            x <-  1 + 2 + 3

            number y[10]
            number z[2, 3]

            y[5] <- 10

            y[6] <-  11

            y[7] <- y[5] + y[6]

            y[x + 3] <- 1 + 2

            y[y[5]] <- 4 + 5 * 3 / 2 % 1

            y[y[4] * 3 - 2] <- 4 *4 * 4 

            z[0, 0] <- 1
            z[1, 0] <- 2
            z[2, 1] <- 34 * 55 - (1 - (2 + 3 * (3 + 4)))
            z[4, 4] <- 1111
        end
        """
        self.assertTrue(TestParser.test(assignment, "successful", "simple_assignment"))

        asgn_syntax_err_0 = """
        func main()
        begin
            x <-

        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_0, "successful", "asgn_syntax_err_0"))

        asgn_syntax_err_1 = """
        func main()
        begin
            x[] <- 100

        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_1, "successful", "asgn_syntax_err_1"))

        asgn_syntax_err_2 = """
        func main()
        begin
            x[1, 2] <- 

        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_2, "successful", "asgn_syntax_err_2"))

        asgn_syntax_err_3 = """
        func main()
        begin
            x[1,2,3] <-
                123
        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_3, "successful", "asgn_syntax_err_3"))

        asgn_syntax_err_4 = """
        func main()
        begin
            x <-
                123
        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_4, "successful", "asgn_syntax_err_4"))

        asgn_syntax_err_5 = """
        func main()
        begin
            5 <- 1 + 2
        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_5, "successful", "asgn_syntax_err_5"))

        asgn_syntax_err_6 = """
        func main()
        begin
            "abc" <- "abc" ... "abc"
        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_6, "successful", "asgn_syntax_err_6"))

        asgn_syntax_err_7 = """
        func main()
        begin
            false <- false and false and f()
        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_7, "successful", "asgn_syntax_err_7"))

        asgn_syntax_err_8 = """
        func main()
        begin
            true <- false and false and f()
        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_8, "successful", "asgn_syntax_err_8"))

        asgn_syntax_err_9 = """
        func main()
        begin
            f() <- false and false and false
        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_9, "successful", "asgn_syntax_err_9"))

        asgn_syntax_err_10 = """
        func main()
        begin
            a[1,2,3,] <- false and false
        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_10, "successful", "asgn_syntax_err_10"))

        asgn_syntax_err_11 = """
        func main()
        begin
            a[ <- false and false
        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_11, "successful", "asgn_syntax_err_11"))

        asgn_syntax_err_12 = """
        func main()
        begin
            a[1] = 1
        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_12, "successful", "asgn_syntax_err_12"))

        asgn_syntax_err_13 = """
        func main()
        begin
            a[1][1] <- 1
        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_13, "successful", "asgn_syntax_err_13"))

        asgn_syntax_err_14 = """
        func main()
        begin
            f()[1] <- 1
        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_14, "successful", "asgn_syntax_err_14"))

        asgn_syntax_err_15 = """
        func main()
        begin
            f(1, 2)[1] <- 1
        end
        """
        self.assertFalse(TestParser.test(asgn_syntax_err_15, "successful", "asgn_syntax_err_15"))

    def test_loop(self):

        simple_loop = """
        func main()
        begin
            for i until f(i, j) > 5 by 5
                print("Hello world")

            ## there can be no newline characters between update expression and body
            for i until f(i, j) > 5 by 5 print("Hello world")

            for i until f(i, j, k) * 5 + 2 < 5 by -5
                print("Hello world")

            for i until a[i] * a[j] < 10 by a[i + 3] * 6
                print("Hello world")

            for i until a[i] * a[j] < 10 by a[i + 3] * 6
                ## the parser should recognize the loop statement if
                ## we put spaces between update expression and body

                print("Hello world")

            for i until (f(i) and (g(i) or h(i))) by (i + 1 + 2 / (3 * 4))
                ## put complex expressions in condition place and update place
                print("Hello world")


            var x <- 1
            var ages <- [1,2,3,4,5]
            var count <- length(age)
            for i until i >= count by 1
            begin
                x <- x + ages[count - i - 1]
                print(x)
            end
        end
        """
        self.assertTrue(TestParser.test(simple_loop, "successful", "simple_loop"))

        loop_syntax_err_1 = """
        func main()
        begin
        for
            i until i > 5 by 1
                print("Hello world")
        end
        """
        self.assertFalse(TestParser.test(loop_syntax_err_1, "successful", "loop_syntax_err_1"))


        loop_syntax_err_2 = """
        func main()
        begin
            for i until
                i > 5 by 1
                    print("Hello world")
        end
        """
        self.assertFalse(TestParser.test(loop_syntax_err_1, "successful", "loop_syntax_err_2"))

        loop_syntax_err_3 = """
        func main()
        begin
            for i until
                i > 5 by
                1
                print("Hello world")
        end
        """
        self.assertFalse(TestParser.test(loop_syntax_err_3, "successful", "loop_syntax_err_3"))

        loop_syntax_err_4 = """
        func main()
        begin
            ## missing loop body
            for i until i > 5 by 1
        end
        """
        self.assertFalse(TestParser.test(loop_syntax_err_4, "successful", "loop_syntax_err_4"))

    def test_if_stmt(self):
        valid_if = """
        func main() begin
            if (x > 1) print(x + 1)

            if (x > 1) print(x + 1)
            elif (x > 2) print(x + 2)
            else print(x)

            if (x > 1) print(x + 1)
            elif (x > 2) print(x + 2)

            if (x > 1) begin
                print(x * 2)
            end
            else begin
                print(x)
            end

            if (x > 1) print(x + 1)
            else print(x)

            if (x > 1) print(x + 1)
            elif (true or false or f() and g(1, 2, 3)) print(x + 2 )
            elif ("abc" == "def") print(x + 3)
            else print(x)
        end
        """
        self.assertTrue(TestParser.test(valid_if, "successful", "valid_if_stmts"))

        if_stmt_newline_test = """
        func main()
        begin
            if (1 = 1)
                print("Hello world")
            elif (2 = 2)
                print("Hello world")
            else
                print("Hello world")

            if (1 = 1)

                print("Hello world")
            elif (2 = 2)


                print("Hello world")
            else



                print("Hello world")
        end
        """
        self.assertTrue(TestParser.test(if_stmt_newline_test, "successful", "if_stmt_newline_test"))

        if_stmt_syntax_err = """
        func main()
        begin
            if
                (x > 2) print("Hello world")
        end
        """
        self.assertFalse(TestParser.test(if_stmt_syntax_err, "successful", "if_stmt_syntax_err"))

        if_stmt_syntax_err_2 = """
        func main()
        begin
            if (x > 2) print("Hello world")
            elif
                (x > 2) print("Hello world")
        end
        """
        self.assertFalse(TestParser.test(if_stmt_syntax_err_2, "successful", "if_stmt_syntax_err_2"))

        if_stmt_syntax_err_3 = """
        func main()
        begin
            if (x > 2) print("Hello world")
            elif (x > 2) print("Hello world")
            else

        end
        """
        self.assertFalse(TestParser.test(if_stmt_syntax_err_3, "successful", "if_stmt_syntax_err_3"))

        if_stmt_syntax_err_4 = """
        func main()
        begin
            if (x > 2)
        end
        """
        self.assertFalse(TestParser.test(if_stmt_syntax_err_4, "successful", "if_stmt_syntax_err_4"))

        if_stmt_syntax_err_5 = """
        func main()
        begin
            if (x > 2) print("Hello world")
            elif (x > 3)
        end
        """
        self.assertFalse(TestParser.test(if_stmt_syntax_err_5, "successful", "if_stmt_syntax_err_5"))

        if_stmt_syntax_err_6 = """
        func main()
        begin
            if x < 2 print("Hello world")
        end
        """
        self.assertFalse(TestParser.test(if_stmt_syntax_err_6, "successful", "if_stmt_syntax_err_6"))

        if_stmt_syntax_err_7 = """
        func main()
        begin
            if (x < 2) print("Hello \\\\\\n world")
            elif x < 3 print("Hello world")
        end
        """
        self.assertFalse(TestParser.test(if_stmt_syntax_err_7, "successful", "if_stmt_syntax_err_7"))

        if_stmt_syntax_err_8 = """
        func main()
        begin
            if (x < 2 print("Hello world")
            elif (x < 3)

                print("Hello world")
            else
                print("Hello world")
        """
        self.assertFalse(TestParser.test(if_stmt_syntax_err_8, "successful", "if_stmt_syntax_err_8"))

        if_stmt_syntax_err_9 = """
        func main()
        begin
            if (x < 2) print("Hello world")
            elif (x < 3

                print("Hello world")
            else
                print("Hello world")
        """
        self.assertFalse(TestParser.test(if_stmt_syntax_err_9, "successful", "if_stmt_syntax_err_9"))

        if_stmt_syntax_err_10 = """
        func main()
        begin
            if (x < 2) print("Hello world")
            elif (x < 3)

                print("Hello world")
            else
                print("Hello world")
            elif (x < 100)
                print("Hello world")
        """
        self.assertFalse(TestParser.test(if_stmt_syntax_err_10, "successful", "if_stmt_syntax_err_10"))

    def test_comment(self):
        valid_comments_1 = """
        ## these are some simple declarations.
        func f()
        func g(number x, number y)
        """
        self.assertTrue(TestParser.test(valid_comments_1, "successful", "valid_comments_1"))

        comment_ends_with_eof = """
        func main()
        begin
            ## print out 'hello world'
            print("Hello world")

            ## print out 'hello'
            print("Hello")
        end
        ## hello world"""
        self.assertTrue(TestParser.test(comment_ends_with_eof, "successful", "comment_ends_with_eof"))

        stmt_and_cmt_in_single_ln = """
        func main() ## comment
        begin

        end
        """
        self.assertTrue(TestParser.test(stmt_and_cmt_in_single_ln , "successful", "stmt_and_cmt_in_single_ln"))

        stmt_and_cmt_in_single_ln_2 = """
        func main()
        begin
            print("hello world")        ## print hello world
        end
        """
        self.assertTrue(TestParser.test(stmt_and_cmt_in_single_ln_2 , "successful", "stmt_and_cmt_in_single_ln_2"))

        stmt_and_cmt_in_single_ln_3 = """
        func main()
        begin
            print("Hello world")
        end ## Hello world
        """
        self.assertTrue(TestParser.test(stmt_and_cmt_in_single_ln_3 , "successful", "stmt_and_cmt_in_single_ln_3 "))

    def test_simple_programs(self):
        prog_1 = """
        func isPrime(number x)

        func main()
            begin
                number x <- readNumber()
                if (isPrime(x)) printString("Yes")
                else printString("No")
            end

        func isPrime(number x)
        ## Check if a number is a prime number
            begin
                if (x <= 1) return false
                var i <- 2
                for i until i > x / 2 by 1
                begin
                    if (x % i = 0) return false
                end
                return true
            end
        """
        self.assertTrue(TestParser.test(prog_1, "successful", "prog_1"))

        prog_2 = """
        func areDivisors(number num1, number num2)
            return ((num1 % num2 = 0) or (num2 % num1 = 0))

        func main()
            begin
                var num1 <- readNumber()
                var num2 <- readNumber()
                if (areDivisors(num1, num2)) printString("Yes")
                else printString("No")
            end
        """
        self.assertTrue(TestParser.test(prog_2, "successful", "prog_2"))

        recursive_fib = """
        func fib(number x)
        begin
            ## compute the xth fibonacci number recursively
            if (x < 2) return x
            return fib(x - 1) + fib(x - 2)
        end

        func main()
        begin
            ## print the 101st fibonacci number
            print(fib(100))
        end
        """
        self.assertTrue(TestParser.test(recursive_fib, "successful", "recursive_fib"))

        loop_fib = """
        func fib(number x) ## function prototype

        func main()
        begin
            print(fib(100))
        end

        ## function definition
        func fib(number x)
        begin
            number prev <- 0
            dynamic curr <- 1
            if (x = 0) return prev
            var i <- 1

            for i until i >= x by 1
            begin
                var temp <- curr
                curr <- curr + prev
                prev <- temp
            end
            return curr
        end
        """
        self.assertTrue(TestParser.test(loop_fib, "successful", "loop_fib"))

        find_sum = """
        ## write a function that returns the sum of all elements in an array.
        ## maximum size: 100
        func sum(number arr[100])
        begin
            number i <- 0
            number _sum <- 0
            for i until i > length(arr) by 1
            begin
                _sum <- _sum + arr[i]
            end
        end
        """
        self.assertTrue(TestParser.test(find_sum, "successful", "find_sum"))

        dot_product = """
        ## compute dot product of two arrays
        func dotProduct(number v1[100], number v2[100])
        begin
            var sum <- 0
            var i <- 0
            for i until i >= 100 by 1
                sum <- sum + v1[i] * v2[i]
            return sum
        end ## end of program"""
        self.assertTrue(TestParser.test(find_sum, "successful", "dot_product"))
