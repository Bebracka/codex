import argparse
import sys

from koteklang.errors import KotekLangError
from koteklang.interpreter import Interpreter
from koteklang.lexer import Lexer
from koteklang.parser import Parser


def run_source(source: str, interpreter: Interpreter | None = None):
    interpreter = interpreter or Interpreter()
    tokens = Lexer(source).tokenize()
    statements = Parser(tokens).parse()
    interpreter.interpret(statements)
    return interpreter


def run_file(path: str):
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    run_source(source)


def repl():
    interpreter = Interpreter()
    print("KotekLang REPL. Ctrl-D/Ctrl-C to exit.")
    while True:
        try:
            line = input(">>> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line.strip():
            continue
        try:
            run_source(line if line.endswith(";") else line + ";", interpreter)
        except KotekLangError as err:
            print(err)


def main(argv=None):
    parser = argparse.ArgumentParser(description="KotekLang interpreter")
    parser.add_argument("file", nargs="?", help="Path to .kotek file")
    args = parser.parse_args(argv)
    try:
        if args.file:
            run_file(args.file)
        else:
            repl()
    except KotekLangError as err:
        print(err, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
