import random as rd
from io import TextIOWrapper

CONDITION_OPERANDS = ["<", "<=", ">=", ">", "==", "!="]

ARITHMETICAL_OPERANDS = ["+=", "-=", "*=", "/="]

VAR_IN_BLOCK_CAP = 2

BLOCKS_IN_BLOCK_CAP = 2

output_file: TextIOWrapper

blocks_left = 100

# Storing variables that are available to the current block
var_stack = []

var_number = 0


class BaseBlock:
    def __init__(self, sp, tabs=0):
        self.sp = sp  # Number of variables created in the block
        self.children = []  # Children in the block tree
        self.tabs = tabs
        if blocks_left > 0:
            self.blocks_generator()
        else:
            if self is IfBlock:
                self.children.append(CalculationBlock(rd.randint(2, 8), self.tabs + 1))
                self.else_children.append(CalculationBlock(rd.randint(2, 8), self.tabs + 1))
            else:
                if rd.choice((0, 1)):
                    self.children.append(CalculationBlock(rd.randint(2, 8), self.tabs + 1))

    def render(self):
        for i in range(self.sp):
            output_file.write("\t" * (self.tabs + 1) + self.var_create() + "\n")

        for block in self.children:
            block.render()

        # self.del_unavlb_vars()

    def blocks_generator(self):
        global blocks_left
        blocks = rd.sample(
            [block for key in probability for block in probability[key]],
            rd.randint(1, BLOCKS_IN_BLOCK_CAP),
        )

        blocks_left -= len(blocks)

        for block in blocks:
            self.children.append(block(rd.randint(0, VAR_IN_BLOCK_CAP), self.tabs + 1))

    def del_unavlb_vars(self):
        global var_number
        for _ in range(self.sp):
            var_stack.pop()
            var_number -= 1

    @staticmethod
    def var_create(liter="a", value=1):
        global var_number
        var_number += 1
        var_stack.append(f"{liter}{var_number}")
        if value:
            return f"int {liter}{var_number} = {rd.randint(0, 100)};"
        return f"int {liter}{var_number} = {value};"

    @staticmethod
    def statement_generate(var, condition=False, cycle=False):
        if condition:
            operand = rd.choice(CONDITION_OPERANDS)
        elif cycle:
            operand = rd.choice(CONDITION_OPERANDS[:2])
        else:
            operand = rd.choice(ARITHMETICAL_OPERANDS)

        term = rd.choice((rd.randint(0, 100), rd.choice(var_stack)))
        if operand == "/=":
            return f"{var} {operand} D0({term})"

        return f"{var} {operand} {term}"


class CalculationBlock(BaseBlock):
    def __init__(self, expr, tabs):
        self.expr = expr
        super().__init__(0, tabs)

    def blocks_generator(self):
        pass

    def render(self):
        for _ in range(self.expr):
            var_ = rd.choice(var_stack)
            while var_[0] == "f":
                var_ = rd.choice(var_stack)

            output_file.write("\t" * self.tabs + f"{self.statement_generate(var_)};\n")


class IfBlock(BaseBlock):
    def __init__(self, sp, tabs):
        self.else_children = []
        super().__init__(sp, tabs)

    def blocks_generator(self):
        super().blocks_generator()
        self.children.insert(0, CalculationBlock(rd.randint(2, 8), self.tabs + 1))

        self.else_children = self.children[::]
        self.children = []

        super().blocks_generator()
        self.children.insert(0, CalculationBlock(rd.randint(2, 8), self.tabs + 1))

    def render(self):
        output_file.write(
            "\t" * self.tabs + f"if ({self.statement_generate(rd.choice(var_stack), condition=True)})" + "{\n"
        )
        super().render()
        output_file.write("\t" * self.tabs + "}\n")
        self.del_unavlb_vars()

        self.children = self.else_children

        output_file.write("\t" * self.tabs + "else{\n")
        super().render()
        output_file.write("\t" * self.tabs + "}\n")
        self.del_unavlb_vars()


class ForBlock(BaseBlock):
    def render(self):
        output_file.write(
            "\t" * self.tabs + f'for ({self.var_create("f", 0)}'
            f"{self.statement_generate(var_stack[-1], cycle=True)};"
            f"{var_stack[-1]}++)" + "{\n"
        )

        super().render()
        self.sp += 1

        output_file.write("\t" * self.tabs + "}\n")

        self.del_unavlb_vars()

    def blocks_generator(self):
        super().blocks_generator()
        if rd.choice((0, 1)):
            self.children.insert(0, CalculationBlock(rd.randint(2, 8), self.tabs + 1))


def generate_test(file, total_blocks, blocks_cap, vars_cap):
    global output_file, VAR_IN_BLOCK_CAP, BLOCKS_IN_BLOCK_CAP, blocks_left, var_stack, var_number
    blocks_left = total_blocks
    BLOCKS_IN_BLOCK_CAP = blocks_cap
    VAR_IN_BLOCK_CAP = vars_cap
    var_stack = []
    var_number = 0

    output_file = open(file, "w")
    output_file.write("# define D0(x) (x==0) ? 1 : x\n\n" "void test_fun(){\n")
    program = BaseBlock(2, 0)
    program.render()
    output_file.write("}")

    output_file.close()


probability = {
    ForBlock: [ForBlock] * 5,
    IfBlock: [IfBlock] * 5,
}
