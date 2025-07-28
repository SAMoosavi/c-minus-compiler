from code_generator import CodeGenerator


class Parser:
    def __init__(self, scanner):
        self.scanner = scanner
        self.lookahead = self.scanner.get_next_token()
        self.output = []
        self.indent_level = 0
        self.syntax_errors = ""
        self.code_gen = CodeGenerator()

    def parse_tree(self):
        lines = self.output
        stack = []
        ans = {}

        def get_indent_level(line):
            return len(line) - len(line.lstrip("\t"))

        stack.append("ROOT")

        for line in lines:
            level = get_indent_level(line)
            content: str = line.strip()
            if level + 1 == len(stack):
                stack.pop()
                node = ans
                for k in stack:
                    node = node[k]

                if content not in node:
                    node[content] = {}
                else:
                    content += "|" + "".join(node.keys())
                    node[content] = {}

                stack.append(content)

            elif level + 1 >= len(stack):
                node = ans
                for k in stack:
                    node = node[k]

                if content not in node:
                    node[content] = {}
                else:
                    content += "|" + "".join(node.keys())
                    node[content] = {}

                stack.append(content)
            else:
                while level + 1 != len(stack):
                    stack.pop()

                stack.pop()
                node = ans
                for k in stack:
                    node = node[k]

                if content not in node:
                    node[content] = {}
                else:
                    content += "|" + "".join(node.keys())
                    node[content] = {}

                stack.append(content)

        return ans

    def print_tree(self, d, prefix=""):
        out = []
        keys = list(d.keys())
        for i, key in enumerate(keys):
            is_terminal = len(d[key]) == 0
            is_last_key = i == len(keys) - 1
            branch = "└── " if is_last_key else "├── "
            connector = "    " if is_last_key else "│   "
            out.append(f"{prefix}{branch}{key.split('|')[0]}")
            if not is_terminal:
                out.extend(self.print_tree(d[key], prefix + connector))
        return out

    def syntax_error(self, error):
        self.syntax_errors += error + "\n"
        while self.lookahead != "$":
            lineno, (tok_type, lexeme) = self.lookahead
            self.syntax_errors += f"#{lineno} : syntax error, illegal {lexeme} \n"
            self.lookahead = self.scanner.get_next_token()
        tree = "\n".join(self.print_tree(self.parse_tree()["Program"]))
        raise SyntaxError((self.syntax_errors, f"Program\n{tree}"))

    def match(self, expected_type, expected_lexeme=None):
        token = self.lookahead
        if token == "$":
            self.syntax_error("Unexpected EOF")
            return

        lineno, (tok_type, lexeme) = token
        if tok_type == expected_type and (
            expected_lexeme is None or lexeme == expected_lexeme
        ):
            self.output.append(self.format_token(tok_type, lexeme))
            self.lookahead = self.scanner.get_next_token()
        else:
            self.syntax_error(
                f"Expected {expected_type}('{expected_lexeme}') but got {tok_type}('{lexeme}')"
            )

    def indent(self, label):
        self.output.append("\t" * self.indent_level + label)
        self.indent_level += 1

    def dedent(self):
        self.indent_level -= 1

    def format_token(self, tok_type, lexeme):
        return "\t" * self.indent_level + f"({tok_type}, {lexeme})"

    def parse(self):
        self.indent("Program")
        self.Program()
        self.indent("$")
        self.dedent()
        self.dedent()
        tree = "\n".join(self.print_tree(self.parse_tree()["Program"]))
        return f"Program\n{tree}", self.syntax_errors

    def Program(self):
        self.indent("Declaration-list")
        self.Declaration_list()
        self.dedent()

    def Declaration_list(self):
        if self.lookahead == "$" or self.lookahead[1][1] not in ("int", "void"):
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

        if self.lookahead[1][0] == "ID":
            self.var_name = self.lookahead[1][1]  # ⬅️ ذخیره اسم متغیر برای مراحل بعد
        self.match("ID")

    def Declaration_prime(self):
        if self.lookahead[1][1] == "(":
            self.indent("Fun-declaration-prime")
            self.Fun_declaration_prime()
            self.dedent()
        else:
            self.indent("Var-declaration-prime")
            self.Var_declaration_prime()
            self.dedent()

    def Var_declaration_prime(self):
        if self.lookahead[1][1] == "[":
            self.match("SYMBOL", "[")
            if self.lookahead[1][0] == "NUM":
                size = int(self.lookahead[1][1])
            else:
                size = 1  # fallback
            self.match("NUM")
            self.match("SYMBOL", "]")
            self.match("SYMBOL", ";")
            # ⬅️ Action Symbol برای آرایه
            for i in range(size):
                name = f"{self.var_name}[{i}]"
                self.code_gen.get_var_address(name)
        else:
            self.match("SYMBOL", ";")

            # ⬅️ Action Symbol برای متغیر معمولی
            self.code_gen.get_var_address(self.var_name)

    def Fun_declaration_prime(self):
        self.match("SYMBOL", "(")
        self.indent("Params")
        self.Params()
        self.dedent()
        self.match("SYMBOL", ")")
        self.indent("Compound-stmt")
        self.Compound_stmt()
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

    def Param_list(self):
        if self.lookahead[1][1] == ",":
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

    def Param_prime(self):
        if self.lookahead[1][1] == "[":
            self.match("SYMBOL", "[")
            self.match("SYMBOL", "]")
        else:
            self.indent("epsilon")
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
        if self.lookahead[1][1] in (
            "if",
            "repeat",
            "return",
            "break",
            "{",
        ) or self.lookahead[1][0] in ("ID", "NUM", "("):
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
        if self.lookahead[1][1] == "if":
            self.indent("Selection-stmt")
            self.Selection_stmt()
            self.dedent()
        elif self.lookahead[1][1] == "repeat":
            self.indent("Iteration-stmt")
            self.Iteration_stmt()
            self.dedent()
        elif self.lookahead[1][1] == "return":
            self.indent("Return-stmt")
            self.Return_stmt()
            self.dedent()
        elif self.lookahead[1][1] == "{":
            self.indent("Compound-stmt")
            self.Compound_stmt()
            self.dedent()
        else:
            self.indent("Expression-stmt")
            self.Expression_stmt()
            self.dedent()

    def Expression_stmt(self):
        if self.lookahead[1][1] == "break":
            self.match("KEYWORD", "break")
            self.match("SYMBOL", ";")
        elif self.lookahead[1][1] == ";":
            self.match("SYMBOL", ";")
        else:
            self.indent("Expression")
            result = self.Expression()  # ← مقدار رو بگیر ولی نیاز نیست استفاده شه
            self.dedent()
            self.match("SYMBOL", ";")

    def Selection_stmt(self):
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

    def Iteration_stmt(self):
        loop_start = self.code_gen.new_label()
        self.code_gen.emit("LABEL", loop_start, "", "")
        self.match("KEYWORD", "repeat")
        self.indent("Statement")
        self.Statement()
        self.dedent()
        self.match("KEYWORD", "until")
        self.match("SYMBOL", "(")
        self.indent("Expression")
        condition = self.Expression()
        self.dedent()
        self.match("SYMBOL", ")")
        self.code_gen.emit("JPF", condition, loop_start, "")

    def Return_stmt(self):
        self.match("KEYWORD", "return")
        self.indent("Return-stmt-prime")
        self.Return_stmt_prime()
        self.dedent()

    def Return_stmt_prime(self):
        if self.lookahead[1][1] != ";":
            self.indent("Expression")
            result = self.Expression()
            self.dedent()
            self.match("SYMBOL", ";")
            self.code_gen.emit("RETURN", result, "", "")
        else:
            self.match("SYMBOL", ";")
            self.code_gen.emit("RETURN", "", "", "")

    def Expression(self):
        if self.lookahead[1][0] == "NUM" or self.lookahead[1][1] == "(":
            self.indent("Simple-expression-zegond")
            result = self.Simple_expression_zegond()
            self.dedent()
            return result
        else:
            var_name = self.lookahead[1][1]  # ذخیره ID برای رجوع بعدی
            self.match("ID")
            self.indent("B")
            result = self.B(var_name)  # تابع جدید
            self.dedent()
            return result

    def B(self, var_name: str):
        if self.lookahead[1][1] == "=":
            self.match("SYMBOL", "=")
            self.indent("Expression")
            rhs_addr = self.Expression()
            self.dedent()
            self.code_gen.emit("ASSIGN", rhs_addr, "", var_name)  # ✅ اصلاح شده
            return var_name
        elif self.lookahead[1][1] == "[":
            self.match("SYMBOL", "[")
            self.indent("Expression")
            index = self.Expression()  # i
            self.dedent()
            self.match("SYMBOL", "]")
            # offset = index * 4
            offset = self.code_gen.new_temp()
            self.code_gen.emit("MULT", index, "#4", offset)
            base_addr = self.code_gen.get_var_address(f"{var_name}[0]")
            addr = self.code_gen.new_temp()
            self.code_gen.emit("ADD", f"#{base_addr}", offset, addr)
            self.indent("H")
            result = self.H(addr)
            self.dedent()
            return result
        else:
            self.indent("Simple-expression-prime")
            result = self.Simple_expression_prime()
            return result

    def H(self, addr):  # ← آدرس محاسبه‌شده a[i] از B
        if self.lookahead[1][1] == "=":
            self.match("SYMBOL", "=")
            self.indent("Expression")
            value = self.Expression()  # مقدار سمت راست
            self.dedent()
            self.code_gen.emit("ASSIGN", value, f"@{addr}", "")
            return None
        else:
            self.indent("G")
            left = self.G(f"@{addr}")  # بخونیم از addr
            self.dedent()
            self.indent("D")
            dres = self.D(left)
            self.dedent()
            self.indent("C")
            cres = self.C(dres)
            self.dedent()
            return cres  # مقدار نهایی expression مثل a[i] * 2 + 1

    def Simple_expression_zegond(self):
        self.indent("Additive-expression-zegond")
        left = self.Additive_expression_zegond()
        self.dedent()
        self.indent("C")
        result = self.C(left)
        self.dedent()
        return result

    def Simple_expression_prime(self):
        self.indent("Additive-expression-prime")
        left = self.Additive_expression_prime()
        self.dedent()

        self.indent("C")
        result = self.C(left)
        self.dedent()

        return result

    def C(self, left):
        if self.lookahead[1][1] in ("<", "=="):
            self.indent("Relop")
            op = self.lookahead[1][1]  # "<" یا "=="
            self.Relop()
            self.dedent()
            self.indent("Additive-expression")
            right = self.Additive_expression()  # مقدار سمت راست مقایسه
            self.dedent()
            result = self.code_gen.new_temp()
            tac_op = "LT" if op == "<" else "EQ"
            self.code_gen.emit(tac_op, left, right, result)
            return result
        else:
            self.indent("epsilon")
            self.dedent()
            return left  # اگر اصلاً عملگر مقایسه نبود، همون عبارت قبلی رو برگردون

    def Relop(self):
        if self.lookahead[1][1] == "<":
            self.match("SYMBOL", "<")
        elif self.lookahead[1][1] == "==":
            self.match("SYMBOL", "==")
        else:
            self.syntax_error("Expected relational operator")

    def Additive_expression(self):
        self.indent("Term")
        left = self.Term()
        self.dedent()

        self.indent("D")
        result = self.D(left)
        self.dedent()

        return result

    def Additive_expression_prime(self):
        self.indent("Term-prime")
        left = self.Term_prime()
        self.dedent()

        self.indent("D")
        result = self.D(left)
        self.dedent()

        return result

    def Additive_expression_zegond(self):
        self.indent("Term-zegond")
        left = self.Term_zegond()  # مقدار سمت چپ (مثلاً a)
        self.dedent()
        self.indent("D")
        result = self.D(left)  # ادامهٔ جمع/تفریق رو انجام بده
        self.dedent()
        return result

    def D(self, inherited=None):
        if self.lookahead[1][1] in ("+", "-"):
            self.indent("Addop")
            op = self.lookahead[1][1]
            self.Addop()
            self.dedent()

            self.indent("Term")
            right = self.Term()  # باید مقدار رو از Term بگیریم
            self.dedent()

            # تولید کد ۳آدرسی
            result = self.code_gen.new_temp()
            tac_op = "ADD" if op == "+" else "SUB"
            self.code_gen.emit(tac_op, inherited, right, result)

            self.indent("D")
            result = self.D(result)  # بازگشت با نتیجه جدید
            self.dedent()
            return result
        else:
            self.indent("epsilon")
            self.dedent()
            return inherited

    def Addop(self):
        if self.lookahead[1][1] == "+":
            self.match("SYMBOL", "+")
        elif self.lookahead[1][1] == "-":
            self.match("SYMBOL", "-")
        else:
            self.syntax_error("Expected additive operator")

    def Term(self):
        self.indent("Factor")
        left = self.Factor()
        self.dedent()

        self.indent("G")
        result = self.G(left)
        self.dedent()

        return result

    def Term_prime(self):
        self.indent("Factor-prime")
        left = self.Factor_prime()
        self.dedent()

        self.indent("G")
        result = self.G(left)
        self.dedent()

        return result

    def Term_zegond(self):
        self.indent("Factor-zegond")
        left = self.Factor_zegond()
        self.dedent()

        self.indent("G")
        result = self.G(left)
        self.dedent()

        return result

    def G(self, inherited=""):
        if self.lookahead[1][1] == "*":
            self.match("SYMBOL", "*")
            self.indent("Factor")
            right = self.Factor()
            self.dedent()
            result = self.code_gen.new_temp()
            self.code_gen.emit("MULT", inherited, right, result)
            self.indent("G")
            result = self.G(result)
            self.dedent()
            return result
        else:
            self.indent("epsilon")
            self.dedent()
            return inherited

    def Factor(self):
        if self.lookahead[1][1] == "(":
            self.match("SYMBOL", "(")
            self.indent("Expression")
            result = self.Expression()
            self.dedent()
            self.match("SYMBOL", ")")
            return result
        elif self.lookahead[1][0] == "ID":
            name = self.lookahead[1][1]
            self.match("ID")
            self.indent("Var-call-prime")
            result = self.Var_call_prime(name)  # اسم متغیر رو پاس می‌دیم
            self.dedent()
            return result
        elif self.lookahead[1][0] == "NUM":
            value = self.lookahead[1][1]
            self.match("NUM")
            return f"#{value}"  # عدد فوری
        else:
            self.syntax_error("Invalid factor")
            return None

    def Var_call_prime(self, name):
        if self.lookahead[1][1] == "(":
            self.match("SYMBOL", "(")
            self.indent("Args")
            args = self.Args()  # ← آرگومان‌ها رو بگیر
            self.dedent()
            self.match("SYMBOL", ")")

            # ← تولید کد برای آرگومان‌ها
            for arg in args:
                self.code_gen.emit("ARG", arg, "", "")

            ret_temp = self.code_gen.new_temp()
            self.code_gen.emit("CALL", name, "", ret_temp)
            return ret_temp
        else:
            self.indent("Var-prime")
            result = self.Var_prime(name)
            self.dedent()
            return result

    def Var_prime(self, name):
        if self.lookahead[1][1] == "[":
            self.match("SYMBOL", "[")
            self.indent("Expression")
            index = self.Expression()
            self.dedent()
            self.match("SYMBOL", "]")

            # offset = index * 4
            offset = self.code_gen.new_temp()
            self.code_gen.emit("MULT", index, "#4", offset)

            base_addr = self.code_gen.get_var_address(f"{name}[0]")

            effective_addr = self.code_gen.new_temp()
            self.code_gen.emit("ADD", f"#{base_addr}", offset, effective_addr)

            result = self.code_gen.new_temp()
            self.code_gen.emit("ASSIGN", effective_addr, "", result)
            return result
        else:
            self.indent("epsilon")
            self.dedent()
            addr = self.code_gen.get_var_address(name)
            temp = self.code_gen.new_temp()
            self.code_gen.emit("ASSIGN", f"#{addr}", "", temp)
            return temp

    def Factor_prime(self, name=""):
        if self.lookahead[1][1] == "(":
            self.match("SYMBOL", "(")
            self.indent("Args")
            args = self.Args()
            self.dedent()
            self.match("SYMBOL", ")")

            # تولید کد ARG برای هر آرگومان
            for arg in args:
                self.code_gen.emit("ARG", arg, "", "")

            ret_temp = self.code_gen.new_temp()
            self.code_gen.emit("CALL", name, "", ret_temp)
            return ret_temp
        else:
            self.indent("epsilon")
            self.dedent()

            addr = self.code_gen.get_var_address(name)
            temp = self.code_gen.new_temp()
            self.code_gen.emit("ASSIGN", f"#{addr}", "", temp)
            return temp

    def Factor_zegond(self):
        if self.lookahead[1][1] == "(":
            self.match("SYMBOL", "(")
            self.indent("Expression")
            result = self.Expression()  # ⬅️ مقدار حاصل داخل پرانتز
            self.dedent()
            self.match("SYMBOL", ")")
            return result

        elif self.lookahead[1][0] == "NUM":
            value = self.lookahead[1][1]
            self.match("NUM")
            return f"#{value}"  # ⬅️ برگردوندن مقدار عددی فوری

        else:
            self.syntax_error("Expected '(' or NUM in Factor-zegond")

    def Args(self):
        if self.lookahead[1][1] != ")":
            self.indent("Arg-list")
            args = self.Arg_list()  # ← آرگومان‌ها رو بگیر
            self.dedent()
            return args
        else:
            self.indent("epsilon")
            self.dedent()
            return []

    def Arg_list(self):
        self.indent("Expression")
        arg = self.Expression()  # ← temp یا immediate
        self.dedent()
        self.indent("Arg-list-prime")
        args = self.Arg_list_prime()
        self.dedent()
        return [arg] + args

    def Arg_list_prime(self):
        if self.lookahead[1][1] == ",":
            self.match("SYMBOL", ",")
            self.indent("Expression")
            arg = self.Expression()
            self.dedent()
            self.indent("Arg-list-prime")
            rest = self.Arg_list_prime()
            self.dedent()
            return [arg] + rest
        else:
            self.indent("epsilon")
            self.dedent()
            return []
