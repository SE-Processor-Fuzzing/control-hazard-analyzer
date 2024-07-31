import random as rd
from copy import copy
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Protocol, Tuple, Type, TypeVar

from typing_extensions import Self

K_T = TypeVar("K_T")


def get_random_key(dct: Dict[K_T, int]) -> K_T:
    """
    Get random key from dict where values is weights.

    :param dct: A used dict.
    :return: Key from dct.
    """
    return rd.choices(list(dct.keys()), weights=list(dct.values()))[0]


class Visitor(Protocol):
    def __init__(self) -> None: ...

    def send(self, string: str) -> None: ...


@dataclass
class Probabilities:
    blocks_chanses: Dict[Type["Block"], int]
    blocks_cut: Tuple[int, int]


class Scope:

    def __init__(
        self,
        max_depth: int,
        operators: Optional[List[str]] = None,
        condition_operators: Optional[List[str]] = None,
    ) -> None:
        if operators is None:
            operators = ["+", "-", "/", "*"]
        if condition_operators is None:
            condition_operators = [">", "<", ">=", "<=", "==", "!="]
        self.operators = operators
        self.condition_operators = condition_operators
        self.current_depth = max_depth
        self.vars: List[str] = []
        self.funcs: List[str] = []
        self.arrs: List[str] = []
        self.vars_count = 0
        self.funcs_count = 0
        self.arrs_count = 0
        self.funcs_args_number: Dict[str, int] = {}
        self.funcs_by_args_number: Dict[int, List[str]] = {}
        self.arrs_args_number: Dict[str, int] = {}
        self.arrs_funcs_number: Dict[str, int] = {}

    def create_new_var(self, prefix: str = "a") -> str:
        self.vars.append(var := f"{prefix}{self.vars_count}")
        self.vars_count += 1
        return var

    def get_random_var(self, rule: Optional[Callable[[str], bool]] = None) -> str:
        if rule is None:
            return rd.choice(self.vars)
        return rd.choice(list(filter(rule, self.vars)))

    def create_new_func(self, prefix: str = "func") -> str:
        self.funcs.append(var := f"{prefix}{self.funcs_count}")
        self.funcs_count += 1
        return var

    def get_random_func(self, rule: Optional[Callable[[str], bool]] = None) -> str:
        if rule is None:
            return rd.choice(self.funcs)
        return rd.choice(list(filter(rule, self.funcs)))

    def create_random_arr(self, prefix: str = "arr") -> str:
        self.arrs.append(arr := f"{prefix}{self.arrs_count}")
        self.arrs_count += 1
        return arr

    def get_random_arr(self, rule: Optional[Callable[[str], bool]] = None) -> str:
        if rule is None:
            return rd.choice(self.arrs)
        return rd.choice(list(filter(rule, self.arrs)))

    def get_random_vars(self, rule: Optional[Callable[[str], bool]] = None, count: int = 1) -> List[str]:
        _vars = self.vars
        if rule is not None:
            _vars = list(filter(rule, _vars))
        if count > len(_vars):
            return rd.choices(_vars, k=count)
        return rd.sample(_vars, k=count)

    def get_random_operator(self) -> str:
        return rd.choice(self.operators)

    def get_random_cond_operator(self) -> str:
        return rd.choice(self.condition_operators)

    def copy(self) -> Self:
        c = copy(self)
        c.vars = self.vars[:]
        c.funcs = self.funcs[:]
        return c


class Block(Protocol):

    def render(self, visitor: Visitor) -> None: ...


class DefineBlock(Block):
    max_value = 100

    def __init__(self, var: str, value: int) -> None:
        self.var = var
        self.value = value

    # def __init__(self, env: Scope, _: Probabilities) -> None:
    #     self.var = env.create_new_var()
    #     self.value = rd.randint(0, DefineBlock.max_value)

    def render(self, visitor: Visitor) -> None:
        string = f"int {self.var} = {self.value};"
        visitor.send(string)


@dataclass
class ApplyBinOperator:
    lvar: str
    rvar: str
    operator: str

    def render(self) -> str:
        return f"{self.lvar} {self.operator} {self.rvar}"


