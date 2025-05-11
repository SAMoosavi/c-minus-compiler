from antlr4 import FileStream, CommonTokenStream
from CMinus import CMinus

class ANTLRScanner:
    def __init__(self, input_file="input.txt"):
        self.lexer = CMinus(FileStream(input_file, encoding='utf-8'))
        self.tokens = CommonTokenStream(self.lexer)
        self.tokens.fill()
        self.index = 0
        self.symbol_table = []
        self.symbol_set = set()
        self.lexical_errors = []
        self.valid_tokens = []

    def get_next_token(self):
        if self.index >= len(self.tokens.tokens) - 1:  # -1 to skip EOF
            return None
        token = self.tokens.tokens[self.index]
        self.index += 1

        token_type = self.lexer.symbolicNames[token.type]
        token_text = token.text
        token_line = token.line

        # Handle error tokens
        if token_type == "INVALID":
            self.lexical_errors.append(f"{token_line}\t({token_text}, Invalid input)")
            return None

        # Handle invalid comment (you may define this in grammar too)
        if token_type == "UnclosedComment":
            self.lexical_errors.append(f"{token_line}\t({token_text}, Unclosed comment)")
            return None
        
        if token_type == "UNMATCHED_COMMENT":
            self.lexical_errors.append(f"{token_line}\t({token_text}, Unmatched comment)")
            return None

        # Track IDs in symbol table
        if token_type == "ID":
            if token_text not in self.symbol_set:
                self.symbol_set.add(token_text)
                self.symbol_table.append(token_text)

        # Save valid token
        self.valid_tokens.append(f"{token_line}\t({token_type}, {token_text})")
        return (token_line, token_type, token_text)

    def scan_all(self):
        while True:
            if self.get_next_token() is None and self.index >= len(self.tokens.tokens) - 1:
                break

    def write_outputs(self):
        with open("tokens.txt", "w", encoding="utf-8") as f:
            for tok in self.valid_tokens:
                f.write(tok + "\n")

        with open("lexical_errors.txt", "w", encoding="utf-8") as f:
            if self.lexical_errors:
                for err in self.lexical_errors:
                    f.write(err + "\n")
            else:
                f.write("There is no lexical error.\n")

        with open("symbol_table.txt", "w", encoding="utf-8") as f:
            for idx, sym in enumerate(self.symbol_table, 1):
                f.write(f"{idx}.\t{sym}\n")

if __name__ == "__main__":
    scanner = ANTLRScanner("input.txt")
    scanner.scan_all()
    scanner.write_outputs()
    print("✅ Done: tokens, errors and symbol table written.")
