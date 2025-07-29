class CodeGenerator:
    def __init__(self):
        self.output = []
        self.temp_count = 500
        self.symbol_table = {}

    def new_temp(self):
        temp = self.temp_count
        self.temp_count += 4
        return temp

    def get_var_address(self, name):
        if name not in self.symbol_table:
            self.symbol_table[name] = len(self.symbol_table) * 4 + 100
        return self.symbol_table[name]

    def emit(self, op, arg1="", arg2="", result=""):
        self.output.append(f"({op}, {arg1}, {arg2}, {result})")

    def write_output(self, filename="output.txt"):
        with open(filename, "w") as f:
            for i, line in enumerate(self.output):
                f.write(f"{i}\t{line}\n")

        print("\nSymbol Table:")
        for name, addr in self.symbol_table.items():
            print(f"{name}: {addr}")
