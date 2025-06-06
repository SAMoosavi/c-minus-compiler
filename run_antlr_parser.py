from antlr4 import FileStream, CommonTokenStream
from CMinus import CMinus
from CMinusParser import CMinusParser
from antlr4.tree.Trees import Trees
from rich.tree import Tree as RichTree
from rich import print
from io import StringIO


def convert_to_rich_tree(parse_tree, rule_names, parent=None):
    text = Trees.getNodeText(parse_tree, rule_names)
    current = RichTree(text) if parent is None else parent.add(text)

    for i in range(parse_tree.getChildCount()):
        convert_to_rich_tree(parse_tree.getChild(i), rule_names, current)

    return current

def rich_tree_to_string(tree):
    out = StringIO()
    print(tree, file=out)
    return out.getvalue()

def main():
    input_file = "input.txt"
    stream = FileStream(input_file, encoding="utf-8")

    # Lexer
    lexer = CMinus(stream)
    token_stream = CommonTokenStream(lexer)

    # Parser
    parser = CMinusParser(token_stream)
    tree = parser.program()  # Start from the root rule

    # Convert parse tree to a rich tree and print it
    rule_names = parser.ruleNames
    rich_tree = convert_to_rich_tree(tree, rule_names)
    with open("antlr_parse_tre.txt", 'w') as f:
        f.write(rich_tree_to_string(rich_tree))

if __name__ == "__main__":
    main()