class OperationBlock(Block):

    def __init__(self, cur_var: str, cond: ApplyBinOperator) -> None:
        self.cur_var = cur_var
        self.statement = cond

    # def __init__(self, env: Scope, probs: Probabilities) -> None:
    #     rule: Callable[[str], bool] = lambda x: x.startswith("a")
    #     self.cur_var = env.get_random_var(rule=rule)

    #     operator = env.get_random_operator()
    #     lvar, rvar = env.get_random_var(), env.get_random_var()
    #     rvar = f"(D0({rvar}))" if operator == "/" else rvar

    #     self.statement = ApplyBinOperator(lvar, rvar, operator)

    def render(self, visitor: Visitor) -> None:
        string = f"{self.cur_var} = {self.statement.render()};"
        visitor.send(string)


class IfConditionBlock(Block):

    def __init__(self, cond: ApplyBinOperator, then_blocks: List[Block], else_blocks: List[Block]) -> None:
        self.condition = cond
        self.then_blocks = then_blocks
        self.else_blocks = else_blocks

    def render(self, visitor: Visitor) -> None:
        string = f"if ({self.condition.render()}) {{"
        visitor.send(string)
        for block in self.then_blocks:
            block.render(visitor)
        visitor.send("} else {")
        for block in self.else_blocks:
            block.render(visitor)
        visitor.send("}")


class ForBlock(Block):
    max_value = 100

    def __init__(self, def_var: str, cond: ApplyBinOperator, next_blocks: List[Block]) -> None:
        self.def_var = def_var
        self.condition = cond
        self.next_blocks = next_blocks

    def render(self, visitor: Visitor) -> None:
        string = f"for (int {self.def_var} = 0; {self.condition.render()}; {self.def_var}++) {{"
        visitor.send(string)
        for block in self.next_blocks:
            block.render(visitor)
        visitor.send("}")


class EntryPointBlock(Block):

    def __init__(
        self, func_sign_blocks, func_blocks: List[Block], func_arr_blocks: List[Block], next_blocks: List[Block]
    ) -> None:
        self.func_sign_blocks = func_sign_blocks
        self.func_blocks = func_blocks
        self.func_arr_blocks = func_arr_blocks
        self.next_blocks = next_blocks

    def render(self, visitor: Visitor) -> None:
        string = "# define D0(x) (x==0) ? 1 : x\n\n"
        visitor.send(string)

        for func in self.func_sign_blocks:
            func.render(visitor)

        for arr in self.func_arr_blocks:
            arr.render(visitor)

        for func in self.func_blocks:
            func.render(visitor)

        visitor.send("void test_fun() { ")

        for block in self.next_blocks:
            block.render(visitor)
        visitor.send("}")


class DefineFunctionArrayBlock(Block):
    """Class of representation array of functions block

    :param arr: name of array
    :param args_num: number of function's arguments
    :param func_names: names of functions in array
    """

    def __init__(self, arr: str, args_num: int, func_names: List[str]) -> None:
        """Constructor method"""
        self.args_num = args_num
        self.name = arr
        self.funcs = func_names

    def render(self, visitor: Visitor) -> None:
        """Method for render block into code

        :param visitor: object of Visitor that render block construction
        :return: None
        """
        visitor.send(f"void (*{self.name}[])(")

        for _ in range(self.args_num - 1):
            visitor.send("int, ")
        visitor.send("int) = { ")

        for i in range(len(self.funcs) - 1):
            visitor.send(f"{self.funcs[i]}, ")
        visitor.send(f"{self.funcs[-1]} }};\n\n")


class CallFunctionArrayBlock(Block):
    """Class of representation function call by pointer from array block

    :param arr: name of array
    :param args: names of variables that we pass to the function
    :param index: index of function in array
    :param arr_len: length of array
    """

    def __init__(self, arr: str, args: List[str], index: str, arr_len: int) -> None:
        """Constructor method"""
        self.name = arr
        self.args = args
        self.index = index
        self.arr_len = arr_len

    def render(self, visitor: Visitor) -> None:
        """Method for render block into code

        :param visitor: object of Visitor that render block construction
        :return: None
        """
        visitor.send(f"{self.name}[{self.index} % {self.arr_len}](")

        for i in range(len(self.args) - 1):
            visitor.send(f"{self.args[i]}, ")
        visitor.send(f"{self.args[-1]}); ")


