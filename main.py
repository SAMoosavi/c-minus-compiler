from scanner import Scanner
from parser import Parser
from shared import parse_tree_lines, syntax_errors

def main():
    with open("input.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    scanner = Scanner(lines)
    parser = Parser(scanner)
    parser.parse()

    with open("parse_tree.txt", "w", encoding="utf-8") as f:
        for line in parse_tree_lines:
            f.write(line + "\n")

    with open("syntax_errors.txt", "w", encoding="utf-8") as f:
        if syntax_errors:
            for err in syntax_errors:
                f.write(err + "\n")
        else:
            f.write("There is no syntax error.\n")

if __name__ == "__main__":
    main()
