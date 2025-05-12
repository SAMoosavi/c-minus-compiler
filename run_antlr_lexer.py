
from antlr4 import FileStream, CommonTokenStream
from CMinus import CMinus

def main():
    input_file = "input.txt"
    output_file = "ANTLR_p1.txt"

    # Set up lexer
    stream = FileStream(input_file)
    lexer = CMinus(stream)

    # Correct way to get all tokens
    tokens = []
    token = lexer.nextToken()
    while token.type != -1:
        token_type = lexer.symbolicNames[token.type]
        if token_type != "INVALID":
            tokens.append(token)
        token = lexer.nextToken()

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        for token in tokens:
            token_type = lexer.symbolicNames[token.type]
            f.write(f"{token.line}\t({token_type}, {token.text})\n")

if __name__ == "__main__":
    main()
