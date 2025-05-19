import re

keywords = {'if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return'}
symbols = {';', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '=='}
symbol_set = set(';,[](){}+-*=</')

symbol_table = []
symbol_table_set = set()
lexical_errors = []

class Scanner:
    def __init__(self, source_lines):
        self.lines = source_lines
        self.lineno = 0
        self.line = ""
        self.index = 0
        self.current_token = None

    def add_to_symbol_table(self, lexeme):
        if lexeme not in symbol_table_set:
            symbol_table_set.add(lexeme)
            symbol_table.append(lexeme)

    def get_next_token(self):
        while self.lineno < len(self.lines):
            if self.index >= len(self.line):
                self.line = self.lines[self.lineno]
                self.lineno += 1
                self.index = 0

            while self.index < len(self.line):
                c = self.line[self.index]

                if c.isspace():
                    self.index += 1
                    continue

                if c == '/' and self.index+1 < len(self.line) and self.line[self.index+1] == '*':
                    end = self.line.find('*/', self.index+2)
                    if end == -1:
                        snippet = self.line[self.index:self.index+10].replace('\n', '') + ('...' if len(self.line[self.index:]) > 10 else '')
                        lexical_errors.append(f"{self.lineno}	({snippet}, Unclosed comment)")
                        self.index = len(self.line)
                        return self.get_next_token()
                    else:
                        self.index = end + 2
                        continue

                if c == '*' and self.index+1 < len(self.line) and self.line[self.index+1] == '/':
                    lexical_errors.append(f"{self.lineno}	(*/, Unmatched comment)")
                    self.index += 2
                    return self.get_next_token()

                if c in symbol_set:
                    if c == '=' and self.index+1 < len(self.line) and self.line[self.index+1] == '=':
                        self.index += 2
                        return (self.lineno, ("SYMBOL", "=="))
                    else:
                        self.index += 1
                        return (self.lineno, ("SYMBOL", c))

                if c.isdigit():
                    j = self.index
                    while j < len(self.line) and self.line[j].isdigit():
                        j += 1
                    lexeme = self.line[self.index:j]
                    if j < len(self.line) and self.line[j].isalpha():
                        k = j
                        while k < len(self.line) and self.line[k].isalnum():
                            k += 1
                        lexical_errors.append(f"{self.lineno}	({self.line[self.index:k]}, Invalid number)")
                        self.index = k
                        return self.get_next_token()
                    else:
                        self.index = j
                        return (self.lineno, ("NUM", lexeme))

                if c.isalpha():
                    j = self.index
                    while j < len(self.line) and self.line[j].isalnum():
                        j += 1
                    lexeme = self.line[self.index:j]
                    self.index = j
                    if lexeme in keywords:
                        return (self.lineno, ("KEYWORD", lexeme))
                    else:
                        self.add_to_symbol_table(lexeme)
                        return (self.lineno, ("ID", lexeme))

                lexical_errors.append(f"{self.lineno}	({c}, Invalid input)")
                self.index += 1
                return self.get_next_token()

        return None  # End of file

def main():
    with open("input.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    scanner = Scanner(lines)
    tokens = []

    while True:
        tok = scanner.get_next_token()
        if tok is None:
            break
        tokens.append(tok)

    with open("tokens.txt", "w", encoding="utf-8") as f:
        for line, (typ, val) in tokens:
            f.write(f"{line}\t({typ}, {val})\n")

    with open("lexical_errors.txt", "w", encoding="utf-8") as f:
        if lexical_errors:
            for err in lexical_errors:
                f.write(err + "\n")
        else:
            f.write("There is no lexical error.\n")

    with open("symbol_table.txt", "w", encoding="utf-8") as f:
        for i, sym in enumerate(keywords,1):
            f.write(f"{i}.	{sym}\n")

        for i, sym in enumerate(symbol_table, len(keywords)):
            f.write(f"{i}.	{sym}\n")

if __name__ == "__main__":
    main()
