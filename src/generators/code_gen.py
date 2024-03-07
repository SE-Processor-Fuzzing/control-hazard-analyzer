import random as rd
from copy import copy
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Protocol, Tuple, TypeVar

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
    blocks_chanses: Dict[Callable[["Scope"], "Block"], int]
    operators_chanses: Dict[str, int]
    conditions_chanses: Dict[str, int]
    blocks_cut: Tuple[int, int]


class Scope:

    def __init__(
        self,
        blocks_count: int,
        bin_operators: Optional[List[str]] = None,
        condition_operators: Optional[List[str]] = None,
    ) -> None:
        if bin_operators is None:
            bin_operators = ["+", "-", "/", "*"]
        if condition_operators is None:
            condition_operators = [">", "<", ">=", "<=", "==", "!="]
        self.bin_operators = bin_operators
        self.condition_operators = condition_operators
        self.blocks_count = blocks_count
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

    def copy(self) -> Self:
        c = copy(self)
        c.vars = self.vars[:]
        return c


class Block(Protocol):
    def __init__(self, env: Scope, probs: Probabilities) -> None: ...

    def render(self, visitor: Visitor) -> None: ...


class DefineBlock(Block):
    max_value = 100

    def __init__(self, env: Scope, _: Probabilities) -> None:
        self.var = env.create_new_var()
        self.value = rd.randint(0, DefineBlock.max_value)

    def render(self, visitor: Visitor) -> None:
        string = f"int {self.var} = {self.value};"
        visitor.send(string)


class OperationBlock(Block):
    def __init__(self, env: Scope, probs: Probabilities) -> None:
        rule: Callable[[str], bool] = lambda x: x.startswith("a")
        self.env = env
        self.cur_var = env.get_random_var(rule=rule)
        self.operator = get_random_key(probs.operators_chanses)
        self.var_1, self.var_2 = env.get_random_var(), env.get_random_var()

    def render(self, visitor: Visitor) -> None:
        self.var_2 = f"(D0({self.var_2}))" if self.operator == "/" else self.var_2
        string = f"{self.cur_var} = {self.var_1} {self.operator} {self.var_2};"
        visitor.send(string)


@dataclass
class Condition:
    lvar: str
    rvar: str
    operator: str

    def render(self) -> str:
        return f"{self.lvar} {self.operator} {self.rvar}"


class IfConditionBlock(Block):
    def __init__(self, env: Scope, probs: Probabilities) -> None:
        lvar, rvar = env.get_random_vars(count=2)
        self.condition = Condition(lvar, rvar, get_random_key(probs.conditions_chanses))
        self.then_blocks: List[Block] = []
        self.else_blocks: List[Block] = []

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

    def __init__(self, env: Scope, _: Probabilities) -> None:
        self.def_var = env.create_new_var(prefix="f")
        self.condition = Condition(self.def_var, str(rd.randint(2, ForBlock.max_value)), "<=")
        self.next_blocks: List[Block] = []

    def render(self, visitor: Visitor) -> None:
        string = f"for (int {self.def_var} = 0; {self.condition.render()}; {self.def_var}++) {{"
        visitor.send(string)
        for block in self.next_blocks:
            block.render(visitor)
        visitor.send("}")


class EntryPointBlock(Block):
    def __init__(self, env: Scope, probs: Probabilities):
        self.env = env
        self.probs = probs
        self.next_blocks: List[Block] = []
        self.blocks_cut = probs.blocks_cut

    def render(self, visitor: Visitor) -> None:
        string = "# define D0(x) (x==0) ? 1 : x\n\nvoid test_fun() {"
        visitor.send(string)
        for block in self.next_blocks:
            block.render(visitor)
        visitor.send("}")


class Generator:
    def __init__(self, random_seed: int, blocks_count: int, probs: Probabilities) -> None:
        self.probs = probs
        rd.seed(random_seed)
        self.env = Scope(blocks_count)
        self.block_generation_functions = [self.__gen_definition, self.__gen_for, self.__gen_if, self.__gen_statement]

    def render(self, visitor: Visitor) -> None:
        self.entry_point.render(visitor)

    def gen(self) -> None:
        env_copy = self.env.copy()
        self.entry_point = EntryPointBlock(env_copy, self.probs)
        def_block: Block = DefineBlock(env_copy, self.probs)
        self.entry_point.next_blocks.append(def_block)
        self.entry_point.next_blocks.extend(self.__gen_local(env_copy))

    def __gen_local(self, env: Scope) -> List[Block]:
        env.blocks_count -= 1
        if env.blocks_count <= 0:
            return []
        gen_blocks: List[Block] = []
        number_of_blocks = rd.randint(*self.probs.blocks_cut)
        for _ in range(number_of_blocks):
            next_block = get_random_key(self.probs.blocks_chanses)(env)
            gen_blocks.append(next_block)
        return gen_blocks

    def __gen_for(self, env: Scope) -> ForBlock:
        env_copy = env.copy()
        block = ForBlock(env_copy, self.probs)
        block.next_blocks = self.__gen_local(env_copy)
        return block

    def __gen_if(self, env: Scope) -> IfConditionBlock:
        env_copy = env.copy()
        block = IfConditionBlock(env_copy, self.probs)
        block.then_blocks = self.__gen_local(env.copy())
        block.else_blocks = self.__gen_local(env.copy())
        return block

    def __gen_statement(self, env: Scope) -> OperationBlock:
        return OperationBlock(env, self.probs)

    def __gen_definition(self, env: Scope) -> DefineBlock:
        return DefineBlock(env, self.probs)