class SignatureFunctionBlock(Block):
    def __init__(self, func: str, args: List[str]) -> None:
        self.name = func
        self.args = args

    def render(self, visitor: Visitor) -> None:
        visitor.send(f"void {self.name}(")
        for i in range(len(self.args)):
            visitor.send(f"int {self.args[i]}")
            if i != len(self.args) - 1:
                visitor.send(", ")
        visitor.send(");\n")


class DefineFunctionBlock(Block):
    """Class of representation function block

    :param func: name of function
    :param args: names of function's variables
    """

    def __init__(self, func: str, args: List[str], next_blocks: List[Block]) -> None:
        """Constructor method"""
        self.name = func
        self.args = args
        self.next_blocks = next_blocks

    def render(self, visitor: Visitor) -> None:
        """Method for render block into code

        :param visitor: object of Visitor that render block construction
        :return: None
        """
        visitor.send(f"void {self.name}(")
        for i in range(len(self.args)):
            visitor.send(f"int {self.args[i]}")
            if i != len(self.args) - 1:
                visitor.send(", ")
        visitor.send(") {")
        for block in self.next_blocks:
            block.render(visitor)
        visitor.send("}\n\n")


class FuncBlock(Block):
    """Class of representation function call by name block

    :param func: name of function
    :param args: names of variables that we pass to the function
    """

    def __init__(self, func: str, args: List[str]) -> None:
        """Constructor method"""
        self.name = func
        self.args = args

    def render(self, visitor: Visitor) -> None:
        """Method for render block into code

        :param visitor: object of Visitor that render block construction
        :return: None
        """
        visitor.send(f"{self.name}(")
        for i in range(len(self.args)):
            visitor.send(f"{self.args[i]}")
            if i != len(self.args) - 1:
                visitor.send(", ")
        visitor.send("); ")


class SwitchCaseBlock(Block):
    """Class of representation switch-case construction block

    :param expr: expression in switch
    :param case_blocks: list of blocks in each case
    :param cases: values for each case
    """

    def __init__(self, expr: ApplyBinOperator, case_blocks: List[List[Block]], cases: List[int]) -> None:
        """Constructor method"""
        self.expression = expr
        self.case_blocks = case_blocks
        self.cases = cases

    def render(self, visitor: Visitor) -> None:
        """Method for render block into code

        :param visitor: object of Visitor that render block construction
        :return: None
        """
        string = f"switch ({self.expression.render()}) {{"
        visitor.send(string)

        for i in range(len(self.cases)):
            visitor.send(f"case {self.cases[i]}: {{")
            for block in self.case_blocks[i]:
                block.render(visitor)
            visitor.send("break; }")
        visitor.send("default: {")

        if len(self.case_blocks) != 0:
            for block in self.case_blocks[-1]:
                block.render(visitor)
        visitor.send("}} ")


