import random as rd
from copy import copy
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Protocol, Type, TypeVar

from typing_extensions import Self

from src.generators.weigths_for_block import WeightsForBlocks

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
    def __init__(self, env: Scope, probs: WeightsForBlocks) -> None: ...

    def render(self, visitor: Visitor) -> None: ...


class DefineBlock(Block):
    max_value = 100

    def __init__(self, env: Scope, _: WeightsForBlocks) -> None:
        self.var = env.create_new_var()
        self.value = rd.randint(0, DefineBlock.max_value)

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
    def __init__(self, env: Scope, _: WeightsForBlocks) -> None:
        rule: Callable[[str], bool] = lambda x: x.startswith("a")
        self.cur_var = env.get_random_var(rule=rule)

        operator = env.get_random_operator()
        lvar, rvar = env.get_random_var(), env.get_random_var()
        rvar = f"(D0({rvar}))" if operator == "/" else rvar

        self.statement = ApplyBinOperator(lvar, rvar, operator)

    def render(self, visitor: Visitor) -> None:
        string = f"{self.cur_var} = {self.statement.render()};"
        visitor.send(string)


class IfConditionBlock(Block):
    def __init__(self, env: Scope, _: WeightsForBlocks) -> None:
        lvar, rvar = env.get_random_vars(count=2)
        self.condition = ApplyBinOperator(lvar, rvar, env.get_random_cond_operator())
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
    max_value = 1000

    def __init__(self, env: Scope, _: WeightsForBlocks) -> None:
        self.def_var = env.create_new_var(prefix="f")
        self.condition = ApplyBinOperator(self.def_var, str(rd.randint(2, ForBlock.max_value)), "<=")
        self.next_blocks: List[Block] = []

    def render(self, visitor: Visitor) -> None:
        string = f"for (int {self.def_var} = 0; {self.condition.render()}; {self.def_var}++) {{"
        visitor.send(string)
        for block in self.next_blocks:
            block.render(visitor)
        visitor.send("}")


class EntryPointBlock(Block):
    def __init__(self, env: Scope, probs: WeightsForBlocks):
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
    def __init__(
        self,
        scope: Scope,
        weights: WeightsForBlocks,
        random_seed: int | None = 42,
        **_: Dict[str, int],
    ) -> None:
        self.weights = weights
        rd.seed(random_seed)
        self.env = scope
        self.block_generation_functions: Dict[Type[Block], Callable[[Scope], Block]] = {
            DefineBlock: self.__gen_definition,
            ForBlock: self.__gen_for,
            IfConditionBlock: self.__gen_if,
            OperationBlock: self.__gen_operation,
        }
        self.gen_funs_add_blocks = {
            self.__gen_definition: self.weights.def_block,
            self.__gen_operation: self.weights.calc_block,
            self.__gen_if: self.weights.if_block,
            self.__gen_for: self.weights.for_block,
        }
        self.gen_funs_without_blocks = {
            self.__gen_definition: self.weights.def_block,
            self.__gen_operation: self.weights.calc_block,
        }

    def render(self, visitor: Visitor) -> None:
        self.entry_point.render(visitor)

    def gen(self) -> None:
        env_copy = self.env.copy()
        self.entry_point = EntryPointBlock(env_copy, self.weights)
        def_block: Block = DefineBlock(env_copy, self.weights)
        self.entry_point.next_blocks.append(def_block)
        self.entry_point.next_blocks.extend(self.__gen_local(env_copy))

    def __gen_local(self, env: Scope) -> List[Block]:
        env.current_depth -= 1
        if env.current_depth <= 0:
            return []
        gen_blocks: List[Block] = []
        number_of_blocks = rd.randint(*self.weights.blocks_cut)
        for _ in range(number_of_blocks):
            if env.current_depth == 1:
                next_block = get_random_key(self.gen_funs_without_blocks)(env)
            else:
                next_block = get_random_key(self.gen_funs_add_blocks)(env)
            gen_blocks.append(next_block)
        return gen_blocks

    def __gen_for(self, env: Scope) -> ForBlock:
        env_copy = env.copy()
        block = ForBlock(env_copy, self.weights)
        block.next_blocks = self.__gen_local(env_copy)
        return block

    def __gen_if(self, env: Scope) -> IfConditionBlock:
        env_copy = env.copy()
        block = IfConditionBlock(env_copy, self.weights)
        block.then_blocks = self.__gen_local(env.copy())
        block.else_blocks = self.__gen_local(env.copy())
        return block

    def __gen_operation(self, env: Scope) -> OperationBlock:
        return OperationBlock(env, self.weights)

    def __gen_definition(self, env: Scope) -> DefineBlock:
        return DefineBlock(env, self.weights)


class Accum:
    def __init__(self) -> None:
        self.acc = ""

    def send(self, string: str) -> None:
        self.acc += string

    def get_acc(self) -> str:
        return self.acc


def gen_test(
    weights_for_block: WeightsForBlocks,
    max_depth: int = 5,
    operators: List[str] | None = None,
    cond_operators: List[str] | None = None,
) -> str:

    if operators is None:
        operators = ["+", "-", "/", "*"]

    if cond_operators is None:
        cond_operators = ["<", "<=", ">", ">=", "==", "!="]

    seed = rd.random()

    scope = Scope(max_depth, operators, cond_operators)
    g = Generator(scope, weights_for_block, random_seed=seed)
    acc = Accum()
    g.gen()
    g.render(acc)
    return acc.get_acc()
