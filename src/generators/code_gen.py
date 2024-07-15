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
        self.vars_count = 0

    def create_new_var(self, prefix: str = "a") -> str:
        self.vars.append(var := f"{prefix}{self.vars_count}")
        self.vars_count += 1
        return var

    def get_random_var(self, rule: Optional[Callable[[str], bool]] = None) -> str:
        if rule is None:
            return rd.choice(self.vars)
        return rd.choice(list(filter(rule, self.vars)))

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

    def __init__(self, next_blocks: List[Block]) -> None:
        self.next_blocks = next_blocks

    def render(self, visitor: Visitor) -> None:
        string = "# define D0(x) (x==0) ? 1 : x\n\nvoid test_fun() {"
        visitor.send(string)
        for block in self.next_blocks:
            block.render(visitor)
        visitor.send("}")


class SwitchCaseBlock(Block):
    """
    Class of representation switch-case construction block.

    Attributes
    --------
    expression : ApplyBinOperator
        expression in switch
    case_blocks : List[List[Block]]
        list of blocks in each case
    cases : List[int]
        values for each case
    """

    def __init__(self, expr: ApplyBinOperator, case_blocks: List[List[Block]], cases: List[int]) -> None:
        """
        Sets all required attributes for an object SwitchCaseBlock.
        :param expr: expression in switch
        :param case_blocks: list of blocks in each case
        :param cases: values for each case
        """
        self.expression = expr
        self.case_blocks = case_blocks
        self.cases = cases

    def render(self, visitor: Visitor) -> None:
        """
        Function for render block into code.
        :param visitor: object of Visitor that render block construction.
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
        }
        self.gen_functions_probabilities = {
            self.block_generation_functions[block]: chanse for block, chanse in probs.blocks_chanses.items()
        }

    def render(self, visitor: Visitor) -> None:
        self.entry_point.render(visitor)

    def gen(self) -> None:
        env_copy = self.env.copy()

        var = env_copy.create_new_var()
        value = rd.randint(0, DefineBlock.max_value)
        def_block: Block = DefineBlock(var, value)

        next_blocks: List[Block] = [def_block]
        next_blocks.extend(self.__gen_local(env_copy))
        self.entry_point = EntryPointBlock(next_blocks)

    def __gen_local(self, env: Scope) -> List[Block]:
        env.current_depth -= 1
        if env.current_depth <= 0:
            return []
        gen_blocks: List[Block] = []
        number_of_blocks = rd.randint(*self.probs.blocks_cut)
        for _ in range(number_of_blocks):
            next_block = get_random_key(self.gen_functions_probabilities)(env)
            gen_blocks.append(next_block)
        return gen_blocks

    def __gen_for(self, env: Scope) -> ForBlock:
        env_copy = env.copy()

        def_var = env_copy.create_new_var(prefix="f")
        cond = ApplyBinOperator(def_var, str(rd.randint(2, ForBlock.max_value)), "<=")
        next_blocks = self.__gen_local(env_copy)

        block = ForBlock(def_var, cond, next_blocks)
        return block

    def __gen_if(self, env: Scope) -> IfConditionBlock:
        env_copy = env.copy()

        lvar, rvar = env_copy.get_random_vars(count=2)
        cond = ApplyBinOperator(lvar, rvar, env_copy.get_random_cond_operator())
        then_blocks = self.__gen_local(env.copy())
        else_blocks = self.__gen_local(env.copy())

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

    def __gen_switch(self, env: Scope) -> SwitchCaseBlock:
        """
        Method that generate switch-case block.
        :param env: environment that keeps all for creating new lines of code.
        :return: object of class SwitchCaseBlock
        """
        env_copy = env.copy()

        lvar, rvar = env_copy.get_random_vars(count=2)
        operator = env_copy.get_random_operator()
        rvar = f"(D0({rvar}))" if operator == "/" else rvar
        expr = ApplyBinOperator(lvar, rvar, operator)
        cases = [rd.randint(-100000, 100000) for _ in range(rd.randint(0, 3))]
        case_blocks = [self.__gen_local(env.copy()) for _ in range(len(cases) + 1)]

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
    max_depth: int = 5,
    operators: List[str] | None = None,
    cond_operators: List[str] | None = None,
    **kwargs: int,
) -> str:

    ch_for = kwargs.get("ch_for", 12)
    ch_if = kwargs.get("ch_if", 12)
    ch_state = kwargs.get("ch_state", 12)
    ch_def = kwargs.get("ch_def", 12)
    ch_switch = kwargs.get("ch_switch", 12)

    if operators is None:
        operators = ["+", "-", "/", "*"]

    if cond_operators is None:
        cond_operators = ["<", "<=", ">", ">=", "==", "!="]

    seed = rd.randint(1, 1000)

    probs = Probabilities(
        blocks_chanses={
            ForBlock: ch_for,
            IfConditionBlock: ch_if,
            DefineBlock: ch_def,
            OperationBlock: ch_state,
            SwitchCaseBlock: ch_switch,
        },
        blocks_cut=(2, 10),
    )

    scope = Scope(max_depth, operators, cond_operators)
    g = Generator(scope, probs, random_seed=seed)
    acc = Accum()
    g.gen()
    g.render(acc)
    return acc.get_acc()
