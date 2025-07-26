class CodeGenerator:
    def __init__(self):
        self.output = []
        self.temp_count = 500  # شروع آدرس برای متغیرهای موقتی
        self.line_no = 0
        self.symbol_table = {}  # نگهداری آدرس متغیرها
        self.jump_stack = []  # برای کنترل پرش‌ها (مثل repeat)

    def new_temp(self):
        temp = self.temp_count
        self.temp_count += 4
        return temp

    def get_var_address(self, name):
        if name not in self.symbol_table:
            self.symbol_table[name] = len(self.symbol_table) * 4 + 100
        return self.symbol_table[name]

    def emit(self, op, arg1="", arg2="", result=""):
        line = f"{self.line_no}\t({op}, {arg1}, {arg2}, {result})"
        self.output.append(line)
        self.line_no += 1
        return self.line_no - 1  # شماره خط تولیدشده

    def backpatch(self, line_no, label):
        old_line = self.output[line_no]
        parts = old_line.split("(")[1].strip(")").split(",")
        parts = [p.strip() for p in parts]
        parts[2] = label  # جایگزینی مقصد پرش
        new_line = f"{line_no}\t({parts[0]}, {parts[1]}, {parts[2]}, {parts[3]})"
        self.output[line_no] = new_line

    def write_output(self, filename="output.txt"):
        if not self.output:
            with open(filename, "w") as f:
                f.write("The output code has not been generated\n")
        else:
            with open(filename, "w") as f:
                f.write("\n".join(self.output))