class Generator:
    def __init__(
        self,
        scope: Scope,
        probs: Probabilities,
        random_seed: int | None = 42,
        **kwargs: Dict[str, int],
    ) -> None:
        self.probs = probs
        rd.seed(random_seed)
        self.env = scope
        self.block_generation_functions: Dict[Type[Block], Callable[[Scope], Block]] = {
            DefineBlock: self.__gen_definition,
            ForBlock: self.__gen_for,
            IfConditionBlock: self.__gen_if,
            OperationBlock: self.__gen_operation,
            SwitchCaseBlock: self.__gen_switch,
            FuncBlock: self.__gen_func_call,
            CallFunctionArrayBlock: self.__gen_func_arr_call,
        }
        self.gen_functions_probabilities = {
            self.block_generation_functions[block]: chanse for block, chanse in probs.blocks_chanses.items()
        }

    def render(self, visitor: Visitor) -> None:
        self.entry_point.render(visitor)

    def gen(self) -> None:
        env_copy = self.env.copy()

        func_sign_blocks = self.__gen_sign_funcs(env_copy)
        funcs_blocks = self.__gen_def_funcs(env_copy)
        var = env_copy.create_new_var()
        value = rd.randint(0, DefineBlock.max_value)
        def_block: Block = DefineBlock(var, value)
        func_arrs_blocks = self.__gen_def_func_arrs(env_copy)

        next_blocks: List[Block] = [def_block]
        next_blocks.extend(self.__gen_local(env_copy, env_copy.funcs_count))
        self.entry_point = EntryPointBlock(func_sign_blocks, funcs_blocks, func_arrs_blocks, next_blocks)

    def __gen_def_func_arrs(self, env: Scope) -> List[Block]:
        """Method that generate arrays of functions in program

        :param env: environment that keeps all for creating new lines of code
        :return: blocks of code with definition of arrays of functions
        """

        arrs_blocks: List[Block] = []
        for args_num, funcs in env.funcs_by_args_number.items():
            arr = env.create_random_arr()
            env.arrs_funcs_number[arr] = len(funcs)
            env.arrs_args_number[arr] = args_num
            arrs_blocks.append(DefineFunctionArrayBlock(arr, args_num, funcs))

        return arrs_blocks

    def __gen_func_arr_call(self, env: Scope) -> CallFunctionArrayBlock:
        """Method that generate function's call by pointer from array block

        :param env: environment that keeps all for creating new lines of code
        :return: new block of code with function's call by pointer
        """
        arr = env.get_random_arr()
        args_num = env.arrs_args_number[arr]
        funcs_num = env.arrs_funcs_number[arr]
        index = env.get_random_var()
        args = env.get_random_vars(count=args_num)

        return CallFunctionArrayBlock(arr, args, index, funcs_num)

    def __gen_sign_funcs(self, env: Scope) -> List[Block]:
        funcs_number = rd.randint(10, 20)
        func_sign_blocks: List[Block] = []

        for _ in range(funcs_number):
            func = env.create_new_func()
            func_args_number = rd.randint(1, 4)
            env.funcs_args_number[func] = func_args_number
            env.funcs_by_args_number[func_args_number] = env.funcs_by_args_number.get(func_args_number, []) + [func]

            env_copy = env.copy()
            func_args: List[str] = []
            for __ in range(func_args_number):
                func_args.append(env_copy.create_new_var(prefix="arg"))
            func_sign_blocks.append(SignatureFunctionBlock(func, func_args))

        return func_sign_blocks

    def __gen_def_funcs(self, env: Scope) -> List[Block]:
        """Method that generate functions in program

        :param env: environment that keeps all for creating new lines of code
        :return: new block of code with function
        """
        func_blocks: List[Block] = []

        for i in range(env.funcs_count):
            func = env.funcs[i]
            env_copy = env.copy()
            func_args: List[str] = []
            for _ in range(env.funcs_args_number[func]):
                func_args.append(env_copy.create_new_var(prefix="arg"))

            func_content_block = self.__gen_local(env_copy, i)
            func_blocks.append(DefineFunctionBlock(func, func_args, func_content_block))

        return func_blocks

    def __gen_func_call(self, env: Scope, curr_func_num: int) -> FuncBlock:
        """Method that generate function's call by name block

        :param env: environment that keeps all for creating new lines of code
        :param curr_func_num: number of the function in which creation occurs
        :return: new block of code with function's call by name
        """
        func = env.get_random_func(rule=lambda x: int(x[4:]) < curr_func_num)
        args = env.get_random_vars(count=env.funcs_args_number[func])

        return FuncBlock(func, args)

    def __gen_local(self, env: Scope, curr_func_num: int) -> List[Block]:
        env.current_depth -= 1
        if env.current_depth <= 0:
            return []
        gen_blocks: List[Block] = []
        number_of_blocks = rd.randint(*self.probs.blocks_cut)
        for _ in range(number_of_blocks):
            gen_func = get_random_key(self.gen_functions_probabilities)
            while (
                gen_func == self.__gen_func_call
                and curr_func_num == 0
                or gen_func == self.__gen_func_arr_call
                and env.arrs_count == 0
            ):
                gen_func = get_random_key(self.gen_functions_probabilities)

            next_block = (
                gen_func(env)
                if (
                    gen_func
                    in [
                        self.__gen_def_funcs,
                        self.__gen_operation,
                        self.__gen_definition,
                        self.__gen_func_arr_call,
                    ]
                )
                else gen_func(env, curr_func_num)
            )
            gen_blocks.append(next_block)
        return gen_blocks

    def __gen_for(self, env: Scope, curr_func_num: int) -> ForBlock:
        env_copy = env.copy()

        def_var = env_copy.create_new_var(prefix="f")
        cond = ApplyBinOperator(def_var, str(rd.randint(2, ForBlock.max_value)), "<=")
        next_blocks = self.__gen_local(env_copy, curr_func_num)

        block = ForBlock(def_var, cond, next_blocks)
        return block

    def __gen_if(self, env: Scope, curr_func_num: int) -> IfConditionBlock:
        env_copy = env.copy()

        lvar, rvar = env_copy.get_random_vars(count=2)
        cond = ApplyBinOperator(lvar, rvar, env_copy.get_random_cond_operator())
        then_blocks = self.__gen_local(env.copy(), curr_func_num)
        else_blocks = self.__gen_local(env.copy(), curr_func_num)

        block = IfConditionBlock(cond, then_blocks, else_blocks)
        return block

    def __gen_operation(self, env: Scope) -> OperationBlock:
        rule: Callable[[str], bool] = lambda x: x.startswith("a")
        cur_var = env.get_random_var(rule=rule)

        operator = env.get_random_operator()
        lvar, rvar = env.get_random_var(), env.get_random_var()
        rvar = f"(D0({rvar}))" if operator == "/" else rvar
        statement = ApplyBinOperator(lvar, rvar, operator)

        return OperationBlock(cur_var, statement)

    def __gen_definition(self, env: Scope) -> DefineBlock:
        var = env.create_new_var()
        value = rd.randint(0, DefineBlock.max_value)

        return DefineBlock(var, value)

    def __gen_switch(self, env: Scope, curr_func_num: int) -> SwitchCaseBlock:
        """Method that generate switch-case block

        :param env: environment that keeps all for creating new lines of code
        :param curr_func_num: number of the function in which creation occurs
        :return: new block of code with switch-case
        """
        env_copy = env.copy()

        lvar, rvar = env_copy.get_random_vars(count=2)
        operator = env_copy.get_random_operator()
        rvar = f"(D0({rvar}))" if operator == "/" else rvar
        expr = ApplyBinOperator(lvar, rvar, operator)
        cases = [rd.randint(-100000, 100000) for _ in range(rd.randint(0, 3))]
        case_blocks = [self.__gen_local(env.copy(), curr_func_num) for _ in range(len(cases) + 1)]

        block = SwitchCaseBlock(expr, case_blocks, cases)
        return block


