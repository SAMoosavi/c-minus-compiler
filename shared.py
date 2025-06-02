# shared.py

parse_tree_lines = []
syntax_errors = []

def add_tree_line(depth, node):
    parse_tree_lines.append('\t' * depth + node)

def add_syntax_error(lineno, error):
    syntax_errors.append(f"{lineno}\t{error}")
