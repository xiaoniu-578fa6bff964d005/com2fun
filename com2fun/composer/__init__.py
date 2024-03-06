from abc import ABC, abstractmethod
from collections import defaultdict, namedtuple
import functools
import ast
from ..func_def import FunctionDefinition
from ..llm_utils import LLMInput


ReadOut = namedtuple(
    "ReadOut", ["cmd", "serialize", "deserialize", "stop"], defaults=[[]]
)
recommend_read_out = defaultdict()
recommend_read_out[str] = ReadOut(
    "print({})",
    lambda x: x,
    lambda x: x,
)


# cannot be replaced with bool(x) because bool("False")==True
def _bool_parse(x: str):
    x = x.strip()
    if x in ["True", "False"]:
        return x == "True"
    else:
        raise ValueError("Invalid boolean value: {}".format(x))


recommend_read_out[bool] = ReadOut(
    "{}",
    lambda x: repr(x),
    _bool_parse,
)


def _naive_parse(t: type, x: str):
    return t(x)


for t in [int, float]:
    recommend_read_out[t] = ReadOut(
        "{}",
        lambda x: repr(x),
        functools.partial(_naive_parse, t),
    )
read_out_struct_eval = ReadOut(
    "{}",
    lambda x: repr(x),
    lambda x: ast.literal_eval(x),
)
recommend_read_out.default_factory = lambda: read_out_struct_eval


class Composer(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def __call__(
        self, func_def: FunctionDefinition, *args, **kwargs
    ) -> (LLMInput, ReadOut):
        """Compose the input to the language model."""


from .python_interpreter import (
    CompletionComposer as DefaultCompletionComposer,
    ChatComposer as DefaultChatComposer,
)
