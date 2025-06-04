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

    def indent(self, label):
        self.output.append("\t" * self.indent_level + label)
        self.indent_level += 1

    def dedent(self):
        self.indent_level -= 1

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
        if self.lookahead[1][1] in ('if', 'repeat', 'return', 'break', '{') or self.lookahead[1][0] in ('ID', 'NUM', '('):
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
        if self.lookahead[1][1] == 'if':
            self.indent("Selection-stmt")
            self.match("KEYWORD", "if")
            self.match("SYMBOL", "(")
            self.indent("Expression")
            self.Expression()
            self.dedent()
            self.match("SYMBOL", ")")
            self.indent("Statement")
            self.Statement()
            self.dedent()
            self.match("KEYWORD", "else")
            self.indent("Statement")
            self.Statement()
            self.dedent()
            self.dedent()
        elif self.lookahead[1][1] == 'repeat':
            self.indent("Iteration-stmt")
            self.match("KEYWORD", "repeat")
            self.indent("Statement")
            self.Statement()
            self.dedent()
            self.match("KEYWORD", "until")
            self.match("SYMBOL", "(")
            self.indent("Expression")
            self.Expression()
            self.dedent()
            self.match("SYMBOL", ")")
            self.dedent()
        elif self.lookahead[1][1] == 'return':
            self.indent("Return-stmt")
            self.match("KEYWORD", "return")
            self.indent("Return-stmt-prime")
            self.Return_stmt_prime()
            self.dedent()
        elif self.lookahead[1][1] == '{':
            self.indent("Compound-stmt")
            self.Compound_stmt()
            self.dedent()
        else:
            self.indent("Expression-stmt")
            self.Expression_stmt()
            self.dedent()
    
    def Return_stmt_prime(self):
        if self.lookahead[1][1] != ';':
            self.indent("Expression")
            self.Expression()
            self.dedent()
        else:
            self.match("SYMBOL", ";")

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
        if self.lookahead[1][0] == "NUM" or self.lookahead[1][1] == "(":
            self.indent("Simple-expression-zegond")
            self.Simple_expression_zegond()
            self.dedent()
        elif self.lookahead[1][0] == "ID":
            self.match("ID")
            self.indent("B")
            self.B()
            self.dedent()

    def B(self):
        if self.lookahead[1][1] == '=':
            self.match("SYMBOL", "=")
            self.indent("Expression")
            self.Expression()
            self.dedent()
        elif self.lookahead[1][1] == '[':
            self.match("SYMBOL", "[")
            self.indent("Expression")
            self.Expression()
            self.dedent()
            self.match("SYMBOL", "]")
            self.indent("H")
            self.H()
            self.dedent()
        else:
            self.indent("Simple-expression-prime")
            self.Simple_expression_prime()
            self.dedent()

    def H(self):
        if self.lookahead[1][1] == '=':
            self.match("SYMBOL", "=")
            self.indent("Expression")
            self.Expression()
            self.dedent()
        else:
            self.indent("G")
            self.G()
            self.dedent()
            self.indent("D")
            self.D()
            self.dedent()
            self.indent("C")
            self.C()
            self.dedent()

    def Simple_expression_prime(self):
        self.indent("Additive-expression-prime")
        self.Additive_expression_prime()
        self.dedent()
        self.indent("C")
        self.C()
        self.dedent()

    def Additive_expression_prime(self):
        self.indent("Term-prime")
        self.Term_prime()
        self.dedent()
        self.indent("D")
        self.D()
        self.dedent()

    def C(self):
        if self.lookahead[1][1] in ('<', '=='):
            self.indent("Relop")
            self.Relop()
            self.dedent()
            self.indent("Additive-expression")
            self.Additive_expression()
            self.dedent()
        else:
            self.indent("epsilon")
            self.dedent()

    def Relop(self):
        if self.lookahead[1][1] == '<':
            self.match("SYMBOL", "<")
        elif self.lookahead[1][1] == '==':
            self.match("SYMBOL", "==")
        else:
            self.syntax_error("Expected relational operator")

    def Additive_expression(self):
        self.indent("Term")
        self.Term()
        self.dedent()
        self.indent("D")
        self.D()
        self.dedent()

    def D(self):
        if self.lookahead[1][1] in ('+', '-'):
            self.indent("Addop")
            self.Addop()
            self.dedent()
            self.indent("Term")
            self.Term()
            self.dedent()
            self.indent("D")
            self.D()
            self.dedent()
        else:
            self.indent("epsilon")
            self.dedent()

    def Addop(self):
        if self.lookahead[1][1] == '+':
            self.match("SYMBOL", "+")
        elif self.lookahead[1][1] == '-':
            self.match("SYMBOL", "-")
        else:
            self.syntax_error("Expected additive operator")

    def Term(self):
        self.indent("Factor")
        self.Factor()
        self.dedent()
        self.indent("G")
        self.G()
        self.dedent()

    def Term_prime(self):
        self.indent("Factor-prime")
        self.Factor_prime()
        self.dedent()
        self.indent("G")
        self.G()
        self.dedent()

    def G(self):
        if self.lookahead[1][1] == '*':
            self.match("SYMBOL", "*")
            self.indent("Factor")
            self.Factor()
            self.dedent()
            self.indent("G")
            self.G()
            self.dedent()
        else:
            self.indent("epsilon")
            self.dedent()

    def Factor(self):
        if self.lookahead[1][1] == '(':
            self.match("SYMBOL", "(")
            self.indent("Expression")
            self.Expression()
            self.dedent()
            self.match("SYMBOL", ")")
        elif self.lookahead[1][0] == "ID":
            self.match("ID")
            self.indent("Var-call-prime")
            self.Var_call_prime()
            self.dedent()
        elif self.lookahead[1][0] == "NUM":
            self.match("NUM")
        else:
            self.syntax_error("Invalid factor")

    def Factor_prime(self):
        if self.lookahead[1][1] == '(':
            self.match("SYMBOL", "(")
            self.indent("Args")
            self.Args()
            self.dedent()
            self.match("SYMBOL", ")")
        else:
            self.indent("epsilon")
            self.dedent()

    def Var_call_prime(self):
        if self.lookahead[1][1] == '(':
            self.match("SYMBOL", "(")
            self.indent("Args")
            self.Args()
            self.dedent()
            self.match("SYMBOL", ")")
        elif self.lookahead[1][1] == '[':
            self.match("SYMBOL", "[")
            self.indent("Expression")
            self.Expression()
            self.dedent()
            self.match("SYMBOL", "]")
        else:
            self.indent("epsilon")
            self.dedent()

    def Args(self):
        if self.lookahead[1][1] != ')':
            self.indent("Arg-list")
            self.Arg_list()
            self.dedent()
        else:
            self.indent("epsilon")
            self.dedent()

    def Arg_list(self):
        self.indent("Expression")
        self.Expression()
        self.dedent()
        self.indent("Arg-list-prime")
        self.Arg_list_prime()
        self.dedent()

    def Arg_list_prime(self):
        if self.lookahead[1][1] == ',':
            self.match("SYMBOL", ",")
            self.indent("Expression")
            self.Expression()
            self.dedent()
            self.indent("Arg-list-prime")
            self.Arg_list_prime()
            self.dedent()
        else:
            self.indent("epsilon")
            self.dedent()

    def Simple_expression_zegond(self):
        self.indent("Additive-expression-zegond")
        self.Additive_expression_zegond()
        self.dedent()
        self.indent("C")
        self.C()
        self.dedent()

    def Additive_expression_zegond(self):
        self.indent("Term-zegond")
        self.Term_zegond()
        self.dedent()
        self.indent("D")
        self.D()
        self.dedent()

    def Term_zegond(self):
        self.indent("Factor-zegond")
        self.Factor_zegond()
        self.dedent()
        self.indent("G")
        self.G()
        self.dedent()

    def Factor_zegond(self):
        if self.lookahead[1][1] == '(':
            self.match("SYMBOL", "(")
            self.indent("Expression")
            self.Expression()
            self.dedent()
            self.match("SYMBOL", ")")
        elif self.lookahead[1][0] == "NUM":
            self.match("NUM")
        else:
            self.syntax_error("Expected '(' or NUM in Factor-zegond")