class Accum:
    def __init__(self) -> None:
        self.acc = ""

    def send(self, string: str) -> None:
        self.acc += string

    def get_acc(self) -> str:
        return self.acc


def gen_test(
    max_depth: int = 3,
    seed: int = 42,
    operators: List[str] | None = None,
    cond_operators: List[str] | None = None,
    **kwargs: int,
) -> str:

    ch_for = kwargs.get("ch_def", 12)
    ch_if = kwargs.get("ch_def", 12)
    ch_state = kwargs.get("ch_state", 12)
    ch_def = kwargs.get("ch_def", 12)
    ch_switch = kwargs.get("ch_def", 12)
    ch_func = kwargs.get("ch_def", 12)
    ch_arr = kwargs.get("ch_func", 12)

    if operators is None:
        operators = ["+", "-", "/", "*"]

    if cond_operators is None:
        cond_operators = ["<", "<=", ">", ">=", "==", "!="]

    probs = Probabilities(
        blocks_chanses={
            ForBlock: ch_for,
            IfConditionBlock: ch_if,
            DefineBlock: ch_def,
            OperationBlock: ch_state,
            SwitchCaseBlock: ch_switch,
            FuncBlock: ch_func,
            CallFunctionArrayBlock: ch_arr,
        },
        blocks_cut=(2, 5),
    )

    scope = Scope(max_depth, operators, cond_operators)
    g = Generator(scope, probs, random_seed=seed)
    acc = Accum()
    g.gen()
    g.render(acc)
    return acc.get_acc()
