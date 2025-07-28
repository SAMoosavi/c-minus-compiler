class CodeGenerator:
    def __init__(self):
        self.output = []
        self.temp_count = 500  # شروع آدرس برای متغیرهای موقتی
        self.line_no = 0
        self.symbol_table = {}  # نگهداری آدرس متغیرها
        self.jump_stack = []  # برای کنترل پرش‌ها (مثل repeat)
        self.program_block = []
        self.label_counter = 0

    def new_temp(self):
        temp = self.temp_count
        self.temp_count += 4
        return temp

    def get_var_address(self, name):
        if name not in self.symbol_table:
            self.symbol_table[name] = len(self.symbol_table) * 4 + 100
        return self.symbol_table[name]

    def add_code(self, code):
        self.program_block.append(code)

    def emit(self, op, arg1="", arg2="", result=""):
        self.output.append(f"({op}, {arg1}, {arg2}, {result})")

    def backpatch(self, line_no, label):
        old_line = self.output[line_no]
        parts = old_line.split("(")[1].strip(")").split(",")
        parts = [p.strip() for p in parts]
        parts[2] = label  # جایگزینی مقصد پرش
        new_line = f"{line_no}\t({parts[0]}, {parts[1]}, {parts[2]}, {parts[3]})"
        self.output[line_no] = new_line

    def new_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def write_output(self, filename="output.txt"):
        if not self.output:
            with open(filename, "w") as f:
                for i, line in enumerate(self.program_block):
                    f.write(f"{i}\t{line}\n")
        else:
            with open(filename, "w") as f:
                for i, line in enumerate(self.output):
                    f.write(f"{i}\t{line}\n")
        print("\nSymbol Table:")
        for name, addr in self.symbol_table.items():
            print(f"{name}: {addr}")
