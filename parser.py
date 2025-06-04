class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.lookahead = self.scanner.get_next_token()
        self.output = []
        self.indent_level = 0

    def match(self, expected_type, expected_lexeme=None):
        token = self.lookahead
        if token == '$':
            self.syntax_error("Unexpected EOF")
            return

        _, (tok_type, lexeme) = token

        if tok_type == expected_type and (expected_lexeme is None or lexeme == expected_lexeme):
            self.output.append(self.format_token(tok_type, lexeme))
            self.lookahead = self.scanner.get_next_token()
        else:
            self.syntax_error(f"Expected {expected_type}('{expected_lexeme}') but got {tok_type}('{lexeme}')")

    def format_token(self, tok_type, lexeme):
        return "\t" * self.indent_level + f"({tok_type}, {lexeme})"

    def syntax_error(self, msg):
        raise SyntaxError(f"Syntax error: {msg}")

    def parse(self):
        self.output.append("Program")
        self.Program()
        self.output.append("$")
        return self.output

    # Grammar Rule: Program → Declaration-list
    def Program(self):
        self.indent("Declaration-list")
        self.Declaration_list()
        self.dedent()

    def Declaration_list(self):
        if self.lookahead == '$' or self.lookahead[1][1] not in ("int", "void"):
            self.indent("epsilon")
            self.dedent()
            return
        self.indent("Declaration")
        self.Declaration()
        self.dedent()
        self.indent("Declaration-list")
        self.Declaration_list()
        self.dedent()

    def Declaration(self):
        self.indent("Declaration-initial")
        self.Declaration_initial()
        self.dedent()
        self.indent("Declaration-prime")
        self.Declaration_prime()
        self.dedent()

    def Declaration_initial(self):
        self.indent("Type-specifier")
        self.Type_specifier()
        self.dedent()
        self.match("ID")

    def Declaration_prime(self):
        if self.lookahead[1][1] == '(':  # Fun-declaration-prime
            self.indent("Fun-declaration-prime")
            self.match("SYMBOL", "(")
            self.indent("Params")
            self.Params()
            self.dedent()
            self.match("SYMBOL", ")")
            self.indent("Compound-stmt")
            self.Compound_stmt()
            self.dedent()
            self.dedent()
        else:  # Var-declaration-prime
            self.indent("Var-declaration-prime")
            if self.lookahead[1][1] == '[':
                self.match("SYMBOL", "[")
                self.match("NUM")
                self.match("SYMBOL", "]")
            self.match("SYMBOL", ";")
            self.dedent()

    def Type_specifier(self):
        if self.lookahead[1][1] in ("int", "void"):
            self.match("KEYWORD")
        else:
            self.syntax_error("Expected type specifier")

    def Params(self):
        if self.lookahead[1][1] == "void":
            self.match("KEYWORD", "void")
        else:
            self.match("KEYWORD", "int")
            self.match("ID")
            self.indent("Param-prime")
            self.Param_prime()
            self.dedent()
            self.indent("Param-list")
            self.Param_list()
            self.dedent()

    def Param_prime(self):
        if self.lookahead[1][1] == '[':
            self.match("SYMBOL", "[")
            self.match("SYMBOL", "]")
        else:
            self.indent("epsilon")
            self.dedent()

    def Param_list(self):
        if self.lookahead[1][1] == ',':
            self.match("SYMBOL", ",")
            self.indent("Param")
            self.Param()
            self.dedent()
            self.indent("Param-list")
            self.Param_list()
            self.dedent()
        else:
            self.indent("epsilon")
            self.dedent()

    def Param(self):
        self.indent("Declaration-initial")
        self.Declaration_initial()
        self.dedent()
        self.indent("Param-prime")
        self.Param_prime()
        self.dedent()

    def Compound_stmt(self):
        self.match("SYMBOL", "{")
        self.indent("Declaration-list")
        self.Declaration_list()
        self.dedent()
        self.indent("Statement-list")
        self.Statement_list()
        self.dedent()
        self.match("SYMBOL", "}")

    def Statement_list(self):
        if self.lookahead[1][1] in ('if', 'repeat', 'return', 'break', '{') or self.lookahead[0] != '$' or self.lookahead[1][0] in ('ID', 'NUM', '('):
            self.indent("Statement")
            self.Statement()
            self.dedent()
            self.indent("Statement-list")
            self.Statement_list()
            self.dedent()
        else:
            self.indent("epsilon")
            self.dedent()

    def Statement(self):
        self.indent("Expression-stmt")
        self.Expression_stmt()
        self.dedent()

    def Expression_stmt(self):
        if self.lookahead[1][1] == 'break':
            self.match("KEYWORD", "break")
            self.match("SYMBOL", ";")
        elif self.lookahead[1][1] == ';':
            self.match("SYMBOL", ";")
        else:
            self.indent("Expression")
            self.Expression()
            self.dedent()
            self.match("SYMBOL", ";")

    def Expression(self):
        self.match("ID")  # simplified
        if self.lookahead[1][1] == '=':
            self.match("SYMBOL", "=")
            self.indent("Expression")
            self.Expression()
            self.dedent()

    # Utility functions to help with indentation for parse tree output
    def indent(self, label):
        self.output.append("\t" * self.indent_level + label)
        self.indent_level += 1

    def dedent(self):
        self.indent_level -= 1
