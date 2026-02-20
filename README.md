# KotekLang

Маленький учебный язык и интерпретатор на Python.

## Грамматика (EBNF)

```ebnf
program        ::= declaration* EOF ;

declaration    ::= functionDecl
                 | varDecl
                 | statement ;

functionDecl   ::= "fun" IDENTIFIER "(" parameters? ")" block ;
parameters     ::= IDENTIFIER ("," IDENTIFIER)* ;

varDecl        ::= "let" IDENTIFIER "=" expression ";" ;

statement      ::= printStmt
                 | ifStmt
                 | whileStmt
                 | returnStmt
                 | block
                 | exprStmt ;

printStmt      ::= "print" expression ";" ;
ifStmt         ::= "if" "(" expression ")" statement ("else" statement)? ;
whileStmt      ::= "while" "(" expression ")" statement ;
returnStmt     ::= "return" expression? ";" ;
block          ::= "{" declaration* "}" ;
exprStmt       ::= expression ";" ;

expression     ::= assignment ;
assignment     ::= IDENTIFIER "=" assignment | logic_or ;
logic_or       ::= logic_and ("or" logic_and)* ;
logic_and      ::= equality ("and" equality)* ;
equality       ::= comparison (("==" | "!=") comparison)* ;
comparison     ::= term ((">" | ">=" | "<" | "<=") term)* ;
term           ::= factor (("+" | "-") factor)* ;
factor         ::= unary (("*" | "/" | "%") unary)* ;
unary          ::= ("!" | "-") unary | call ;
call           ::= primary (("(" arguments? ")") | ("[" expression "]"))* ;
arguments      ::= expression ("," expression)* ;
primary        ::= NUMBER | STRING | "true" | "false" | "nil"
                 | IDENTIFIER
                 | "(" expression ")"
                 | "[" arguments? "]" ;
```

## Возможности

- Лексер + парсер (рекурсивный спуск) + AST.
- Интерпретатор со scope-окружениями.
- Ошибки с line/column.
- REPL и запуск `.kotek` файла.

## Запуск

```bash
python -m koteklang.main
python -m koteklang.main examples/demo.kotek
```

## Примеры программ

### 1) Условия и циклы

```kotek
let i = 0;
while (i < 3) {
  if (i % 2 == 0) print "even";
  else print "odd";
  i = i + 1;
}
```

### 2) Функции и рекурсия

```kotek
fun fib(n) {
  if (n <= 1) return n;
  return fib(n - 1) + fib(n - 2);
}

print fib(8);
```

### 3) Списки

```kotek
let cats = ["Murka", "Barsik", "Keks"];
print cats[1];
```

## Тесты

```bash
python -m unittest discover -s tests -v
```

В проекте 15 тестов на синтаксис и семантику.
