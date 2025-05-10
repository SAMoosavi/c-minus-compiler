
import re

keywords = {'if', 'else', 'void', 'int', 'repeat', 'break', 'until', 'return'}
symbols = {';', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '=', '<', '=='}
symbol_set = set(';,[](){}+-*=</')

token_output = []
lexical_errors = []
symbol_table = []
symbol_table_set = set()

lineno = 0

def add_token(token_type, value):
    global lineno
    token_output.append(f"{lineno}\t({token_type}, {value})")

def add_error(value, msg="Invalid input"):
    global lineno
    lexical_errors.append(f"{lineno}\t({value}, {msg})")

def add_to_symbol_table(lexeme):
    if lexeme not in symbol_table_set:
        symbol_table_set.add(lexeme)
        symbol_table.append(lexeme)

def tokenize_line(line):
    i = 0
    while i < len(line):
        c = line[i]

        # Skip whitespace
        if c.isspace():
            i += 1
            continue

        # COMMENT START
        if c == '/' and i+1 < len(line) and line[i+1] == '*':
            end = line.find('*/', i+2)
            if end == -1:
                snippet = line[i:i+10].replace('\n', '') + ('...' if len(line[i:]) > 10 else '')
                add_error(snippet, "Unclosed comment")
                break
            else:
                i = end + 2
                continue

        # UNMATCHED COMMENT
        if c == '*' and i+1 < len(line) and line[i+1] == '/':
            add_error("*/", "Unmatched comment")
            i += 2
            continue

        # SYMBOLS
        if c in symbol_set:
            if c == '=' and i+1 < len(line) and line[i+1] == '=':
                add_token("SYMBOL", '==')
                i += 2
            else:
                add_token("SYMBOL", c)
                i += 1
            continue

        # NUMBER
        if c.isdigit():
            j = i
            while j < len(line) and line[j].isdigit():
                j += 1
            lexeme = line[i:j]
            if j < len(line) and line[j].isalpha():
                k = j
                while k < len(line) and line[k].isalnum():
                    k += 1
                add_error(line[i:k], "Invalid number")
                i = k
            else:
                add_token("NUM", lexeme)
                i = j
            continue

        # IDENTIFIER or KEYWORD
        if c.isalpha():
            j = i
            while j < len(line) and line[j].isalnum():
                j += 1
            lexeme = line[i:j]
            if lexeme in keywords:
                add_token("KEYWORD", lexeme)
            else:
                add_token("ID", lexeme)
                add_to_symbol_table(lexeme)
            i = j
            continue

        # Invalid character
        add_error(c, "Invalid input")
        i += 1

def main():
    global lineno
    with open("input.txt", "r", encoding="utf-8") as f:
        for line in f:
            lineno += 1
            tokenize_line(line)

    # Write token output
    with open("tokens.txt", "w", encoding="utf-8") as f:
        for token in token_output:
            f.write(token + "\n")

    # Write lexical errors
    with open("lexical_errors.txt", "w", encoding="utf-8") as f:
        if lexical_errors:
            for err in lexical_errors:
                f.write(err + "\n")
        else:
            f.write("There is no lexical error.\n")

    # Write symbol table
    with open("symbol_table.txt", "w", encoding="utf-8") as f:
        for i, entry in enumerate(symbol_table, 1):
            f.write(f"{i}.\t{entry}\n")

if __name__ == "__main__":
    main()
