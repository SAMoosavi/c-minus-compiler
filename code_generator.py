class CodeGenerator:
    def __init__(self):
        self.output = []  # list of tuples (op, arg1, arg2, result)
        self.temp_count = 500
        self.symbol_table = {}
        self.break_target_stack = []  # stack for nested repeat-until
        self.break_jumps = []  # stack of lists for break jump indices

    def emit(self, op, arg1="", arg2="", result=""):
        line_no = len(self.output)

        # Track break jumps needing backpatch
        if op == "JP" and arg1 == "TO_BE_FILLED":
            if not self.break_jumps:
                self.break_jumps.append([])  # ensure at least one level exists
            self.break_jumps[-1].append(line_no)

        self.output.append(f"({op}, {arg1}, {arg2}, {result})")

    def resolve_breaks(self, target_line):
        if not self.break_jumps:
            return

        for index in self.break_jumps[-1]:
            self.output[index] = f"(JP, {target_line}, , )"

        self.break_jumps.pop()

    def new_temp(self):
        temp = self.temp_count
        self.temp_count += 4
        return temp

    def get_var_address(self, name):
        if name not in self.symbol_table:
            self.symbol_table[name] = len(self.symbol_table) * 4 + 100
        return self.symbol_table[name]

    def write_output(self, filename="output.txt"):
        with open(filename, "w") as f:
            for i, line in enumerate(self.output):
                f.write(f"{i}\t{line}\n")

        print("\nSymbol Table:")
        for name, addr in self.symbol_table.items():
            print(f"{name}: {addr}")
