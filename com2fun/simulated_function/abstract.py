from abc import ABC, abstractmethod
from typing import Any
import functools

from ..func_def import InOutExample, FunctionDefinition
from ..composer import Composer


class InvalidCompletionResult(Exception):
    def __init__(self, message, data):
        self.message = message
        self.data = data
        super().__init__(self.message)

    def __str__(self):
        return self.message + "\n" + str(self.data)


class SimulatedFunction(ABC):
    def __init__(
        self,
        func_def: FunctionDefinition,
        composer: Composer,
    ):
        self.func_def = func_def
        self.composer = composer
        super().__init__()

    @abstractmethod
    def invoke(self, *args, **kwargs) -> dict[str, Any]:
        """
        Should return a dictionary, where
        'return' is the return value of the function and
        the rest is the details of the function call including prompt, param(eters for OpenAI API), (full) response etc.
        """

    @abstractmethod
    async def ainvoke(self, *args, **kwargs) -> dict[str, Any]:
        """async version of invoke"""

    def __call__(self, *args, **kwargs):
        self.check_arg(*args, **kwargs)
        return self.invoke(*args, **kwargs)["return"]

    async def acall(self, *args, **kwargs):
        self.check_arg(*args, **kwargs)
        return (await self.ainvoke(*args, **kwargs))["return"]

    def add_example(self, *args, **kwargs):
        self.check_arg(*args, **kwargs)
        examples = self.func_def.extension.examples

        def _add_example(examples, result, explanation=None):
            exam = InOutExample(args, kwargs, result, explanation)
            if exam.id() in examples:
                if not result == examples[exam.id()].result:
                    raise ValueError(
                        f"Example {exam.id()} already exists with different result. Old: {examples[exam.id()].result}. New: {result}"
                    )
            else:
                examples[exam.id()] = exam

        return functools.partial(_add_example, examples)

    def check_arg(self, *args, **kwargs):
        if self.func_def.intension.signature is None:
            return
        return self.func_def.intension.signature.bind(*args, **kwargs)
