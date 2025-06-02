from scanner import Scanner
from shared import add_tree_line, add_syntax_error, parse_tree_lines, syntax_errors

class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.lookahead = self.scanner.get_next_token()

    def match(self, expected_type, expected_value=None):
        if self.lookahead is None:
            return

        lineno, (token_type, token_value) = self.lookahead
        if token_type == expected_type and (expected_value is None or token_value == expected_value):
            matched = self.lookahead
            self.lookahead = self.scanner.get_next_token()
            return matched
        else:
            expected = expected_value if expected_value else expected_type
            add_syntax_error(lineno, f"{lineno}\tsyntax error, missing {expected}")
            self.lookahead = self.scanner.get_next_token()
            return None

    def parse(self):
        self.program(0)

    def program(self, depth):
        add_tree_line(depth, "Program")
        self.declaration_list(depth + 1)

    def declaration_list(self, depth):
        add_tree_line(depth, "Declaration-list")
        while self.lookahead and (self.lookahead[1][0] == "KEYWORD" and self.lookahead[1][1] in {"int", "void"}):
            self.declaration(depth + 1)

    def declaration(self, depth):
        add_tree_line(depth, "Declaration")
        self.declaration_initial(depth + 1)
        self.declaration_prime(depth + 1)

    def declaration_initial(self, depth):
        add_tree_line(depth, "Declaration-initial")
        self.type_specifier(depth + 1)
        self.match("ID")

    def declaration_prime(self, depth):
        add_tree_line(depth, "Declaration-prime")
        if self.lookahead and self.lookahead[1][1] == '(':
            self.fun_declaration_prime(depth + 1)
        else:
            self.var_declaration_prime(depth + 1)

    def type_specifier(self, depth):
        add_tree_line(depth, "Type-specifier")
        if self.lookahead and self.lookahead[1][1] in {"int", "void"}:
            self.match("KEYWORD", self.lookahead[1][1])
        else:
            add_syntax_error(self.lookahead[0], f"{self.lookahead[0]}\tsyntax error, missing type")
            self.lookahead = self.scanner.get_next_token()

    def var_declaration_prime(self, depth):
        add_tree_line(depth, "Var-declaration-prime")
        if self.lookahead and self.lookahead[1][1] == '[':
            self.match("SYMBOL", "[")
            self.match("NUM")
            self.match("SYMBOL", "]")
            self.match("SYMBOL", ";")
        else:
            self.match("SYMBOL", ";")

    def fun_declaration_prime(self, depth):
        add_tree_line(depth, "Fun-declaration-prime")
        self.match("SYMBOL", "(")
        self.params(depth + 1)
        self.match("SYMBOL", ")")
        self.compound_stmt(depth + 1)

    def params(self, depth):
        add_tree_line(depth, "Params")
        if self.lookahead and self.lookahead[1][1] == "void":
            self.match("KEYWORD", "void")
        else:
            self.match("KEYWORD", "int")
            self.match("ID")
            self.param_prime(depth + 1)
            self.param_list(depth + 1)

    def param_prime(self, depth):
        add_tree_line(depth, "Param-prime")
        if self.lookahead and self.lookahead[1][1] == "[":
            self.match("SYMBOL", "[")
            self.match("SYMBOL", "]")

    def param_list(self, depth):
        add_tree_line(depth, "Param-list")
        while self.lookahead and self.lookahead[1][1] == ",":
            self.match("SYMBOL", ",")
            self.param(depth + 1)

    def param(self, depth):
        add_tree_line(depth, "Param")
        self.declaration_initial(depth + 1)
        self.param_prime(depth + 1)

    def compound_stmt(self, depth):
        add_tree_line(depth, "Compound-stmt")
        self.match("SYMBOL", "{")
        self.declaration_list(depth + 1)
        self.statement_list(depth + 1)
        self.match("SYMBOL", "}")

    def statement_list(self, depth):
        add_tree_line(depth, "Statement-list")
        while self.lookahead and self.lookahead[1][0] in {"KEYWORD", "ID", "NUM", "SYMBOL"}:
            self.statement(depth + 1)

    def statement(self, depth):
        add_tree_line(depth, "Statement")
        token = self.lookahead[1][1] if self.lookahead else None
        if token == "{":
            self.compound_stmt(depth + 1)
        elif token == "if":
            self.selection_stmt(depth + 1)
        elif token == "repeat":
            self.iteration_stmt(depth + 1)
        elif token == "return":
            self.return_stmt(depth + 1)
        elif token == "break" or token == ";" or token == "(" or (self.lookahead and self.lookahead[1][0] in {"ID", "NUM"}):
            self.expression_stmt(depth + 1)
        else:
            self.expression_stmt(depth + 1)

    def expression_stmt(self, depth):
        add_tree_line(depth, "Expression-stmt")
        if self.lookahead and self.lookahead[1][1] == "break":
            self.match("KEYWORD", "break")
            self.match("SYMBOL", ";")
        elif self.lookahead and self.lookahead[1][1] == ";":
            self.match("SYMBOL", ";")
        else:
            self.expression(depth + 1)
            self.match("SYMBOL", ";")

    def selection_stmt(self, depth):
        add_tree_line(depth, "Selection-stmt")
        self.match("KEYWORD", "if")
        self.match("SYMBOL", "(")
        self.expression(depth + 1)
        self.match("SYMBOL", ")")
        self.statement(depth + 1)
        self.match("KEYWORD", "else")
        self.statement(depth + 1)

    def iteration_stmt(self, depth):
        add_tree_line(depth, "Iteration-stmt")
        self.match("KEYWORD", "repeat")
        self.statement(depth + 1)
        self.match("KEYWORD", "until")
        self.match("SYMBOL", "(")
        self.expression(depth + 1)
        self.match("SYMBOL", ")")

    def return_stmt(self, depth):
        add_tree_line(depth, "Return-stmt")
        self.match("KEYWORD", "return")
        self.return_stmt_prime(depth + 1)

    def return_stmt_prime(self, depth):
        add_tree_line(depth, "Return-stmt-prime")
        if self.lookahead and self.lookahead[1][1] == ";":
            self.match("SYMBOL", ";")
        else:
            self.expression(depth + 1)
            self.match("SYMBOL", ";")

    def expression(self, depth):
        add_tree_line(depth, "Expression")
        self.simple_expression_zegond(depth + 1)

    def simple_expression_zegond(self, depth):
        add_tree_line(depth, "Simple-expression-zegond")
        self.additive_expression_zegond(depth + 1)
        self.C(depth + 1)

    def additive_expression_zegond(self, depth):
        add_tree_line(depth, "Additive-expression-zegond")
        self.term_zegond(depth + 1)
        self.D(depth + 1)

    def term_zegond(self, depth):
        add_tree_line(depth, "Term-zegond")
        self.factor_zegond(depth + 1)
        self.G(depth + 1)

    def factor_zegond(self, depth):
        add_tree_line(depth, "Factor-zegond")
        if self.lookahead and self.lookahead[1][1] == "(":
            self.match("SYMBOL", "(")
            self.expression(depth + 1)
            self.match("SYMBOL", ")")
        else:
            self.match("NUM")

    def C(self, depth):
        add_tree_line(depth, "C")
        if self.lookahead and self.lookahead[1][1] in {"<", "=="}:
            self.match("SYMBOL", self.lookahead[1][1])
            self.additive_expression(depth + 1)
        else:
            add_tree_line(depth + 1, "EPSILON")

    def D(self, depth):
        add_tree_line(depth, "D")
        while self.lookahead and self.lookahead[1][1] in {"+", "-"}:
            self.match("SYMBOL", self.lookahead[1][1])
            self.term(depth + 1)

    def additive_expression(self, depth):
        add_tree_line(depth, "Additive-expression")
        self.term(depth + 1)
        self.D(depth + 1)

    def term(self, depth):
        add_tree_line(depth, "Term")
        self.factor(depth + 1)
        self.G(depth + 1)

    def factor(self, depth):
        add_tree_line(depth, "Factor")
        if self.lookahead and self.lookahead[1][1] == "(":
            self.match("SYMBOL", "(")
            self.expression(depth + 1)
            self.match("SYMBOL", ")")
        elif self.lookahead and self.lookahead[1][0] == "ID":
            self.match("ID")
        elif self.lookahead and self.lookahead[1][0] == "NUM":
            self.match("NUM")
        else:
            add_syntax_error(self.lookahead[0], f"{self.lookahead[0]}\tsyntax error, illegal factor")
            self.lookahead = self.scanner.get_next_token()

    def G(self, depth):
        add_tree_line(depth, "G")
        while self.lookahead and self.lookahead[1][1] == "*":
            self.match("SYMBOL", "*")
            self.factor(depth + 1)