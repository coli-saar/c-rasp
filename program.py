import operator
import sys
import traceback
from dataclasses import dataclass, field
from typing import Union, Callable
import inspect

from tracing import Trace
import predefined

@dataclass
class Environment:
    tokens: list[Union[str, int]]
    vars: dict[str, Union[list[bool], list[int]]] = field(default_factory=dict)
    c_star: bool = False
    binary_functions: dict[str, Callable[[int, int], bool]] = field(default_factory=dict)


def parse_token(token: Union[str, int]) -> Union[str, int]:
    if isinstance(token, int):
        if token < 0:
            raise ValueError("Object IDs must be nonnegative integers")
        return token
    try:
        value = int(token)
    except ValueError:
        return token
    if value < 0:
        raise ValueError("Object IDs must be nonnegative integers")
    return value


class BoolExpr:
    def evaluate(self, env: Environment) -> list[bool]:
        pass


class CountExpr:
    def evaluate(self, env: Environment) -> list[int]:
        pass


# boolean expressions

@dataclass
class BoolLiteral(BoolExpr):
    value: bool

    def evaluate(self, env:Environment) -> list[bool]:
        return [self.value] * len(env.tokens)

@dataclass
class StringLiteral(BoolExpr):
    value: str

    def evaluate(self, env: Environment) -> list[bool]:
        if env.c_star:
            try:
                int(self.value)
            except ValueError:
                pass
            else:
                raise ValueError("Object IDs cannot be queried as literals in C*-RASP; use match")
        return [tok == self.value for tok in env.tokens]

@dataclass
class BoolVariable(BoolExpr):
    name: str

    def evaluate(self, env: Environment) -> list[bool]:
        return env.vars[self.name]

@dataclass
class NotExpr(BoolExpr):
    expr: BoolExpr

    def evaluate(self, env: Environment) -> list[bool]:
        return [not x for x in self.expr.evaluate(env)]

@dataclass
class BinaryBoolExpr(BoolExpr):
    left: BoolExpr
    op: str
    right: BoolExpr
    _op: Callable = field(init=False)

    def __post_init__(self):
        if self.op == 'and':
            self._op = lambda a, b: a and b
        else: # or
            self._op = lambda a, b: a or b

    def evaluate(self, env: Environment) -> list[bool]:
        return [self._op(a,b) for a, b in zip(self.left.evaluate(env), self.right.evaluate(env))]

_comparison_dict = {
    '==': operator.eq,
    '!=': operator.ne,
    '<': operator.lt,
    '>': operator.gt,
    '<=': operator.le,
    '>=': operator.ge
}

@dataclass
class Comparison(BoolExpr):
    left: CountExpr
    op: str  # '<' or '==' or '<=' or ...
    right: CountExpr
    _op: Callable  = field(init=False)

    def __post_init__(self):
        self._op = _comparison_dict[self.op]

    def evaluate(self, env: Environment) -> list[bool]:
        return [self._op(val1, val2) for val1, val2 in zip(self.left.evaluate(env), self.right.evaluate(env))]



# count expressions

@dataclass
class CountLiteral(CountExpr):
    value: int

    def evaluate(self, env: Environment) -> list[int]:
        return [self.value] * len(env.tokens)


@dataclass
class CountVariable(CountExpr):
    name: str

    def evaluate(self, env: Environment) -> list[int]:
        return env.vars[self.name]

@dataclass
class Count(CountExpr):
    expr: BoolExpr

    def evaluate(self, env: Environment) -> list[int]:
        bools = self.expr.evaluate(env)
        count_of_trues = 0
        counts = []

        for i, val in enumerate(bools):
            if val:
                count_of_trues += 1
            counts.append(count_of_trues)

        return counts

@dataclass
class MatchPredicate:
    # Definition 3.3: c[j - delta[k]] = c[i - gamma[k]] + tau[k].
    constraints: list[tuple[int, int, int]]

    def __post_init__(self):
        if any(type(item) is not tuple or len(item) != 3 for item in self.constraints):
            raise ValueError("Match constraints must be (delta, gamma, tau) tuples")
        if any(type(offset) is not int for item in self.constraints for offset in item):
            raise ValueError("Match offsets must be integers")
        if any(delta < 0 or gamma < 0 for delta, gamma, _ in self.constraints):
            raise ValueError("Match position offsets must be nonnegative lookbacks")

    def matches(self, tokens: list[Union[str, int]], i: int, j: int) -> bool:
        for delta, gamma, tau in self.constraints:
            earlier, current = j - delta, i - gamma
            if not (0 <= earlier < len(tokens) and 0 <= current < len(tokens)):
                return False
            left, right = tokens[earlier], tokens[current]
            if type(left) is not int or type(right) is not int:
                return False
            if left != right + tau:
                return False
        return True


