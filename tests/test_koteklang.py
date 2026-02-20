import unittest

from koteklang.errors import LexerError, ParserError, RuntimeError_
from koteklang.interpreter import Interpreter
from koteklang.lexer import Lexer
from koteklang.main import run_source
from koteklang.parser import Parser


def run_capture(source: str):
    out = []
    interpreter = Interpreter(output=out.append)
    run_source(source, interpreter)
    return out


class KotekLangTests(unittest.TestCase):
    def test_01_lexer_tokenizes_numbers_strings(self):
        tokens = Lexer('let x = 12; let s = "cat";').tokenize()
        types = [t.type for t in tokens]
        self.assertIn("NUMBER", types)
        self.assertIn("STRING", types)

    def test_02_lexer_reports_unterminated_string(self):
        with self.assertRaises(LexerError) as ctx:
            Lexer('print "abc;').tokenize()
        self.assertIn("line 1, col 7", str(ctx.exception))

    def test_03_parser_reports_missing_semicolon(self):
        tokens = Lexer("let x = 1").tokenize()
        with self.assertRaises(ParserError) as ctx:
            Parser(tokens).parse()
        self.assertIn("line 1", str(ctx.exception))

    def test_04_print_arithmetic(self):
        out = run_capture("print 2 + 3 * 4;")
        self.assertEqual(out, ["14"])

    def test_05_variables_and_assignment(self):
        out = run_capture("let x = 2; x = x + 5; print x;")
        self.assertEqual(out, ["7"])

    def test_06_if_else(self):
        out = run_capture("if (2 > 1) print \"yes\"; else print \"no\";")
        self.assertEqual(out, ["yes"])

    def test_07_while_loop(self):
        src = "let i = 0; while (i < 3) { print i; i = i + 1; }"
        out = run_capture(src)
        self.assertEqual(out, ["0", "1", "2"])

    def test_08_function_call(self):
        src = "fun add(a, b) { return a + b; } print add(2, 4);"
        out = run_capture(src)
        self.assertEqual(out, ["6"])

    def test_09_recursion(self):
        src = "fun fact(n) { if (n <= 1) return 1; return n * fact(n - 1); } print fact(5);"
        out = run_capture(src)
        self.assertEqual(out, ["120"])

    def test_10_scopes_shadowing(self):
        src = "let x = 1; { let x = 2; print x; } print x;"
        out = run_capture(src)
        self.assertEqual(out, ["2", "1"])

    def test_11_lists_and_index(self):
        out = run_capture("let xs = [10, 20, 30]; print xs[1];")
        self.assertEqual(out, ["20"])

    def test_12_comparisons(self):
        out = run_capture("print 3 >= 3; print 3 != 2;")
        self.assertEqual(out, ["true", "true"])

    def test_13_runtime_undefined_variable(self):
        with self.assertRaises(RuntimeError_) as ctx:
            run_capture("print z;")
        self.assertIn("Undefined variable 'z'", str(ctx.exception))

    def test_14_runtime_wrong_arity(self):
        with self.assertRaises(RuntimeError_) as ctx:
            run_capture("fun f(a) { return a; } print f(1, 2);")
        self.assertIn("Expected 1 arguments but got 2", str(ctx.exception))

    def test_15_runtime_type_error(self):
        with self.assertRaises(RuntimeError_) as ctx:
            run_capture('print "a" - "b";')
        self.assertIn("Operands must be numbers", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
