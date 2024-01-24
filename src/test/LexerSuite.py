import unittest
from lexererr import *
from TestUtils import TestLexer

class LexerSuite(unittest.TestCase):
    def testcase_name_getter(self, prefix: str=''):
        # create a testcase name getter that generates a file name for a testcase.
        # generated names have the following form:
        # <prefix>_<test_index>
        # well-formed file names make it easier to check scanner's output for each testcase.

        test_index = 0
        def get_testcase_name():
            nonlocal test_index
            test_index += 1
            return f"{prefix}_{test_index}"
        return get_testcase_name

    def test_simple_string(self):
        """test simple string"""
        tc_name_getter = self.testcase_name_getter(prefix="simplestringtest")
        # "Hello\n world"
        self.assertTrue(TestLexer.test("\"Hello\\n world\"", "Hello\\n world,<EOF>", tc_name_getter()))

        # normal string literal
        self.assertTrue(TestLexer.test("\"Yanxi Palace - 2018\"","Yanxi Palace - 2018,<EOF>",tc_name_getter()))
        self.assertTrue(TestLexer.test("\"\"", ",<EOF>", tc_name_getter()))

    def test_unclosed_string(self):
        tc_name_getter = self.testcase_name_getter(prefix="unclosedstringtest")

        # unclosed strings
        """ 
        "Hello
         world"
        " """
        self.assertTrue(TestLexer.test("\"Hello\n world\"", UncloseString("Hello").message, tc_name_getter()))
        # "'"
        self.assertTrue(TestLexer.test("\"'\"", UncloseString("'\"").message, tc_name_getter()))

        """
        "Hello'"
         world"
        """
        self.assertTrue(TestLexer.test("\"Hello'\"\n world\"", UncloseString("Hello'\"").message, tc_name_getter()))
        self.assertTrue(TestLexer.test("\"Hello'\"'\"\n\n\n\tworld\"", UncloseString("Hello'\"'\"").message, tc_name_getter()))

        # "abc\\ 
        self.assertTrue(TestLexer.test("\"abc\\\\ ", UncloseString("abc\\\\ ").message, tc_name_getter()))

        # "abc'"'"
        self.assertTrue(TestLexer.test("\"abc'\"'\"", UncloseString("abc'\"'\"").message, tc_name_getter()))

        # "Hello \n world '""
        self.assertTrue(TestLexer.test("\"Hello \\n world '\"", UncloseString("Hello \\n world '\"").message, tc_name_getter()))

        # "Hello \\'"
        self.assertTrue(TestLexer.test("\"Hello \\\\'\"", UncloseString("Hello \\\\'\"").message, tc_name_getter()))

    def test_invalid_escape_with_slash(self):
        tc_name_getter = self.testcase_name_getter("testInvalidEscSlash")

        # invalid escape starting with \
        #"Hello\a"
        self.assertTrue(TestLexer.test("\"Hello\\a\"", IllegalEscape("Hello\\a").message, tc_name_getter()))

        # "Hello\q\u"        
        self.assertTrue(TestLexer.test("\"Hello\\q\\u\"", IllegalEscape("Hello\\q").message, tc_name_getter()))

        # "Helloaaa\o\u"        
        self.assertTrue(TestLexer.test("\"Helloaaa\\o\\u\"", IllegalEscape("Helloaaa\\o").message, tc_name_getter()))

        # "Hello \\\m"        
        self.assertTrue(TestLexer.test("\"Hello \\\\\\m\"", IllegalEscape("Hello \\\\\\m").message, tc_name_getter()))

        # "Hello \k"
        self.assertTrue(TestLexer.test("\"Hello\\k\"", IllegalEscape("Hello\\k").message, tc_name_getter()))

        # "Hello \\\"
        self.assertTrue(TestLexer.test("\"Hello \\\\\\\"", IllegalEscape("Hello \\\\\\").message, tc_name_getter()))

        # "Hello \\\ "
        self.assertTrue(TestLexer.test("\"Hello \\\\\\ \"", IllegalEscape("Hello \\\\\\ ").message, tc_name_getter()))

    def test_invalid_escape_with_sg_quote(self):
        tc_name_getter = self.testcase_name_getter("testInvalidEscSgQuote")
        # invalid escape starting with '
        self.assertTrue(TestLexer.test("\"' \"", IllegalEscape("' ").message, tc_name_getter()))
        self.assertTrue(TestLexer.test("\"'t\"", IllegalEscape("'t").message, tc_name_getter()))
        self.assertTrue(TestLexer.test("\"a't\"", IllegalEscape("a't").message, tc_name_getter()))

        # "\\a't"
        self.assertTrue(TestLexer.test("\"\\\\a't\"", IllegalEscape("\\\\a't").message, tc_name_getter()))
        self.assertTrue(TestLexer.test("\"abc 'a\"", IllegalEscape("abc 'a").message, tc_name_getter()))

        # "\'Hello''' "
        self.assertTrue(TestLexer.test("\"\\'Hello''' \"", IllegalEscape("\\'Hello''").message, tc_name_getter()))

        # "Hello \\'t"
        self.assertTrue(TestLexer.test("\"Hello \\\\'t\"", IllegalEscape("Hello \\\\'t").message, tc_name_getter()))
    
    def test_valid_escape(self):
        # valid escape sequence
        tc_name_getter = self.testcase_name_getter("testValidEscape")
        # "\\a"
        self.assertTrue(TestLexer.test("\"\\\\a\"", "\\\\a,<EOF>", tc_name_getter()))

        # "Hello\rWorld\n\b"
        self.assertTrue(TestLexer.test("\"Hello\\rWorld\\n\\b\"", "Hello\\rWorld\\n\\b,<EOF>", tc_name_getter()))

        # "Hello\'world\\ \f"
        self.assertTrue(TestLexer.test("\"Hello\\'World\\\\ \\f\"", "Hello\\'World\\\\ \\f,<EOF>", tc_name_getter()))

        # "\''"Hello world\''""
        self.assertTrue(TestLexer.test("\"\\''\"Hello world\\''\"\"", "\\''\"Hello world\\''\",<EOF>", tc_name_getter()))

        # "Hello \\k"
        self.assertTrue(TestLexer.test("\"Hello\\\\k\"", "Hello\\\\k,<EOF>", tc_name_getter()))

        # "Hello \\m"
        self.assertTrue(TestLexer.test("\"Hello \\\\m\"", "Hello \\\\m,<EOF>", tc_name_getter()))

        # "\\\'Hello world\'"
        self.assertTrue(TestLexer.test("\"\\\\\\'Hello world \\'\"", "\\\\\\'Hello world \\',<EOF>", tc_name_getter()))

        # not-escaped doublequotes
        self.assertTrue(TestLexer.test("\"'\"Hello world\" world", "'\"Hello world,world,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("\"'\"I forgot to escape the right double-quote!\" he said", "'\"I forgot to escape the right double-quote!,he,said,<EOF>", tc_name_getter()))

    def test_keyword(self):
        tc_name_getter = self.testcase_name_getter(prefix="testKeyword")

        self.assertTrue(TestLexer.test("dynamic x", "dynamic,x,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("var x", "var,x,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("for if    \n", "for,if,\n,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("for by until \n\n\t   dynamic x", "for,by,until,\n,\n,dynamic,x,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("true false truefalse falsetrue and andor or,", "true,false,truefalse,falsetrue,and,andor,or,,,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("bool string   number ", "bool,string,number,<EOF>", tc_name_getter()))

    def test_number(self):
        tc_name_getter = self.testcase_name_getter(prefix="testNumber")

        self.assertTrue(TestLexer.test("123", "123,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("0123 456", "0123,456,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("23.12 441E4 11.11e45", "23.12,441E4,11.11e45,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("23.12e12.12", "23.12e12," + ErrorToken(".").message, tc_name_getter()))
        self.assertTrue(TestLexer.test("-23.12e+32", "-,23.12e+32,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("+23.12e-32", "+,23.12e-32,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("+23.12E-32", "+,23.12E-32,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("23.E-1", "23.E-1,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("1.e-1", "1.e-1,<EOF>", tc_name_getter()))

        # a number literal consists of an integer part, an optional decimal part and 
        # an optional exponent part.
        # the integer part must have at least one digit, so the two following cases are invalid.
        self.assertTrue(TestLexer.test("abc .123e13", "abc," + ErrorToken(".").message, tc_name_getter()))
        self.assertTrue(TestLexer.test("abc .1", "abc," + ErrorToken(".").message, tc_name_getter()))

    def test_expression(self):
        tc_name_getter = self.testcase_name_getter(prefix="testExpr")

        self.assertTrue(TestLexer.test("1234567", "1234567,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("1234.567", "1234.567,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("1.1293e12 +  1.23e13 * -13", "1.1293e12,+,1.23e13,*,-,13,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("1.1293 e  -12 + 1.23e13 -8", "1.1293,e,-,12,+,1.23e13,-,8,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("abc % _def() - 23    + ghi12()   >= 584 and 2 ", "abc,%,_def,(,),-,23,+,ghi12,(,),>=,584,and,2,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("abc == _def12(1,2,5) and ghi() <= er12", "abc,==,_def12,(,1,,,2,,,5,),and,ghi,(,),<=,er12,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("1 + 2 < 3 and  \"fdi\" == \"fkkdf\"", "1,+,2,<,3,and,fdi,==,fkkdf,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("foo([1,2,3,4],5) + 8 < 12", "foo,(,[,1,,,2,,,3,,,4,],,,5,),+,8,<,12,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("_foo__([[1],[2]]) != 3", "_foo__,(,[,[,1,],,,[,2,],],),!=,3,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("__12f__ ... __13f__ = __14f__", "__12f__,...,__13f__,=,__14f__,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("a[1] + b[1, 2] + c[1, 3]", "a,[,1,],+,b,[,1,,,2,],+,c,[,1,,,3,],<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("not true", "not,true,<EOF>", tc_name_getter()))

    def test_statement(self):
        tc_name_getter = self.testcase_name_getter(prefix="testStmt")
        # assignment statement
        self.assertTrue(TestLexer.test("var x <- 1\ndynamic x<- 2", "var,x,<-,1,\n,dynamic,x,<-,2,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("bool x[2, 2] <- [[1, 2], [3,4]]", "bool,x,[,2,,,2,],<-,[,[,1,,,2,],,,[,3,,,4,],],<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("number _12y <- 3\nstring _13z <- \"abc\"", "number,_12y,<-,3,\n,string,_13z,<-,abc,<EOF>", tc_name_getter()))

        # branch statement
        self.assertTrue(TestLexer.test("if 1 = 1\n  print(\"abc\") elif 1 = 2\n print(\"def\") else print(123)",
                                       "if,1,=,1,\n,print,(,abc,),elif,1,=,2,\n,print,(,def,),else,print,(,123,),<EOF>"
                                       , tc_name_getter()))

        # loop statement
        self.assertTrue(TestLexer.test("for i until i > 10 by 2\n   f(i)", "for,i,until,i,>,10,by,2,\n,f,(,i,),<EOF>", tc_name_getter()))

        # block statement
        self.assertTrue(TestLexer.test("begin\nf(1,2,3)\ng(4,5,6)\nend\n", "begin,\n,f,(,1,,,2,,,3,),\n,g,(,4,,,5,,,6,),\n,end,\n,<EOF>", tc_name_getter()))

    def test_invalid_character(self):
        tc_name_getter = self.testcase_name_getter(prefix="testInvalidChar")

        self.assertTrue(TestLexer.test(";;;", ErrorToken(";").message, tc_name_getter()))
        self.assertTrue(TestLexer.test("abc__123;", "abc__123," + ErrorToken(";").message, tc_name_getter()))
        self.assertTrue(TestLexer.test("# hello world", ErrorToken("#").message, tc_name_getter()))
        self.assertTrue(TestLexer.test("abc__123 + 123 ;", "abc__123,+,123," + ErrorToken(";").message, tc_name_getter()))
        self.assertTrue(TestLexer.test("abc__123 && + 123 ;", "abc__123," + ErrorToken("&").message, tc_name_getter()))
        self.assertTrue(TestLexer.test("a and !b", "a,and," + ErrorToken("!").message, tc_name_getter()))

        """ "Hello \\"'" """
        self.assertTrue(TestLexer.test("\"Hello \\\\\"'\"", "Hello \\\\," + ErrorToken("'").message, tc_name_getter()))


    def _test_comment(self):
        tc_name_getter = self.testcase_name_getter(prefix="testComment")

        self.assertTrue(TestLexer.test("123 + 456\n##hello world\n", "123,+,456,\n,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("123 + 456\n##hello world", "123,+,456,\n,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("123 + 456\n## hello world \n\n\n\n\n", "123,+,456,\n,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("hello world \n\n ## hello world\n\n", "hello,world,\n,\n,<EOF>", tc_name_getter()))
        self.assertTrue(TestLexer.test("## this is a boolean expression\n\n  true and false and true\n",
                                       "true,and,false,and,true,\n,<EOF>", tc_name_getter()))
        ##########
        ##      ##
        ##      ##
        ##########
        self.assertTrue(TestLexer.test("##########\n##      ##\n##      ##\n##########", "<EOF>", tc_name_getter()))
