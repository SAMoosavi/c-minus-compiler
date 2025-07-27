from scanner import Scanner
from parser import Parser

def write_to_file(filename: str, content: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    with open("input.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    scanner = Scanner(lines)
    parser = Parser(scanner)

    try:
        parse_tree_lines, syntax_errors = parser.parse()
        parser.code_gen.write_output("output.txt")
    except SyntaxError as e:
        syntax_error_msg, parse_tree_str = e.args[0]
        write_to_file("syntax_errors.txt", syntax_error_msg)
        write_to_file("parse_tree.txt", parse_tree_str)
    else:
        write_to_file("syntax_errors.txt", "There is no syntax error.\n")
        write_to_file("parse_tree.txt", parse_tree_lines)

if __name__ == "__main__":
    main()