@dataclass
class Match(CountExpr):
    predicate: MatchPredicate
    expr: BoolExpr
    inclusive: bool = True

    def evaluate(self, env: Environment) -> list[int]:
        if not env.c_star:
            raise ValueError("match requires C*-RASP mode (--c-star)")
        bools = self.expr.evaluate(env)
        counts = []

        for i in range(len(env.tokens)):
            count = 0
            for j in range(i + int(self.inclusive)):
                if bools[j] and self.predicate.matches(env.tokens, i, j):
                    count += 1
            counts.append(count)

        return counts


@dataclass
class GuardedCount(CountExpr):
    expr: BoolExpr
    guard: str

    def evaluate(self, env: Environment) -> list[int]:
        bools: list[bool] = self.expr.evaluate(env) # value of expr at each position
        counts: list[int] = []

        guard_func = env.binary_functions[self.guard]

        for i, val in enumerate(bools):
            count_of_trues = 0

            for j in range(i + 1):
                if not bools[j]:
                    continue
                if not guard_func(i, j):
                    continue
                count_of_trues += 1

            counts.append(count_of_trues)

        return counts


@dataclass
class BinaryOp(CountExpr):
    left: CountExpr
    op: str  # '+' or '-'  or 'min' or 'max'
    right: CountExpr
    _op: Callable  = field(init=False)

    def __post_init__(self):
        if self.op == '+':
            self._op = operator.add
        elif self.op == '-':
            self._op = operator.sub
        elif self.op == 'min':
            self._op = min
        else: # max
            self._op = max

    def combine(self, val1: int, val2: int) -> bool:
        return self._op(val1, val2)

    def evaluate(self, env: Environment) -> list[int]:
        return [self.combine(val1, val2) for val1, val2 in zip(self.left.evaluate(env), self.right.evaluate(env))]

@dataclass
class MultiplicationOp(CountExpr):
    factor: int
    expr: CountExpr

    def evaluate(self, env: Environment) -> list[int]:
        return [self.factor * val for val in self.expr.evaluate(env)]

@dataclass
class IfExpr(CountExpr):
    then_branch: CountExpr
    condition: BoolExpr
    else_branch: CountExpr

    def evaluate(self, env: Environment) -> list[int]:
        condition_vals = self.condition.evaluate(env)
        then_vals = self.then_branch.evaluate(env)
        else_vals = self.else_branch.evaluate(env)

        ret = []
        for i in range(len(condition_vals)):
            if condition_vals[i]:
                ret.append(then_vals[i])
            else:
                ret.append(else_vals[i])

        return ret


## program

@dataclass
class Assignment:
    variable: str
    expression: Union[BoolExpr, CountExpr]

@dataclass
class Program:
    statements: list[Assignment]
    imports: list[str]
    c_star: bool = False

    def execute(self, tokens, verbose=False, tracing: Trace = None, c_star: bool = False) -> bool:
        c_star = c_star or self.c_star
        # initialize empty environment with the given tokens
        tokens = [parse_token(token) for token in tokens] if c_star else list(tokens)
        env = Environment(tokens, c_star=c_star)
        most_recent_value = None

        # import predefined functions
        for imp in self.imports:
            func = getattr(predefined, imp)
            params = list(inspect.signature(func).parameters.values())

            if len(params) == 1:
                # unary function - evaluate it on all input positions and store results as variables
                values = [func(i) for i in range(len(tokens))]
                env.vars[imp] = values
            elif len(params) == 2:
                # binary function - store function itself
                env.binary_functions[imp] = func

        # set up tracing
        if tracing is not None:
            tracing.accept_tokens(tokens)

        # execute program
        for i, assignment in enumerate(self.statements):
            try:

                val = assignment.expression.evaluate(env)
                env.vars[assignment.variable] = val
                most_recent_value = val

                if tracing is not None:
                    tracing.accept(assignment.variable, val)

                if verbose:
                    print(assignment.variable)
                    print(val)
                    print()

            except Exception as e:
                print(f"Exception in statement {i+1}:", file=sys.stderr)
                print(f"Statement: {assignment}", file=sys.stderr)
                traceback.print_exc()
                sys.exit(1)

        if c_star and (not most_recent_value or type(most_recent_value[-1]) is not bool):
            raise ValueError("The final C*-RASP statement must be Boolean")

        if tracing is not None:
            tracing.accept_result(most_recent_value[-1])

        return most_recent_value[-1]
