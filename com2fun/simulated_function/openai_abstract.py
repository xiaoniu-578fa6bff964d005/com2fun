#!/usr/bin/env python
# -*- coding: utf-8 -*-

import openai

from abc import abstractmethod
from collections import namedtuple
import functools
import ast

from . import InvalidCompletionResult, SimulatedFunction

DEFAULT_PARAM = {
    "model": "text-davinci-003",
    #  "model": "code-davinci-002",
    "best_of": 1,
    "temperature": 0.0,
    "max_tokens": 2048,
    "stream": False,
}

ReadOut = namedtuple("ReadOut", ["cmd", "serialize", "deserialize"])


class SimpleOpenAISF(SimulatedFunction):
    """
    This class should emit exactly one prompt and the completion output should be serialization of the result.
    """

    default_param = {}

    def __init__(self, *args, **kwargs):
        self.param = {}
        super().__init__(*args, **kwargs)

    @abstractmethod
    def invoke_prompt(self, *args, **kwargs) -> str:
        """Should return the prompt that is posted to OpenAI API"""

    def invoke_read_out_method(self) -> ReadOut:
        # get return type
        sig = self.func_def.intension.signature
        return_type = sig.return_annotation
        if return_type in recommand_read_out:
            return recommand_read_out[return_type]
        return read_out_struct_eval

    def invoke_param(self) -> dict:
        return {**DEFAULT_PARAM, **type(self).default_param, **self.param}

    def invoke(self, *args, **kwargs):
        prompt = self.invoke_prompt(*args, **kwargs)
        param = self.invoke_param()

        response = openai.Completion.create(prompt=prompt, **param)
        result_str = response["choices"][0]["text"]
        r = {
            "prompt": prompt,
            "param": param,
            "response": response,
            "result_str": result_str,
        }
        try:
            result = self.invoke_read_out_method().deserialize(result_str)
        except Exception as e:
            raise InvalidCompletionResult(
                "The completion result is not serializable.",
                {
                    **r,
                    "error": e,
                },
            )
        return {
            **r,
            "return": result,
        }


# cmd is the one line python command that could be used in python interpreter
# to let the serialized result shows up in console. It should contain a single
# positional argument that is the name of the variable that contains the result.
ReadOut = namedtuple("ReadOut", ["cmd", "serialize", "deserialize"])
recommand_read_out = {}
recommand_read_out[str] = ReadOut(
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


recommand_read_out[bool] = ReadOut(
    "{}",
    lambda x: repr(x),
    _bool_parse,
)


def _naive_parse(t: type, x: str):
    return t(x)


for t in [int, float]:
    recommand_read_out[t] = ReadOut(
        "{}",
        lambda x: repr(x),
        functools.partial(_naive_parse, t),
    )

read_out_struct_eval = ReadOut(
    "{}",
    lambda x: repr(x),
    lambda x: ast.literal_eval(x),
)
